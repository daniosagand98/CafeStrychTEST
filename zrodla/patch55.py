# V4.9.1 – stopka bez opisu zmian; menu konta bez „Zgłoszenia błędów” i „Ukryj kwoty” (są w Ustawieniach); bez podpowiedzi przy planowaniu
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:120]!r}')
    s = s.replace(old, new)
rep('<b>Cafe Strych Manager <span>V4.9</span></b>', '<b>Cafe Strych Manager <span>V4.9.1</span></b>')
rep('<small>Aktualizacja: 26.10.2026 • Planowanie aktualności, utarg dnia dla zespołu, powiadomienia o zgłoszeniach</small>', '')
rep('<p>Cafe Strych Manager <b>V4.9</b> • 26.10.2026</p>', '<p>Cafe Strych Manager <b>V4.9.1</b> • 26.10.2026</p>')
rep('<button id="bugsMenu" class="hide" onclick="admin(\'bugs\')">🐞 Zgłoszenia błędów</button><button id="moneyMenu" class="hide" onclick="toggleHideMoney()">🙈 Ukryj kwoty</button>', '')
rep('<p class="muted newsSchedHint">Puste „od” = od razu po zapisaniu. Puste „do” = bez końca. Np. koncert: od poniedziałku 10:00 do soboty 23:59.</p>', '')
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
