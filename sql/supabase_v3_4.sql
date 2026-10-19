-- =====================================================================
-- Cafe Strych – aktualizacja bazy pod wersję V3.4 aplikacji i nową stronę www
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Skrypt można uruchomić ponownie – niczego nie zdubluje.
-- =====================================================================

-- 0. Funkcja pomocnicza: czy zalogowany użytkownik to kierownik lub admin
create or replace function public.is_manager() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from public.profiles
    where id = auth.uid() and role in ('admin','manager') and coalesce(active, true)
  );
$$;

-- =====================================================================
-- 1. MENU POS – 180 pozycji z karty (październik 2026)
--    VAT ustawiony orientacyjnie (8% jedzenie, soki, czekolada, koktajle
--    i napoje bezalkoholowe; 23% alkohol, kawa, herbata, napoje gazowane,
--    woda). SPRAWDŹ STAWKI Z KSIĘGOWĄ – zmienisz je w aplikacji: Lokal → Menu POS.
-- =====================================================================
-- (opcjonalnie) wyłącz stare pozycje demo przed importem – odkomentuj:
-- update public.menu_items set active = false;

insert into public.menu_items (name, category, price, tax_rate, active)
select v.name, v.category, v.price, v.tax_rate, true
from (values
  ('Kawa aromatyzowana', 'Kawa', 17.00, 23),
  ('Kawa czarna', 'Kawa', 13.00, 23),
  ('Flat White (kawa biała)', 'Kawa', 16.00, 23),
  ('Cappuccino', 'Kawa', 16.00, 23),
  ('Latte Macchiato', 'Kawa', 17.00, 23),
  ('Kawa z bitą śmietaną', 'Kawa', 22.00, 23),
  ('Espresso, woda', 'Kawa', 13.00, 23),
  ('Podwójne espresso', 'Kawa', 20.00, 23),
  ('Espresso z tonikiem i cytryną', 'Kawa', 20.00, 23),
  ('Kawa mrożona', 'Kawa', 18.00, 23),
  ('Kawa mrożona z mlekiem i bitą śmietaną 0,4 l', 'Kawa', 25.00, 23),
  ('Syrop do kawy', 'Dodatki', 3.00, 23),
  ('Gorąca czekolada 0,3 l', 'Czekolada', 17.00, 8),
  ('Gorąca czekolada z bitą śmietaną 0,3 l', 'Czekolada', 23.00, 8),
  ('Gorąca czekolada z konfiturą i bitą śmietaną 0,3 l', 'Czekolada', 26.00, 8),
  ('Czekolada mrożona z bitą śmietaną 0,4 l', 'Czekolada', 26.00, 8),
  ('Syrop do czekolady', 'Dodatki', 3.00, 8),
  ('Herbata w torebce 0,3 l', 'Herbata', 13.00, 23),
  ('Herbata liściasta 0,3 l', 'Herbata', 17.00, 23),
  ('Napar 0,3 l', 'Herbata', 17.00, 23),
  ('Herbata Rybaka 0,3 l', 'Herbata po naszemu', 16.00, 23),
  ('Herbata Rybaka 0,5 l', 'Herbata po naszemu', 21.00, 23),
  ('Herbata Gdyńska 0,3 l', 'Herbata po naszemu', 18.00, 23),
  ('Herbata Gdyńska 0,5 l', 'Herbata po naszemu', 23.00, 23),
  ('Herbata Strychowa 0,3 l', 'Herbata po naszemu', 18.00, 23),
  ('Herbata Strychowa 0,5 l', 'Herbata po naszemu', 23.00, 23),
  ('Herbata Babuni 0,3 l', 'Herbata po naszemu', 18.00, 23),
  ('Coca-Cola 0,3 l', 'Napoje i soki', 10.00, 23),
  ('Coca-Cola 1,0 l', 'Napoje i soki', 22.00, 23),
  ('Sprite 0,3 l', 'Napoje i soki', 10.00, 23),
  ('Sprite 1,0 l', 'Napoje i soki', 22.00, 23),
  ('Tonic 0,3 l', 'Napoje i soki', 10.00, 23),
  ('Tonic 1,0 l', 'Napoje i soki', 22.00, 23),
  ('Sok 0,3 l', 'Napoje i soki', 10.00, 8),
  ('Sok 1,0 l', 'Napoje i soki', 22.00, 8),
  ('Woda źródlana 0,3 l', 'Napoje i soki', 7.00, 23),
  ('Woda źródlana 1,0 l', 'Napoje i soki', 15.00, 23),
  ('Red Bull 0,25 l', 'Napoje i soki', 15.00, 23),
  ('Wilk Morski', 'Koktajle bezalkoholowe', 18.00, 8),
  ('Shrek', 'Koktajle bezalkoholowe', 18.00, 8),
  ('Czerwony Kapturek', 'Koktajle bezalkoholowe', 18.00, 8),
  ('Lemoniada', 'Koktajle bezalkoholowe', 18.00, 8),
  ('Wino czerwone z przyprawami 0,2 l', 'Grzańce bezalkoholowe', 20.00, 8),
  ('Piwo z przyprawami 0,5 l', 'Grzańce bezalkoholowe', 21.00, 8),
  ('Miłosław IPA 0,0% 0,5 l', 'Piwo bezalkoholowe', 17.00, 8),
  ('Lech Smakowy 0,0% 0,5 l', 'Piwo bezalkoholowe', 17.00, 8),
  ('Heineken 0,0% 0,5 l', 'Piwo bezalkoholowe', 17.00, 8),
  ('Książęce Pszenica 0,0% 0,5 l', 'Piwo bezalkoholowe', 17.00, 8),
  ('Wino bezalkoholowe kieliszek', 'Wino bezalkoholowe', 15.00, 8),
  ('Wino bezalkoholowe butelka', 'Wino bezalkoholowe', 80.00, 8),
  ('Tyskie Gronie 0,3 l', 'Piwo z beczki', 13.00, 23),
  ('Tyskie Gronie 0,5 l', 'Piwo z beczki', 16.00, 23),
  ('Tyskie Gronie 1,0 l', 'Piwo z beczki', 30.00, 23),
  ('Książęce Złote Pszeniczne 0,3 l', 'Piwo z beczki', 14.00, 23),
  ('Książęce Złote Pszeniczne 0,5 l', 'Piwo z beczki', 17.00, 23),
  ('Książęce Złote Pszeniczne 1,0 l', 'Piwo z beczki', 32.00, 23),
  ('Lech Premium 0,5 l', 'Piwo z butelki', 16.00, 23),
  ('Lech Premium 1,0 l', 'Piwo z butelki', 30.00, 23),
  ('Perła 0,5 l', 'Piwo z butelki', 16.00, 23),
  ('Perła 1,0 l', 'Piwo z butelki', 30.00, 23),
  ('Pilsner Urquell 0,5 l', 'Piwo z butelki', 17.00, 23),
  ('Pilsner Urquell 1,0 l', 'Piwo z butelki', 32.00, 23),
  ('Heineken 0,5 l', 'Piwo z butelki', 17.00, 23),
  ('Heineken 1,0 l', 'Piwo z butelki', 32.00, 23),
  ('Kozel Ciemny 0,5 l', 'Piwo z butelki', 17.00, 23),
  ('Kozel Ciemny 1,0 l', 'Piwo z butelki', 32.00, 23),
  ('Piwo kraftowe 0,5 l', 'Piwo z butelki', 22.00, 23),
  ('Piwo kraftowe 1,0 l', 'Piwo z butelki', 37.00, 23),
  ('Syrop do piwa 0,3 l', 'Dodatki', 2.00, 23),
  ('Syrop do piwa 0,5 l', 'Dodatki', 3.00, 23),
  ('Syrop do piwa 1,0 l', 'Dodatki', 4.00, 23),
  ('Winiarnia Zamojska kieliszek', 'Wino', 14.00, 23),
  ('Winiarnia Zamojska butelka', 'Wino', 80.00, 23),
  ('Luna Argenta Moscato kieliszek', 'Wino', 15.00, 23),
  ('Luna Argenta Moscato butelka', 'Wino', 90.00, 23),
  ('Beauvillion kieliszek', 'Wino', 14.00, 23),
  ('Beauvillion butelka', 'Wino', 85.00, 23),
  ('Cono Sur kieliszek', 'Wino', 14.00, 23),
  ('Cono Sur butelka', 'Wino', 80.00, 23),
  ('Sheep Dreams Sauvignon Blanc kieliszek', 'Wino', 17.00, 23),
  ('Sheep Dreams Sauvignon Blanc butelka', 'Wino', 110.00, 23),
  ('Los Pagos kieliszek', 'Wino', 14.00, 23),
  ('Los Pagos butelka', 'Wino', 80.00, 23),
  ('Primitivo Puglia kieliszek', 'Wino', 14.00, 23),
  ('Primitivo Puglia butelka', 'Wino', 80.00, 23),
  ('Primitivo di Manduria kieliszek', 'Wino', 16.00, 23),
  ('Primitivo di Manduria butelka', 'Wino', 110.00, 23),
  ('Wino spod lady kieliszek', 'Wino', 15.00, 23),
  ('Wino spod lady butelka', 'Wino', 90.00, 23),
  ('Martini Prosecco kieliszek', 'Wino', 15.00, 23),
  ('Martini Prosecco butelka', 'Wino', 90.00, 23),
  ('Martini Bianco', 'Wermuty', 14.00, 23),
  ('Martini Rosso', 'Wermuty', 14.00, 23),
  ('Cuba Libre', 'Drinki', 26.00, 23),
  ('Whisky Sour', 'Drinki', 32.00, 23),
  ('Mojito', 'Drinki', 32.00, 23),
  ('Aperol Spritz', 'Drinki', 30.00, 23),
  ('Margarita', 'Drinki', 28.00, 23),
  ('Caipiroska', 'Drinki', 27.00, 23),
  ('Krwawa Mary', 'Drinki', 28.00, 23),
  ('Sex on the Beach', 'Drinki', 28.00, 23),
  ('Tequila Sour', 'Drinki', 30.00, 23),
  ('Negroni', 'Drinki', 30.00, 23),
  ('Hugo', 'Drinki', 27.00, 23),
  ('Początek', 'Drinki – nasze', 24.00, 23),
  ('Wspomnienie', 'Drinki – nasze', 24.00, 23),
  ('Przytulny Kącik', 'Drinki – nasze', 25.00, 23),
  ('Rok 1926', 'Drinki – nasze', 25.00, 23),
  ('Strychowy', 'Drinki – nasze', 26.00, 23),
  ('Samotna Dziewczyna', 'Drinki – nasze', 26.00, 23),
  ('Marzenie', 'Drinki – nasze', 27.00, 23),
  ('Satyra', 'Drinki – nasze', 27.00, 23),
  ('Stały Bywalec', 'Drinki – nasze', 27.00, 23),
  ('Poezja', 'Drinki – nasze', 27.00, 23),
  ('Ojciec Chrzestny', 'Drinki – nasze', 27.00, 23),
  ('Zachód Słońca', 'Drinki – nasze', 27.00, 23),
  ('Miętowy Lodowiec', 'Drinki – nasze', 28.00, 23),
  ('Zazdrosna Żona', 'Drinki – nasze', 30.00, 23),
  ('Melancholia', 'Drinki – nasze', 32.00, 23),
  ('Krwawy Zdzisiu', 'Drinki – nasze', 32.00, 23),
  ('Na Pożegnanie', 'Drinki – nasze', 32.00, 23),
  ('Wściekły Pies', 'Shoty', 12.00, 23),
  ('Małpi Mózg', 'Shoty', 13.00, 23),
  ('Kamikadze – set 4 shoty', 'Shoty', 34.00, 23),
  ('Tequila złota', 'Shoty', 15.00, 23),
  ('Tequila srebrna', 'Shoty', 15.00, 23),
  ('Luksusowa 40 ml', 'Wódka', 10.00, 23),
  ('Luksusowa butelka 0,5 l', 'Wódka', 100.00, 23),
  ('Finlandia 40 ml', 'Wódka', 11.00, 23),
  ('Finlandia butelka 0,5 l', 'Wódka', 115.00, 23),
  ('Biały Bocian 40 ml', 'Wódka', 11.00, 23),
  ('Biały Bocian butelka 0,5 l', 'Wódka', 115.00, 23),
  ('Żurawinowa', 'Wódka', 10.00, 23),
  ('Wiśniówka', 'Wódka', 10.00, 23),
  ('Malinówka', 'Wódka', 10.00, 23),
  ('Pigwówka', 'Wódka', 10.00, 23),
  ('Żubrówka Trawiasta', 'Wódka', 10.00, 23),
  ('Kieliszek nalewki', 'Nalewki', 13.00, 23),
  ('Ballantine''s 40 ml', 'Whisky', 16.00, 23),
  ('Ballantine''s butelka 0,7 l', 'Whisky', 220.00, 23),
  ('Johnnie Walker 40 ml', 'Whisky', 16.00, 23),
  ('Johnnie Walker butelka 0,7 l', 'Whisky', 220.00, 23),
  ('Jameson Irish 40 ml', 'Whisky', 17.00, 23),
  ('Jameson Irish butelka 0,7 l', 'Whisky', 240.00, 23),
  ('Jim Beam White Bourbon 40 ml', 'Whisky', 16.00, 23),
  ('Jack Daniel''s 40 ml', 'Whisky', 18.00, 23),
  ('Jack Daniel''s butelka 0,7 l', 'Whisky', 260.00, 23),
  ('Chivas Regal 40 ml', 'Whisky', 20.00, 23),
  ('Blue Curacao', 'Likiery i kremy', 14.00, 23),
  ('Melon', 'Likiery i kremy', 14.00, 23),
  ('Banan', 'Likiery i kremy', 14.00, 23),
  ('Amaretto', 'Likiery i kremy', 14.00, 23),
  ('Kahlua', 'Likiery i kremy', 15.00, 23),
  ('Passoa', 'Likiery i kremy', 14.00, 23),
  ('Archers', 'Likiery i kremy', 15.00, 23),
  ('Triple Sec', 'Likiery i kremy', 14.00, 23),
  ('Jagermeister', 'Likiery i kremy', 14.00, 23),
  ('Fernet Blanca', 'Likiery i kremy', 16.00, 23),
  ('Campari', 'Likiery i kremy', 15.00, 23),
  ('Baileys', 'Likiery i kremy', 16.00, 23),
  ('Advocaat', 'Likiery i kremy', 10.00, 23),
  ('Seagram''s', 'Gin, rum, brandy', 14.00, 23),
  ('Lubuski', 'Gin, rum, brandy', 14.00, 23),
  ('Bacardi', 'Gin, rum, brandy', 16.00, 23),
  ('Havana Club', 'Gin, rum, brandy', 16.00, 23),
  ('Captain Morgan', 'Gin, rum, brandy', 16.00, 23),
  ('Stock 84', 'Gin, rum, brandy', 17.00, 23),
  ('Ciasto domowej roboty', 'Desery', 21.00, 8),
  ('Ciasto spod lady', 'Desery', 24.00, 8),
  ('Lody w pucharku', 'Desery', 28.00, 8),
  ('Paluszki Lajkonik', 'Przekąski', 16.00, 8),
  ('Orzeszki solone', 'Przekąski', 16.00, 8),
  ('Chipsy', 'Przekąski', 16.00, 8),
  ('Nachos z sosem serowym', 'Przekąski', 23.00, 8),
  ('Pajda chleba', 'Zakąski', 17.00, 8),
  ('Domowe tosty na ciepło', 'Zakąski', 17.00, 8),
  ('Panini', 'Zakąski', 18.00, 8),
  ('Krokiety na ciepło (2 szt.)', 'Zakąski', 17.00, 8),
  ('Łazanki na ciepło', 'Zakąski', 18.00, 8),
  ('Deska rozmaitości dla 2 osób', 'Zakąski', 38.00, 8)
) as v(name, category, price, tax_rate)
where not exists (
  select 1 from public.menu_items m where m.name = v.name and m.category = v.category
);

