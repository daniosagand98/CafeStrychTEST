-- =====================================================================
-- Cafe Strych – V4.1 (23.10.2026)
-- Kadrowanie zdjęcia w aktualnościach: zapamiętuje, który fragment
-- zdjęcia ma być widoczny na stronie (np. „50% 30%”).
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

alter table public.site_news add column if not exists image_pos text;

do $$ begin
  alter table public.site_news add constraint site_news_image_pos_format
    check (image_pos is null or image_pos ~ '^\d{1,3}(\.\d+)?% \d{1,3}(\.\d+)?%$');
exception when duplicate_object then null; end $$;

notify pgrst, 'reload schema';
