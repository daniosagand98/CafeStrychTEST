-- =====================================================================
-- Cafe Strych – V5.3 (03.11.2026)
--  1) Czat: ogólny (z oznaczaniem @osoba) i prywatne wiadomości
--  2) Zamiany zmian między pracownikami (prośba → zgoda kolegi →
--     zatwierdzenie kierownika; zatwierdzanie można wyłączyć)
--  3) Powiadomienia push o czacie i zamianach
--  4) Strona: prośba o stolik maksymalnie dla 10 osób
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- PAMIĘTAJ też zaktualizować funkcję notify-booking (Edge Functions).
-- =====================================================================

-- ---------- ustawienia ----------
alter table public.cafe_settings add column if not exists module_chat boolean not null default true;
alter table public.cafe_settings add column if not exists swap_needs_approval boolean not null default true;
alter table public.push_subscriptions add column if not exists notify_chat  boolean not null default true;
alter table public.push_subscriptions add column if not exists notify_swaps boolean not null default true;

-- ---------- wspólne: wywołanie funkcji powiadomień ----------
create or replace function public.cafe_push(p_body jsonb) returns void
language plpgsql security definer set search_path = public as $$
begin
  perform net.http_post(
    url     := 'https://dhqsjwanjrcblrhevfcq.supabase.co/functions/v1/notify-booking',
    headers := jsonb_build_object('Content-Type', 'application/json'),
    body    := p_body);
exception when others then
  raise warning 'cafe_push: %', sqlerrm;   -- powiadomienie nigdy nie blokuje zapisu
end $$;
revoke all on function public.cafe_push(jsonb) from public, anon, authenticated;

-- =====================================================================
-- 1) CZAT
-- kanał: 'general' (wszyscy) albo 'dm:<uuid>:<uuid>' (dwie osoby, uuid rosnąco)
-- =====================================================================
create table if not exists public.chat_messages (
  id           uuid primary key default gen_random_uuid(),
  created_at   timestamptz not null default now(),
  channel      text not null,
  sender_id    uuid not null default auth.uid(),
  sender_name  text,
  body         text not null check (char_length(body) between 1 and 2000),
  mentions     uuid[] not null default '{}',
  push_sent_at timestamptz
);
create index if not exists chat_messages_channel_idx on public.chat_messages (channel, created_at desc);
create index if not exists chat_messages_created_idx on public.chat_messages (created_at desc);

create or replace function public.chat_can_see(p_channel text) returns boolean
language sql stable security definer set search_path = public as $$
  select public.is_active_member() and (
    p_channel = 'general'
    or (p_channel ~ '^dm:[0-9a-f-]{36}:[0-9a-f-]{36}$' and position(auth.uid()::text in p_channel) > 0))
$$;
grant execute on function public.chat_can_see(text) to authenticated;

alter table public.chat_messages enable row level security;
drop policy if exists "chat: czyta uczestnik" on public.chat_messages;
create policy "chat: czyta uczestnik" on public.chat_messages
  for select to authenticated using (public.chat_can_see(channel));
drop policy if exists "chat: pisze uczestnik" on public.chat_messages;
create policy "chat: pisze uczestnik" on public.chat_messages
  for insert to authenticated with check (sender_id = auth.uid() and public.chat_can_see(channel));
drop policy if exists "chat: usuwa autor lub kierownik" on public.chat_messages;
create policy "chat: usuwa autor lub kierownik" on public.chat_messages
  for delete to authenticated using (sender_id = auth.uid() or (public.is_manager() and channel = 'general'));
grant select, insert, delete on public.chat_messages to authenticated;

-- nazwa nadawcy zawsze z profilu (nie da się podszyć)
create or replace function public.chat_before_insert() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  new.sender_id := auth.uid();
  new.created_at := now();
  new.push_sent_at := null;
  select coalesce(nullif(trim(full_name), ''), email, 'Użytkownik') into new.sender_name from public.profiles where id = auth.uid();
  new.body := trim(new.body);
  return new;
end $$;
drop trigger if exists chat_messages_before on public.chat_messages;
create trigger chat_messages_before before insert on public.chat_messages
  for each row execute function public.chat_before_insert();

create or replace function public.chat_after_insert() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  perform public.cafe_push(jsonb_build_object('type', 'chat', 'id', new.id));
  return null;
end $$;
drop trigger if exists chat_messages_push on public.chat_messages;
create trigger chat_messages_push after insert on public.chat_messages
  for each row execute function public.chat_after_insert();

-- przeczytane (do licznika nieprzeczytanych)
create table if not exists public.chat_reads (
  user_id      uuid not null default auth.uid(),
  channel      text not null,
  last_read_at timestamptz not null default now(),
  primary key (user_id, channel)
);
alter table public.chat_reads enable row level security;
drop policy if exists "chat_reads: własne" on public.chat_reads;
create policy "chat_reads: własne" on public.chat_reads
  for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on public.chat_reads to authenticated;

