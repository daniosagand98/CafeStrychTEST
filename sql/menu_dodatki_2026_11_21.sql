-- Cafe Strych – kawy i czekolady z alkoholem (zgłoszenie Weroniki, 21.11.2026)
-- Każda: 30 ml alkoholu + bita śmietana. VAT 23%.
-- Uruchom w Supabase: SQL Editor → wklej całość → Run. Można uruchomić ponownie – niczego nie zdubluje.
insert into public.menu_items (name, category, price, tax_rate, active)
select v.name, v.category, v.price, v.tax_rate, true
from (values
  ('Kawa z kremem Baileys', 'Kawa i czekolada z alkoholem', 30.00, 23),
  ('Kawa z whisky Jameson', 'Kawa i czekolada z alkoholem', 30.00, 23),
  ('Kawa z kremem Advocaat', 'Kawa i czekolada z alkoholem', 26.00, 23),
  ('Kawa z likierem Amaretto', 'Kawa i czekolada z alkoholem', 26.00, 23),
  ('Czekolada z kremem Baileys', 'Kawa i czekolada z alkoholem', 30.00, 23),
  ('Czekolada z whisky Jameson', 'Kawa i czekolada z alkoholem', 30.00, 23),
  ('Czekolada z kremem Advocaat', 'Kawa i czekolada z alkoholem', 26.00, 23),
  ('Czekolada z likierem Amaretto', 'Kawa i czekolada z alkoholem', 26.00, 23)
) as v(name, category, price, tax_rate)
where not exists (select 1 from public.menu_items m where lower(m.name) = lower(v.name));

select name, category, price, tax_rate, active from public.menu_items
where name in ('Kawa z kremem Baileys', 'Kawa z whisky Jameson', 'Kawa z kremem Advocaat', 'Kawa z likierem Amaretto', 'Czekolada z kremem Baileys', 'Czekolada z whisky Jameson', 'Czekolada z kremem Advocaat', 'Czekolada z likierem Amaretto') order by name;
