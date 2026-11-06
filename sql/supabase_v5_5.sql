-- =====================================================================
-- Cafe Strych – V5.5 (06.11.2026) – rezerwacje w „System i logi”
-- Baza zapisuje w logach, kto i kiedy: dodał, zatwierdził, odrzucił,
-- zmienił lub usunął rezerwację (także prośby ze strony www).
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

create or replace function public.bookings_activity_log() returns trigger
language plpgsql security definer set search_path = public as $$
declare b record; who text; what text; info text;
begin
  b := case when tg_op = 'DELETE' then old else new end;
  select email into who from auth.users where id = auth.uid();
  who := coalesce(who, case when b.source = 'www' and tg_op = 'INSERT' then 'strona www' else 'system' end);
  info := format('%s, %s os., %s', coalesce(b.title, 'Gość'), coalesce(b.guests_count::text, '?'),
                 to_char(b.start_at at time zone 'Europe/Warsaw', 'DD.MM.YYYY HH24:MI'));

  if tg_op = 'INSERT' then
    what := case when b.source = 'www' then 'Nowa prośba o rezerwację ze strony' else 'Dodano rezerwację' end;
  elsif tg_op = 'DELETE' then
    what := 'Usunięto rezerwację';
  elsif new.booking_status is distinct from old.booking_status then
    what := case new.booking_status
              when 'confirmed' then 'Zatwierdzono rezerwację'
              when 'rejected'  then 'Odrzucono rezerwację'
              when 'pending'   then 'Rezerwacja czeka na zatwierdzenie'
              else 'Zmieniono status rezerwacji na ' || coalesce(new.booking_status, '—') end;
  elsif (new.start_at, new.end_at, new.guests_count, new.title, new.notes, new.table_label, new.reservation_place_id, new.whole_room)
        is distinct from
        (old.start_at, old.end_at, old.guests_count, old.title, old.notes, old.table_label, old.reservation_place_id, old.whole_room) then
    what := 'Zmieniono rezerwację';
  else
    return null;   -- zmiana techniczna (np. powiadomienie) – bez wpisu
  end if;

  insert into public.activity_logs (action, user_email) values (what || ': ' || info, who);
  return null;
exception when others then
  raise warning 'bookings_activity_log: %', sqlerrm;   -- log nigdy nie blokuje rezerwacji
  return null;
end $$;
revoke all on function public.bookings_activity_log() from public, anon, authenticated;

drop trigger if exists bookings_activity_log on public.bookings;
create trigger bookings_activity_log after insert or update or delete on public.bookings
  for each row execute function public.bookings_activity_log();

notify pgrst, 'reload schema';
