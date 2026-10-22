# V3.9.1 – bez sekcji „Posty z social mediów” (strona pokazuje tylko ikonki i nazwy profili)
#   python3 zrodla/patch40.py panel/index.html panel/index.html
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:100]!r}')
    s = s.replace(old, new)
rep('<b>Cafe Strych Manager <span>V3.9</span></b>', '<b>Cafe Strych Manager <span>V3.9.1</span></b>')
rep('<small>Aktualizacja: 22.10.2026 • Posty z Instagrama, TikToka i Facebooka na stronie www</small>',
    '<small>Aktualizacja: 22.10.2026 • Strona: social media jako ikonki z linkami (bez podglądu postów)</small>')
rep('<p>Cafe Strych Manager <b>V3.9</b> • 22.10.2026</p>', '<p>Cafe Strych Manager <b>V3.9.1</b> • 22.10.2026</p>')
rep("""<section class="socSection"><div class="toolbar"><div><h2>Posty z social mediów</h2><small class="muted">Wklej link do posta z Instagrama, filmiku z TikToka lub posta z Facebooka – pokaże się w sekcji „Na bieżąco” na stronie (najnowsze 9)</small></div><button class="primary" onclick="socialForm()">+ Dodaj post</button></div><div class="cards">${(state.social||[]).map(socialCard).join('')||'<div class="empty">Brak postów. Dodaj link do najnowszego posta z Instagrama albo filmiku z TikToka.</div>'}</div></section>""", "")
rep("news:`${state.news.filter(n=>n.published).length} aktualności • ${(state.social||[]).filter(x=>x.published).length} postów`",
    "news:`${state.news.filter(n=>n.published).length} na stronie`")
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
