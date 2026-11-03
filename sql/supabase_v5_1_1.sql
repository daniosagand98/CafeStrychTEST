-- =====================================================================
-- Cafe Strych – V5.1.1 (03.11.2026) – powiadomienia o wiadomościach
-- Gdy kierownik wyśle wiadomość (Wiadomości do zespołu), wybrani
-- pracownicy dostają powiadomienie na telefon.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- PAMIĘTAJ też zaktualizować funkcję notify-booking (instrukcja w README).
-- =====================================================================

alter table public.push_subscriptions add column if not exists notify_messages boolean not null default true;
alter table public.announcements      add column if not exists push_sent_at timestamptz;

create or replace function public.notify_new_message() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  perform net.http_post(
    url     := 'https://dhqsjwanjrcblrhevfcq.supabase.co/functions/v1/notify-booking',
    headers := jsonb_build_object('Content-Type', 'application/json'),
    body    := jsonb_build_object('type', 'message', 'id', new.id)
  );
  return new;
exception when others then
  raise warning 'notify_new_message: %', sqlerrm;   -- powiadomienie nie może zablokować wysłania wiadomości
  return new;
end $$;
revoke execute on function public.notify_new_message() from public, anon, authenticated;

drop trigger if exists announcements_notify_push on public.announcements;
create trigger announcements_notify_push after insert on public.announcements
  for each row execute function public.notify_new_message();

notify pgrst, 'reload schema';
