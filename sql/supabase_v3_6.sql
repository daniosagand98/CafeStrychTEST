-- =====================================================================
-- Cafe Strych – POWIADOMIENIA PUSH O NOWYCH REZERWACJACH (V3.6, 19.10.2026)
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Najpierw wdróż funkcję notify-booking (instrukcja: POWIADOMIENIA.md).
-- Można uruchomić wielokrotnie.
-- =====================================================================

-- 1. Urządzenia (telefony/komputery), które włączyły powiadomienia ------
create table if not exists public.push_subscriptions (
  id              uuid primary key default gen_random_uuid(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  endpoint        text not null unique,
  p256dh          text not null,
  auth            text not null,
  device          text,
  notify_bookings boolean not null default true,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz
);
alter table public.push_subscriptions enable row level security;
grant select, insert, update, delete on public.push_subscriptions to authenticated;

drop policy if exists "push_subscriptions: własne urządzenia" on public.push_subscriptions;
create policy "push_subscriptions: własne urządzenia" on public.push_subscriptions
  for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());

-- 2. Znacznik „powiadomienie wysłane” (żeby nie wysłać dwa razy) -----------
alter table public.bookings add column if not exists push_sent_at timestamptz;
alter table public.bookings add column if not exists created_at timestamptz not null default now();

-- 3. Po dodaniu rezerwacji baza wywołuje funkcję notify-booking ----------
create extension if not exists pg_net;

create or replace function public.notify_new_booking() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  perform net.http_post(
    url     := 'https://dhqsjwanjrcblrhevfcq.supabase.co/functions/v1/notify-booking',
    headers := jsonb_build_object('Content-Type', 'application/json'),
    body    := jsonb_build_object('id', new.id)
  );
  return new;
exception when others then
  -- powiadomienie nie może nigdy zablokować zapisu rezerwacji
  raise warning 'notify_new_booking: %', sqlerrm;
  return new;
end $$;

drop trigger if exists bookings_notify_push on public.bookings;
create trigger bookings_notify_push
  after insert on public.bookings
  for each row execute function public.notify_new_booking();

-- odśwież listę tabel w API
notify pgrst, 'reload schema';
