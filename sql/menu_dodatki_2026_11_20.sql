-- Cafe Strych – 3 brakujące pozycje w menu POS (zgłoszenie Weroniki, 20.11.2026)
-- Uruchom w Supabase: SQL Editor → wklej całość → Run. Można uruchomić ponownie – niczego nie zdubluje.
-- Kategorie i VAT jak w podobnych pozycjach; w razie potrzeby popraw w aplikacji: Lokal → Menu POS.
insert into public.menu_items (name, category, price, tax_rate, active)
select v.name, v.category, v.price, v.tax_rate, true
from (values
  ('Synek Mamusi',                              'Koktajle bezalkoholowe', 25.00, 8),
  ('Cydr jabłkowy półsłodki z przyprawami',     'Grzańce bezalkoholowe',  22.00, 8),
  ('Miód pitny z przyprawami',                  'Grzańce bezalkoholowe',  20.00, 8)
) as v(name, category, price, tax_rate)
where not exists (select 1 from public.menu_items m where lower(m.name) = lower(v.name));

select name, category, price, tax_rate, active from public.menu_items
where name in ('Synek Mamusi','Cydr jabłkowy półsłodki z przyprawami','Miód pitny z przyprawami');
