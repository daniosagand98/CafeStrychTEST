import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
rep("window.discountForm=id=>{const o=state.orders.find(x=>x.id===id);if(!o||!canManage())return;","window.discountForm=id=>{const o=state.orders.find(x=>x.id===id);if(!o)return;")
rep("if(!canManage())return alert('Rachunek może anulować kierownik lub administrator.');\n modal('Anuluj rachunek'","\n modal('Anuluj rachunek'")
# pracownik: te same przyciski co kierownik
rep("""const actions=closed?closedOrderInfo(o):canManage()?`<div class="actions ticketActions"><button class="primary" onclick="pay('${id}')">Płatność</button><button class="ghost discBtn" onclick="discountForm('${id}')">％ ${orderDiscount(id)?`Rabat ${pctTxt(orderDiscount(id))}`:'Rabat'}</button><button class="danger" onclick="cancelOrder('${id}')">Anuluj rachunek</button></div>`:`<div class="actions ticketActions"><button class="primary" onclick="pay('${id}')">Płatność</button></div><p class="muted" style="margin-top:6px;font-size:12px">Rabat i anulowanie rachunku – kierownik.</p>`;""",
    """const actions=closed?closedOrderInfo(o):`<div class="actions ticketActions"><button class="primary" onclick="pay('${id}')">Płatność</button><button class="ghost discBtn" onclick="discountForm('${id}')">％ ${orderDiscount(id)?`Rabat ${pctTxt(orderDiscount(id))}`:'Rabat'}</button><button class="danger" onclick="cancelOrder('${id}')">Anuluj rachunek</button></div>`;""")
rep("""${canManage()?`<button class="danger ticketCancel" onclick="cancelOrder('${o.id}')">Anuluj opłacony rachunek</button>`:''}""",
    """<button class="danger ticketCancel" onclick="cancelOrder('${o.id}')">Anuluj opłacony rachunek</button>""")
rep("""${canManage()?`<div class="histBtns">${!c?`<button class="ghost historyDelete" onclick="cancelOrder('${o.id}')">Anuluj</button>`:''}<button class="danger historyDelete" onclick="deleteHistoricalOrder('${o.id}')">Usuń</button></div>`:''}""",
    """${canManage()||!c?`<div class="histBtns">${!c?`<button class="ghost historyDelete" onclick="cancelOrder('${o.id}')">Anuluj</button>`:''}${canManage()?`<button class="danger historyDelete" onclick="deleteHistoricalOrder('${o.id}')">Usuń</button>`:''}</div>`:''}""")
rep("${canManage()?'Anuluj – rachunek zostaje w historii, bez wpływu na utarg. Usuń – znika na zawsze, także z podsumowań.':'Opłacone rachunki może anulować lub usunąć kierownik.'}",
    "${canManage()?'Anuluj – rachunek zostaje w historii, bez wpływu na utarg. Usuń – znika na zawsze, także z podsumowań.':'Anuluj – rachunek zostaje w historii jako anulowany. Usuwać rachunki może tylko kierownik.'}")
rep('Cafe Strych Manager <span>V5.7</span>','Cafe Strych Manager <span>V5.7.1</span>')
rep('Cafe Strych Manager <b>V5.7</b> • 20.11.2026','Cafe Strych Manager <b>V5.7.1</b> • 20.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
