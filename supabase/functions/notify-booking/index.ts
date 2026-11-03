// Cafe Strych – powiadomienia push o nowych rezerwacjach i zgłoszeniach błędów (Supabase Edge Function)
// V4.7: {"type":"bug","id":...} → powiadomienie dla administratorów o nowym zgłoszeniu błędu.
// V5.1.1: {"type":"message","id":...} → powiadomienie dla pracowników, do których kierownik wysłał wiadomość.
// V5.3: {"type":"chat","id":...} → czat (ogólny / prywatny, oznaczenia @osoba); {"type":"swap","id":...} → zamiany zmian.
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

  let id = "", type = "booking";
  try {
    const body = await req.json();
    id = String(body?.id ?? body?.record?.id ?? "");
    if (body?.type === "bug") type = "bug";
    if (body?.type === "message") type = "message";
    if (body?.type === "chat") type = "chat";
    if (body?.type === "swap") type = "swap";
  } catch { /* puste body */ }
  if (!/^[0-9a-f-]{36}$/i.test(id) && !(type === "message" && /^\d+$/.test(id))) return json({ error: "brak id" }, 400);
  if (!Deno.env.get("VAPID_PUBLIC_KEY") || !Deno.env.get("VAPID_PRIVATE_KEY")) {
    console.error("Brak sekretów VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY – dodaj je w Edge Functions → Secrets");
    return json({ error: "brak sekretów VAPID" }, 500);
  }

  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
    auth: { persistSession: false },
  });

  if (type === "bug") return await notifyBug(sb, id);
  if (type === "message") return await notifyMessage(sb, id);
  if (type === "chat") return await notifyChat(sb, id);
  if (type === "swap") return await notifySwap(sb, id);

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

// ---------- V4.7: zgłoszenia błędów → administratorzy ----------
// deno-lint-ignore no-explicit-any
async function notifyBug(sb: any, id: string) {
  const { data: bug, error } = await sb.from("bug_reports").select("*").eq("id", id).maybeSingle();
  if (error || !bug) return json({ skipped: "nie ma takiego zgłoszenia" });
  if (bug.push_sent_at) return json({ skipped: "już wysłano" });
  if (Date.now() - new Date(bug.created_at ?? Date.now()).getTime() > 15 * 60 * 1000) return json({ skipped: "zgłoszenie nie jest nowe" });
  const claim = await sb.from("bug_reports").update({ push_sent_at: new Date().toISOString() }).eq("id", id).is("push_sent_at", null).select("id");
  if (!claim.data?.length) return json({ skipped: "już wysłano" });

  const author = bug.reporter_id ?? bug.user_id ?? bug.created_by ?? null;
  const { data: admins } = await sb.from("profiles").select("id").eq("role", "admin").or("active.is.null,active.eq.true");
  const ids = (admins ?? []).map((p: { id: string }) => p.id).filter((uid: string) => uid !== author);
  if (!ids.length) return json({ sent: 0, reason: "brak odbiorców" });
  const { data: subs } = await sb.from("push_subscriptions").select("id, endpoint, p256dh, auth").in("user_id", ids).eq("notify_bugs", true);
  if (!subs?.length) return json({ sent: 0, reason: "nikt nie włączył powiadomień" });

  webpush.setVapidDetails(Deno.env.get("VAPID_SUBJECT") ?? "mailto:admin@example.com", Deno.env.get("VAPID_PUBLIC_KEY")!, Deno.env.get("VAPID_PRIVATE_KEY")!);
  const text = String(bug.description ?? bug.details ?? bug.message ?? "").replace(/\s+/g, " ").trim();
  const appUrl = (Deno.env.get("APP_URL") ?? "./").replace(/\/?$/, "/");
  const payload = JSON.stringify({
    title: "🐞 Nowe zgłoszenie błędu",
    body: `${bug.reporter_name ?? "Ktoś z zespołu"}${bug.page ? " • " + bug.page : ""}: ${text.slice(0, 120)}${text.length > 120 ? "…" : ""}`,
    tag: `bug-${bug.id}`,
    url: `${appUrl}?bugs=1`,
  });
  let sent = 0, removed = 0;
  await Promise.all(subs.map(async (s: { id: string; endpoint: string; p256dh: string; auth: string }) => {
    try { await webpush.sendNotification({ endpoint: s.endpoint, keys: { p256dh: s.p256dh, auth: s.auth } }, payload, { TTL: 86400 }); sent++; }
    catch (e) {
      const code = (e as { statusCode?: number }).statusCode;
      if (code === 404 || code === 410) { await sb.from("push_subscriptions").delete().eq("id", s.id); removed++; }
      else console.error("push error", code, (e as Error).message);
    }
  }));
  return json({ sent, removed });
}

