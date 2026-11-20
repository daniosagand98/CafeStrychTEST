-- =====================================================================
-- Cafe Strych – V5.7.1 (20.11.2026)
-- Pracownik (na tablecie firmowym) może też dać rabat i anulować rachunek
-- (otwarty i opłacony – z powodem, zostaje w historii jako ANULOWANY).
-- Trwałe USUWANIE rachunków z historii – tylko kierownik i administrator.
-- Każda zmiana zapisuje się w „Historii rachunków” (kto i o której).
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

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

  -- V5.7: płatność i zamknięcie rachunku – każdy aktywny członek zespołu
  -- (pracownik tylko na tablecie firmowym – pilnuje tego zasada „tablet” z V5.4)
  if new.status = 'paid' and old.status is distinct from 'paid' and not public.is_active_member() then
    raise exception 'Brak dostępu do zamykania rachunków.';
  end if;

  if old.status = 'paid' and new.status is distinct from 'paid' then
    if new.status = 'cancelled' then
      if not public.is_active_member() then
        raise exception 'Brak dostępu do anulowania rachunków.';
      end if;
    elsif exists (select 1 from public.pos_payments where order_id = old.id) then
      raise exception 'Opłaconego rachunku nie można ponownie otworzyć.';
    end if;
  end if;

  if new.status = 'cancelled' and old.status is distinct from 'cancelled' then
    if not public.is_active_member() then
      raise exception 'Brak dostępu do anulowania rachunków.';
    end if;
    new.cancelled_at := coalesce(new.cancelled_at, now());
    new.cancelled_by := coalesce(new.cancelled_by, auth.uid());
  end if;

  return new;
end $$;



create or replace function public.pos_orders_discount_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then return new; end if;   -- operacje z panelu Supabase
  if new.discount_pct is distinct from old.discount_pct then
    if not public.is_active_member() then
      raise exception 'Brak dostępu do rabatów.';
    end if;
    if old.status in ('paid', 'cancelled') then
      raise exception 'Rachunek jest zamknięty – nie można zmienić rabatu.';
    end if;
  end if;
  return new;
end $$;

drop trigger if exists pos_orders_discount_guard on public.pos_orders;
create trigger pos_orders_discount_guard before update of discount_pct on public.pos_orders
  for each row execute function public.pos_orders_discount_guard();

notify pgrst, 'reload schema';
