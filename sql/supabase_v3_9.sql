-- =====================================================================
-- Cafe Strych – V3.9 (22.10.2026)
-- Posty z Instagrama, TikToka i Facebooka na stronie www.
-- Kierownik wkleja w aplikacji link do posta/filmiku → strona pokazuje
-- go w sekcji „Na bieżąco” (oficjalne osadzenie pojedynczego posta).
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

create table if not exists public.site_social_posts (
  id          uuid primary key default gen_random_uuid(),
  platform    text not null check (platform in ('instagram', 'tiktok', 'facebook')),
  url         text not null check (char_length(url) between 10 and 500),
  note        text check (char_length(note) <= 200),
  published   boolean not null default true,
  created_at  timestamptz not null default now(),
  created_by  uuid references auth.users(id) on delete set null
);
create unique index if not exists site_social_posts_url_key on public.site_social_posts (url);

alter table public.site_social_posts enable row level security;
grant select on public.site_social_posts to anon, authenticated;
grant insert, update, delete on public.site_social_posts to authenticated;

drop policy if exists "site_social_posts: wszyscy widzą opublikowane" on public.site_social_posts;
create policy "site_social_posts: wszyscy widzą opublikowane" on public.site_social_posts
  for select using (published = true);

drop policy if exists "site_social_posts: kierownik zarządza" on public.site_social_posts;
create policy "site_social_posts: kierownik zarządza" on public.site_social_posts
  for all to authenticated using (public.is_manager()) with check (public.is_manager());

do $$ begin
  alter publication supabase_realtime add table public.site_social_posts;
exception when duplicate_object then null; end $$;

notify pgrst, 'reload schema';