-- =====================================================================
-- 2. AKTUALNOŚCI NA STRONĘ WWW (wysyłane z aplikacji przez kierownika)
-- =====================================================================
create table if not exists public.site_news (
  id          uuid primary key default gen_random_uuid(),
  title       text not null check (char_length(title) between 1 and 120),
  body        text check (char_length(body) <= 2000),
  image_url   text,
  image_path  text,
  event_date  date,
  published   boolean not null default true,
  pinned      boolean not null default false,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz,
  created_by  uuid references auth.users(id) on delete set null
);
alter table public.site_news enable row level security;
grant select on public.site_news to anon, authenticated;
grant insert, update, delete on public.site_news to authenticated;

drop policy if exists "site_news: wszyscy czytają opublikowane" on public.site_news;
create policy "site_news: wszyscy czytają opublikowane" on public.site_news
  for select using (published = true);

drop policy if exists "site_news: kierownik widzi wszystko" on public.site_news;
create policy "site_news: kierownik widzi wszystko" on public.site_news
  for select to authenticated using (public.is_manager());

drop policy if exists "site_news: kierownik dodaje" on public.site_news;
create policy "site_news: kierownik dodaje" on public.site_news
  for insert to authenticated with check (public.is_manager());

drop policy if exists "site_news: kierownik edytuje" on public.site_news;
create policy "site_news: kierownik edytuje" on public.site_news
  for update to authenticated using (public.is_manager()) with check (public.is_manager());

