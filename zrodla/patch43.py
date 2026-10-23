# V4.1.1 – przycisk „Zaloguj” nie nachodzi na pole hasła (odstęp, pełna szerokość)
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:110]!r}')
    s = s.replace(old, new)
rep('<b>Cafe Strych Manager <span>V4.1</span></b>', '<b>Cafe Strych Manager <span>V4.1.1</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • Reset hasła przy logowaniu, usuwanie produktów z menu, kadrowanie zdjęć aktualności</small>',
    '<small>Aktualizacja: 23.10.2026 • Poprawiony wygląd logowania, reset hasła, usuwanie produktów z menu, kadrowanie zdjęć</small>')
rep('<p>Cafe Strych Manager <b>V4.1</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.1.1</b> • 23.10.2026</p>')
rep('#resetForm .primary{margin-top:14px}', '#loginForm .primary,#signupForm .primary,#resetForm .primary{display:block;width:100%;margin-top:18px;padding:13px}')
open(dst, 'w', encoding='utf-8').write(s); print('OK')
