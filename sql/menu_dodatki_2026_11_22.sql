-- Cafe Strych – herbaty z alkoholem (zgłoszenie Weroniki, 22.11.2026)
-- Każda: herbata czarna + 40 ml alkoholu. VAT 23%.
-- Uruchom w Supabase: SQL Editor → wklej całość → Run. Można uruchomić ponownie – niczego nie zdubluje.
insert into public.menu_items (name, category, price, tax_rate, active)
select v.name, v.category, v.price, v.tax_rate, true
from (values
  ('Herbata z rumem Captain Morgan', 'Herbata z alkoholem', 26.00, 23),
  ('Herbata z wódką Luksusowa', 'Herbata z alkoholem', 21.00, 23),
  ('Herbata z wódką wiśniową', 'Herbata z alkoholem', 21.00, 23)
) as v(name, category, price, tax_rate)
where not exists (select 1 from public.menu_items m where lower(m.name) = lower(v.name));

select name, category, price, tax_rate, active from public.menu_items
where name in ('Herbata z rumem Captain Morgan', 'Herbata z wódką Luksusowa', 'Herbata z wódką wiśniową') order by name;
