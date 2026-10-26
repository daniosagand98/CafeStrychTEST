-- =====================================================================
-- Cafe Strych – V4.8 (26.10.2026) – galeria strony do samodzielnej obsługi
-- Kierownik / administrator w aplikacji: dodaje zdjęcia (kilka naraz), wpisuje opisy,
-- ukrywa, zmienia kolejność i usuwa. Strona pokazuje tylko widoczne zdjęcia, w tej kolejności.
-- Na start wpisane są wszystkie obecne zdjęcia strony (z opisami) – można je od razu edytować.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie (zdjęcia startowe dodają się tylko do pustej galerii).
-- =====================================================================

create table if not exists public.site_gallery (
  id          uuid primary key default gen_random_uuid(),
  image_url   text not null check (char_length(image_url) between 5 and 1000),
  image_path  text,                       -- plik w Storage (site-news/gallery/...), pusty dla zdjęć wbudowanych w stronę
  caption     text check (char_length(caption) <= 160),
  sort_order  int  not null default 0,
  published   boolean not null default true,
  created_at  timestamptz not null default now(),
  created_by  uuid references auth.users(id) on delete set null
);
create index if not exists site_gallery_order_idx on public.site_gallery (sort_order, created_at);

alter table public.site_gallery enable row level security;
grant select on public.site_gallery to anon, authenticated;
grant insert, update, delete on public.site_gallery to authenticated;

drop policy if exists "site_gallery: wszyscy widzą opublikowane" on public.site_gallery;
create policy "site_gallery: wszyscy widzą opublikowane" on public.site_gallery
  for select using (published = true);
drop policy if exists "site_gallery: kierownik zarządza" on public.site_gallery;
create policy "site_gallery: kierownik zarządza" on public.site_gallery
  for all to authenticated using (public.is_manager()) with check (public.is_manager());

do $$ begin
  alter publication supabase_realtime add table public.site_gallery;
exception when duplicate_object then null; end $$;

-- zdjęcia startowe (tylko gdy galeria jest pusta)
insert into public.site_gallery (image_url, caption, sort_order)
select v.image_url, v.caption, v.sort_order
  from (values
  ('img/foto-bar-pianino.webp', 'Bar pod schodami, pianino i gitary', 10),
  ('img/foto-piec.webp', 'Żeliwny piec – zimą zawsze napalony', 20),
  ('img/foto-pianino.webp', 'Pianino dla gości – zagraj coś!', 30),
  ('img/foto-ciasta.webp', 'Ciasta domowej roboty', 40),
  ('img/foto-planszowki.webp', 'Planszówki ze znajomymi', 50),
  ('img/foto-czekolada-tosty.webp', 'Gorąca czekolada, tosty i nalewki', 60),
  ('img/foto-shoty.webp', 'Nalewki na desce Strychu', 70),
  ('img/foto-piwo-nalewanie.webp', 'Tyskie prosto z nalewaka', 80),
  ('img/foto-koktajle.webp', 'Kolorowe koktajle', 90),
  ('img/foto-deska-serow.webp', 'Deska serów i wędlin', 100),
  ('img/foto-deska-desery.webp', 'Deska wędlin, lody i koktajle', 110),
  ('img/foto-krupnik.webp', 'Krupnik, drinki i przekąski', 120),
  ('img/foto-fartuch.webp', 'Precel z twarożkiem i orzeszki', 130),
  ('img/hero-witraz.webp', 'Sala z witrażem', 140),
  ('img/hero-antresola.webp', 'Sala z antresolą i białym piecem', 150),
  ('img/strych-antresola.webp', 'Antresola na strychu', 160),
  ('img/strych-stolik.webp', 'Stolik pod dachem', 170),
  ('img/brama.webp', 'Malowana brama od podwórza', 180)
  ) as v(image_url, caption, sort_order)
 where not exists (select 1 from public.site_gallery);

notify pgrst, 'reload schema';
