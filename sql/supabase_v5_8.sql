-- Cafe Strych Manager V5.8 – dzielenie rachunku
-- Uruchom w Supabase: SQL Editor → wklej całość → Run.
--
-- Funkcja pos_split_order przenosi wybrane pozycje (całe albo część sztuk)
-- z otwartego rachunku na nowy rachunek. Wszystko dzieje się naraz:
-- albo przeniesie się wszystko, albo nic. Działa tylko na tablecie firmowym.
-- W historii rachunku zapisuje się, kto i o której podzielił rachunek.

create or replace function public.pos_split_order(
  p_order uuid,       -- rachunek, z którego przenosimy
  p_new   uuid,       -- id nowego rachunku (nadaje aplikacja)
  p_no    text,       -- numer nowego rachunku, np. "20.11.2026 • Rachunek 5"
  p_name  text,       -- nazwa nowego rachunku, np. "Stolik 3 – część 2"
  p_items jsonb       -- [{"id": "<id pozycji>", "qty": 2}, ...]
) returns uuid
language plpgsql security definer set search_path = public as $$
declare
  o record; it record; e jsonb; n numeric; moved int := 0;
  w record; v_old text; v_new text;
begin
  if not public.is_active_member() then raise exception 'Brak dostępu.'; end if;
  if not public.pos_write_allowed() then raise exception 'POS działa tylko na tablecie firmowym.'; end if;

  select * into o from public.pos_orders where id = p_order for update;
  if not found then raise exception 'Nie znaleziono rachunku.'; end if;
  if o.status in ('paid', 'cancelled') then
    raise exception 'Rachunek jest zamknięty – nie można go podzielić.';
  end if;
  if p_items is null or jsonb_typeof(p_items) <> 'array' or jsonb_array_length(p_items) = 0 then
    raise exception 'Wybierz pozycje do przeniesienia.';
  end if;
  if exists (select 1 from public.pos_orders where id = p_new) then
    return p_new;                                   -- ten podział już zapisano (ponowne kliknięcie)
  end if;

  insert into public.pos_orders (id, order_no, table_id, customer_name, status, source, created_by, created_at)
  values (p_new, nullif(trim(p_no), ''), o.table_id, nullif(trim(p_name), ''), 'new', 'pos', auth.uid(), now());

  for e in select * from jsonb_array_elements(p_items) loop
    n := coalesce((e->>'qty')::numeric, 0);
    if n <= 0 then continue; end if;
    select * into it from public.pos_order_items
     where id = (e->>'id')::uuid and order_id = p_order for update;
    if not found then raise exception 'Pozycja nie należy do tego rachunku (ktoś mógł ją zmienić – odśwież).'; end if;
    if n > it.qty then raise exception 'Na rachunku jest tylko % szt. „%”.', it.qty, it.item_name; end if;

    if n = it.qty then
      delete from public.pos_order_items where id = it.id;
    else
      update public.pos_order_items set qty = qty - n where id = it.id;
    end if;
    insert into public.pos_order_items (order_id, menu_item_id, item_name, qty, unit_price, tax_rate, notes)
    values (p_new, it.menu_item_id, it.item_name, n, it.unit_price, it.tax_rate, it.notes);
    moved := moved + 1;
  end loop;

  if moved = 0 then raise exception 'Wybierz pozycje do przeniesienia.'; end if;
  if not exists (select 1 from public.pos_order_items where order_id = p_order) then
    raise exception 'Na pierwszym rachunku musi coś zostać. Żeby przenieść wszystko, zmień po prostu nazwę lub stolik.';
  end if;

  -- wpis w historii obu rachunków
  begin
    select * into w from public.audit_who();
    v_old := public.audit_order_label(p_order);
    v_new := public.audit_order_label(p_new);
    insert into public.pos_audit (order_id, order_label, action, details, user_id, user_name)
    values (p_order, v_old, 'split', 'przeniesiono ' || moved || ' poz. na rachunek „' || v_new || '”', w.uid, w.who),
           (p_new,   v_new, 'split', 'utworzono z podziału rachunku „' || v_old || '”', w.uid, w.who);
  exception when others then
    raise warning 'pos_split_order audit: %', sqlerrm;
  end;

  return p_new;
end $$;

revoke all on function public.pos_split_order(uuid, uuid, text, text, jsonb) from public, anon;
grant execute on function public.pos_split_order(uuid, uuid, text, text, jsonb) to authenticated;

notify pgrst, 'reload schema';
