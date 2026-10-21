-- =====================================================================
-- Cafe Strych – V3.7: bezpieczeństwo, zatwierdzanie kont, rezerwacje, realtime
-- (21.10.2026) Wprowadzone bezpośrednio w projekcie CafeStrych.
-- Przed zmianą kopia zasad/funkcji/triggerów zapisana w cs_backup.v37_before.
-- =====================================================================

-- 0. KOPIA ZAPASOWA obecnych zasad dostępu, funkcji i triggerów -------------
create schema if not exists cs_backup;
revoke all on schema cs_backup from public, anon, authenticated;
create table if not exists cs_backup.v37_before (created_at timestamptz default now(), kind text, sql text);
insert into cs_backup.v37_before(kind, sql)
select 'policy', format('create policy %I on %I.%I as %s for %s to %s%s%s;', polname, n.nspname, c.relname,
  case when polpermissive then 'permissive' else 'restrictive' end,
  case polcmd when 'r' then 'select' when 'a' then 'insert' when 'w' then 'update' when 'd' then 'delete' else 'all' end,
  (select string_agg(case when r = 0 then 'public' else pg_get_userbyid(r) end, ', ') from unnest(polroles) r),
  coalesce(' using (' || pg_get_expr(polqual, polrelid) || ')', ''),
  coalesce(' with check (' || pg_get_expr(polwithcheck, polrelid) || ')', ''))
from pg_policy p join pg_class c on c.oid = p.polrelid join pg_namespace n on n.oid = c.relnamespace
where n.nspname in ('public', 'storage')
union all
select 'function', pg_get_functiondef(p.oid) || ';' from pg_proc p join pg_namespace n on n.oid = p.pronamespace
where n.nspname = 'public' and p.prokind = 'f' and p.prolang <> (select oid from pg_language where lanname = 'c')
union all
select 'trigger', pg_get_triggerdef(t.oid) || ';' from pg_trigger t join pg_class c on c.oid = t.tgrelid
join pg_namespace n on n.oid = c.relnamespace where not t.tgisinternal and n.nspname in ('public', 'auth');

-- 1. Pomocnicza funkcja: zalogowany i ZATWIERDZONY członek zespołu -----------
create or replace function public.is_active_member() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles where id = auth.uid() and coalesce(active, false));
$$;

create or replace function public.is_manager_or_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles
    where id = auth.uid() and role in ('admin', 'manager') and coalesce(active, true));
$$;

-- 2. NOWE KONTA CZEKAJĄ NA ZATWIERDZENIE -----------------------------------
--    + rejestracja łączy się z istniejącym pracownikiem (po e-mailu lub nazwisku)
--      zamiast kończyć się błędem przy takim samym imieniu i nazwisku
drop trigger if exists on_auth_user_created on auth.users;   -- stary, zdublowany mechanizm
drop function if exists public.new_user_profile();

create or replace function public.cafe_handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  v_name text := trim(coalesce(new.raw_user_meta_data->>'full_name', ''));
  v_emp  uuid;
begin
  if v_name = '' then v_name := split_part(new.email, '@', 1); end if;

  insert into public.profiles(id, full_name, email, role, active, last_seen_at)
  values (new.id, v_name, new.email, 'user', false, now())
  on conflict (id) do update set full_name = excluded.full_name, email = excluded.email;

  -- istniejący pracownik bez konta: dopasuj po e-mailu, potem po imieniu i nazwisku
  select id into v_emp from public.employees
   where user_id is null and lower(email) = lower(new.email) limit 1;
  if v_emp is null then
    select id into v_emp from public.employees
     where user_id is null and lower(trim(full_name)) = lower(v_name) limit 1;
  end if;

  if v_emp is not null then
    update public.employees set user_id = new.id, email = new.email where id = v_emp;
  else
    insert into public.employees(full_name, email, user_id, active)
    values (v_name, new.email, new.id, false)
    on conflict (user_id) where user_id is not null do nothing;
  end if;
  return new;
exception when others then
  -- rejestracja nie może się wywalić przez dane pracownika; profil musi powstać
  insert into public.profiles(id, full_name, email, role, active)
  values (new.id, v_name, new.email, 'user', false) on conflict (id) do nothing;
  return new;
