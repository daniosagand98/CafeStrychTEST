# Wgranie strony i aplikacji na cafestrychgdynia.pl (OVH)

Program do wgrywania: **FileZilla** (darmowa).
Połączenie: host `sftp://ftp.cluster131.hosting.ovh.net`, port **22**, login `cafestr`, hasło z maila od poprzedniej firmy.
Na serwerze pracujesz w katalogu **`www`**.

Paczka do wgrania: **`na-serwer.zip`** (rozpakuj u siebie). Zawiera dokładnie:

```
.htaccess        ← przekierowania i ustawienia (plik ukryty – w FileZilli: Serwer → Wymuś pokazywanie ukrytych plików)
index.html       ← strona
img/             ← zdjęcia strony
panel/           ← aplikacja Cafe Strych Manager
```

Nie wgrywaj na serwer folderów `sql/`, `podglad/`, `zrodla/`, `supabase/` z repozytorium.

## Krok 1 – kopia starej strony (zanim cokolwiek zmienisz)
1. W FileZilli pobierz na swój dysk **cały katalog `www`**.
2. W `cafestrychgdynia.pl/wp-admin`: Narzędzia → Eksport → Cała zawartość → pobierz plik.
3. Zapisz obie rzeczy na Dysku Google w `02_Klienci/CafeStrych`.

## Krok 2 – test bez ruszania obecnej strony
1. W `www` utwórz folder **`nowa`**.
2. Wgraj do niego `index.html`, `img/` i `panel/` (**bez** `.htaccess`).
3. Sprawdź: `cafestrychgdynia.pl/nowa/` (strona) i `cafestrychgdynia.pl/nowa/panel/` (logowanie, rezerwacja ze strony, aktualności).

## Krok 3 – podmiana (najlepiej rano, gdy lokal jest zamknięty)
1. W `www` utwórz folder **`_stara-strona`** i przenieś do niego wszystkie pliki WordPressa
   (wszystko poza folderem `nowa` i `_stara-strona`). Plik `.htaccess` z niego zablokuje dostęp z internetu.
2. Wgraj do `www` całą zawartość paczki: `.htaccess`, `index.html`, `img/`, `panel/`.
3. Usuń folder `nowa`.
4. Sprawdź: `cafestrychgdynia.pl` i `cafestrychgdynia.pl/panel/`.

Gdyby coś poszło źle: usuń nowe pliki i przenieś z powrotem zawartość `_stara-strona` do `www`.

## Krok 4 – HTTPS (potrzebny do logowania i powiadomień)
1. Panel OVH → Hosting → **Multisite**: przy `cafestrychgdynia.pl` i `www.cafestrychgdynia.pl` włącz **SSL**.
   Potem zakładka **Certyfikat SSL** → Zamów → **Let's Encrypt** (darmowy). Trwa to do kilku godzin.
2. Gdy `https://cafestrychgdynia.pl` działa: w pliku `.htaccess` na serwerze usuń znaki `#` z 5 linii w sekcji 1 (HTTPS i www).

Do kroku 4 potrzebny jest dostęp do panelu OVH – albo zrobi to poprzednia firma, albo zrobisz po przeniesieniu konta na klientkę.

## Krok 5 – Supabase (po kroku 4)
1. Authentication → **URL Configuration**:
   - Site URL: `https://cafestrychgdynia.pl/panel/`
   - Redirect URLs: dodaj `https://cafestrychgdynia.pl/panel/` (testowy adres z GitHuba możesz zostawić).
2. Edge Functions → Secrets → **`APP_URL`** = `https://cafestrychgdynia.pl/panel/`.

## Krok 6 – zespół
- Każdy loguje się pod nowym adresem `https://cafestrychgdynia.pl/panel/`.
- Powiadomienia trzeba włączyć ponownie (menu konta → 🔔 Powiadomienia).
- iPhone: dodać aplikację do ekranu początkowego jeszcze raz z nowego adresu (Safari → Udostępnij → „Do ekranu początkowego”).

## Na koniec
- Gdy nowa strona działa kilka dni bez problemów: usuń `_stara-strona` z serwera (kopia jest u Ciebie).
- Po przejęciu konta OVH przez klientkę: zmień hasło SFTP i hasło konta OVH.
