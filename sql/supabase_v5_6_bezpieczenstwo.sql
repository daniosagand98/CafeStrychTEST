-- =====================================================================
-- Cafe Strych – V5.6 (06.11.2026) – POPRAWKI BEZPIECZEŃSTWA (audyt)
--  1) Rolę (pracownik / kierownik / admin) i aktywację konta zmienia
--     wyłącznie administrator – nikt nie nada sobie uprawnień sam,
--     nawet z pominięciem aplikacji.
--  2) Usunięcie starych, zbyt luźnych zasad dostępu z pierwszych wersji
--     (gdyby jeszcze istniały) – np. „każdy zalogowany może wszystko”
--     przy rachunkach, płatnościach, zakupach i zamianach zmian.
--  3) Zamiany zmian: tylko przez funkcje aplikacji (koniec z bezpośrednim
--     zapisem) + uzupełnienie brakujących kolumn w starej tabeli.
--  4) Strona www: ograniczenie liczby próśb o rezerwację (ochrona przed
--     zalaniem fałszywymi rezerwacjami przez boty).
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie. Niczego nie usuwa z danych.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1) OCHRONA RÓL I AKTYWACJI KONT
-- ---------------------------------------------------------------------
create or replace function public.profiles_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  -- system (rejestracja, funkcje bazy) i operacje administracyjne – bez ograniczeń
  if auth.uid() is null or current_setting('cafe.admin_op', true) = 'on' then
    return new;
  end if;
  if new.id is distinct from old.id then
    raise exception 'Nie można zmienić identyfikatora konta.';
  end if;
  if (new.role is distinct from old.role or new.active is distinct from old.active)
     and not public.is_admin() then
    raise exception 'Rolę i aktywację konta zmienia tylko administrator.';
  end if;
  if new.id = auth.uid() and new.role is distinct from old.role then
    raise exception 'Nie możesz zmienić roli własnego konta.';
  end if;
  return new;
end $$;
revoke all on function public.profiles_guard() from public, anon, authenticated;

drop trigger if exists profiles_guard on public.profiles;
create trigger profiles_guard before update on public.profiles
  for each row execute function public.profiles_guard();

-- nowe konta zawsze startują jako zwykły, nieaktywny pracownik (nawet przy ręcznym insercie)
create or replace function public.profiles_insert_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is not null and not public.is_admin() then
    new.role := 'user';
    new.active := false;
  end if;
  return new;
end $$;
revoke all on function public.profiles_insert_guard() from public, anon, authenticated;
drop trigger if exists profiles_insert_guard on public.profiles;
create trigger profiles_insert_guard before insert on public.profiles
  for each row execute function public.profiles_insert_guard();

-- usuwanie kont (V5.3.1) – oznaczenie operacji administracyjnej dla ochrony powyżej
create or replace function public.admin_delete_account(p_user uuid)
returns text language plpgsql security definer set search_path = public, auth as $$
declare v_mail text; v_name text; v_role text;
begin
  if not public.is_manager() then raise exception 'Konto może usunąć kierownik lub administrator.'; end if;
  if p_user = auth.uid() then raise exception 'Nie możesz usunąć własnego konta.'; end if;
  select email, full_name, role into v_mail, v_name, v_role from public.profiles where id = p_user;
  if v_role = 'admin' then raise exception 'Konta administratora nie można usunąć.'; end if;
  if not public.is_admin() and coalesce(v_role, 'user') <> 'user' then
    raise exception 'Kierownik może usunąć tylko konto pracownika. Konta kierowników i administratorów usuwa administrator.';
  end if;
  perform set_config('cafe.admin_op', 'on', true);

  delete from public.push_subscriptions where user_id = p_user;
  delete from public.chat_reads where user_id = p_user;
  begin
    delete from public.profiles where id = p_user;
    delete from auth.users where id = p_user;
    insert into public.activity_logs (action, user_email)
    values (format('Usunięto konto: %s (%s)', coalesce(v_name, '—'), coalesce(v_mail, '—')),
            (select email from auth.users where id = auth.uid()));
    return 'deleted';
  exception when foreign_key_violation then
    null;
  end;
  update public.profiles set active = false, deleted_at = now() where id = p_user;
  update auth.users set banned_until = 'infinity' where id = p_user;
  delete from auth.sessions where user_id = p_user;
  insert into public.activity_logs (action, user_email)
  values (format('Usunięto (zablokowano na stałe) konto: %s (%s)', coalesce(v_name, '—'), coalesce(v_mail, '—')),
          (select email from auth.users where id = auth.uid()));
  return 'blocked';
end $$;
revoke all on function public.admin_delete_account(uuid) from public, anon;
grant execute on function public.admin_delete_account(uuid) to authenticated;

