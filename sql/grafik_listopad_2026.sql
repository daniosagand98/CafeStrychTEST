-- =====================================================================
-- Cafe Strych – grafik na listopad 2026 (z kartki)
-- Jedna osoba: cała zmiana 12:00–24:00 (pt i sob 12:00–02:00).
-- Dwie osoby: „do X” = od 12:00 do X, „od Y” = od Y do zamknięcia.
-- Pracownicy są szukani po imieniu w „Pracownicy” (Martyna, Krzysztof,
-- Weronika, Natalia). Zmiany, które już są w grafiku, nie zostaną zdublowane.
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- =====================================================================
do $$
declare r record; v_emp uuid; n_add int := 0; n_skip int := 0; braki text := '';
begin
  for r in select * from (values
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
  ('Martyna', date '2026-11-30', time '12:00', time '00:00')
  ) as t(imie, dzien, od, do_)
  loop
    select id into v_emp from public.employees
     where split_part(trim(full_name), ' ', 1) ilike r.imie
     order by created_at limit 1;
    if v_emp is null then
      if position(r.imie in braki) = 0 then braki := braki || r.imie || ' '; end if;
      continue;
    end if;
    if exists (select 1 from public.work_shifts
                where employee_id = v_emp and shift_date = r.dzien and start_time = r.od) then
      n_skip := n_skip + 1; continue;
    end if;
    insert into public.work_shifts (employee_id, shift_date, start_time, end_time)
    values (v_emp, r.dzien, r.od, r.do_);
    n_add := n_add + 1;
  end loop;
  raise notice 'Dodano zmian: %, pominięto (już były): %', n_add, n_skip;
  if braki <> '' then
    raise exception 'Nie znaleziono w „Pracownicy”: % – dodaj ich w aplikacji i uruchom ponownie (nic nie zostało zapisane).', braki;
  end if;
end $$;
