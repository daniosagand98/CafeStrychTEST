# Cafe Strych – repozytorium testowe

| Ścieżka | Co to jest |
|---|---|
| `index.html` + `img/` | Strona lokalu (v1.5) – aktualności, menu, galeria, rezerwacje |
| `.htaccess` + `WDROZENIE-OVH.md` | Ustawienia serwera OVH (przekierowania ze starego WordPressa, HTTPS, pamięć podręczna) i instrukcja wgrania na cafestrychgdynia.pl |
| `panel/` | Aplikacja **Cafe Strych Manager V3.9** (instalowana na telefonie, z powiadomieniami) (logowanie przez Supabase) |
| `sql/` | Skrypty do Supabase – uruchamiać po kolei: `supabase_v3_5_1.sql` (naprawa tabel), `supabase_v3_4.sql`, `supabase_v3_5.sql`, `supabase_v3_6.sql` (powiadomienia), `supabase_v3_7.sql` (bezpieczeństwo), `supabase_v3_8.sql` (powiadomienia + anulowanie rachunków; zawiera v3.6) |
| `supabase/functions/notify-booking/` | Funkcja wysyłająca powiadomienia push – konfiguracja w `POWIADOMIENIA.md` |
| `podglad/` | Wersje bez logowania na danych demo – do testów, nic nie zapisują w bazie |
| `zrodla/` | Karta menu (`menu_data.py`) i skrypty budujące stronę oraz podgląd |

Na serwerze klienta: zawartość głównego katalogu (bez `sql/`, `podglad/`, `zrodla/`) → katalog główny domeny, aplikacja dostępna pod `/panel/`.

## Aplikacja V4.6.1 – 23.10.2026
- Rabat działa też bez internetu (zapis w pamięci urządzenia, wysyłany przed płatnością). Offline nie działają tylko: anulowanie, edycja i usuwanie rachunków.

## Aplikacja V4.6 – 23.10.2026 (pełna ochrona: sql/supabase_v4_6.sql)
- POS odporny na brak internetu i zanik prądu: dodawanie/±/usuwanie pozycji, nowy rachunek i płatność zapisują się najpierw w pamięci urządzenia (skrzynka zmian w localStorage), potem wysyłają się po kolei. Bez internetu: czerwony pasek „📴 Brak internetu – zapisane w pamięci tego urządzenia (N czeka)”; po powrocie sieci wszystko wysyła się samo i pojawia się „✓ Wysłano zmiany zapisane offline (N)”.
- Zamknięcie aplikacji / zanik prądu / restart telefonu: niewysłane zmiany zostają w pamięci i wysyłają się przy następnym uruchomieniu. Aplikacja otwiera się także bez internetu (service worker + kopia ostatnich danych), na ostatnio zapisanych danych.
- Brak sieci nie czyści już danych na ekranie (wcześniej nieudane pobranie dawało puste listy).
- SQL v4.6: każde kliknięcie ma własny numer – jeśli zostanie wysłane dwa razy (zerwanie w trakcie wysyłania), baza go nie doliczy drugi raz. Płatność i nowy rachunek też mają własne numery (bez dublowania).
- Bez internetu nie działają: rabat, anulowanie, edycja i usuwanie rachunków (komunikat).

## Aplikacja V4.5 – 23.10.2026 (wymaga sql/supabase_v4_5.sql)
- Historia rachunków: administrator ma przy każdym rachunku „Usuń” (obok „Anuluj”). Przed usunięciem okno z ostrzeżeniem: kwota zniknie z utargu dnia/miesiąca/roku, wcześniejsze podsumowania (np. raport z kasy fiskalnej) mogą się nie zgadzać, nie da się cofnąć; trzeba zaznaczyć „Rozumiem” i kliknąć „Usuń na zawsze”. Usunięcie zapisuje się w „System i logi” (kto, rachunek, kwota). Baza pozwala na to tylko administratorowi (funkcja pos_delete_order).

## Aplikacja V4.4.1 – 23.10.2026 (wymaga sql/supabase_v4_4.sql)
- Rachunek: bez „Przygotowanie”/„Gotowe”; „Płatność” na całą szerokość, pod nią „％ Rabat” obok „Anuluj rachunek”.
- Okno rabatu: samo pole „Rabat w %” i podgląd „Do zapłaty”; 0 lub puste = bez rabatu.
- Poprawka: usuwanie produktu z Menu POS, który był na zamkniętym rachunku (baza blokowała odpięcie produktu od starej pozycji). Stare rachunki zachowują nazwę, ilość i cenę.