-- =====================================================================
-- 2) ZAMIANY ZMIAN
-- =====================================================================
-- pracownik (z listy „Pracownicy”) zalogowanego konta
create or replace function public.my_employee_ids() returns setof uuid
language sql stable security definer set search_path = public as $$
  select e.id from public.employees e, public.profiles p
   where p.id = auth.uid() and e.active is not false
     and ( to_jsonb(e)->>'user_id' = auth.uid()::text
        or to_jsonb(e)->>'profile_id' = auth.uid()::text
        or (e.email is not null and lower(trim(e.email)) = lower(trim(p.email)))
        or (e.full_name is not null and lower(trim(e.full_name)) = lower(trim(p.full_name))))
$$;
grant execute on function public.my_employee_ids() to authenticated;

create table if not exists public.shift_swaps (
  id             uuid primary key default gen_random_uuid(),
  created_at     timestamptz not null default now(),
  shift_id       uuid not null references public.work_shifts(id) on delete cascade,
  from_employee  uuid not null,
  to_employee    uuid,                 -- null = „ktokolwiek chętny”
  other_shift_id uuid references public.work_shifts(id) on delete cascade,  -- zmiana kolegi w zamian (opcjonalnie)
  note           text,
  status         text not null default 'open' check (status in ('open', 'accepted', 'approved', 'rejected', 'cancelled')),
  requested_by   uuid default auth.uid(),
  accepted_at    timestamptz,
  decided_by     uuid,
  decided_at     timestamptz,
  pushed_status  text
);
create index if not exists shift_swaps_status_idx on public.shift_swaps (status, created_at desc);

alter table public.shift_swaps enable row level security;
drop policy if exists "shift_swaps: zespół czyta" on public.shift_swaps;
create policy "shift_swaps: zespół czyta" on public.shift_swaps
  for select to authenticated using (public.is_active_member());
grant select on public.shift_swaps to authenticated;
-- zmiany wyłącznie przez funkcje poniżej

create or replace function public.swap_apply(s public.shift_swaps) returns void
language plpgsql security definer set search_path = public as $$
begin
  update public.work_shifts set employee_id = s.to_employee where id = s.shift_id;
  if s.other_shift_id is not null then
    update public.work_shifts set employee_id = s.from_employee where id = s.other_shift_id;
  end if;
end $$;
revoke all on function public.swap_apply(public.shift_swaps) from public, anon, authenticated;

create or replace function public.swap_request(p_shift uuid, p_to uuid, p_other uuid, p_note text)
returns uuid language plpgsql security definer set search_path = public as $$
declare sh record; ot record; v_id uuid;
begin
  if not public.is_active_member() then raise exception 'Brak dostępu.'; end if;
  select * into sh from public.work_shifts where id = p_shift;
  if not found then raise exception 'Nie ma takiej zmiany.'; end if;
  if sh.shift_date < (now() at time zone 'Europe/Warsaw')::date then raise exception 'Ta zmiana już minęła.'; end if;
  if not (public.is_manager() or sh.employee_id in (select public.my_employee_ids())) then
    raise exception 'Możesz oddać lub zamienić tylko swoją zmianę.';
  end if;
  if p_to is not null and p_to = sh.employee_id then raise exception 'Wybierz inną osobę.'; end if;
  if p_other is not null then
    if p_to is null then raise exception 'Do wymiany zmian wybierz konkretną osobę.'; end if;
    select * into ot from public.work_shifts where id = p_other;
    if not found or ot.employee_id is distinct from p_to then raise exception 'Wybrana zmiana nie należy do tej osoby.'; end if;
  end if;
  if exists (select 1 from public.shift_swaps where shift_id = p_shift and status in ('open', 'accepted')) then
    raise exception 'Dla tej zmiany jest już otwarta prośba o zamianę.';
  end if;
  insert into public.shift_swaps (shift_id, from_employee, to_employee, other_shift_id, note)
  values (p_shift, sh.employee_id, p_to, p_other, nullif(trim(coalesce(p_note, '')), ''))
  returning id into v_id;
  return v_id;
end $$;