end $$;

-- zatwierdzenie konta przez admina aktywuje też pracownika (i odwrotnie przy blokadzie)
create or replace function public.cafe_sync_profile_active() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.active is distinct from old.active then
    update public.employees set active = coalesce(new.active, false)
     where user_id = new.id
       and (coalesce(new.active, false) = false
            or not exists (select 1 from public.employees e2
                            where e2.active and e2.id <> employees.id
                              and lower(trim(e2.full_name)) = lower(trim(employees.full_name))));
  end if;
  return new;
end $$;
drop trigger if exists cafe_profile_active_sync on public.profiles;
create trigger cafe_profile_active_sync after update of active on public.profiles
  for each row execute function public.cafe_sync_profile_active();

-- obecne konta zostają aktywne (zabezpieczenie na wypadek pustych wartości)
update public.profiles set active = true where active is null;
alter table public.profiles alter column active set default false;

-- 3. DOSTĘP TYLKO DLA ZATWIERDZONYCH CZŁONKÓW ZESPOŁU ----------------------
-- profile: każdy widzi swój (żeby aplikacja pokazała „czeka na zatwierdzenie”), zespół – wszystkie
drop policy if exists "profiles read authenticated" on public.profiles;
drop policy if exists "profiles: własny lub zespół" on public.profiles;
create policy "profiles: własny lub zespół" on public.profiles for select to authenticated
  using (id = auth.uid() or public.is_active_member());

drop policy if exists "employees read" on public.employees;
drop policy if exists "employees: zespół czyta" on public.employees;
create policy "employees: zespół czyta" on public.employees for select to authenticated
  using (public.is_active_member());

-- rezerwacje
drop policy if exists "bookings read" on public.bookings;
drop policy if exists "bookings: zespół widzi" on public.bookings;
create policy "bookings: zespół widzi" on public.bookings for select to authenticated
  using (public.is_active_member());
drop policy if exists "bookings insert own" on public.bookings;
drop policy if exists "bookings: zespół dodaje" on public.bookings;
create policy "bookings: zespół dodaje" on public.bookings for insert to authenticated
  with check (public.is_manager() or (public.is_active_member() and created_by = auth.uid() and booking_status = 'pending'));
drop policy if exists "bookings update owner admin" on public.bookings;
drop policy if exists "bookings: autor poprawia oczekującą" on public.bookings;
create policy "bookings: autor poprawia oczekującą" on public.bookings for update to authenticated
  using (public.is_active_member() and created_by = auth.uid() and booking_status = 'pending')
  with check (created_by = auth.uid() and booking_status = 'pending');
drop policy if exists "bookings delete owner admin" on public.bookings;
drop policy if exists "bookings: autor usuwa oczekującą" on public.bookings;
create policy "bookings: autor usuwa oczekującą" on public.bookings for delete to authenticated
  using (public.is_active_member() and created_by = auth.uid() and booking_status = 'pending');
-- rezerwacje ze strony www: do 120 osób (było 40)
drop policy if exists "bookings: prośba o rezerwację ze strony" on public.bookings;
create policy "bookings: prośba o rezerwację ze strony" on public.bookings for insert to anon
  with check (booking_status = 'pending' and source = 'www' and created_by is null
    and guests_count between 1 and 120 and start_at > now() and start_at < now() + interval '180 days'
    and char_length(title) between 2 and 80 and char_length(coalesce(notes, '')) <= 600
    and coalesce(whole_room, false) = false);

