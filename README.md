# Cafe Strych – repozytorium testowe

| Ścieżka | Co to jest |
|---|---|
| `index.html` + `img/` | Strona lokalu (v1.2.1) – aktualności, menu, galeria, rezerwacje |
| `.htaccess` + `WDROZENIE-OVH.md` | Ustawienia serwera OVH (przekierowania ze starego WordPressa, HTTPS, pamięć podręczna) i instrukcja wgrania na cafestrychgdynia.pl |
| `panel/` | Aplikacja **Cafe Strych Manager V3.8** (instalowana na telefonie, z powiadomieniami) (logowanie przez Supabase) |
| `sql/` | Skrypty do Supabase – uruchamiać po kolei: `supabase_v3_5_1.sql` (naprawa tabel), `supabase_v3_4.sql`, `supabase_v3_5.sql`, `supabase_v3_6.sql` (powiadomienia), `supabase_v3_7.sql` (bezpieczeństwo), `supabase_v3_8.sql` (powiadomienia + anulowanie rachunków; zawiera v3.6) |
| `supabase/functions/notify-booking/` | Funkcja wysyłająca powiadomienia push – konfiguracja w `POWIADOMIENIA.md` |
| `podglad/` | Wersje bez logowania na danych demo – do testów, nic nie zapisują w bazie |
| `zrodla/` | Karta menu (`menu_data.py`) i skrypty budujące stronę oraz podgląd |

Na serwerze klienta: zawartość głównego katalogu (bez `sql/`, `podglad/`, `zrodla/`) → katalog główny domeny, aplikacja dostępna pod `/panel/`.

## Aplikacja V3.8 – 21.10.2026 (+ `sql/supabase_v3_8.sql`)
- Rachunków opłaconych nie da się już usunąć: zamiast „Usuń” jest „Anuluj” z obowiązkowym powodem – opłacony rachunek anuluje tylko administrator, otwarty – kierownik. Anulowany rachunek zostaje w historii (filtr Wszystkie / Opłacone / Anulowane) i nie liczy się do utargu.
- Baza pilnuje tego sama: płatności są nieusuwalne, pozycji zamkniętego rachunku nie da się zmienić, płatność zatwierdza tylko kierownik/admin, anulowanego rachunku nie da się przywrócić.
- Funkcja powiadomień `notify-booking` jest wdrożona w Supabase (21.10); do działania brakuje sekretów VAPID – patrz `POWIADOMIENIA.md`.

## Aplikacja V3.7 – 21.10.2026 (+ `sql/supabase_v3_7.sql`)
- Rezerwacje: nakładanie blokuje już tylko rezerwację **całej sali** (nowa opcja w formularzu dla kierownika). Wcześniej dwa stoliki w tej samej sali o tej samej porze kończyły się błędem.
- Nowe konta czekają na zatwierdzenie przez admina (Ustawienia → Konta i role → „✓ Zatwierdź”); do tego czasu nie widzą żadnych danych. Rejestracja łączy się z istniejącym pracownikiem o tym samym e-mailu lub imieniu i nazwisku.
- Zabezpieczenia bazy: dane (pracownicy, rezerwacje, POS, grafik, zakupy, menu) tylko dla zatwierdzonego zespołu; dyspozycyjność – własna lub kierownik; pracownik nie zatwierdzi sam swojej rezerwacji; zablokowana stara funkcja płatności i wywoływanie funkcji bez logowania.
- Odświeżanie na żywo dla wszystkich tabel aplikacji (wcześniej nie działało m.in. dla rezerwacji i POS).
- Rezerwacje ze strony do 120 osób.

## Aplikacja V3.6.1 – 19.10.2026
- Okno zmiany w grafiku: „Usuń zmianę” i „Zapisz” w jednej linii (także na telefonie).

## Aplikacja V3.6 – 19.10.2026
- Powiadomienia push o nowych rezerwacjach (także gdy aplikacja jest zamknięta) dla kierowników i administratorów: menu konta → 🔔 Powiadomienia. Stuknięcie powiadomienia otwiera ten dzień w Rezerwacjach. Konfiguracja: `POWIADOMIENIA.md`.
- Aplikację można zainstalować na telefonie (ikona Cafe Strych na ekranie głównym, pełny ekran) – manifest, service worker, ikony z logo.
- Wyłączone powiększanie (szczypanie, podwójne stuknięcie, powiększanie przy wpisywaniu).
- Pola daty i godziny nie wychodzą poza okna; „Od”/„Do” i „Data”/„Godzina” w jednej linii, niższe pola.