// ---------- V5.1.1: wiadomości od kierownika → pracownicy ----------
// deno-lint-ignore no-explicit-any
async function notifyMessage(sb: any, id: string) {
  const { data: msg, error } = await sb.from("announcements").select("*").eq("id", id).maybeSingle();
  if (error || !msg) return json({ skipped: "nie ma takiej wiadomości" });
  if (msg.push_sent_at) return json({ skipped: "już wysłano" });
  if (Date.now() - new Date(msg.created_at ?? Date.now()).getTime() > 15 * 60 * 1000) return json({ skipped: "wiadomość nie jest nowa" });
  const claim = await sb.from("announcements").update({ push_sent_at: new Date().toISOString() }).eq("id", id).is("push_sent_at", null).select("id");
  if (!claim.data?.length) return json({ skipped: "już wysłano" });

  const { data: profiles } = await sb.from("profiles").select("id, email, full_name, active");
  const active = (profiles ?? []).filter((p: { active?: boolean }) => p.active !== false);
  const targets: string[] = Array.isArray(msg.target_employee_ids) ? msg.target_employee_ids.map(String) : [];
  const ids = new Set<string>();
  if (targets.length) {
    // pracownik z listy „Pracownicy” → jego konto (powiązanie, e-mail albo imię i nazwisko)
    const { data: emps } = await sb.from("employees").select("*").in("id", targets);
    const low = (v: unknown) => String(v ?? "").trim().toLowerCase();
    for (const e of emps ?? []) {
      const direct = e.user_id ?? e.profile_id;
      if (direct) { ids.add(String(direct)); continue; }
      const p = active.find((x: { email?: string; full_name?: string }) =>
        (e.email && low(x.email) === low(e.email)) || (e.full_name && low(x.full_name) === low(e.full_name)));
      if (p) ids.add(p.id);
    }
  } else {
    for (const p of active) ids.add(p.id);   // wiadomość do wszystkich
  }
  if (msg.created_by) ids.delete(String(msg.created_by));
  if (!ids.size) return json({ sent: 0, reason: "odbiorcy nie mają kont w aplikacji" });

  const { data: subs } = await sb.from("push_subscriptions").select("id, endpoint, p256dh, auth, notify_messages").in("user_id", [...ids]);
  const list = (subs ?? []).filter((s: { notify_messages?: boolean }) => s.notify_messages !== false);
  if (!list.length) return json({ sent: 0, reason: "nikt z odbiorców nie włączył powiadomień" });

  webpush.setVapidDetails(Deno.env.get("VAPID_SUBJECT") ?? "mailto:admin@example.com", Deno.env.get("VAPID_PUBLIC_KEY")!, Deno.env.get("VAPID_PRIVATE_KEY")!);
  const author = active.find((p: { id: string }) => p.id === msg.created_by)?.full_name || "Kierownik";
  const text = String(msg.message ?? msg.content ?? "").replace(/\s+/g, " ").trim();
  const appUrl = (Deno.env.get("APP_URL") ?? "./").replace(/\/?$/, "/");
  const payload = JSON.stringify({
    title: `✉️ Wiadomość od: ${author}`,
    body: text.slice(0, 160) + (text.length > 160 ? "…" : ""),
    tag: `msg-${msg.id}`,
    url: `${appUrl}?msg=1`,
  });
  let sent = 0, removed = 0;
  await Promise.all(list.map(async (s: { id: string; endpoint: string; p256dh: string; auth: string }) => {
    try { await webpush.sendNotification({ endpoint: s.endpoint, keys: { p256dh: s.p256dh, auth: s.auth } }, payload, { TTL: 86400, urgency: "high" }); sent++; }
    catch (e) {
      const code = (e as { statusCode?: number }).statusCode;
      if (code === 404 || code === 410) { await sb.from("push_subscriptions").delete().eq("id", s.id); removed++; }
      else console.error("push error", code, (e as Error).message);
    }
  }));
  return json({ sent, removed });
}

