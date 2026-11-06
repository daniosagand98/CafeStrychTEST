-- =====================================================================
-- Cafe Strych – AUDYT BEZPIECZEŃSTWA (tylko odczyt – niczego nie zmienia)
-- Uruchom w Supabase: SQL Editor → New query → wklej całość → Run.
-- Wynik: tabela „co / gdzie / szczegóły / uwaga”. Skopiuj ją (Copy → CSV)
-- albo zrób zrzut i wyślij – na tej podstawie sprawdzam zasady w bazie.
-- =====================================================================
with
pol as (
  select n.nspname as sch, c.relname as tbl, p.polname,
         case p.polcmd when 'r' then 'SELECT' when 'a' then 'INSERT' when 'w' then 'UPDATE' when 'd' then 'DELETE' else 'ALL' end as cmd,
         case when p.polpermissive then '' else 'RESTRICTIVE ' end as kind,
         (select string_agg(case when r = 0 then 'public' else pg_get_userbyid(r) end, ',') from unnest(p.polroles) r) as roles,
         coalesce(pg_get_expr(p.polqual, p.polrelid), '') as using_expr,
         coalesce(pg_get_expr(p.polwithcheck, p.polrelid), '') as check_expr
    from pg_policy p join pg_class c on c.oid = p.polrelid join pg_namespace n on n.oid = c.relnamespace
   where n.nspname in ('public', 'storage')
)
select * from (
  -- 1) tabele bez ochrony RLS
  select 1 as nr, 'TABELA BEZ RLS' as co, c.relname as gdzie, '' as szczegoly, '!!! każdy z kluczem strony może czytać/pisać' as uwaga
    from pg_class c join pg_namespace n on n.oid = c.relnamespace
   where n.nspname = 'public' and c.relkind = 'r' and not c.relrowsecurity
  union all
  -- 2) wszystkie zasady dostępu
  select 2, 'ZASADA', sch || '.' || tbl, kind || cmd || ' [' || roles || '] ' || polname || ' | USING: ' || using_expr || ' | CHECK: ' || check_expr,
         case when (using_expr in ('true', '') and check_expr in ('true', '')) and cmd <> 'SELECT' and roles like '%authenticated%' then '! zapis dla każdego zalogowanego'
              when using_expr = 'true' and roles ~ '(anon|public)' then '! odczyt dla wszystkich (także bez logowania)'
              when using_expr = 'true' and roles like '%authenticated%' then 'odczyt dla każdego zalogowanego (także niezatwierdzonego)'
              else '' end
    from pol
  union all
  -- 3) foldery na pliki (buckety)
  select 3, 'BUCKET', b.id, case when b.public then 'PUBLICZNY' else 'prywatny' end, case when b.public and b.id <> 'site-news' then '! publiczny – sprawdzić' else '' end
    from storage.buckets b
  union all
  -- 4) uprawnienia dla gości bez logowania (anon) na tabelach
  select 4, 'ANON MA PRAWO', table_name, string_agg(privilege_type, ',' order by privilege_type), ''
    from information_schema.role_table_grants
   where grantee = 'anon' and table_schema = 'public'
   group by table_name
  union all
  -- 5) funkcje z pełnymi prawami bez ustalonej ścieżki (search_path)
  select 5, 'FUNKCJA BEZ search_path', p.proname, pg_get_function_identity_arguments(p.oid), '! do poprawy'
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'public' and p.prosecdef and not exists (
           select 1 from unnest(coalesce(p.proconfig, '{}')) cfg where cfg like 'search_path=%')
  union all
  -- 6) funkcje, które może wywołać gość bez logowania
  select 6, 'FUNKCJA DLA ANON', p.proname, pg_get_function_identity_arguments(p.oid), ''
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'public' and has_function_privilege('anon', p.oid, 'execute')
     and p.prorettype <> 'trigger'::regtype
  union all
  -- 7) konta: ile i jakie role
  select 7, 'KONTA', coalesce(role, '—'), 'aktywne: ' || count(*) filter (where active) || ', nieaktywne: ' || count(*) filter (where not coalesce(active, false)), ''
    from public.profiles group by role
  union all
  -- 8) tabela zamian zmian – kolumny
  select 8, 'shift_swaps KOLUMNA', column_name, data_type || case when is_nullable = 'NO' then ' NOT NULL' else '' end, ''
    from information_schema.columns where table_schema = 'public' and table_name = 'shift_swaps'
  union all
  -- 9) triggery ochronne
  select 9, 'TRIGGER', event_object_table, trigger_name, ''
    from information_schema.triggers where trigger_schema = 'public'
     and trigger_name in ('profiles_guard', 'profiles_insert_guard', 'bookings_www_limit', 'pos_orders_guard', 'pos_items_guard', 'bookings_activity_log', 'pos_order_items_audit', 'pos_orders_audit')
) x
order by nr, uwaga desc, gdzie, szczegoly;
