-- =====================================================================
-- Cafe Strych – V5.1.2 (03.11.2026)
-- Kierownik ma te same prawa do rachunków co administrator:
--   • może anulować opłacony rachunek,
--   • może trwale usunąć z historii każdy rachunek (opłacony i anulowany).
-- Usunięcie zapisuje się w „System i logi” (kto, co, kwota).
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- =====================================================================

-- zabezpieczenia rachunków: opłacony rachunek anuluje kierownik lub administrator
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
      if not public.is_manager() then
        raise exception 'Opłacony rachunek może anulować kierownik lub administrator.';
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

-- trwałe usunięcie rachunku z historii (kierownik i administrator)
create or replace function public.pos_delete_order(p_order uuid)
returns void language plpgsql security definer set search_path = public as $$
declare o record; v_total numeric; v_paid numeric;
begin
  select * into o from public.pos_orders where id = p_order;
  if not found then return; end if;
  if not public.is_manager() then
    raise exception 'Rachunek z historii może usunąć kierownik lub administrator.';
  end if;
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
