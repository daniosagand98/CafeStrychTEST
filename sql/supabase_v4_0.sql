-- =====================================================================
-- Cafe Strych – V4.0 (23.10.2026)
-- 1) Admin włącza/wyłącza rezerwacje ze strony www
--    (wyłączone → strona pokazuje „rezerwacje tylko telefonicznie” + numer,
--     a baza i tak odrzuci prośbę wysłaną ze starej, otwartej karty).
-- 2) Admin włącza/wyłącza całe moduły: POS, Grafik, Rezerwacje, Zakupy
--    (wyłączony moduł znika z kont pracowników i kierowników).
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

alter table public.cafe_settings add column if not exists www_bookings    boolean not null default true;
alter table public.cafe_settings add column if not exists module_pos      boolean not null default true;
alter table public.cafe_settings add column if not exists module_schedule boolean not null default true;
alter table public.cafe_settings add column if not exists module_bookings boolean not null default true;
alter table public.cafe_settings add column if not exists module_shopping boolean not null default true;
insert into public.cafe_settings (id) values (1) on conflict (id) do nothing;

-- czy strona może przyjmować prośby o rezerwację (włączone rezerwacje www ORAZ moduł rezerwacji)
create or replace function public.www_bookings_open() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((select www_bookings and module_bookings from public.cafe_settings order by id limit 1), true)
$$;

-- publiczne ustawienia dla strony www (tylko to, co strona musi wiedzieć)
create or replace function public.site_settings() returns json
language sql stable security definer set search_path = public as $$
  select json_build_object('www_bookings', public.www_bookings_open())
$$;

revoke all on function public.www_bookings_open() from public;
revoke all on function public.site_settings() from public;
grant execute on function public.www_bookings_open() to anon, authenticated;
grant execute on function public.site_settings() to anon, authenticated;

-- prośba o rezerwację ze strony – tylko gdy rezerwacje www są włączone
drop policy if exists "bookings: prośba o rezerwację ze strony" on public.bookings;
create policy "bookings: prośba o rezerwację ze strony" on public.bookings for insert to anon
  with check (public.www_bookings_open()
    and booking_status = 'pending' and source = 'www' and created_by is null
    and guests_count between 1 and 120 and start_at > now() and start_at < now() + interval '180 days'
    and char_length(title) between 2 and 80 and char_length(coalesce(notes, '')) <= 600
    and coalesce(whole_room, false) = false);

-- zmiana ustawień od razu widoczna u wszystkich zalogowanych
do $$ begin
  alter publication supabase_realtime add table public.cafe_settings;
exception when duplicate_object then null; end $$;

notify pgrst, 'reload schema';
