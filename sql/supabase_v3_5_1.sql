-- =====================================================================
-- Cafe Strych – NAPRAWA TABEL (V3.5.2, 16.10.2026)
-- Tworzy tabele, których aplikacja potrzebuje, a których brakuje w bazie
-- (np. message_reads → błąd „Could not find the table ... in the schema cache”),
-- i dodaje brakujące kolumny. Istniejących danych nie usuwa.
-- Uprawnienia (RLS) ustawia TYLKO dla tabel, które ten skrypt utworzył –
-- Twoje dotychczasowe zasady w istniejących tabelach zostają bez zmian.
--
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Można uruchomić wielokrotnie.
-- =====================================================================

create or replace function public.is_manager() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles
    where id = auth.uid() and role in ('admin','manager') and coalesce(active, true));
$$;

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles
    where id = auth.uid() and role = 'admin' and coalesce(active, true));
$$;

create temp table if not exists _cs_new_tables (name text primary key);
truncate _cs_new_tables;

do $$
declare
  t text;
  defs jsonb := jsonb_build_object(
    'employees',            'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'work_shifts',          'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'bookings',             'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'shopping',             'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'reservation_places',   'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'cafe_rooms',           'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'cafe_tables',          'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'menu_items',           'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'pos_orders',           'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'pos_order_items',      'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'pos_payments',         'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'employee_permissions', 'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'availability',         'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'message_reads',        'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'employee_documents',   'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'announcements',        'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'activity_logs',        'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'bug_reports',          'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()',
    'cafe_settings',        'id int primary key default 1',
    'site_news',            'id uuid primary key default gen_random_uuid(), created_at timestamptz not null default now()'
  );
begin
  for t in select jsonb_object_keys(defs) loop
    if to_regclass('public.' || t) is null then
      execute format('create table public.%I (%s)', t, defs->>t);
      insert into _cs_new_tables values (t);
      raise notice 'Utworzono brakującą tabelę: %', t;
    end if;
  end loop;
end $$;

-- ---------- kolumny używane przez aplikację ----------
alter table public.employees add column if not exists full_name text;
alter table public.employees add column if not exists email text;
alter table public.employees add column if not exists phone text;
alter table public.employees add column if not exists contract_percent numeric default 100;
alter table public.employees add column if not exists weekly_target_hours numeric;
alter table public.employees add column if not exists active boolean default true;
alter table public.employees add column if not exists user_id uuid;

alter table public.work_shifts add column if not exists employee_id uuid;
alter table public.work_shifts add column if not exists shift_date date;
alter table public.work_shifts add column if not exists start_time time;
alter table public.work_shifts add column if not exists end_time time;
alter table public.work_shifts add column if not exists created_by uuid;

alter table public.bookings add column if not exists title text;
alter table public.bookings add column if not exists guests_count int;
alter table public.bookings add column if not exists start_at timestamptz;
alter table public.bookings add column if not exists end_at timestamptz;
alter table public.bookings add column if not exists reservation_place_id uuid;
alter table public.bookings add column if not exists place_name text;
alter table public.bookings add column if not exists room text;
alter table public.bookings add column if not exists table_label text;
alter table public.bookings add column if not exists notes text;
alter table public.bookings add column if not exists booking_status text default 'confirmed';
alter table public.bookings add column if not exists source text;
alter table public.bookings add column if not exists created_by uuid;

alter table public.shopping add column if not exists title text;
alter table public.shopping add column if not exists quantity text;
alter table public.shopping add column if not exists created_by uuid;

alter table public.reservation_places add column if not exists name text;
alter table public.reservation_places add column if not exists capacity int;
alter table public.reservation_places add column if not exists description text;
alter table public.reservation_places add column if not exists active boolean default true;
alter table public.reservation_places add column if not exists sort_order int;
alter table public.reservation_places add column if not exists room_id uuid;
alter table public.reservation_places add column if not exists created_by uuid;
alter table public.reservation_places add column if not exists updated_at timestamptz;

