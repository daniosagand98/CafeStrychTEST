-- =====================================================================
-- Cafe Strych – V3.8 (21.10.2026)
--   A) powiadomienia push o nowych rezerwacjach (to samo co v3.6 – jeśli już
--      uruchamiałeś v3.6, nic się nie zdubluje)
--   B) rachunki: opłaconych nie da się usunąć ani zmienić, tylko anulować
--      (opłacony – tylko administrator, z powodem); płatności są nieusuwalne
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

-- ============ A) POWIADOMIENIA =========================================
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

alter table public.bookings add column if not exists push_sent_at timestamptz;
alter table public.bookings add column if not exists created_at timestamptz not null default now();

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
revoke execute on function public.notify_new_booking() from public, anon, authenticated;

drop trigger if exists bookings_notify_push on public.bookings;
create trigger bookings_notify_push
  after insert on public.bookings
  for each row execute function public.notify_new_booking();

-- ============ B) ANULOWANIE RACHUNKÓW ==================================
alter table public.pos_orders add column if not exists cancelled_at  timestamptz;
alter table public.pos_orders add column if not exists cancelled_by  uuid;
alter table public.pos_orders add column if not exists cancel_reason text;

-- Strażnik rachunku: kto może zamknąć, anulować i usunąć
create or replace function public.pos_orders_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  -- operacje z panelu Supabase / serwera (bez zalogowanego użytkownika) – bez ograniczeń
  if auth.uid() is null then
    if tg_op = 'DELETE' then return old; end if;
    return new;
  end if;

  if tg_op = 'DELETE' then
    if old.status in ('paid', 'cancelled') or exists (select 1 from public.pos_payments where order_id = old.id) then
      raise exception 'Opłaconego ani anulowanego rachunku nie można usunąć – użyj „Anuluj”.';
    end if;
    return old;
  end if;

  if old.status = 'cancelled' and new.status is distinct from 'cancelled' then
    raise exception 'Anulowanego rachunku nie można przywrócić.';
  end if;

  if new.status = 'paid' and old.status is distinct from 'paid' and not public.is_manager() then
    raise exception 'Płatność zatwierdza kierownik lub administrator.';
  end if;

  if old.status = 'paid' and new.status is distinct from 'paid' then
    if new.status = 'cancelled' then
      if not public.is_admin() then
        raise exception 'Opłacony rachunek może anulować tylko administrator.';
      end if;
    elsif exists (select 1 from public.pos_payments where order_id = old.id) then
      raise exception 'Opłaconego rachunku nie można ponownie otworzyć.';
    end if;
  end if;

  if new.status = 'cancelled' and old.status is distinct from 'cancelled' then
    if old.status is distinct from 'paid' and not public.is_manager() then
      raise exception 'Rachunek może anulować kierownik lub administrator.';
    end if;
    new.cancelled_at := coalesce(new.cancelled_at, now());
    new.cancelled_by := coalesce(new.cancelled_by, auth.uid());
  end if;

  return new;
end $$;
revoke execute on function public.pos_orders_guard() from public, anon, authenticated;

drop trigger if exists pos_orders_guard on public.pos_orders;
create trigger pos_orders_guard
  before update or delete on public.pos_orders
  for each row execute function public.pos_orders_guard();

-- Pozycji zamkniętego (opłaconego/anulowanego) rachunku nie można zmieniać
create or replace function public.pos_items_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare s text;
begin
  if auth.uid() is null then
    if tg_op = 'DELETE' then return old; end if;
    return new;
  end if;
  select status into s from public.pos_orders
   where id = case when tg_op = 'DELETE' then old.order_id else new.order_id end;
  if s in ('paid', 'cancelled') then
    raise exception 'Rachunek jest zamknięty – nie można zmieniać jego pozycji.';
  end if;
  if tg_op = 'DELETE' then return old; end if;
  return new;
end $$;
revoke execute on function public.pos_items_guard() from public, anon, authenticated;

drop trigger if exists pos_items_guard on public.pos_order_items;
create trigger pos_items_guard
  before insert or update or delete on public.pos_order_items
  for each row execute function public.pos_items_guard();

-- Płatności: kierownik/administrator dodaje i widzi, nikt nie zmienia ani nie usuwa
drop policy if exists management_payments on public.pos_payments;
drop policy if exists "pos_payments: kierownik widzi" on public.pos_payments;
create policy "pos_payments: kierownik widzi" on public.pos_payments
  for select to authenticated using (public.cafe_is_management());
drop policy if exists "pos_payments: kierownik dodaje" on public.pos_payments;
create policy "pos_payments: kierownik dodaje" on public.pos_payments
  for insert to authenticated with check (public.cafe_is_management());
revoke update, delete on public.pos_payments from authenticated, anon;

-- Usuwanie rachunków: tylko otwarte (np. założone przez pomyłkę), przez kierownika
drop policy if exists "pos_orders: kierownik usuwa" on public.pos_orders;
create policy "pos_orders: kierownik usuwa" on public.pos_orders
  for delete to authenticated using (public.is_manager() and status not in ('paid', 'cancelled'));

notify pgrst, 'reload schema';