-- POS: rachunki i pozycje – zespół, usuwanie – kierownik
drop policy if exists team_read on public.pos_orders;
drop policy if exists team_write on public.pos_orders;
drop policy if exists "pos_orders: zespół czyta" on public.pos_orders;
create policy "pos_orders: zespół czyta" on public.pos_orders for select to authenticated using (public.is_active_member());
drop policy if exists "pos_orders: zespół dodaje" on public.pos_orders;
create policy "pos_orders: zespół dodaje" on public.pos_orders for insert to authenticated with check (public.is_active_member());
drop policy if exists "pos_orders: zespół zmienia" on public.pos_orders;
create policy "pos_orders: zespół zmienia" on public.pos_orders for update to authenticated using (public.is_active_member()) with check (public.is_active_member());
drop policy if exists "pos_orders: kierownik usuwa" on public.pos_orders;
create policy "pos_orders: kierownik usuwa" on public.pos_orders for delete to authenticated using (public.is_manager());
drop policy if exists team_read on public.pos_order_items;
drop policy if exists team_write on public.pos_order_items;
drop policy if exists "pos_order_items: zespół obsługuje" on public.pos_order_items;
create policy "pos_order_items: zespół obsługuje" on public.pos_order_items for all to authenticated
  using (public.is_active_member()) with check (public.is_active_member());

-- grafik, dyspozycyjność, zamiany, urlopy
drop policy if exists "shifts read" on public.work_shifts;
drop policy if exists "work_shifts: zespół czyta" on public.work_shifts;
create policy "work_shifts: zespół czyta" on public.work_shifts for select to authenticated using (public.is_active_member());
drop policy if exists "shifts read" on public.shifts;
drop policy if exists "shifts: zespół czyta" on public.shifts;
create policy "shifts: zespół czyta" on public.shifts for select to authenticated using (public.is_active_member());
drop policy if exists availability_all on public.availability;
drop policy if exists "availability: własna lub kierownik czyta" on public.availability;
create policy "availability: własna lub kierownik czyta" on public.availability for select to authenticated
  using (user_id = auth.uid() or public.is_manager());
drop policy if exists "availability: własna" on public.availability;
create policy "availability: własna" on public.availability for insert to authenticated
  with check (user_id = auth.uid() and public.is_active_member());
drop policy if exists "availability: własna zmiana" on public.availability;
create policy "availability: własna zmiana" on public.availability for update to authenticated
  using (user_id = auth.uid() or public.is_manager()) with check (user_id = auth.uid() or public.is_manager());
drop policy if exists "availability: własna usuwa" on public.availability;
create policy "availability: własna usuwa" on public.availability for delete to authenticated
  using (user_id = auth.uid() or public.is_manager());
drop policy if exists shift_swaps_all on public.shift_swaps;
drop policy if exists "shift_swaps: zespół" on public.shift_swaps;
create policy "shift_swaps: zespół" on public.shift_swaps for all to authenticated
  using (public.is_active_member()) with check (public.is_active_member());
drop policy if exists "time off read" on public.time_off_requests;
drop policy if exists "time_off: zespół czyta" on public.time_off_requests;
create policy "time_off: zespół czyta" on public.time_off_requests for select to authenticated using (public.is_active_member());

-- zakupy: zespół dodaje i czyta, zmienia autor lub kierownik
drop policy if exists "shopping read" on public.shopping;
drop policy if exists "shopping insert own" on public.shopping;
drop policy if exists "shopping update" on public.shopping;
drop policy if exists "shopping delete owner admin" on public.shopping;
drop policy if exists "shopping: zespół czyta" on public.shopping;
create policy "shopping: zespół czyta" on public.shopping for select to authenticated using (public.is_active_member());
drop policy if exists "shopping: zespół dodaje" on public.shopping;
create policy "shopping: zespół dodaje" on public.shopping for insert to authenticated with check (public.is_active_member() and created_by = auth.uid());
drop policy if exists "shopping: autor lub kierownik zmienia" on public.shopping;
create policy "shopping: autor lub kierownik zmienia" on public.shopping for update to authenticated
  using (public.is_manager() or created_by = auth.uid()) with check (public.is_manager() or created_by = auth.uid());
drop policy if exists "shopping: autor lub kierownik usuwa" on public.shopping;
create policy "shopping: autor lub kierownik usuwa" on public.shopping for delete to authenticated
  using (public.is_manager() or created_by = auth.uid());

