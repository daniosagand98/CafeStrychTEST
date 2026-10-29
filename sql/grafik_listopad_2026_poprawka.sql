-- =====================================================================
-- Cafe Strych – POPRAWKA grafiku na listopad 2026
-- Poprzedni skrypt mógł przypisać zmiany do usuniętych (nieaktywnych)
-- wpisów z listy Pracownicy – stąd „Pracownik” w grafiku.
-- Ten skrypt:
--  1) usuwa tylko zmiany z listopadowej kartki (te same dni i godziny),
--  2) dodaje je ponownie, przypisane do AKTYWNYCH pracowników po imieniu,
--  3) na końcu pokazuje listę pracowników i liczbę ich zmian w listopadzie.
-- Jeśli imię pasuje do 0 albo do 2+ aktywnych osób – nic nie zostanie zmienione,
-- a komunikat powie, kogo poprawić.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- =====================================================================
do $$
declare r record; v_emp uuid; v_admin uuid; n int; n_add int := 0; n_del int := 0; problem text := '';
begin
  select id into v_admin from public.profiles where role = 'admin' limit 1;

  create temp table _g (imie text, dzien date, od time, do_ time) on commit drop;
  insert into _g values
  ('Martyna', date '2026-11-01', time '12:00', time '00:00'),
  ('Krzysztof', date '2026-11-02', time '12:00', time '00:00'),
  ('Martyna', date '2026-11-03', time '12:00', time '19:00'),
  ('Weronika', date '2026-11-03', time '18:30', time '00:00'),
  ('Krzysztof', date '2026-11-04', time '12:00', time '00:00'),
  ('Martyna', date '2026-11-05', time '12:00', time '20:00'),
  ('Weronika', date '2026-11-05', time '19:00', time '00:00'),
  ('Krzysztof', date '2026-11-06', time '12:00', time '00:00'),
  ('Natalia', date '2026-11-06', time '16:30', time '02:00'),
  ('Weronika', date '2026-11-07', time '12:00', time '00:00'),
  ('Martyna', date '2026-11-07', time '16:00', time '02:00'),
  ('Natalia', date '2026-11-08', time '12:00', time '21:00'),
  ('Krzysztof', date '2026-11-08', time '13:00', time '00:00'),
  ('Martyna', date '2026-11-09', time '12:00', time '00:00'),
  ('Weronika', date '2026-11-10', time '12:00', time '00:00'),
  ('Krzysztof', date '2026-11-11', time '12:00', time '00:00'),
  ('Martyna', date '2026-11-12', time '12:00', time '00:00'),
  ('Krzysztof', date '2026-11-13', time '12:00', time '00:00'),
  ('Natalia', date '2026-11-13', time '17:00', time '02:00'),
  ('Martyna', date '2026-11-14', time '12:00', time '00:00'),
  ('Weronika', date '2026-11-14', time '17:00', time '02:00'),
  ('Natalia', date '2026-11-15', time '12:00', time '21:00'),
  ('Krzysztof', date '2026-11-15', time '13:00', time '00:00'),
  ('Weronika', date '2026-11-16', time '12:00', time '00:00'),
  ('Krzysztof', date '2026-11-17', time '12:00', time '00:00'),
  ('Weronika', date '2026-11-18', time '12:00', time '00:00'),
  ('Krzysztof', date '2026-11-19', time '12:00', time '00:00'),
  ('Weronika', date '2026-11-20', time '12:00', time '00:00'),
  ('Natalia', date '2026-11-20', time '16:30', time '02:00'),
  ('Krzysztof', date '2026-11-21', time '12:00', time '02:00'),
  ('Natalia', date '2026-11-22', time '12:00', time '21:00'),
  ('Weronika', date '2026-11-22', time '13:00', time '00:00'),
  ('Martyna', date '2026-11-23', time '12:00', time '00:00'),
  ('Krzysztof', date '2026-11-24', time '12:00', time '00:00'),
  ('Weronika', date '2026-11-25', time '12:00', time '00:00'),
  ('Martyna', date '2026-11-26', time '12:00', time '00:00'),
  ('Krzysztof', date '2026-11-27', time '12:00', time '00:00'),
  ('Natalia', date '2026-11-27', time '17:00', time '02:00'),
  ('Martyna', date '2026-11-28', time '12:00', time '00:00'),
  ('Weronika', date '2026-11-28', time '16:30', time '02:00'),
  ('Natalia', date '2026-11-29', time '12:00', time '21:00'),
  ('Krzysztof', date '2026-11-29', time '13:00', time '00:00'),
  ('Martyna', date '2026-11-30', time '12:00', time '00:00');

  -- sprawdzenie imion: dokładnie jedna aktywna osoba dla każdego imienia
  for r in select distinct imie from _g loop
    select count(*) into n from public.employees
     where active is not false and split_part(trim(full_name), ' ', 1) ilike r.imie;
    if n <> 1 then
      problem := problem || format('%s: %s aktywnych; ', r.imie, n);
    end if;
  end loop;
  if problem <> '' then
    raise exception 'Popraw listę Pracownicy (każde imię ma pasować do jednej aktywnej osoby): %', problem;
  end if;

  -- 1) usuń zmiany z kartki (dowolny pracownik, te same dzień + godziny)
  delete from public.work_shifts w using _g
   where w.shift_date = _g.dzien and w.start_time = _g.od and w.end_time = _g.do_;
  get diagnostics n_del = row_count;

  -- 2) dodaj ponownie z właściwymi osobami
  for r in select * from _g loop
    select id into v_emp from public.employees
     where active is not false and split_part(trim(full_name), ' ', 1) ilike r.imie;
    insert into public.work_shifts (employee_id, shift_date, start_time, end_time, created_by)
    values (v_emp, r.dzien, r.od, r.do_, coalesce(v_admin, (select id from public.profiles limit 1)));
    n_add := n_add + 1;
  end loop;
  raise notice 'Usunięto: %, dodano: %', n_del, n_add;
end $$;

-- 3) kontrola: pracownicy i ich zmiany w listopadzie
select e.full_name, case when e.active is false then 'USUNIĘTY' else 'aktywny' end as status,
       count(w.id) as zmian_w_listopadzie
  from public.employees e
  left join public.work_shifts w on w.employee_id = e.id
       and w.shift_date between date '2026-11-01' and date '2026-11-30'
 group by e.id, e.full_name, e.active
 order by e.active desc nulls first, e.full_name;
