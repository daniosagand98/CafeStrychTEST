-- =====================================================================
-- Cafe Strych – aktualizacja bazy pod wersję V3.5 aplikacji (16.10.2026)
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Najpierw musi być uruchomiony supabase_v3_4.sql (funkcja is_manager).
-- Skrypt można uruchomić ponownie – niczego nie zdubluje.
-- =====================================================================

-- 0. Funkcje pomocnicze ------------------------------------------------
create or replace function public.is_manager() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles
    where id = auth.uid() and role in ('admin','manager') and coalesce(active, true));
$$;

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles
    where id = auth.uid() and role = 'admin' and coalesce(active, true));
$$;

-- =====================================================================
-- 1. ZGŁOSZENIA BŁĘDÓW (każdy zgłasza, admin przegląda i pobiera TXT)
-- =====================================================================
create table if not exists public.bug_reports (
  id         uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now()
);
alter table public.bug_reports add column if not exists description    text;
alter table public.bug_reports add column if not exists image_path     text;
alter table public.bug_reports add column if not exists reporter_id    uuid;
alter table public.bug_reports add column if not exists reporter_name  text;
alter table public.bug_reports add column if not exists reporter_email text;
alter table public.bug_reports add column if not exists page           text;
alter table public.bug_reports add column if not exists user_agent     text;
alter table public.bug_reports add column if not exists status         text default 'new';
alter table public.bug_reports add column if not exists resolved_at    timestamptz;

alter table public.bug_reports enable row level security;
grant select, insert, update, delete on public.bug_reports to authenticated;

drop policy if exists "bug_reports: każdy zalogowany zgłasza" on public.bug_reports;
create policy "bug_reports: każdy zalogowany zgłasza" on public.bug_reports
  for insert to authenticated with check (reporter_id = auth.uid());

drop policy if exists "bug_reports: admin i autor widzą" on public.bug_reports;
create policy "bug_reports: admin i autor widzą" on public.bug_reports
  for select to authenticated using (public.is_admin() or reporter_id = auth.uid());

drop policy if exists "bug_reports: admin zmienia status" on public.bug_reports;
create policy "bug_reports: admin zmienia status" on public.bug_reports
  for update to authenticated using (public.is_admin()) with check (public.is_admin());

drop policy if exists "bug_reports: admin usuwa" on public.bug_reports;
create policy "bug_reports: admin usuwa" on public.bug_reports
  for delete to authenticated using (public.is_admin());

do $$ begin
  alter publication supabase_realtime add table public.bug_reports;
exception when duplicate_object then null; end $$;

-- Prywatny folder na zdjęcia do zgłoszeń (każdy wrzuca do swojego podfolderu)
insert into storage.buckets (id, name, public)
values ('bug-reports', 'bug-reports', false)
on conflict (id) do update set public = false;

drop policy if exists "bug-reports: zalogowani wysyłają zdjęcia" on storage.objects;
create policy "bug-reports: zalogowani wysyłają zdjęcia" on storage.objects
  for insert to authenticated
  with check (bucket_id = 'bug-reports' and (storage.foldername(name))[1] = auth.uid()::text);

drop policy if exists "bug-reports: admin ogląda zdjęcia" on storage.objects;
create policy "bug-reports: admin ogląda zdjęcia" on storage.objects
  for select to authenticated using (bucket_id = 'bug-reports' and public.is_admin());

drop policy if exists "bug-reports: admin usuwa zdjęcia" on storage.objects;
create policy "bug-reports: admin usuwa zdjęcia" on storage.objects
  for delete to authenticated using (bucket_id = 'bug-reports' and public.is_admin());

-- =====================================================================
-- 2. LOKAL: sala ↔ miejsce rezerwacji + usuwanie sal, stolików, miejsc
-- =====================================================================
alter table public.reservation_places
  add column if not exists room_id uuid references public.cafe_rooms(id) on delete set null;
alter table public.reservation_places add column if not exists description text;
alter table public.reservation_places add column if not exists sort_order  int;
alter table public.cafe_rooms         add column if not exists sort_order  int;

-- połącz istniejące miejsca z salami o tej samej nazwie
update public.reservation_places p set room_id = r.id
from public.cafe_rooms r
where p.room_id is null and lower(trim(p.name)) = lower(trim(r.name));

do $$
declare t text;
begin
  foreach t in array array['cafe_rooms','cafe_tables','reservation_places'] loop
    execute format('drop policy if exists "%s: kierownik zarządza" on public.%I', t, t);
    execute format('create policy "%s: kierownik zarządza" on public.%I for all to authenticated using (public.is_manager()) with check (public.is_manager())', t, t);
    execute format('grant select, insert, update, delete on public.%I to authenticated', t);
  end loop;
end $$;

-- =====================================================================
-- 3. REZERWACJE: kolumny używane przez aplikację + dodawanie przez zespół
--    (brak którejś z tych kolumn powodował błąd przy dodawaniu rezerwacji)
-- =====================================================================
alter table public.bookings add column if not exists reservation_place_id uuid;
alter table public.bookings add column if not exists place_name     text;
alter table public.bookings add column if not exists room           text;
alter table public.bookings add column if not exists table_label    text;
alter table public.bookings add column if not exists end_at         timestamptz;
alter table public.bookings add column if not exists notes          text;
alter table public.bookings add column if not exists booking_status text default 'confirmed';
alter table public.bookings add column if not exists source         text;

drop policy if exists "bookings: zespół dodaje" on public.bookings;
create policy "bookings: zespół dodaje" on public.bookings
  for insert to authenticated
  with check (public.is_manager() or (created_by = auth.uid() and booking_status = 'pending'));

drop policy if exists "bookings: kierownik zarządza" on public.bookings;
create policy "bookings: kierownik zarządza" on public.bookings
  for all to authenticated using (public.is_manager()) with check (public.is_manager());

drop policy if exists "bookings: zespół widzi" on public.bookings;
create policy "bookings: zespół widzi" on public.bookings
  for select to authenticated using (true);
grant select, insert, update, delete on public.bookings to authenticated;

-- =====================================================================
-- 4. GRAFIK i DYSPOZYCYJNOŚĆ
-- =====================================================================
-- pozwól na dwie zmiany jednego pracownika w ten sam dzień
do $$
declare c text;
begin
  for c in select con.conname from pg_constraint con
    join pg_class rel on rel.oid = con.conrelid
    where rel.relname = 'work_shifts' and con.contype = 'u'
      and pg_get_constraintdef(con.oid) ilike '%employee_id%shift_date%'
  loop
    execute format('alter table public.work_shifts drop constraint %I', c);
  end loop;
end $$;

-- dyspozycyjność: jeden wpis na osobę i dzień (wymagane przez zapis z aplikacji)
do $$ begin
  if not exists (select 1 from pg_constraint con join pg_class rel on rel.oid = con.conrelid
                 where rel.relname = 'availability' and con.contype in ('u','p')
                   and pg_get_constraintdef(con.oid) ilike '%(user_id, work_date)%') then
    delete from public.availability a using public.availability b
      where a.user_id = b.user_id and a.work_date = b.work_date and a.ctid < b.ctid;
    alter table public.availability add constraint availability_user_day_key unique (user_id, work_date);
  end if;
end $$;
