import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:80]}')
    s=s.replace(a,b)
# Wróć po prawej, równo z tytułem
rep("const backBtn=(fn,label='← Wróć')=>state.inAdmin?'':`<button class=\"ghost\" onclick=\"${fn}\">${label}</button>`;",
"const backBtn=(fn,label='← Wróć')=>state.inAdmin?'':`<button class=\"ghost backTop\" onclick=\"${fn}\">${label}</button>`;")
rep("""<div class="toolbar"><div>${backBtn('posConfiguration()')}<h2>Lokal</h2><small class="muted">Sale i przypisane do nich stoliki</small></div><div class="actions"><button class="primary" onclick="roomForm()">+ Sala</button></div></div>""",
"""<div class="toolbar inline"><div><h2>Lokal</h2><small class="muted">Sale i przypisane do nich stoliki</small></div>${backBtn('posConfiguration()')}</div><div class="toolActs"><button class="primary" onclick="roomForm()">+ Sala</button></div>""")
rep("""<div class="toolbar"><div>${backBtn('posConfiguration()')}<h2>Menu POS</h2><small class="muted">${state.menu.filter(x=>x.active!==false).length} aktywnych produktów</small></div><button class="primary" onclick="menuForm()">+ Produkt</button></div>""",
"""<div class="toolbar inline"><div><h2>Menu POS</h2><small class="muted">${state.menu.filter(x=>x.active!==false).length} aktywnych produktów</small></div>${backBtn('posConfiguration()')}</div><div class="toolActs"><button class="primary" onclick="menuForm()">+ Produkt</button></div>""")
rep("<p>Sale, stoliki i miejsca rezerwacji – wszystko w jednym widoku.</p>","<p>Sale i przypisane do nich stoliki.</p>")
# kafelek sali: Edytuj w prawym górnym rogu, bez „+ Stolik”
rep("""<div class="actions"><button class="ghost" onclick="tableForm(null,'${r.id}')">+ Stolik</button><button class="ghost" onclick="roomForm('${r.id}')">Edytuj salę</button></div></div>""",
"""<button class="ghost roomEdit" onclick="roomForm('${r.id}')">Edytuj</button></div>""")
# „+ Dodaj stolik” w edycji sali
rep("""${r?`<div class="shiftModalActions"><button type="button" class="danger" onclick="deleteRoom('${r.id}')">Usuń salę</button>""",
"""${r?`<button type="button" class="ghost addTableBtn" onclick="tableForm(null,'${r.id}')">+ Dodaj stolik do tej sali</button><div class="shiftModalActions"><button type="button" class="danger" onclick="deleteRoom('${r.id}')">Usuń salę</button>""")
# CSS
rep("</style></head>","""
/* V5.0.5 */
.toolbar.inline{align-items:flex-start!important}
.toolbar>button.backTop{width:auto!important;height:40px;padding:0 14px!important;white-space:nowrap;margin-top:2px}
.toolActs{display:flex;gap:9px;margin:0 0 12px}.toolActs button{flex:1}
@media(min-width:760px){.toolActs{justify-content:flex-end}.toolActs button{flex:0 0 auto;min-width:180px}}
.venueRoom>.sectionHead{align-items:flex-start}
.venueRoom .roomEdit{flex:0 0 auto;padding:8px 14px;min-height:0}
.addTableBtn{width:100%;margin-top:12px}
.kpis,.venueKpis{display:grid!important;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);grid-template-columns:none!important;gap:8px}
.kpis .kpi,.venueKpis .kpi{grid-column:auto!important;min-width:0}
@media(max-width:600px){.kpis .kpi,.venueKpis .kpi{padding:11px 10px}.kpis .kpi span,.venueKpis .kpi span{font-size:11.5px;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.kpis .kpi strong,.venueKpis .kpi strong{font-size:18px;white-space:nowrap}.kpis .kpi small,.venueKpis .kpi small{font-size:11px}}
</style></head>""")
rep('Cafe Strych Manager <span>V5.0.4</span>','Cafe Strych Manager <span>V5.0.5</span>')
rep('Cafe Strych Manager <b>V5.0.4</b>','Cafe Strych Manager <b>V5.0.5</b>')
open(p,'w',encoding='utf-8').write(s); print('ok')