-- odczyt konfiguracji tylko dla zespołu
do $$
declare r record;
begin
  for r in select * from (values
    ('menu_items', 'team_read'), ('cafe_rooms', 'team_read'), ('cafe_tables', 'team_read'),
    ('reservation_places', 'reservation_places_read_authenticated'), ('employee_permissions', 'permissions_read'),
    ('cafe_settings', 'settings_read'), ('inventory_items', 'inventory_read'),
    ('inventory_movements', 'inventory_movements_read'), ('activity_logs', 'activity_logs: zespół czyta'),
    ('announcements', 'announcements_read')) v(t, p)
  loop
    execute format('drop policy if exists %I on public.%I', r.p, r.t);
    execute format('drop policy if exists %I on public.%I', r.t || ': zespół czyta', r.t);
    execute format('create policy %I on public.%I for select to authenticated using (public.is_active_member())',
                   r.t || ': zespół czyta', r.t);
  end loop;
end $$;

-- stare, zdublowane zasady zgłoszeń błędów (zostają nowe z V3.5)
drop policy if exists "bug insert own" on public.bug_reports;
drop policy if exists "bug read own admin" on public.bug_reports;
drop policy if exists "bug admin update" on public.bug_reports;
drop policy if exists "bug admin delete" on public.bug_reports;

-- 4. REZERWACJE: nakładanie blokuje tylko rezerwację CAŁEJ SALI/LOKALU -------
create or replace function public.prevent_booking_overlap() returns trigger
language plpgsql set search_path = public as $$
begin
  if new.reservation_place_id is not null
     and coalesce(new.booking_status, 'confirmed') <> 'rejected'
     and new.end_at is not null
     and exists (
       select 1 from public.bookings b
        where b.id <> coalesce(new.id, '00000000-0000-0000-0000-000000000000'::uuid)
          and b.reservation_place_id = new.reservation_place_id
          and coalesce(b.booking_status, 'confirmed') <> 'rejected'
          and (coalesce(new.whole_room, false) or coalesce(b.whole_room, false))
          and b.start_at < new.end_at and b.end_at > new.start_at)
  then
    raise exception 'Ta sala jest już zarezerwowana w całości w wybranym czasie.' using errcode = '23P01';
  end if;
  return new;
end $$;
drop trigger if exists bookings_prevent_overlap on public.bookings;
create trigger bookings_prevent_overlap
  before insert or update of reservation_place_id, start_at, end_at, whole_room, booking_status on public.bookings
  for each row execute function public.prevent_booking_overlap();

-- 5. FUNKCJE: bez wywoływania z zewnątrz -----------------------------------
-- stara funkcja płatności (dowolna kwota) – nieużywana przez aplikację
revoke execute on function public.finalize_pos_payment(uuid, text, numeric, numeric, uuid) from public, anon, authenticated;
revoke execute on function public.cafe_finalize_pos_order(uuid, text, numeric) from public, anon;
-- funkcje triggerów – nie do wywoływania przez API
revoke execute on function public.cafe_handle_new_user() from public, anon, authenticated;
revoke execute on function public.cafe_sync_employee_email() from public, anon, authenticated;
revoke execute on function public.cafe_sync_profile_active() from public, anon, authenticated;
-- funkcje sprawdzające uprawnienia – tylko dla zalogowanych (używają ich zasady dostępu)
do $$
declare f text;
begin
  foreach f in array array['is_admin()', 'is_manager()', 'cafe_is_management()', 'is_manager_or_admin()',
                           'is_cafe_manager_or_admin()', 'is_active_member()'] loop
    execute 'revoke execute on function public.' || f || ' from public, anon';
    execute 'grant execute on function public.' || f || ' to authenticated';
  end loop;
end $$;
alter function public.prevent_shift_on_approved_leave() set search_path = public;
alter function public.remove_shifts_after_approval() set search_path = public;

-- 6. ODŚWIEŻANIE NA ŻYWO dla wszystkich tabel aplikacji ---------------------
do $$
declare t text;
begin
  foreach t in array array['employees', 'work_shifts', 'bookings', 'shopping', 'profiles', 'pos_orders',
    'pos_order_items', 'pos_payments', 'availability', 'announcements', 'message_reads', 'employee_documents',
    'menu_items', 'cafe_tables', 'cafe_rooms', 'reservation_places', 'site_news', 'bug_reports'] loop
    begin
      execute format('alter publication supabase_realtime add table public.%I', t);
    exception when duplicate_object then null;
    end;
  end loop;
end $$;

notify pgrst, 'reload schema';
