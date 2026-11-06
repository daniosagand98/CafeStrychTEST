# Cafe Strych – kopie zapasowe

## Co jest chronione i gdzie

| Co | Kopia | Jak długo |
|---|---|---|
| **Strona i aplikacja (pliki)** | GitHub, każda wersja w historii zmian | na zawsze |
| **Strona i aplikacja na serwerze OVH** | automatyczne kopie OVH (zakładka „FTP - SSH”) | dziś, wczoraj, przedwczoraj + 2 ostatnie niedziele |
| **Baza Supabase** (rachunki, grafik, rezerwacje, czat, ustawienia…) | GitHub Actions → „Kopia zapasowa”, co noc | 30 dni |
| **Konta użytkowników** (logowanie) | jw., w tej samej kopii | 30 dni |
| **Pliki w Supabase** (zdjęcia aktualności i galerii, dokumenty pracowników, zrzuty zgłoszeń) | jw., w tej samej kopii | 30 dni |

Supabase na darmowym planie **nie robi** własnych kopii bazy – dlatego robimy je sami.
Na planie Pro (później) Supabase dodatkowo trzyma 7 dni własnych kopii.

## Ustawienie (raz)

GitHub → repozytorium → **Settings → Secrets and variables → Actions → New repository secret**:

1. `SUPABASE_DB_URL` – Supabase → przycisk **Connect** (u góry) → **Session pooler** → skopiuj URI
   i wpisz w nim hasło do bazy w miejsce `[YOUR-PASSWORD]`
   (hasło do bazy: Project Settings → Database → Reset database password, jeśli go nie znasz).
2. `SUPABASE_SERVICE_KEY` – Supabase → Project Settings → **API Keys** → klucz *secret* (albo *service_role*).
3. `BACKUP_PASSWORD` – wymyśl mocne hasło i **zapisz je w bezpiecznym miejscu**
   (np. menedżer haseł). Bez niego kopii nie da się otworzyć.

Potem: **Actions → „Kopia zapasowa” → Run workflow** – pierwsza kopia od razu.
Każda następna robi się sama co noc ok. 4:30.

## Gdzie są kopie

GitHub → **Actions → „Kopia zapasowa”** → kliknij przebieg z danego dnia → na dole **Artifacts**
→ plik `cafe-strych-kopia-RRRR-MM-DD_GGMM` (zaszyfrowany).

Kopie są zaszyfrowane (AES-256), więc nawet jeśli ktoś pobierze plik, bez hasła nic nie odczyta.

## Przywracanie (awaryjnie – najlepiej z pomocą)

1. Pobierz artefakt (zip) i rozpakuj – w środku jest plik `….tar.gz.enc`.
2. Odszyfruj (Terminal / PowerShell z OpenSSL):
   ```
   openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in cafe-strych-kopia-….tar.gz.enc -out kopia.tar.gz
   tar -xzf kopia.tar.gz
   ```
3. W folderze `kopia/`:
   - `baza-public.dump` – wszystkie tabele aplikacji. Przywrócenie do bazy:
     ```
     pg_restore --clean --if-exists --no-owner -d "URI_BAZY" kopia/baza-public.dump
     ```
     (lub pojedyncze tabele: dodaj `-t nazwa_tabeli`)
   - `baza-public-struktura.sql` – sama struktura (do podglądu).
   - `konta-auth.dump` – konta logowania.
   - `pliki/` – zdjęcia i dokumenty, w podfolderach według nazwy „bucketa” w Supabase
     (wgrywa się je z powrotem w Supabase → Storage).

## Pliki na OVH – przywracanie

- Cała strona do stanu z danego dnia: panel OVH → Hosting → **FTP - SSH → Przywróć kopię zapasową**.
- Pojedynczy plik: FileZilla, login FTP z dopiskiem `-snap1` (wczoraj), `-snap2` (przedwczoraj) itd.
- Najprościej: na GitHubie jest zawsze aktualna wersja – wystarczy **Actions → „Wgraj na OVH” → Run workflow**.
