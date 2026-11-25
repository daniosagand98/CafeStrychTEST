# V5.8.4: Ustawienia → Przegląd – kafelki „Historia rachunków” i „Tablety firmowe” pokazywały „undefined” (brak podpisu)
import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
rep("bugs:nb?`${nb} do sprawdzenia`:'brak nowych',system:'Wersja i aktywność'}",
    "bugs:nb?`${nb} do sprawdzenia`:'brak nowych',audit:'Anulowane i usunięte rachunki',devices:'Tablety dla pracowników',system:'Wersja i aktywność'}")
rep('Cafe Strych Manager <span>V5.8.3</span>','Cafe Strych Manager <span>V5.8.4</span>')
rep('Cafe Strych Manager <b>V5.8.3</b> • 20.11.2026','Cafe Strych Manager <b>V5.8.4</b> • 25.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
