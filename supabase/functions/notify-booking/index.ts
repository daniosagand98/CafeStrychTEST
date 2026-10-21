// Cafe Strych – powiadomienia push o nowych rezerwacjach (Supabase Edge Function)
// Wywołuje ją baza danych (trigger po dodaniu rezerwacji – patrz supabase_v3_6.sql).
// Wysyła powiadomienie na telefony kierowników i administratorów, którzy je włączyli.
//
// Sekrety (Supabase → Edge Functions → Secrets):
//   VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY, VAPID_SUBJECT (mailto:...), APP_URL (adres panelu, np. https://cafestrychgdynia.pl/panel/)
// SUPABASE_URL i SUPABASE_SERVICE_ROLE_KEY Supabase podaje funkcji automatycznie.
// Ustawienie funkcji: „Verify JWT” WYŁĄCZONE (baza wywołuje ją bez logowania; ochrona jest niżej).

import webpush from "npm:web-push@3.6.7";
import { createClient } from "npm:@supabase/supabase-js@2";

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

Deno.serve(async (req) => {
  if (req.method !== "POST") return json({ error: "POST only" }, 405);

  let id = "";
  try {
    const body = await req.json();
    id = String(body?.id ?? body?.record?.id ?? "");
  } catch { /* puste body */ }
  if (!/^[0-9a-f-]{36}$/i.test(id)) return json({ error: "brak id rezerwacji" }, 400);
  if (!Deno.env.get("VAPID_PUBLIC_KEY") || !Deno.env.get("VAPID_PRIVATE_KEY")) {
    console.error("Brak sekretów VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY – dodaj je w Edge Functions → Secrets");
    return json({ error: "brak sekretów VAPID" }, 500);
  }

  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
    auth: { persistSession: false },
  });

  // Ochrona przed nadużyciem: wysyłamy tylko dla prawdziwej, świeżej rezerwacji i tylko raz.
  const { data: booking, error } = await sb.from("bookings").select("*").eq("id", id).maybeSingle();
  if (error || !booking) return json({ skipped: "nie ma takiej rezerwacji" });
  if (booking.push_sent_at) return json({ skipped: "już wysłano" });
  if (Date.now() - new Date(booking.created_at ?? Date.now()).getTime() > 15 * 60 * 1000) {
    return json({ skipped: "rezerwacja nie jest nowa" });
  }
  const claim = await sb.from("bookings").update({ push_sent_at: new Date().toISOString() })
    .eq("id", id).is("push_sent_at", null).select("id");
  if (!claim.data?.length) return json({ skipped: "już wysłano" });

  // Odbiorcy: aktywni kierownicy i administratorzy, poza autorem rezerwacji
  const { data: staff } = await sb.from("profiles").select("id").in("role", ["admin", "manager"]).or("active.is.null,active.eq.true");
  const ids = (staff ?? []).map((p) => p.id).filter((uid) => uid !== booking.created_by);
  if (!ids.length) return json({ sent: 0, reason: "brak odbiorców" });

  const { data: subs } = await sb.from("push_subscriptions")
    .select("id, endpoint, p256dh, auth").in("user_id", ids).eq("notify_bookings", true);
  if (!subs?.length) return json({ sent: 0, reason: "nikt nie włączył powiadomień" });

  webpush.setVapidDetails(
    Deno.env.get("VAPID_SUBJECT") ?? "mailto:admin@example.com",
    Deno.env.get("VAPID_PUBLIC_KEY")!,
    Deno.env.get("VAPID_PRIVATE_KEY")!,
  );

  const start = new Date(booking.start_at);
  const tz = "Europe/Warsaw";
  const day = start.toLocaleDateString("sv-SE", { timeZone: tz }); // RRRR-MM-DD
  const when = start.toLocaleDateString("pl-PL", { timeZone: tz, weekday: "short", day: "numeric", month: "numeric" }) +
    ", " + start.toLocaleTimeString("pl-PL", { timeZone: tz, hour: "2-digit", minute: "2-digit" });
  const notes = String(booking.notes ?? "");
  const kind = booking.whole_room ? " • cała sala" : notes.includes("CAŁEGO LOKALU") ? " • cały lokal" : notes.includes("SALI") ? " • sala" : "";
  const appUrl = (Deno.env.get("APP_URL") ?? "./").replace(/\/?$/, "/");

  const payload = JSON.stringify({
    title: `Nowa rezerwacja${booking.source === "www" ? " ze strony" : ""}`,
    body: `${booking.title ?? "Gość"} • ${booking.guests_count ?? "?"} os. • ${when}${kind}`,
    tag: `booking-${booking.id}`,
    url: `${appUrl}?day=${day}`,
  });

  let sent = 0, removed = 0;
  await Promise.all(subs.map(async (s) => {
    try {
      await webpush.sendNotification({ endpoint: s.endpoint, keys: { p256dh: s.p256dh, auth: s.auth } }, payload, { TTL: 86400, urgency: "high" });
      sent++;
    } catch (e) {
      const code = (e as { statusCode?: number }).statusCode;
      if (code === 404 || code === 410) { // urządzenie wyrejestrowane – usuń
        await sb.from("push_subscriptions").delete().eq("id", s.id);
        removed++;
      } else {
        console.error("push error", code, (e as Error).message);
      }
    }
  }));

  return json({ sent, removed });
});