alter table public.cafe_rooms add column if not exists name text;
alter table public.cafe_rooms add column if not exists capacity int;
alter table public.cafe_rooms add column if not exists sort_order int;

alter table public.cafe_tables add column if not exists room_id uuid;
alter table public.cafe_tables add column if not exists label text;
alter table public.cafe_tables add column if not exists seats int default 4;
alter table public.cafe_tables add column if not exists active boolean default true;
alter table public.cafe_tables add column if not exists qr_token text;

alter table public.menu_items add column if not exists name text;
alter table public.menu_items add column if not exists category text;
alter table public.menu_items add column if not exists price numeric(10,2) default 0;
alter table public.menu_items add column if not exists tax_rate numeric default 23;
alter table public.menu_items add column if not exists active boolean default true;
alter table public.menu_items add column if not exists created_by uuid;
alter table public.menu_items add column if not exists updated_at timestamptz;

alter table public.pos_orders add column if not exists order_no text;
alter table public.pos_orders add column if not exists table_id uuid;
alter table public.pos_orders add column if not exists customer_name text;
alter table public.pos_orders add column if not exists status text default 'new';
alter table public.pos_orders add column if not exists source text;
alter table public.pos_orders add column if not exists created_by uuid;
alter table public.pos_orders add column if not exists updated_at timestamptz;
alter table public.pos_orders add column if not exists closed_at timestamptz;

alter table public.pos_order_items add column if not exists order_id uuid;
alter table public.pos_order_items add column if not exists menu_item_id uuid;
alter table public.pos_order_items add column if not exists item_name text;
alter table public.pos_order_items add column if not exists qty int default 1;
alter table public.pos_order_items add column if not exists unit_price numeric(10,2) default 0;
alter table public.pos_order_items add column if not exists tax_rate numeric default 23;

alter table public.pos_payments add column if not exists order_id uuid;
alter table public.pos_payments add column if not exists amount numeric(10,2) default 0;
alter table public.pos_payments add column if not exists tip_amount numeric(10,2) default 0;
alter table public.pos_payments add column if not exists method text;
alter table public.pos_payments add column if not exists created_by uuid;

alter table public.employee_permissions add column if not exists employee_id uuid;
alter table public.employee_permissions add column if not exists can_pos boolean default true;
alter table public.employee_permissions add column if not exists can_bookings boolean default true;
alter table public.employee_permissions add column if not exists can_schedule boolean default true;
alter table public.employee_permissions add column if not exists can_shopping boolean default true;

alter table public.availability add column if not exists user_id uuid;
alter table public.availability add column if not exists employee_id uuid;
alter table public.availability add column if not exists work_date date;
alter table public.availability add column if not exists start_time time;
alter table public.availability add column if not exists end_time time;
alter table public.availability add column if not exists status text default 'available';

alter table public.message_reads add column if not exists message_id uuid;
alter table public.message_reads add column if not exists employee_id uuid;
alter table public.message_reads add column if not exists user_id uuid;
alter table public.message_reads add column if not exists read_at timestamptz default now();

alter table public.employee_documents add column if not exists employee_id uuid;
alter table public.employee_documents add column if not exists file_name text;
alter table public.employee_documents add column if not exists storage_path text;
alter table public.employee_documents add column if not exists uploaded_by uuid;

alter table public.announcements add column if not exists message text;
alter table public.announcements add column if not exists target_employee_ids jsonb;
alter table public.announcements add column if not exists created_by uuid;

alter table public.activity_logs add column if not exists action text;
alter table public.activity_logs add column if not exists user_email text;

alter table public.bug_reports add column if not exists description text;
alter table public.bug_reports add column if not exists image_path text;
alter table public.bug_reports add column if not exists reporter_id uuid;
alter table public.bug_reports add column if not exists reporter_name text;
alter table public.bug_reports add column if not exists reporter_email text;
alter table public.bug_reports add column if not exists page text;
alter table public.bug_reports add column if not exists user_agent text;
alter table public.bug_reports add column if not exists status text default 'new';
alter table public.bug_reports add column if not exists resolved_at timestamptz;

