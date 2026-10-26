-- =====================================================================
-- Cafe Strych – V4.7 (26.10.2026)
-- 1) Aktualności: „Pokaż od” / „Pokaż do” – strona pokazuje wpis tylko w tym czasie.
-- 2) Powiadomienia push dla administratora o nowych zgłoszeniach błędów.
-- 3) Utarg dnia dla pracowników (dziś i wczoraj) – do raportu na koniec zmiany.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

-- 1) planowanie aktualności -----------------------------------------------
alter table public.site_news add column if not exists publish_at timestamptz;
alter table public.site_news add column if not exists expire_at  timestamptz;

drop policy if exists "site_news: wszyscy czytają opublikowane" on public.site_news;
create policy "site_news: wszyscy czytają opublikowane" on public.site_news
  for select using (published = true
                    and (publish_at is null or publish_at <= now())
                    and (expire_at  is null or expire_at  >  now()));

-- 2) powiadomienia o zgłoszeniach błędów ------------------------------------
alter table public.bug_reports add column if not exists push_sent_at timestamptz;
alter table public.push_subscriptions add column if not exists notify_bugs boolean not null default true;

create or replace function public.notify_new_bug() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  perform net.http_post(
    url     := 'https://dhqsjwanjrcblrhevfcq.supabase.co/functions/v1/notify-booking',
    headers := jsonb_build_object('Content-Type', 'application/json'),
    body    := jsonb_build_object('type', 'bug', 'id', new.id)
  );
  return new;
exception when others then
  raise warning 'notify_new_bug: %', sqlerrm;   -- powiadomienie nie może zablokować zgłoszenia
  return new;
end $$;
revoke execute on function public.notify_new_bug() from public, anon, authenticated;

drop trigger if exists bug_reports_notify_push on public.bug_reports;
create trigger bug_reports_notify_push after insert on public.bug_reports
  for each row execute function public.notify_new_bug();

-- 3) utarg dnia dla zespołu ------------------------------------------------
-- Kierownik/admin: dowolny dzień. Pracownik: dziś i wczoraj (raport po zmianie, także po północy).
create or replace function public.sales_day(p_day date)
returns table (id uuid, order_id uuid, amount numeric, method text, created_at timestamptz,
               order_name text, order_status text, discount_pct numeric, cancel_reason text)
language plpgsql stable security definer set search_path = public as $$
declare today date := (now() at time zone 'Europe/Warsaw')::date;
begin
  if not public.is_active_member() then raise exception 'Brak dostępu.'; end if;
  if not public.is_manager() and p_day not in (today, today - 1) then
    raise exception 'Pracownik widzi utarg z dzisiaj i wczoraj.';
  end if;
  return query
    select p.id, p.order_id, p.amount, p.method, p.created_at,
           coalesce(o.customer_name, o.order_no, 'Rachunek'), o.status, o.discount_pct, o.cancel_reason
      from public.pos_payments p left join public.pos_orders o on o.id = p.order_id
     where (p.created_at at time zone 'Europe/Warsaw')::date = p_day
     order by p.created_at desc;
end $$;
revoke all on function public.sales_day(date) from public, anon;
grant execute on function public.sales_day(date) to authenticated;

notify pgrst, 'reload schema';