-- ---------------------------------------------------------------------
-- 2) STARE, ZBYT LUŹNE ZASADY Z PIERWSZYCH WERSJI (jeśli jeszcze są)
--    Właściwe zasady z V3.7+ zostają bez zmian.
-- ---------------------------------------------------------------------
drop policy if exists "pos_orders: zespół obsługuje"       on public.pos_orders;
drop policy if exists "pos_order_items: zespół dodaje"     on public.pos_order_items;
drop policy if exists "pos_order_items: zespół zmienia"    on public.pos_order_items;
drop policy if exists "pos_order_items: kierownik usuwa"   on public.pos_order_items;
drop policy if exists "pos_payments: zespół obsługuje"     on public.pos_payments;
drop policy if exists "pos_payments: zespół dodaje"        on public.pos_payments;
drop policy if exists "pos_payments: zespół zmienia"       on public.pos_payments;
drop policy if exists "shopping: zespół czyta i dodaje"    on public.shopping;
drop policy if exists "shopping: kierownik zarządza"       on public.shopping;
drop policy if exists "availability: odczyt"               on public.availability;
drop policy if exists team_read  on public.pos_payments;
drop policy if exists team_write on public.pos_payments;

-- ---------------------------------------------------------------------
-- 3) ZAMIANY ZMIAN – tylko przez funkcje aplikacji
-- ---------------------------------------------------------------------
drop policy if exists "shift_swaps: zespół" on public.shift_swaps;   -- stara zasada: każdy mógł wszystko
revoke insert, update, delete on public.shift_swaps from anon, authenticated;

alter table public.shift_swaps add column if not exists shift_id       uuid;
alter table public.shift_swaps add column if not exists from_employee  uuid;
alter table public.shift_swaps add column if not exists to_employee    uuid;
alter table public.shift_swaps add column if not exists other_shift_id uuid;
alter table public.shift_swaps add column if not exists note           text;
alter table public.shift_swaps add column if not exists status         text default 'open';
alter table public.shift_swaps add column if not exists requested_by   uuid;
alter table public.shift_swaps add column if not exists accepted_at    timestamptz;
alter table public.shift_swaps add column if not exists decided_by     uuid;
alter table public.shift_swaps add column if not exists decided_at     timestamptz;
alter table public.shift_swaps add column if not exists pushed_status  text;
alter table public.shift_swaps add column if not exists created_at     timestamptz default now();

-- stare ograniczenia wartości statusu (inne nazwy statusów) – zastąpione aktualnymi
do $$
declare c record;
begin
  for c in select conname from pg_constraint
            where conrelid = 'public.shift_swaps'::regclass and contype = 'c'
              and pg_get_constraintdef(oid) ilike '%status%'
  loop
    execute format('alter table public.shift_swaps drop constraint %I', c.conname);
  end loop;
  alter table public.shift_swaps add constraint shift_swaps_status_check
    check (status in ('open', 'accepted', 'approved', 'rejected', 'cancelled'));
exception when check_violation then
  raise notice 'shift_swaps: są stare wpisy z innym statusem – ograniczenie pominięte';
end $$;
alter table public.shift_swaps alter column status set default 'open';

-- kolumny ze starej wersji tabeli, których aplikacja nie wypełnia – bez wymogu wartości
do $$
declare c record;
begin
  for c in select column_name from information_schema.columns
            where table_schema = 'public' and table_name = 'shift_swaps'
              and is_nullable = 'NO' and column_default is null
              and column_name not in ('id', 'shift_id', 'from_employee', 'status')
  loop
    execute format('alter table public.shift_swaps alter column %I drop not null', c.column_name);
  end loop;
end $$;

alter table public.bookings add column if not exists created_at timestamptz default now();

-- ---------------------------------------------------------------------
-- 4) STRONA WWW – limit próśb o rezerwację (ochrona przed botami)
--    maks. 3 prośby z tego samego numeru na dobę i 40 próśb na godzinę łącznie
-- ---------------------------------------------------------------------
create or replace function public.www_booking_limit() returns trigger
language plpgsql security definer set search_path = public as $$
declare tel text; n int;
begin
  if coalesce(new.source, '') <> 'www' or auth.uid() is not null then return new; end if;
  select count(*) into n from public.bookings where source = 'www' and created_at > now() - interval '1 hour';
  if n >= 40 then
    raise exception 'Za dużo próśb o rezerwację w krótkim czasie. Zadzwoń do nas: 58 620 30 38.';
  end if;
  tel := regexp_replace(coalesce(substring(new.notes from 'tel\.?\s*:?\s*(\+?[0-9][0-9 -]{6,}[0-9])'), ''), '[^0-9]', '', 'g');
  if length(tel) >= 9 then
    select count(*) into n from public.bookings
     where source = 'www' and created_at > now() - interval '24 hours'
       and right(regexp_replace(coalesce(substring(notes from 'tel\.?\s*:?\s*(\+?[0-9][0-9 -]{6,}[0-9])'), ''), '[^0-9]', '', 'g'), 9) = right(tel, 9);
    if n >= 3 then
      raise exception 'Z tego numeru wysłano już kilka próśb dzisiaj. Zadzwoń do nas: 58 620 30 38.';
    end if;
  end if;
  return new;
end $$;
revoke all on function public.www_booking_limit() from public, anon, authenticated;
drop trigger if exists bookings_www_limit on public.bookings;
create trigger bookings_www_limit before insert on public.bookings
  for each row execute function public.www_booking_limit();

notify pgrst, 'reload schema';
