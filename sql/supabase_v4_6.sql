-- =====================================================================
-- Cafe Strych – V4.6 (23.10.2026) – POS odporny na brak internetu
-- Każde kliknięcie na rachunku ma swój numer (id). Jeśli telefon wyśle
-- je drugi raz (np. internet zerwał się w trakcie wysyłania), baza
-- rozpozna powtórkę i NIE doliczy sztuki drugi raz.
-- Uprawnienia jak dotąd: zalogowany, aktywny członek zespołu;
-- zamknięte rachunki nadal są zablokowane (pos_items_guard).
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

create table if not exists public.pos_ops (
  id         uuid primary key,
  created_at timestamptz not null default now()
);
create index if not exists pos_ops_created_idx on public.pos_ops (created_at);
alter table public.pos_ops enable row level security;   -- bez zasad: dostęp tylko przez funkcję poniżej

create or replace function public.pos_bump_op(p_op uuid, p_order uuid, p_menu uuid, p_item uuid, p_delta int)
returns text language plpgsql security definer set search_path = public as $$
declare n int; v_id uuid; v_qty numeric; m record;
begin
  if not public.is_active_member() then raise exception 'Brak dostępu.'; end if;

  insert into public.pos_ops (id) values (p_op) on conflict (id) do nothing;
  get diagnostics n = row_count;
  if n = 0 then return 'duplicate'; end if;          -- to kliknięcie już zapisano wcześniej

  if p_menu is not null then
    select id, qty into v_id, v_qty from public.pos_order_items
     where order_id = p_order and menu_item_id = p_menu order by created_at limit 1 for update;
  else
    select id, qty into v_id, v_qty from public.pos_order_items where id = p_item for update;
  end if;

  if v_id is null then
    if p_delta <= 0 or p_menu is null then return 'ok'; end if;
    select name, price, tax_rate into m from public.menu_items where id = p_menu;
    if not found then raise exception 'Tego produktu nie ma już w menu.'; end if;
    insert into public.pos_order_items (order_id, menu_item_id, item_name, qty, unit_price, tax_rate)
    values (p_order, p_menu, m.name, p_delta, m.price, coalesce(m.tax_rate, 23));
  elsif v_qty + p_delta <= 0 then
    delete from public.pos_order_items where id = v_id;
  else
    update public.pos_order_items set qty = qty + p_delta where id = v_id;
  end if;

  -- sprzątanie starych numerów kliknięć (raz na ~200 wywołań)
  if random() < 0.005 then delete from public.pos_ops where created_at < now() - interval '30 days'; end if;
  return 'ok';
end $$;

revoke all on function public.pos_bump_op(uuid, uuid, uuid, uuid, int) from public, anon;
grant execute on function public.pos_bump_op(uuid, uuid, uuid, uuid, int) to authenticated;

notify pgrst, 'reload schema';