// ---------- V5.3: wspólne ----------
type Sub = { id: string; endpoint: string; p256dh: string; auth: string };
// deno-lint-ignore no-explicit-any
async function sendTo(sb: any, userIds: string[], flag: string, payload: Record<string, unknown>) {
  const ids = [...new Set(userIds.filter(Boolean))];
  if (!ids.length) return { sent: 0 };
  const { data: subs } = await sb.from("push_subscriptions").select("*").in("user_id", ids);
  // deno-lint-ignore no-explicit-any
  const list = (subs ?? []).filter((x: any) => x[flag] !== false);
  if (!list.length) return { sent: 0 };
  webpush.setVapidDetails(Deno.env.get("VAPID_SUBJECT") ?? "mailto:admin@example.com", Deno.env.get("VAPID_PUBLIC_KEY")!, Deno.env.get("VAPID_PRIVATE_KEY")!);
  const body = JSON.stringify(payload);
  let sent = 0;
  await Promise.all(list.map(async (x: Sub) => {
    try { await webpush.sendNotification({ endpoint: x.endpoint, keys: { p256dh: x.p256dh, auth: x.auth } }, body, { TTL: 86400, urgency: "high" }); sent++; }
    catch (e) {
      const code = (e as { statusCode?: number }).statusCode;
      if (code === 404 || code === 410) await sb.from("push_subscriptions").delete().eq("id", x.id);
      else console.error("push error", code, (e as Error).message);
    }
  }));
  return { sent };
}
const appBase = () => (Deno.env.get("APP_URL") ?? "./").replace(/\/?$/, "/");
const clip = (t: unknown, n = 160) => { const v = String(t ?? "").replace(/\s+/g, " ").trim(); return v.length > n ? v.slice(0, n) + "…" : v; };

// pracownik z listy „Pracownicy” → konto (powiązanie, e-mail albo imię i nazwisko)
// deno-lint-ignore no-explicit-any
async function employeeUsers(sb: any, empIds: string[]) {
  const ids = empIds.filter(Boolean);
  if (!ids.length) return [] as string[];
  const [{ data: emps }, { data: profs }] = await Promise.all([
    sb.from("employees").select("*").in("id", ids),
    sb.from("profiles").select("id, email, full_name, active"),
  ]);
  const low = (v: unknown) => String(v ?? "").trim().toLowerCase();
  const out: string[] = [];
  for (const e of emps ?? []) {
    const direct = e.user_id ?? e.profile_id;
    if (direct) { out.push(String(direct)); continue; }
    // deno-lint-ignore no-explicit-any
    const p = (profs ?? []).find((x: any) => x.active !== false &&
      ((e.email && low(x.email) === low(e.email)) || (e.full_name && low(x.full_name) === low(e.full_name))));
    if (p) out.push(p.id);
  }
  return out;
}

// ---------- V5.3: czat ----------
// deno-lint-ignore no-explicit-any
async function notifyChat(sb: any, id: string) {
  const { data: m } = await sb.from("chat_messages").select("*").eq("id", id).maybeSingle();
  if (!m) return json({ skipped: "brak wiadomości" });
  if (m.push_sent_at) return json({ skipped: "już wysłano" });
  if (Date.now() - new Date(m.created_at).getTime() > 15 * 60 * 1000) return json({ skipped: "stara wiadomość" });
  const claim = await sb.from("chat_messages").update({ push_sent_at: new Date().toISOString() }).eq("id", id).is("push_sent_at", null).select("id");
  if (!claim.data?.length) return json({ skipped: "już wysłano" });

  const who = m.sender_name || "Ktoś z zespołu";
  const url = `${appBase()}?chat=${encodeURIComponent(m.channel)}`;
  if (m.channel === "general") {
    const { data: profs } = await sb.from("profiles").select("id, active");
    // deno-lint-ignore no-explicit-any
    const all = (profs ?? []).filter((p: any) => p.active !== false && p.id !== m.sender_id).map((p: { id: string }) => p.id);
    const mentioned: string[] = (m.mentions ?? []).map(String).filter((x: string) => all.includes(x));
    const rest = all.filter((x: string) => !mentioned.includes(x));
    const a = await sendTo(sb, mentioned, "notify_chat", { title: `📣 ${who} oznaczył(a) Cię na czacie`, body: clip(m.body), tag: `chat-mention-${m.id}`, url });
    const b = await sendTo(sb, rest, "notify_chat", { title: `💬 ${who} • Czat ogólny`, body: clip(m.body), tag: "chat-general", url });
    return json({ sent: a.sent + b.sent });
  }
  const parts = String(m.channel).replace(/^dm:/, "").split(":");
  const to = parts.filter((x) => x !== m.sender_id);
  const r = await sendTo(sb, to, "notify_chat", { title: `💬 ${who}`, body: clip(m.body), tag: `chat-dm-${m.sender_id}`, url });
  return json(r);
}