## Strona v1.2.1 – 19.10.2026
- Formularz rezerwacji: liczbę osób wpisuje się ręcznie (1–120, powyżej – prośba o telefon); pola daty i godziny nie wychodzą już poza okno na iPhonie.
- Nowa stopka: równe kolumny (logo i social media, nawigacja, kontakt, godziny otwarcia), na telefonie wyśrodkowana; „Projekt i wykonanie DWSystem” z linkiem do dwsystem.eu.

## Strona v1.2 – 19.10.2026
- Nowa sekcja „Na bieżąco”: najnowsze posty z Instagrama i TikToka (@cafe_strych) przez oficjalne osadzenia obu serwisów – aktualizują się same. Gdy przeglądarka blokuje treści zewnętrzne, pokazuje się karta z linkiem do profilu.
- Usunięte zdjęcia sprzed remontu 2024 (kominek z zieloną kanapą, bar z gitarami, widok z antresoli, sufit z wentylatorem, kącik przy piecu) – z pokazu na górze, sekcji muzyki i galerii. Galeria sama dopasowuje układ do liczby zdjęć.

## Strona v1.1 – 19.10.2026 (poprawki od klientki)
- Godziny otwarcia od 12:00.
- Nowa sekcja „Imprezy i spotkania”: rezerwacja stolika, sali lub całego lokalu; formularz ma rodzaj rezerwacji, a zapytania trafiają do aplikacji jako rezerwacje oczekujące z dopiskiem REZERWACJA SALI / CAŁEGO LOKALU.
- Historia: 2024 – remont generalny.
- Pasek z napisami pod zdjęciem jest prosty (bez przechylenia).
- Instagram (@cafe_strych) i TikTok (@cafe_strych) obok Facebooka – w kontakcie i w stopce.
- `sql/supabase_v3_4.sql`: rezerwacja ze strony do 120 osób (wcześniej 40).

## V3.5.2 – 16.10.2026
- Naprawa: wysyłanie zgłoszenia błędu kończyło się „null value in column "details" of relation "bug_reports" violates not-null constraint” – starsza tabela miała wymaganą kolumnę `details`. Aplikacja wypełnia ją teraz automatycznie, a `sql/supabase_v3_5_1.sql` zdejmuje wymóg NOT NULL i stare ograniczenie statusu z `bug_reports`.
- Stare statusy zgłoszeń („closed”, „fixed”) są traktowane jak naprawione.

## V3.5.1 – 16.10.2026
- Naprawa: potwierdzanie przeczytania wiadomości kończyło się błędem „Could not find the table 'public.message_reads'” – w bazie brakowało tabeli. Nowy skrypt `sql/supabase_v3_5_1.sql` tworzy wszystkie brakujące tabele i kolumny, których używa aplikacja.
- Ustawienia → System i logi: „Stan bazy danych” sprawdza wszystkie 21 tabel; w Przeglądzie pojawia się ostrzeżenie, gdy czegoś brakuje.
- Zamiast technicznego błędu aplikacja mówi, której tabeli brakuje i jaki skrypt uruchomić.

## V3.5 – 16.10.2026
- Rezerwacje: naprawione dodawanie (brakujące kolumny w bazie + odporny zapis), klik w dzień otwiera okno z listą rezerwacji, z niego edycja i „+ Rezerwacja na ten dzień”, podpowiedzi stolików dla wybranej sali, status i czas trwania.
- Grafik: klik w dzień → okno dnia z listą zmian, szybkim dodawaniem pracownika i godzin oraz dyspozycyjnością zespołu na ten dzień.
- Dyspozycyjność przeniesiona do Grafiku (zakładka „Dyspozycyjność”); na Starcie pracownika został skrót.
- POS: −/+ przy każdej pozycji (usuwanie po jednej sztuce), 🗑 usuwa całą pozycję (kierownik), na telefonie produkty na górze, rachunek jako pasek na dole, skróty kategorii, szybsze dodawanie.
- Ustawienia admina przebudowane: stałe menu z zakładkami, wszystkie sekcje otwierają się w środku, przycisk „Zamknij”.
- Lokal: sale, stoliki i miejsca rezerwacji w jednym widoku, usuwanie, sala może automatycznie przyjmować rezerwacje.
- Zgłoszenia błędów: „🐞 Zgłoś błąd” w menu konta dla każdego (opis + zdjęcie); admin widzi kto, kiedy, z jakiego ekranu i urządzenia, oznacza jako naprawione, pobiera TXT.