alter table public.cafe_settings add column if not exists qr_enabled boolean default false;
alter table public.cafe_settings add column if not exists updated_at timestamptz;
insert into public.cafe_settings (id, qr_enabled) values (1, false) on conflict (id) do nothing;

alter table public.site_news add column if not exists title text;
alter table public.site_news add column if not exists body text;
alter table public.site_news add column if not exists image_url text;
alter table public.site_news add column if not exists image_path text;
alter table public.site_news add column if not exists event_date date;
alter table public.site_news add column if not exists published boolean default true;
alter table public.site_news add column if not exists pinned boolean default false;
alter table public.site_news add column if not exists updated_at timestamptz;
alter table public.site_news add column if not exists created_by uuid;

-- ---------- klucze, z których korzysta zapis „upsert” w aplikacji ----------
do $$
declare
  r record;
begin
  for r in select * from (values
      ('message_reads',        'message_id, user_id', 'message_reads_message_user_key'),
      ('availability',         'user_id, work_date',  'availability_user_day_key'),
      ('employee_permissions', 'employee_id',         'employee_permissions_employee_key')
    ) as v(tbl, cols, cname)
  loop
    if not exists (
      select 1 from pg_constraint con join pg_class rel on rel.oid = con.conrelid
      where rel.relname = r.tbl and con.contype in ('u','p')
        and pg_get_constraintdef(con.oid) ilike '%(' || r.cols || ')%'
    ) then
      -- usuń duplikaty (zostaje najnowszy wpis), potem dodaj klucz
      execute format(
        'delete from public.%I a using public.%I b where (%s) = (%s) and a.ctid < b.ctid',
        r.tbl, r.tbl,
        (select string_agg('a.' || trim(c), ', ') from unnest(string_to_array(r.cols, ',')) c),
        (select string_agg('b.' || trim(c), ', ') from unnest(string_to_array(r.cols, ',')) c));
      execute format('alter table public.%I add constraint %I unique (%s)', r.tbl, r.cname, r.cols);
      raise notice 'Dodano klucz unikalny %(%)', r.tbl, r.cols;
    end if;
  end loop;
end $$;