drop policy if exists "site_news: kierownik usuwa" on public.site_news;
create policy "site_news: kierownik usuwa" on public.site_news
  for delete to authenticated using (public.is_manager());

-- odświeżanie na żywo (strona i aplikacja widzą nowe wpisy od razu)
do $$ begin
  alter publication supabase_realtime add table public.site_news;
exception when duplicate_object then null; end $$;

-- Publiczny folder na zdjęcia do aktualności
insert into storage.buckets (id, name, public)
values ('site-news', 'site-news', true)
on conflict (id) do update set public = true;

drop policy if exists "site-news: kierownik wysyła zdjęcia" on storage.objects;
create policy "site-news: kierownik wysyła zdjęcia" on storage.objects
  for insert to authenticated with check (bucket_id = 'site-news' and public.is_manager());

drop policy if exists "site-news: kierownik usuwa zdjęcia" on storage.objects;
create policy "site-news: kierownik usuwa zdjęcia" on storage.objects
  for delete to authenticated using (bucket_id = 'site-news' and public.is_manager());

-- =====================================================================
-- 3. PROŚBY O REZERWACJĘ ZE STRONY WWW
--    Gość może tylko DODAĆ rezerwację ze statusem "pending" (nie widzi
--    cudzych rezerwacji). Kierownik zatwierdza ją w aplikacji.
-- =====================================================================
alter table public.bookings add column if not exists source text;
alter table public.bookings add column if not exists notes text;
alter table public.bookings add column if not exists booking_status text default 'confirmed';
alter table public.bookings add column if not exists end_at timestamptz;
alter table public.bookings alter column created_by drop not null;

drop policy if exists "bookings: prośba o rezerwację ze strony" on public.bookings;
create policy "bookings: prośba o rezerwację ze strony" on public.bookings
  for insert to anon
  with check (
    booking_status = 'pending'
    and source = 'www'
    and created_by is null
    and guests_count between 1 and 120
    and start_at > now()
    and start_at < now() + interval '180 days'
    and char_length(title) between 2 and 80
    and char_length(coalesce(notes, '')) <= 600
  );
grant insert on public.bookings to anon;
