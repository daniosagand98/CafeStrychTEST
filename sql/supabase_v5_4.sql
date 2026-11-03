-- =====================================================================
-- Cafe Strych – V5.4 (03.11.2026) – tablety firmowe
-- Pracownik na swoim telefonie: Start (wiadomości), Grafik, Czat, Moje konto.
-- POS, Rezerwacje i Zakupy – tylko na urządzeniu zarejestrowanym jako
-- firmowe (tablet w lokalu). Kierownik i administrator – bez ograniczeń.
-- Blokada działa też w bazie: z niezarejestrowanego urządzenia pracownik
-- nie doda, nie zmieni ani nie usunie niczego na rachunkach, w rezerwacjach
-- i zakupach (nawet z pominięciem aplikacji).
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

create extension if not exists pgcrypto with schema extensions;

create table if not exists public.company_devices (
  id           uuid primary key default gen_random_uuid(),
  created_at   timestamptz not null default now(),
  name         text not null,
  token_hash   text not null unique,
  created_by   uuid default auth.uid(),
  last_seen_at timestamptz,
  active       boolean not null default true
);
alter table public.company_devices enable row level security;
drop policy if exists "company_devices: kierownik czyta" on public.company_devices;
create policy "company_devices: kierownik czyta" on public.company_devices
  for select to authenticated using (public.is_manager());
drop policy if exists "company_devices: kierownik zmienia" on public.company_devices;
create policy "company_devices: kierownik zmienia" on public.company_devices
  for update to authenticated using (public.is_manager()) with check (public.is_manager());
drop policy if exists "company_devices: kierownik usuwa" on public.company_devices;
create policy "company_devices: kierownik usuwa" on public.company_devices
  for delete to authenticated using (public.is_manager());
revoke all on public.company_devices from anon, authenticated;
grant select (id, created_at, name, created_by, last_seen_at, active) on public.company_devices to authenticated;
grant update (name, active) on public.company_devices to authenticated;
grant delete on public.company_devices to authenticated;

-- znacznik urządzenia przychodzi z aplikacji w nagłówku x-cs-device
create or replace function public.device_hash(p_token text) returns text
language sql immutable set search_path = public, extensions as $$
  select encode(extensions.digest(coalesce(p_token, ''), 'sha256'), 'hex')
$$;

create or replace function public.on_company_device() returns boolean
language plpgsql stable security definer set search_path = public, extensions as $$
declare t text;
begin
  begin
    t := current_setting('request.headers', true)::json ->> 'x-cs-device';
  exception when others then t := null;
  end;
  if t is null or length(t) < 32 then return false; end if;
  return exists (select 1 from public.company_devices where active and token_hash = public.device_hash(t));
end $$;
grant execute on function public.on_company_device() to authenticated;

create or replace function public.pos_write_allowed() returns boolean
language sql stable security definer set search_path = public as $$
  select public.is_manager() or public.on_company_device()
$$;
grant execute on function public.pos_write_allowed() to authenticated;

-- rejestracja tabletu (kierownik/admin, na tym tablecie)
create or replace function public.register_company_device(p_name text, p_token text) returns uuid
language plpgsql security definer set search_path = public as $$
declare v uuid;
begin
  if not public.is_manager() then raise exception 'Urządzenie firmowe dodaje kierownik lub administrator.'; end if;
  if p_token is null or length(p_token) < 32 then raise exception 'Nieprawidłowy znacznik urządzenia.'; end if;
  insert into public.company_devices (name, token_hash) values (coalesce(nullif(trim(p_name), ''), 'Tablet'), public.device_hash(p_token))
  on conflict (token_hash) do update set name = excluded.name, active = true
  returning id into v;
  return v;
end $$;
revoke all on function public.register_company_device(text, text) from public, anon;
grant execute on function public.register_company_device(text, text) to authenticated;

-- sprawdzenie przy starcie aplikacji: czy to urządzenie jest firmowe
create or replace function public.check_company_device(p_token text) returns json
language plpgsql security definer set search_path = public as $$
declare d record;
begin
  if p_token is null or length(p_token) < 32 then return null; end if;
  update public.company_devices set last_seen_at = now()
   where active and token_hash = public.device_hash(p_token)
  returning id, name into d;
  if not found then return null; end if;
  return json_build_object('id', d.id, 'name', d.name);
end $$;
revoke all on function public.check_company_device(text) from public, anon;
grant execute on function public.check_company_device(text) to authenticated;

