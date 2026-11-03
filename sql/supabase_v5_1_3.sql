-- =====================================================================
-- Cafe Strych – V5.1.3 (03.11.2026) – poprawka rezerwacji
-- Błąd: „violates check constraint bookings_room_valid”.
-- Stara zasada w bazie pozwalała wpisać w rezerwacji tylko dawne nazwy
-- sal. Po dodaniu nowych sal (Sala, Góra, Kominek…) zapis był blokowany.
-- Sala w rezerwacji jest i tak powiązana z listą sal w aplikacji
-- (reservation_place_id), więc tę starą zasadę usuwamy.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- =====================================================================

alter table public.bookings drop constraint if exists bookings_room_valid;

notify pgrst, 'reload schema';