// ---------- V5.3: zamiany zmian ----------
// deno-lint-ignore no-explicit-any
async function notifySwap(sb: any, id: string) {
  const { data: s } = await sb.from("shift_swaps").select("*").eq("id", id).maybeSingle();
  if (!s) return json({ skipped: "brak zamiany" });
  if (s.pushed_status === s.status) return json({ skipped: "już wysłano" });
  const claim = await sb.from("shift_swaps").update({ pushed_status: s.status }).eq("id", id).or(`pushed_status.is.null,pushed_status.neq.${s.status}`).select("id");
  if (!claim.data?.length) return json({ skipped: "już wysłano" });

  const ids = [s.shift_id, s.other_shift_id].filter(Boolean);
  const { data: shifts } = await sb.from("work_shifts").select("*").in("id", ids);
  const { data: emps } = await sb.from("employees").select("id, full_name").in("id", [s.from_employee, s.to_employee].filter(Boolean));
  // deno-lint-ignore no-explicit-any
  const nm = (eid: string) => (emps ?? []).find((e: any) => e.id === eid)?.full_name || "ktoś";
  // deno-lint-ignore no-explicit-any
  const sh = (sid: string) => (shifts ?? []).find((x: any) => x.id === sid);
  // deno-lint-ignore no-explicit-any
  const fmt = (x: any) => x ? `${new Date(x.shift_date + "T12:00:00").toLocaleDateString("pl-PL", { weekday: "short", day: "numeric", month: "numeric" })} ${String(x.start_time).slice(0, 5)}–${String(x.end_time).slice(0, 5)}` : "";
  const what = fmt(sh(s.shift_id)) + (s.other_shift_id ? ` ⇄ ${fmt(sh(s.other_shift_id))}` : "");
  const url = `${appBase()}?swaps=1`;
  const fromUsers = await employeeUsers(sb, [s.from_employee]);
  let r = { sent: 0 };

  if (s.status === "open") {
    let to: string[];
    if (s.to_employee) to = await employeeUsers(sb, [s.to_employee]);
    else {
      const { data: all } = await sb.from("employees").select("id").eq("active", true);
      // deno-lint-ignore no-explicit-any
      to = await employeeUsers(sb, (all ?? []).map((e: any) => e.id).filter((x: string) => x !== s.from_employee));
    }
    r = await sendTo(sb, to.filter((u) => !fromUsers.includes(u)), "notify_swaps", {
      title: s.other_shift_id ? `🔁 ${nm(s.from_employee)} proponuje zamianę` : `🔁 ${nm(s.from_employee)} oddaje zmianę`,
      body: what + (s.note ? ` • ${clip(s.note, 80)}` : ""), tag: `swap-${s.id}`, url });
  } else if (s.status === "accepted") {
    const { data: mgr } = await sb.from("profiles").select("id").in("role", ["admin", "manager"]).or("active.is.null,active.eq.true");
    // deno-lint-ignore no-explicit-any
    const a = await sendTo(sb, (mgr ?? []).map((p: any) => p.id), "notify_swaps", { title: "🔁 Zamiana czeka na zatwierdzenie", body: `${nm(s.from_employee)} → ${nm(s.to_employee)} • ${what}`, tag: `swap-${s.id}`, url });
    const b = await sendTo(sb, fromUsers, "notify_swaps", { title: `🔁 ${nm(s.to_employee)} przyjął(a) Twoją prośbę`, body: `${what} • czeka na zatwierdzenie kierownika`, tag: `swap-${s.id}`, url });
    r = { sent: a.sent + b.sent };
  } else if (s.status === "approved" || s.status === "rejected") {
    const toUsers = s.to_employee ? await employeeUsers(sb, [s.to_employee]) : [];
    const ok = s.status === "approved";
    r = await sendTo(sb, [...fromUsers, ...toUsers], "notify_swaps", { title: ok ? "✅ Zamiana zatwierdzona – grafik zmieniony" : "❌ Zamiana odrzucona", body: `${nm(s.from_employee)} → ${nm(s.to_employee)} • ${what}`, tag: `swap-${s.id}`, url });
  }
  return json(r);
}