## Aplikacja V4.4 – 23.10.2026 (wymaga sql/supabase_v4_3.sql)
- Rabat procentowy na rachunku: przycisk „％ Dodaj rabat” (kierownik/admin) – szybkie 5–100% lub dowolna wartość, podgląd kwoty. Rachunek pokazuje sumę, rabat i „Razem po rabacie”; płatność i utarg są po rabacie; na liście rachunków znaczek „−15%”, w utargu dnia dopisek „rabat 15%”. Baza pilnuje: rabat tylko kierownik/admin i tylko na otwartym rachunku.
- Sprawdzenie menu: baza ma 182 produkty, strona 180 – nadmiarowe testowe „Piwo corona” i „Vódka 40 ml”; reszta (nazwy, ceny, VAT, kategorie) zgodna 1:1.

## Aplikacja V4.3.1 – 23.10.2026
- Start pracownika bez przycisku „Dyspozycyjność” (zgłasza się ją w Grafiku → Dyspozycyjność).

## Aplikacja V4.3 – 23.10.2026 (szybki POS: sql/supabase_v4_2.sql)
- Dyspozycyjność: „Dostępny w godzinach”, „Niedostępny w godzinach” (np. bez 12:00–16:00), „Niedostępny cały dzień”. Kierownik widzi „✗ niedostępny 12:00–16:00” na pomarańczowo; przy wyborze do zmiany nie podpowiadają się te godziny.
- Grafik i Rezerwacje: nawigacja „‹ 19–25 paź 2026 ›” z opisem (ten / następny tydzień) i przyciskiem „↺ Dziś”, gdy oglądasz inny okres; Tydzień/Miesiąc pod spodem.
- Utarg: jasne opisy („Sprzedaż w poszczególnych dniach – kliknij dzień…”), dzień z dowolnej daty (starsze płatności dociągane z bazy), podsumowanie nie przelicza się przy każdym kliknięciu.
- POS: dodawanie, +/−, usuwanie pozycji widać od razu, zapis w tle w kolejce (SQL v4.2: jedno atomowe zapytanie; bez SQL działa po staremu). Zmiany POS z innych urządzeń odświeżają tylko POS zamiast całej aplikacji i nie przerywają klikania. Płatność czeka na zapis wszystkich kliknięć. Nowy rachunek otwiera się natychmiast. Otwarty rachunek podświetla POS w menu.

## Aplikacja V4.2 – 23.10.2026
- Start pracownika: powitanie i „Dyspozycyjność” w jednej linii, „Najbliższa zmiana” i „Godziny w miesiącu” jako dwa małe kafelki obok siebie, odstępy między komunikatami.
- Rezerwacje i Grafik: tytuł z przyciskiem w jednej linii, ‹ Dziś › i Tydzień/Miesiąc w jednym pasku, odstępy między kartami rezerwacji.
- Daty zmian w formacie „Pt 23.10 • 12:00–20:00”.
- Utarg: podsumowanie za miesiąc, rok lub wybrany okres (suma, płatności, średnio dziennie, karta/gotówka/BLIK/przelew, wykres dni lub miesięcy – kliknięcie dnia otwiera jego szczegóły), bez anulowanych rachunków.

## Aplikacja V4.1.1 – 23.10.2026
- Logowanie: przycisk „Zaloguj” / „Utwórz konto” / „Wyślij link” na całą szerokość z odstępem od pola hasła (nie nachodzi na nie na komputerze).

## Aplikacja V4.1 + Strona v1.7.1 – 23.10.2026 (kadrowanie wymaga sql/supabase_v4_1.sql)
- Logowanie: „Nie pamiętasz hasła?” – link do ustawienia nowego hasła na e-mail; komunikaty błędów logowania po polsku.
- Menu POS: przycisk „Usuń” przy produkcie (stare rachunki zachowują nazwę i cenę).
- Aktualności: kadrowanie zdjęcia – przeciągnij zdjęcie w podglądzie, strona pokazuje wybrany fragment.

