-- =====================================================================
-- Cafe Strych – V5.3.1 (03.11.2026)
-- 1) Czat: „Wyświetlono” – uczestnicy rozmowy widzą, kto i kiedy przeczytał
--    wiadomości (czat ogólny – cały zespół, prywatny – tylko Wy dwoje).
-- 2) Usuwanie kont: administrator – pracowników i kierowników,
--    kierownik – pracowników. Konta administratora nie da się usunąć.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

drop policy if exists "chat_reads: własne" on public.chat_reads;
drop policy if exists "chat_reads: czytają uczestnicy" on public.chat_reads;
create policy "chat_reads: czytają uczestnicy" on public.chat_reads
  for select to authenticated using (user_id = auth.uid() or public.chat_can_see(channel));
drop policy if exists "chat_reads: zapis własnych" on public.chat_reads;
create policy "chat_reads: zapis własnych" on public.chat_reads
  for insert to authenticated with check (user_id = auth.uid() and public.chat_can_see(channel));
drop policy if exists "chat_reads: zmiana własnych" on public.chat_reads;
create policy "chat_reads: zmiana własnych" on public.chat_reads
  for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());

do $$
begin
  alter publication supabase_realtime add table public.chat_reads;
exception when duplicate_object then null;
end $$;

-- =====================================================================
-- 2) usuwanie kont (admin: każde poza własnym; kierownik: konta pracowników)
-- Konto i logowanie znikają na zawsze. Jeśli baza nie pozwala usunąć
-- (konto jest powiązane z danymi), konto zostaje trwale zablokowane:
-- nie da się na nie zalogować i znika z listy.
-- =====================================================================
alter table public.profiles add column if not exists deleted_at timestamptz;

create or replace function public.admin_delete_account(p_user uuid)
returns text language plpgsql security definer set search_path = public, auth as $$
declare v_mail text; v_name text; v_role text;
begin
  if not public.is_manager() then raise exception 'Konto może usunąć kierownik lub administrator.'; end if;
  if p_user = auth.uid() then raise exception 'Nie możesz usunąć własnego konta.'; end if;
  select email, full_name, role into v_mail, v_name, v_role from public.profiles where id = p_user;
  if v_role = 'admin' then raise exception 'Konta administratora nie można usunąć.'; end if;
  if not public.is_admin() and coalesce(v_role, 'user') <> 'user' then
    raise exception 'Kierownik może usunąć tylko konto pracownika. Konta kierowników i administratorów usuwa administrator.';
  end if;

  delete from public.push_subscriptions where user_id = p_user;
  delete from public.chat_reads where user_id = p_user;
  begin
    delete from public.profiles where id = p_user;
    delete from auth.users where id = p_user;
    insert into public.activity_logs (action, user_email)
    values (format('Usunięto konto: %s (%s)', coalesce(v_name, '—'), coalesce(v_mail, '—')),
            (select email from auth.users where id = auth.uid()));
    return 'deleted';
  exception when foreign_key_violation then
    null;   -- konto powiązane z danymi – blokujemy zamiast usuwać
  end;
  update public.profiles set active = false, deleted_at = now() where id = p_user;
  update auth.users set banned_until = 'infinity' where id = p_user;
  delete from auth.sessions where user_id = p_user;
  insert into public.activity_logs (action, user_email)
  values (format('Usunięto (zablokowano na stałe) konto: %s (%s)', coalesce(v_name, '—'), coalesce(v_mail, '—')),
          (select email from auth.users where id = auth.uid()));
  return 'blocked';
end $$;
revoke all on function public.admin_delete_account(uuid) from public, anon;
grant execute on function public.admin_delete_account(uuid) to authenticated;

notify pgrst, 'reload schema';