-- blokada zapisu poza tabletem (dodatkowa zasada – działa razem z dotychczasowymi)
do $$
declare t text;
begin
  foreach t in array array['pos_orders', 'pos_order_items', 'pos_payments', 'bookings', 'shopping'] loop
    execute format('drop policy if exists "tablet: dodawanie" on public.%I', t);
    execute format('drop policy if exists "tablet: zmiany" on public.%I', t);
    execute format('drop policy if exists "tablet: usuwanie" on public.%I', t);
    execute format('create policy "tablet: dodawanie" on public.%I as restrictive for insert to authenticated with check (public.pos_write_allowed())', t);
    execute format('create policy "tablet: zmiany" on public.%I as restrictive for update to authenticated using (public.pos_write_allowed()) with check (public.pos_write_allowed())', t);
    execute format('create policy "tablet: usuwanie" on public.%I as restrictive for delete to authenticated using (public.pos_write_allowed())', t);
  end loop;
end $$;

-- funkcje POS działające z pełnymi prawami – ta sama blokada
create or replace function public.pos_bump_op(p_op uuid, p_order uuid, p_menu uuid, p_item uuid, p_delta int)
returns text language plpgsql security definer set search_path = public as $$
declare n int; v_id uuid; v_qty numeric; m record;
begin
  if not public.is_active_member() then raise exception 'Brak dostępu.'; end if;
  if not public.pos_write_allowed() then raise exception 'POS działa tylko na tablecie firmowym.'; end if;

  insert into public.pos_ops (id) values (p_op) on conflict (id) do nothing;
  get diagnostics n = row_count;
  if n = 0 then return 'duplicate'; end if;          -- to kliknięcie już zapisano wcześniej

  if p_menu is not null then
    select id, qty into v_id, v_qty from public.pos_order_items
     where order_id = p_order and menu_item_id = p_menu order by created_at limit 1 for update;
  else
    select id, qty into v_id, v_qty from public.pos_order_items where id = p_item for update;
  end if;

  if v_id is null then
    if p_delta <= 0 or p_menu is null then return 'ok'; end if;
    select name, price, tax_rate into m from public.menu_items where id = p_menu;
    if not found then raise exception 'Tego produktu nie ma już w menu.'; end if;
    insert into public.pos_order_items (order_id, menu_item_id, item_name, qty, unit_price, tax_rate)
    values (p_order, p_menu, m.name, p_delta, m.price, coalesce(m.tax_rate, 23));
  elsif v_qty + p_delta <= 0 then
    delete from public.pos_order_items where id = v_id;
  else
    update public.pos_order_items set qty = qty + p_delta where id = v_id;
  end if;

  -- sprzątanie starych numerów kliknięć (raz na ~200 wywołań)
  if random() < 0.005 then delete from public.pos_ops where created_at < now() - interval '30 days'; end if;
  return 'ok';
end $$;

revoke all on function public.pos_bump_op(uuid, uuid, uuid, uuid, int) from public, anon;
grant execute on function public.pos_bump_op(uuid, uuid, uuid, uuid, int) to authenticated;

create or replace function public.sales_day(p_day date)
returns table (id uuid, order_id uuid, amount numeric, method text, created_at timestamptz,
               order_name text, order_status text, discount_pct numeric, cancel_reason text)
language plpgsql stable security definer set search_path = public as $$
declare today date := (now() at time zone 'Europe/Warsaw')::date;
begin
  if not public.is_active_member() then raise exception 'Brak dostępu.'; end if;
  if not public.pos_write_allowed() then raise exception 'Utarg jest dostępny na tablecie firmowym.'; end if;
  if not public.is_manager() and p_day not in (today, today - 1) then
    raise exception 'Pracownik widzi utarg z dzisiaj i wczoraj.';
  end if;
  return query
    select p.id, p.order_id, p.amount, p.method, p.created_at,
           coalesce(o.customer_name, o.order_no, 'Rachunek'), o.status, o.discount_pct, o.cancel_reason
      from public.pos_payments p left join public.pos_orders o on o.id = p.order_id
     where (p.created_at at time zone 'Europe/Warsaw')::date = p_day
     order by p.created_at desc;
end $$;
revoke all on function public.sales_day(date) from public, anon;
grant execute on function public.sales_day(date) to authenticated;

notify pgrst, 'reload schema';
