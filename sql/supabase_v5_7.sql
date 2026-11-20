-- =====================================================================
-- Cafe Strych – V5.7 (20.11.2026)
--  1) Pracownik (na tablecie firmowym) może przyjąć płatność i zamknąć rachunek.
--     Anulowanie i usuwanie rachunków – nadal kierownik / administrator.
--  2) Kierownik może aktywować i blokować konta pracowników.
--     Role (pracownik / kierownik / admin) zmienia nadal tylko administrator.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1) PŁATNOŚCI
-- ---------------------------------------------------------------------
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


drop policy if exists "pos_payments: zespół przyjmuje" on public.pos_payments;
create policy "pos_payments: zespół przyjmuje" on public.pos_payments
  for insert to authenticated with check (public.is_active_member());

-- pracownik widzi płatności z ostatnich 2 dni (zamknięte rachunki, raport zmiany);
-- kierownik i administrator – wszystkie (zasada „kierownik widzi” zostaje)
drop policy if exists "pos_payments: zespół widzi ostatnie" on public.pos_payments;
create policy "pos_payments: zespół widzi ostatnie" on public.pos_payments
  for select to authenticated using (public.is_active_member() and created_at > now() - interval '2 days');

grant select, insert on public.pos_payments to authenticated;

-- ---------------------------------------------------------------------
-- 2) AKTYWACJA KONT PRZEZ KIEROWNIKA
-- ---------------------------------------------------------------------
create or replace function public.profiles_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null or current_setting('cafe.admin_op', true) = 'on' then
    return new;
  end if;
  if new.id is distinct from old.id then
    raise exception 'Nie można zmienić identyfikatora konta.';
  end if;
  if new.role is distinct from old.role and not public.is_admin() then
    raise exception 'Rolę konta zmienia tylko administrator.';
  end if;
  if new.id = auth.uid() and new.role is distinct from old.role then
    raise exception 'Nie możesz zmienić roli własnego konta.';
  end if;
  if new.active is distinct from old.active then
    if new.id = auth.uid() then raise exception 'Nie możesz zmienić aktywacji własnego konta.'; end if;
    if not (public.is_admin() or (public.is_manager() and coalesce(old.role, 'user') = 'user')) then
      raise exception 'Konto pracownika aktywuje kierownik lub administrator; konta kierowników – tylko administrator.';
    end if;
  end if;
  return new;
end $$;
revoke all on function public.profiles_guard() from public, anon, authenticated;
drop trigger if exists profiles_guard on public.profiles;
create trigger profiles_guard before update on public.profiles
  for each row execute function public.profiles_guard();

create or replace function public.set_account_active(p_user uuid, p_active boolean)
returns void language plpgsql security definer set search_path = public as $$
declare v_role text; v_name text; v_mail text;
begin
  if not public.is_manager() then raise exception 'Konto aktywuje kierownik lub administrator.'; end if;
  if p_user = auth.uid() then raise exception 'Nie możesz zmienić aktywacji własnego konta.'; end if;
  select role, full_name, email into v_role, v_name, v_mail from public.profiles where id = p_user;
  if not found then raise exception 'Nie ma takiego konta.'; end if;
  if not public.is_admin() and coalesce(v_role, 'user') <> 'user' then
    raise exception 'Kierownik może aktywować tylko konta pracowników.';
  end if;
  perform set_config('cafe.admin_op', 'on', true);
  update public.profiles set active = p_active where id = p_user;
  insert into public.activity_logs (action, user_email)
  values (format('%s konto: %s (%s)', case when p_active then 'Aktywowano' else 'Zablokowano' end,
                 coalesce(v_name, '—'), coalesce(v_mail, '—')),
          (select email from auth.users where id = auth.uid()));
end $$;
revoke all on function public.set_account_active(uuid, boolean) from public, anon;
grant execute on function public.set_account_active(uuid, boolean) to authenticated;

notify pgrst, 'reload schema';
