# Powiadomienia o nowych rezerwacjach – konfiguracja (jednorazowo, ok. 10 minut)

Jak to działa: gdy w bazie pojawia się nowa rezerwacja (ze strony www albo od zespołu),
baza wywołuje funkcję `notify-booking` w Supabase, a ta wysyła powiadomienie push na telefony
kierowników i administratorów, którzy włączyli powiadomienia w aplikacji.
Działa także, gdy aplikacja jest zamknięta.

## 1. Funkcja w Supabase (Edge Function)

1. Supabase → **Edge Functions** → **Deploy a new function** → **Via Editor**.
2. Nazwa funkcji: **`notify-booking`** (dokładnie tak).
3. Wklej całą zawartość pliku `supabase/functions/notify-booking/index.ts` → **Deploy**.
4. W ustawieniach funkcji (Details / Settings) **wyłącz „Verify JWT” / „Enforce JWT verification”**.
   Funkcja ma własne zabezpieczenie: wysyła tylko dla prawdziwej, nowej rezerwacji i tylko raz.

## 2. Sekrety funkcji

Supabase → **Edge Functions** → **Secrets** → dodaj 4 wartości z pliku
**`PRYWATNE-klucze-powiadomien.txt`** (dostałeś go osobno – nie wrzucaj go do repozytorium):

| Nazwa | Wartość |
|---|---|
| `VAPID_PUBLIC_KEY` | klucz publiczny z pliku |
| `VAPID_PRIVATE_KEY` | klucz prywatny z pliku |
| `VAPID_SUBJECT` | `mailto:` + Twój e-mail |
| `APP_URL` | adres panelu, np. `https://daniosagand98.github.io/CafeStrychTEST/panel/` (później `https://cafestrych.pl/panel/`) |

## 3. Baza danych

Supabase → **SQL Editor** → wklej `supabase_v3_6.sql` → **Run**.
Tworzy tabelę urządzeń `push_subscriptions` i włącza wywołanie funkcji po dodaniu rezerwacji.
Jeśli wysyłka powiadomienia się nie uda, rezerwacja i tak się zapisze.

## 4. Telefon

**Android (Chrome):** zaloguj się → menu konta (kółko z literą) → **🔔 Powiadomienia** → **Włącz powiadomienia** → Zezwól.
Możesz też dodać aplikację do ekranu głównego (menu ⋮ → „Dodaj do ekranu głównego” / „Zainstaluj aplikację”).

**iPhone (iOS 16.4 lub nowszy) – powiadomienia działają tylko z ikony na ekranie początkowym:**
1. Otwórz panel w **Safari**.
2. **Udostępnij** (kwadrat ze strzałką) → **„Do ekranu początkowego”**.
3. Otwórz aplikację z nowej ikony **Strych** i zaloguj się.
4. Menu konta → **🔔 Powiadomienia** → **Włącz powiadomienia** → Zezwól.

Każde urządzenie włącza się osobno. Na ekranie Powiadomień jest przycisk **„Wyślij test”**
i lista Twoich urządzeń (można je usuwać).

## 5. Sprawdzenie

Dodaj rezerwację na stronie www (albo z innego konta w aplikacji) → w ciągu kilku sekund
powinno przyjść powiadomienie „Nowa rezerwacja ze strony”. Stuknięcie otwiera ten dzień w Rezerwacjach.

Jeśli nie przychodzi: Supabase → Edge Functions → notify-booking → **Logs**
(np. „nikt nie włączył powiadomień” albo błąd klucza).
