-- =====================================================================
-- Cafe Strych – V4.4 (23.10.2026)
-- Poprawka: usuwanie produktu z Menu POS, który był na zamkniętym rachunku.
-- Przy usuwaniu produktu baza odpina go od starych pozycji (menu_item_id = null),
-- a zabezpieczenie zamkniętych rachunków blokowało to odpięcie.
-- Teraz samo odpięcie jest dozwolone – nazwa, ilość i cena na starym
-- rachunku zostają bez zmian. Każda inna zmiana zamkniętego rachunku
-- jest nadal blokowana.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- =====================================================================

create or replace function public.pos_items_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare s text;
begin
  if auth.uid() is null then
    if tg_op = 'DELETE' then return old; end if;
    return new;
  end if;

  -- odpięcie usuniętego produktu z menu (ON DELETE SET NULL) – tylko menu_item_id → null
  if tg_op = 'UPDATE' and new.menu_item_id is null and old.menu_item_id is not null
     and new.order_id = old.order_id and new.item_name is not distinct from old.item_name
     and new.qty = old.qty and new.unit_price = old.unit_price
     and new.tax_rate is not distinct from old.tax_rate and new.notes is not distinct from old.notes then
    return new;
  end if;

  select status into s from public.pos_orders
   where id = case when tg_op = 'DELETE' then old.order_id else new.order_id end;
  if s in ('paid', 'cancelled') then
    raise exception 'Rachunek jest zamknięty – nie można zmieniać jego pozycji.';
  end if;
  if tg_op = 'DELETE' then return old; end if;
  return new;
end $$;

notify pgrst, 'reload schema';
