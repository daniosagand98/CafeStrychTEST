-- =====================================================================
-- Cafe Strych – V4.3 (23.10.2026) – rabat procentowy na rachunku
-- Rabat ustawia kierownik lub administrator, tylko na otwartym rachunku.
-- Kwota płatności (i utarg) jest już po rabacie.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

alter table public.pos_orders add column if not exists discount_pct numeric(5,2) not null default 0;

do $$ begin
  alter table public.pos_orders add constraint pos_orders_discount_range check (discount_pct >= 0 and discount_pct <= 100);
exception when duplicate_object then null; end $$;

create or replace function public.pos_orders_discount_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then return new; end if;   -- operacje z panelu Supabase
  if new.discount_pct is distinct from old.discount_pct then
    if not public.is_manager() then
      raise exception 'Rabat może ustawić kierownik lub administrator.';
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