## Aplikacja V4.0 + Strona v1.7 – 23.10.2026 (wymaga sql/supabase_v4_0.sql)
- Ustawienia → Przegląd → „Moduły aplikacji”: admin włącza/wyłącza POS, Grafik, Rezerwacje, Listę zakupów. Wyłączony moduł znika z menu i pulpitu kierowników i pracowników (admin widzi go z oznaczeniem „wył.”), dane zostają w bazie. Zmiana działa od razu u wszystkich zalogowanych.
- „Strona www → Rezerwacje ze strony”: po wyłączeniu przycisk „Rezerwacja” na stronie pokazuje „rezerwacje tylko telefonicznie” z numerem. Baza dodatkowo odrzuca prośby wysłane ze strony otwartej przed wyłączeniem. Wyłączenie modułu Rezerwacje też przełącza stronę na telefon.

## Strona v1.6 + Aplikacja V3.9.1 – 22.10.2026
- Na życzenie klientki: sekcja „Na bieżąco” pokazuje tylko ikonki i nazwy Instagram / TikTok / Facebook z przyciskiem „Obserwuj” – bez podglądu postów.
- Aplikacja: usunięta sekcja „Posty z social mediów” w Aktualnościach (tabela site_social_posts zostaje w bazie, nieużywana).

## Strona v1.5.3 – 22.10.2026
- Kolumny Instagram / TikTok / Facebook mają równą wysokość, stopki „Odśwież podgląd / Otwórz profil” w jednej linii.
- Facebook: nagłówek strony (zdjęcie, obserwujący) + karta „Zobacz posty na Facebooku” zamiast osi czasu, której Facebook nie wyświetla poza facebook.com dla tej strony.

## Strona v1.5.2 – 22.10.2026
- Pasek „Jak to działa?” w sekcji imprez przebudowany: numerowane kroki w równych kolumnach, telefon jako przycisk „Zadzwoń” (komputer, tablet i telefon).

## Strona v1.5.1 – 22.10.2026
- Pola podglądu Instagrama, TikToka i Facebooka dopasowują się do wysokości postów (bez pustego białego miejsca i podwójnej ramki).

## Strona v1.5 – 22.10.2026
- „Na bieżąco”: przywrócony **automatyczny** podgląd profili Instagram, TikTok i Facebook (oficjalne osadzenia, wczytywane przy przewinięciu do sekcji). Pod każdym przycisk „↻ Odśwież podgląd” (gdy serwis chwilowo nie odda postów) i „Otwórz profil”.
- Ręcznie dodawane posty z aplikacji zostają jako karuzela „Wybrane posty” (pokazuje się tylko, gdy są jakieś posty).

## Strona v1.4.1 – 22.10.2026
- Rezerwacja **stolika** tylko w godzinach otwarcia (ostatnia 1 h przed zamknięciem, z uwzględnieniem nocy po północy w pt–sb); sala i cały lokal – bez ograniczeń.
- Po wysłaniu rezerwacji nagłówek okna „Prośba o rezerwację wysłana” jest wyśrodkowany.

## Strona v1.4 + aplikacja V3.9 – 22.10.2026 (+ `sql/supabase_v3_9.sql`)
- „Na bieżąco”: karty profili Instagram / TikTok / Facebook + karuzela **Najnowsze posty**. Posty dodaje kierownik w aplikacji: Aktualności (strona) → **Posty z social mediów** → wklej link do posta/filmiku. Strona pokazuje 9 najnowszych przez oficjalne osadzenie pojedynczych postów (bez limitów, w przeciwieństwie do automatycznego podglądu profilu).
- Usunięty podgląd osi czasu Facebooka (pokazywał tylko nagłówek strony bez postów).
- Menu strony: zakładka **Rezerwacja** otwiera okno rezerwacji (na komputerze jest przycisk w nagłówku).
- Po wysłaniu rezerwacji okno zamienia się w potwierdzenie z podsumowaniem (wcześniej formularz zostawał widoczny).

## Strona v1.3 – 22.10.2026
- Sekcja „Na bieżąco”: najnowsze posty z **Facebooka** (oficjalna wtyczka strony, ładowana przy przewinięciu).
- Instagram i TikTok jako karty z przyciskiem „Obserwuj”; filmiki z TikToka wczytują się dopiero po kliknięciu „Pokaż filmiki tutaj” (TikTok blokował automatyczne wczytywanie – „ratelimit triggered”, a podgląd profilu Instagrama był pusty).

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