create or replace function public.swap_respond(p_swap uuid, p_accept boolean)
returns text language plpgsql security definer set search_path = public as $$
declare s public.shift_swaps; me uuid; need boolean;
begin
  if not public.is_active_member() then raise exception 'Brak dostępu.'; end if;
  select * into s from public.shift_swaps where id = p_swap for update;
  if not found or s.status <> 'open' then raise exception 'Ta prośba nie czeka już na odpowiedź.'; end if;
  select t.id into me from public.my_employee_ids() as t(id)
   where (s.to_employee is null and t.id <> s.from_employee) or t.id = s.to_employee limit 1;
  if me is null then raise exception 'Ta prośba nie jest skierowana do Ciebie.'; end if;
  if not p_accept then
    if s.to_employee is null then return 'skip'; end if;   -- „ktokolwiek”: odmowa jednej osoby nic nie zmienia
    update public.shift_swaps set status = 'rejected', decided_at = now(), decided_by = auth.uid() where id = p_swap;
    return 'rejected';
  end if;
  if exists (select 1 from public.work_shifts w, public.work_shifts x
              where x.id = s.shift_id and w.employee_id = me and w.shift_date = x.shift_date and w.id is distinct from s.other_shift_id) then
    raise exception 'Masz już zmianę tego dnia.';
  end if;
  update public.shift_swaps set status = 'accepted', to_employee = me, accepted_at = now() where id = p_swap returning * into s;
  select coalesce((select swap_needs_approval from public.cafe_settings order by id limit 1), true) into need;
  if not need then
    perform public.swap_apply(s);
    update public.shift_swaps set status = 'approved', decided_at = now() where id = p_swap;
    return 'approved';
  end if;
  return 'accepted';
end $$;

create or replace function public.swap_decide(p_swap uuid, p_approve boolean)
returns text language plpgsql security definer set search_path = public as $$
declare s public.shift_swaps;
begin
  if not public.is_manager() then raise exception 'Zamianę zatwierdza kierownik lub administrator.'; end if;
  select * into s from public.shift_swaps where id = p_swap for update;
  if not found or s.status not in ('accepted', 'open') then raise exception 'Ta zamiana nie czeka na decyzję.'; end if;
  if p_approve then
    if s.to_employee is null then raise exception 'Nikt jeszcze nie przyjął tej zmiany.'; end if;
    perform public.swap_apply(s);
  end if;
  update public.shift_swaps set status = case when p_approve then 'approved' else 'rejected' end,
         decided_by = auth.uid(), decided_at = now() where id = p_swap;
  return case when p_approve then 'approved' else 'rejected' end;
end $$;

create or replace function public.swap_cancel(p_swap uuid)
returns void language plpgsql security definer set search_path = public as $$
declare s public.shift_swaps;
begin
  select * into s from public.shift_swaps where id = p_swap for update;
  if not found or s.status not in ('open', 'accepted') then raise exception 'Tej prośby nie można już anulować.'; end if;
  if not (public.is_manager() or s.requested_by = auth.uid() or s.from_employee in (select public.my_employee_ids())) then
    raise exception 'Anulować może tylko osoba, która poprosiła o zamianę.';
  end if;
  update public.shift_swaps set status = 'cancelled', decided_at = now(), decided_by = auth.uid() where id = p_swap;
end $$;

revoke all on function public.swap_request(uuid, uuid, uuid, text) from public, anon;
revoke all on function public.swap_respond(uuid, boolean) from public, anon;
revoke all on function public.swap_decide(uuid, boolean) from public, anon;
revoke all on function public.swap_cancel(uuid) from public, anon;
grant execute on function public.swap_request(uuid, uuid, uuid, text) to authenticated;
grant execute on function public.swap_respond(uuid, boolean) to authenticated;
grant execute on function public.swap_decide(uuid, boolean) to authenticated;
grant execute on function public.swap_cancel(uuid) to authenticated;

create or replace function public.swap_after_change() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'INSERT' or new.status is distinct from old.status then
    perform public.cafe_push(jsonb_build_object('type', 'swap', 'id', new.id));
  end if;
  return null;
end $$;
drop trigger if exists shift_swaps_push on public.shift_swaps;
create trigger shift_swaps_push after insert or update on public.shift_swaps
  for each row execute function public.swap_after_change();

-- =====================================================================
-- 3) odświeżanie na żywo
-- =====================================================================
do $$
declare t text;
begin
  foreach t in array array['chat_messages', 'shift_swaps'] loop
    begin
      execute format('alter publication supabase_realtime add table public.%I', t);
    exception when duplicate_object then null;
    end;
  end loop;
end $$;

-- =====================================================================
-- 4) strona: stolik maksymalnie dla 10 osób
-- =====================================================================
drop policy if exists "bookings: prośba o rezerwację ze strony" on public.bookings;
create policy "bookings: prośba o rezerwację ze strony" on public.bookings for insert to anon
  with check (public.www_bookings_open()
    and booking_status = 'pending' and source = 'www' and created_by is null
    and guests_count between 1 and 10 and start_at > now() and start_at < now() + interval '180 days'
    and char_length(title) between 2 and 80 and char_length(coalesce(notes, '')) <= 600
    and coalesce(whole_room, false) = false);

notify pgrst, 'reload schema';
