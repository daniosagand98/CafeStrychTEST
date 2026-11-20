-- Cafe Strych – 3 brakujące drinki w menu POS (zgłoszenie Weroniki, 20.11.2026)
-- Wszystkie trzy są alkoholowe (VAT 23%).
-- Uruchom w Supabase: SQL Editor → wklej całość → Run.
-- Działa też, jeśli wcześniejszą wersję tego pliku już uruchomiono – poprawi kategorię i VAT, niczego nie zdubluje.
insert into public.menu_items (name, category, price, tax_rate, active)
select v.name, v.category, v.price, v.tax_rate, true
from (values
  ('Synek Mamusi',                          'Drinki – nasze', 25.00, 23),
  ('Cydr jabłkowy półsłodki z przyprawami', 'Grzańce',        22.00, 23),
  ('Miód pitny z przyprawami',              'Grzańce',        20.00, 23)
) as v(name, category, price, tax_rate)
where not exists (select 1 from public.menu_items m where lower(m.name) = lower(v.name));

update public.menu_items set category = 'Drinki – nasze', tax_rate = 23
 where lower(name) = lower('Synek Mamusi');
update public.menu_items set category = 'Grzańce', tax_rate = 23
 where lower(name) in (lower('Cydr jabłkowy półsłodki z przyprawami'), lower('Miód pitny z przyprawami'));

select name, category, price, tax_rate, active from public.menu_items
where name in ('Synek Mamusi','Cydr jabłkowy półsłodki z przyprawami','Miód pitny z przyprawami');
