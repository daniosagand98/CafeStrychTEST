-- =====================================================================
-- Cafe Strych – V4.5 (23.10.2026) – usuwanie rachunków z historii
-- Tylko ADMINISTRATOR może trwale usunąć rachunek z historii
-- (opłacony lub anulowany) razem z jego pozycjami i płatnościami.
-- Usunięty rachunek znika też z utargu (dzień / miesiąc / rok).
-- Każde usunięcie jest zapisywane w „System i logi” (kto, co, kwota).
-- Zwykłe zabezpieczenia zamkniętych rachunków działają dalej – omija je
-- wyłącznie ta funkcja.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

-- 1) zabezpieczenia rachunków: przepuszczają tylko usuwanie przez funkcję poniżej
create or replace function public.pos_orders_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null or current_setting('cafe.delete_order', true) = 'on' then
    if tg_op = 'DELETE' then return old; end if;
    return new;
  end if;

  if tg_op = 'DELETE' then
    if old.status in ('paid', 'cancelled') or exists (select 1 from public.pos_payments where order_id = old.id) then
      raise exception 'Opłaconego ani anulowanego rachunku nie można usunąć – użyj „Anuluj”.';
    end if;
    return old;
  end if;

  if old.status = 'cancelled' and new.status is distinct from 'cancelled' then
    raise exception 'Anulowanego rachunku nie można przywrócić.';
  end if;

  if new.status = 'paid' and old.status is distinct from 'paid' and not public.is_manager() then
    raise exception 'Płatność zatwierdza kierownik lub administrator.';
  end if;

  if old.status = 'paid' and new.status is distinct from 'paid' then
    if new.status = 'cancelled' then
      if not public.is_admin() then
        raise exception 'Opłacony rachunek może anulować tylko administrator.';
      end if;
    elsif exists (select 1 from public.pos_payments where order_id = old.id) then
      raise exception 'Opłaconego rachunku nie można ponownie otworzyć.';
    end if;
  end if;

  if new.status = 'cancelled' and old.status is distinct from 'cancelled' then
    if old.status is distinct from 'paid' and not public.is_manager() then
      raise exception 'Rachunek może anulować kierownik lub administrator.';
    end if;
    new.cancelled_at := coalesce(new.cancelled_at, now());
    new.cancelled_by := coalesce(new.cancelled_by, auth.uid());
  end if;

  return new;
end $$;

create or replace function public.pos_items_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare s text;
begin
  if auth.uid() is null or current_setting('cafe.delete_order', true) = 'on' then
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

-- 2) trwałe usunięcie rachunku z historii (tylko admin)
create or replace function public.pos_delete_order(p_order uuid)
returns void language plpgsql security definer set search_path = public as $$
declare o record; v_total numeric; v_paid numeric;
begin
  if not public.is_admin() then
    raise exception 'Rachunek z historii może usunąć tylko administrator.';
  end if;
  select * into o from public.pos_orders where id = p_order;
  if not found then return; end if;
  select coalesce(sum(qty * unit_price), 0) into v_total from public.pos_order_items where order_id = p_order;
  select coalesce(sum(amount), 0) into v_paid from public.pos_payments where order_id = p_order;

  perform set_config('cafe.delete_order', 'on', true);
  delete from public.pos_payments    where order_id = p_order;
  delete from public.pos_order_items where order_id = p_order;
  delete from public.pos_orders      where id = p_order;
  perform set_config('cafe.delete_order', 'off', true);

  insert into public.activity_logs (action, user_email)
  values (format('Usunięto rachunek z historii: %s (%s, %s) – pozycje %s zł, płatności %s zł',
                 coalesce(o.customer_name, o.order_no, 'Rachunek'), o.status,
                 to_char(o.created_at at time zone 'Europe/Warsaw', 'DD.MM.YYYY HH24:MI'),
                 to_char(v_total, 'FM999990.00'), to_char(v_paid, 'FM999990.00')),
          (select email from auth.users where id = auth.uid()));
end $$;

revoke all on function public.pos_delete_order(uuid) from public, anon;
grant execute on function public.pos_delete_order(uuid) to authenticated;

notify pgrst, 'reload schema';