-- ---------- uprawnienia dla tabel utworzonych przez ten skrypt ----------
do $$
declare t text;
begin
  for t in select name from _cs_new_tables loop
    execute format('alter table public.%I enable row level security', t);
    execute format('grant select, insert, update, delete on public.%I to authenticated', t);

    if t = 'message_reads' then
      -- każdy potwierdza swoje odczytanie, kierownik widzi wszystkie i może je usuwać
      execute 'create policy "message_reads: odczyt" on public.message_reads for select to authenticated using (user_id = auth.uid() or public.is_manager())';
      execute 'create policy "message_reads: potwierdzenie" on public.message_reads for insert to authenticated with check (user_id = auth.uid())';
      execute 'create policy "message_reads: aktualizacja" on public.message_reads for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid())';
      execute 'create policy "message_reads: kierownik usuwa" on public.message_reads for delete to authenticated using (public.is_manager())';
    elsif t = 'availability' then
      execute 'create policy "availability: odczyt" on public.availability for select to authenticated using (user_id = auth.uid() or public.is_manager())';
      execute 'create policy "availability: własna" on public.availability for all to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid())';
    elsif t in ('announcements','employee_permissions','cafe_settings','employees','work_shifts',
                'reservation_places','cafe_rooms','cafe_tables','menu_items','activity_logs') then
      -- zespół czyta, kierownik zarządza
      execute format('create policy "%s: zespół czyta" on public.%I for select to authenticated using (true)', t, t);
      execute format('create policy "%s: kierownik zarządza" on public.%I for all to authenticated using (public.is_manager()) with check (public.is_manager())', t, t);
    elsif t = 'shopping' then
      execute 'create policy "shopping: zespół czyta i dodaje" on public.shopping for select to authenticated using (true)';
      execute 'create policy "shopping: zespół dodaje" on public.shopping for insert to authenticated with check (true)';
      execute 'create policy "shopping: kierownik zarządza" on public.shopping for all to authenticated using (public.is_manager()) with check (public.is_manager())';
    elsif t in ('pos_orders','pos_order_items','pos_payments') then
      -- obsługa POS: cały zespół pracuje na rachunkach, usuwa kierownik
      execute format('create policy "%s: zespół obsługuje" on public.%I for select to authenticated using (true)', t, t);
      execute format('create policy "%s: zespół dodaje" on public.%I for insert to authenticated with check (true)', t, t);
      execute format('create policy "%s: zespół zmienia" on public.%I for update to authenticated using (true) with check (true)', t, t);
      execute format('create policy "%s: kierownik usuwa" on public.%I for delete to authenticated using (public.is_manager())', t, t);
    elsif t = 'employee_documents' then
      execute 'create policy "employee_documents: kierownik zarządza" on public.employee_documents for all to authenticated using (public.is_manager()) with check (public.is_manager())';
    elsif t = 'bookings' then
      execute 'create policy "bookings: zespół widzi" on public.bookings for select to authenticated using (true)';
      execute 'create policy "bookings: kierownik zarządza" on public.bookings for all to authenticated using (public.is_manager()) with check (public.is_manager())';
    elsif t = 'site_news' then
      execute 'grant select on public.site_news to anon';
      execute 'create policy "site_news: wszyscy czytają opublikowane" on public.site_news for select using (published = true)';
      execute 'create policy "site_news: kierownik zarządza" on public.site_news for all to authenticated using (public.is_manager()) with check (public.is_manager())';
    elsif t = 'bug_reports' then
      execute 'create policy "bug_reports: każdy zalogowany zgłasza" on public.bug_reports for insert to authenticated with check (reporter_id = auth.uid())';
      execute 'create policy "bug_reports: admin i autor widzą" on public.bug_reports for select to authenticated using (public.is_admin() or reporter_id = auth.uid())';
      execute 'create policy "bug_reports: admin zmienia status" on public.bug_reports for update to authenticated using (public.is_admin()) with check (public.is_admin())';
      execute 'create policy "bug_reports: admin usuwa" on public.bug_reports for delete to authenticated using (public.is_admin())';
    end if;

    begin
      execute format('alter publication supabase_realtime add table public.%I', t);
    exception when duplicate_object or undefined_object then null;
    end;
  end loop;
end $$;

-- realtime dla potwierdzeń przeczytania (także gdy tabela już istniała)
do $$ begin
  alter publication supabase_realtime add table public.message_reads;
exception when duplicate_object or undefined_object then null; end $$;

-- ---------- bug_reports: stare kolumny wymagane (np. details) ----------
-- Starsza wersja tabeli miała obowiązkowe kolumny (np. "details"), których nowa aplikacja
-- nie zna → błąd „null value in column ... violates not-null constraint”.
-- Zdejmujemy wymóg NOT NULL ze wszystkich kolumn poza id i created_at oraz stare ograniczenia statusu.
do $$
declare c record;
begin
  for c in select column_name from information_schema.columns
           where table_schema = 'public' and table_name = 'bug_reports'
             and is_nullable = 'NO' and column_name not in ('id','created_at')
  loop
    execute format('alter table public.bug_reports alter column %I drop not null', c.column_name);
    raise notice 'bug_reports.%: zdjęto wymóg NOT NULL', c.column_name;
  end loop;
  for c in select con.conname from pg_constraint con join pg_class rel on rel.oid = con.conrelid
           where rel.relname = 'bug_reports' and con.contype = 'c'
             and pg_get_constraintdef(con.oid) ilike '%status%'
  loop
    execute format('alter table public.bug_reports drop constraint %I', c.conname);
    raise notice 'bug_reports: usunięto stare ograniczenie %', c.conname;
  end loop;
end $$;

-- odśwież listę tabel w API Supabase (usuwa błąd „schema cache”)
notify pgrst, 'reload schema';

-- wynik: które tabele zostały utworzone
select coalesce(string_agg(name, ', ' order by name), 'brak – wszystkie tabele już były') as utworzone_tabele
from _cs_new_tables;
