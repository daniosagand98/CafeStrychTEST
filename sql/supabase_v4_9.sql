-- =====================================================================
-- Cafe Strych – V5.1 (03.11.2026) – historia zmian rachunków
-- Baza sama zapisuje KAŻDĄ zmianę na rachunku: kto i o której
--   • otworzył rachunek,
--   • dodał lub usunął pozycję (ile sztuk),
--   • zmienił cenę / opis pozycji,
--   • dał rabat, przyjął płatność, anulował rachunek.
-- Zapisu nie da się ominąć ani poprawić z aplikacji – robi go baza.
-- Historię widzi tylko kierownik i administrator.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

create table if not exists public.pos_audit (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  order_id    uuid,
  order_label text,
  action      text not null,        -- open | add | remove | edit | discount | paid | cancelled | reopen
  item_name   text,
  qty_delta   numeric,
  unit_price  numeric,
  details     text,
  user_id     uuid,
  user_name   text
);
create index if not exists pos_audit_created_idx on public.pos_audit (created_at desc);
create index if not exists pos_audit_order_idx   on public.pos_audit (order_id, created_at);
create index if not exists pos_audit_user_idx    on public.pos_audit (user_id, created_at desc);

alter table public.pos_audit enable row level security;
drop policy if exists "pos_audit: kierownik czyta" on public.pos_audit;
create policy "pos_audit: kierownik czyta" on public.pos_audit
  for select to authenticated using (public.is_manager());
-- brak zasad insert/update/delete: wpisy dodają wyłącznie funkcje poniżej
revoke insert, update, delete on public.pos_audit from anon, authenticated;

-- kto wykonuje zmianę
create or replace function public.audit_who(out uid uuid, out who text)
language plpgsql stable security definer set search_path = public as $$
begin
  uid := auth.uid();
  if uid is null then who := 'System'; return; end if;
  select coalesce(nullif(trim(p.full_name), ''), p.email, 'Użytkownik') into who
    from public.profiles p where p.id = uid;
  if who is null then
    select email into who from auth.users where id = uid;
  end if;
  who := coalesce(who, 'Użytkownik');
end $$;
revoke all on function public.audit_who() from public, anon, authenticated;

create or replace function public.audit_order_label(p_order uuid) returns text
language sql stable security definer set search_path = public as $$
  select coalesce(nullif(o.customer_name, ''), t.label, o.order_no, 'Rachunek')
    from public.pos_orders o left join public.cafe_tables t on t.id = o.table_id
   where o.id = p_order
$$;
revoke all on function public.audit_order_label(uuid) from public, anon, authenticated;

-- pozycje rachunku
create or replace function public.pos_items_audit() returns trigger
language plpgsql security definer set search_path = public as $$
declare w record; d numeric; o uuid;
begin
  if current_setting('cafe.delete_order', true) = 'on' then return null; end if;  -- usuwanie całego rachunku z historii (zapisane w logach)
  select * into w from public.audit_who();
  o := case when tg_op = 'DELETE' then old.order_id else new.order_id end;

  if tg_op = 'INSERT' then
    insert into public.pos_audit (order_id, order_label, action, item_name, qty_delta, unit_price, user_id, user_name)
    values (o, public.audit_order_label(o), 'add', new.item_name, new.qty, new.unit_price, w.uid, w.who);

  elsif tg_op = 'DELETE' then
    insert into public.pos_audit (order_id, order_label, action, item_name, qty_delta, unit_price, user_id, user_name)
    values (o, public.audit_order_label(o), 'remove', old.item_name, -old.qty, old.unit_price, w.uid, w.who);

  else
    d := new.qty - old.qty;
    if d <> 0 then
      insert into public.pos_audit (order_id, order_label, action, item_name, qty_delta, unit_price, user_id, user_name)
      values (o, public.audit_order_label(o), case when d > 0 then 'add' else 'remove' end, new.item_name, d, new.unit_price, w.uid, w.who);
    end if;
    if new.unit_price is distinct from old.unit_price or new.item_name is distinct from old.item_name
       or new.notes is distinct from old.notes then
      insert into public.pos_audit (order_id, order_label, action, item_name, unit_price, details, user_id, user_name)
      values (o, public.audit_order_label(o), 'edit', new.item_name, new.unit_price,
              concat_ws(' • ',
                case when new.item_name is distinct from old.item_name then format('nazwa: %s → %s', old.item_name, new.item_name) end,
                case when new.unit_price is distinct from old.unit_price then format('cena: %s → %s zł', old.unit_price, new.unit_price) end,
                case when new.notes is distinct from old.notes then format('uwagi: %s', coalesce(new.notes, '—')) end),
              w.uid, w.who);
    end if;
  end if;
  return null;
exception when others then
  raise warning 'pos_items_audit: %', sqlerrm;   -- zapis historii nigdy nie blokuje POS
  return null;
end $$;
revoke all on function public.pos_items_audit() from public, anon, authenticated;

drop trigger if exists pos_order_items_audit on public.pos_order_items;
create trigger pos_order_items_audit after insert or update or delete on public.pos_order_items
  for each row execute function public.pos_items_audit();

-- rachunki: otwarcie, rabat, płatność, anulowanie
create or replace function public.pos_orders_audit() returns trigger
language plpgsql security definer set search_path = public as $$
declare w record; lbl text;
begin
  if current_setting('cafe.delete_order', true) = 'on' then return null; end if;
  select * into w from public.audit_who();

  if tg_op = 'INSERT' then
    lbl := coalesce(nullif(new.customer_name, ''), (select label from public.cafe_tables where id = new.table_id), new.order_no, 'Rachunek');
    insert into public.pos_audit (order_id, order_label, action, user_id, user_name)
    values (new.id, lbl, 'open', w.uid, w.who);
    return null;
  end if;

  if tg_op = 'UPDATE' then
    lbl := coalesce(nullif(new.customer_name, ''), (select label from public.cafe_tables where id = new.table_id), new.order_no, 'Rachunek');
    if new.discount_pct is distinct from old.discount_pct then
      insert into public.pos_audit (order_id, order_label, action, details, user_id, user_name)
      values (new.id, lbl, 'discount', format('rabat: %s%% → %s%%', coalesce(old.discount_pct, 0), coalesce(new.discount_pct, 0)), w.uid, w.who);
    end if;
    if new.status is distinct from old.status
       and (new.status in ('paid', 'cancelled') or old.status in ('paid', 'cancelled')) then
      insert into public.pos_audit (order_id, order_label, action, details, user_id, user_name)
      values (new.id, lbl,
              case new.status when 'paid' then 'paid' when 'cancelled' then 'cancelled' else 'reopen' end,
              case when new.status = 'cancelled' then nullif(new.cancel_reason, '') end,
              w.uid, w.who);
    end if;
  end if;
  return null;
exception when others then
  raise warning 'pos_orders_audit: %', sqlerrm;
  return null;
end $$;
revoke all on function public.pos_orders_audit() from public, anon, authenticated;

drop trigger if exists pos_orders_audit on public.pos_orders;
create trigger pos_orders_audit after insert or update on public.pos_orders
  for each row execute function public.pos_orders_audit();

notify pgrst, 'reload schema';
