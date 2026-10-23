-- =====================================================================
-- Cafe Strych – V4.2 (23.10.2026)  – szybszy i pewniejszy POS
-- 1) Dodawanie / odejmowanie pozycji na rachunku jednym zapytaniem
--    (atomowo: dwa telefony klikające naraz nie „zgubią” sztuki).
-- 2) Indeksy przyspieszające rachunki i utarg.
-- Uprawnienia i blokada zamkniętych rachunków działają jak dotąd
-- (funkcje działają z prawami zalogowanej osoby).
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

-- +/- sztuka produktu z menu na rachunku
create or replace function public.pos_bump_item(p_order uuid, p_menu uuid, p_delta int)
returns void language plpgsql security invoker set search_path = public as $$
declare v_id uuid; v_qty numeric; m record;
begin
  if not public.is_active_member() then raise exception 'Brak dostępu.'; end if;
  select id, qty into v_id, v_qty from public.pos_order_items
   where order_id = p_order and menu_item_id = p_menu
   order by created_at limit 1 for update;
  if v_id is null then
    if p_delta <= 0 then return; end if;
    select name, price, tax_rate into m from public.menu_items where id = p_menu;
    if not found then raise exception 'Tego produktu nie ma już w menu.'; end if;
    insert into public.pos_order_items (order_id, menu_item_id, item_name, qty, unit_price, tax_rate)
    values (p_order, p_menu, m.name, p_delta, m.price, coalesce(m.tax_rate, 23));
  elsif v_qty + p_delta <= 0 then
    delete from public.pos_order_items where id = v_id;
  else
    update public.pos_order_items set qty = qty + p_delta where id = v_id;
  end if;
end $$;

-- +/- sztuka konkretnej pozycji (np. produkt usunięty już z menu)
create or replace function public.pos_bump_line(p_item uuid, p_delta int)
returns void language plpgsql security invoker set search_path = public as $$
declare v_qty numeric;
begin
  if not public.is_active_member() then raise exception 'Brak dostępu.'; end if;
  select qty into v_qty from public.pos_order_items where id = p_item for update;
  if not found then return; end if;
  if v_qty + p_delta <= 0 then delete from public.pos_order_items where id = p_item;
  else update public.pos_order_items set qty = qty + p_delta where id = p_item; end if;
end $$;

revoke all on function public.pos_bump_item(uuid, uuid, int) from public, anon;
revoke all on function public.pos_bump_line(uuid, int) from public, anon;
grant execute on function public.pos_bump_item(uuid, uuid, int) to authenticated;
grant execute on function public.pos_bump_line(uuid, int) to authenticated;

-- indeksy
create index if not exists pos_order_items_order_menu_idx on public.pos_order_items (order_id, menu_item_id);
create index if not exists pos_payments_created_idx on public.pos_payments (created_at);
create index if not exists pos_payments_order_idx on public.pos_payments (order_id);
create index if not exists pos_orders_created_idx on public.pos_orders (created_at desc);

notify pgrst, 'reload schema';
