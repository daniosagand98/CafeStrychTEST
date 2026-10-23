# V4.3.1 – bez przycisku „Dyspozycyjność” na Starcie pracownika (jest w Grafiku)
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:110]!r}')
    s = s.replace(old, new)
rep('<b>Cafe Strych Manager <span>V4.3</span></b>', '<b>Cafe Strych Manager <span>V4.3.1</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • Niedostępność w godzinach, czytelna nawigacja tygodni, szybszy POS</small>',
    '<small>Aktualizacja: 23.10.2026 • Prostszy Start pracownika, niedostępność w godzinach, szybszy POS</small>')
rep('<p>Cafe Strych Manager <b>V4.3</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.3.1</b> • 23.10.2026</p>')
rep("""${moduleOn('schedule')?`<button class="ghost btnSm" onclick="${goAvail}">📅 Dyspozycyjność</button>`:''}</div>""", "</div>")
open(dst, 'w', encoding='utf-8').write(s); print('OK')
