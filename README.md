# Cafe Strych – repozytorium testowe

| Ścieżka | Co to jest |
|---|---|
| `index.html` + `img/` | Strona lokalu (v1.0) – aktualności, menu, galeria, rezerwacje |
| `panel/` | Aplikacja **Cafe Strych Manager V3.5.1** (logowanie przez Supabase) |
| `sql/` | Skrypty do Supabase – uruchamiać po kolei: `supabase_v3_5_1.sql` (naprawa tabel), `supabase_v3_4.sql`, `supabase_v3_5.sql` |
| `podglad/` | Wersje bez logowania na danych demo – do testów, nic nie zapisują w bazie |
| `zrodla/` | Karta menu (`menu_data.py`) i skrypty budujące stronę oraz podgląd |

Na serwerze klienta: zawartość głównego katalogu (bez `sql/`, `podglad/`, `zrodla/`) → katalog główny domeny, aplikacja dostępna pod `/panel/`.

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
