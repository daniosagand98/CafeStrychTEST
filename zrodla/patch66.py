import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:80]}')
    s=s.replace(a,b)
rep("window.deleteHistoricalOrder=id=>{if(!isAdmin())return alert('Rachunek z historii może usunąć tylko administrator.');const o=state.orders.find(x=>x.id===id);if(!o)return;",
    "window.deleteHistoricalOrder=id=>{const o=state.orders.find(x=>x.id===id);if(!o)return;if(!isAdmin()&&!(canManage()&&isCancelled(o)))return alert('Kierownik może usunąć tylko anulowany rachunek. Opłacony rachunek usuwa administrator.');")
rep("""${isAdmin()?`<div class="histBtns">${!c?`<button class="ghost historyDelete" onclick="cancelOrder('${o.id}')">Anuluj</button>`:''}<button class="danger historyDelete" onclick="deleteHistoricalOrder('${o.id}')">Usuń</button></div>`:''}""",
    """${isAdmin()||(c&&canManage())?`<div class="histBtns">${!c&&isAdmin()?`<button class="ghost historyDelete" onclick="cancelOrder('${o.id}')">Anuluj</button>`:''}<button class="danger historyDelete" onclick="deleteHistoricalOrder('${o.id}')">Usuń</button></div>`:''}""")
rep("""<button class="danger historyDelete" onclick="deleteHistoricalOrder('${o.id}')">Usuń</button></div>`).join""",
    """${isAdmin()||(isCancelled(o)&&canManage())?`<button class="danger historyDelete" onclick="deleteHistoricalOrder('${o.id}')">Usuń</button>`:''}</div>`).join""")
rep("'Opłacone rachunki może anulować lub usunąć administrator.'","(canManage()?'Anulowany rachunek możesz usunąć. Opłacone rachunki anuluje lub usuwa administrator.':'Opłacone rachunki może anulować lub usunąć administrator.')")
rep("'Najpierw uruchom w Supabase plik sql/supabase_v4_5.sql (usuwanie rachunków z historii).'","'Najpierw uruchom w Supabase plik sql/supabase_v5_1_2.sql (usuwanie rachunków z historii).'")
rep('Cafe Strych Manager <span>V5.1.1</span>','Cafe Strych Manager <span>V5.1.2</span>')
rep('Cafe Strych Manager <b>V5.1.1</b> • 03.11.2026','Cafe Strych Manager <b>V5.1.2</b> • 03.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
