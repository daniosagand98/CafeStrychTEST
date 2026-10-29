import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:80]}')
    s=s.replace(a,b)
# 3+4: bez „Miejsc” i bez górnego „+ Stolik”
rep('<div class="actions"><button class="ghost" onclick="placeForm()">+ Miejsce</button><button class="ghost" onclick="tableForm()">+ Stolik</button><button class="primary" onclick="roomForm()">+ Sala</button></div>',
'<div class="actions"><button class="primary" onclick="roomForm()">+ Sala</button></div>')
rep('<small class="muted">Sale, stoliki i miejsca rezerwacji w jednym miejscu</small>','<small class="muted">Sale i przypisane do nich stoliki</small>')
rep('<div class="kpi"><span>Miejsca siedzące</span><strong>${seats}</strong></div><div class="kpi"><span>Miejsca rezerwacji</span><strong>${state.places.filter(p=>p.active!==false).length}</strong></div></div>',
'<div class="kpi"><span>Miejsca siedzące</span><strong>${seats}</strong></div></div>')
a=s.index("${loose.length?`<section class=\"panel venueRoom\"><div class=\"sectionHead\"><h3>Stoliki bez sali</h3>")
b=s.index("`}\nwindow.venueAdmin=venueAdmin;")
seg=s[a:b]
assert '<h3>Inne miejsca rezerwacji</h3>' in seg
loose_end=seg.index(":''}")+4
s=s[:a]+seg[:loose_end]+s[b:]
# 1: sala – Usuń obok Zapisz
rep("""${r?`<button type="button" class="danger" style="margin-top:10px" onclick="deleteRoom('${r.id}')">Usuń salę</button>`:''}`,async()=>{const name=$('#roomName')""",
"""${r?`<div class="shiftModalActions"><button type="button" class="danger" onclick="deleteRoom('${r.id}')">Usuń salę</button><button type="submit" class="primary">Zapisz</button></div>`:''}`,async()=>{const name=$('#roomName')""")
rep("""await afterVenue();toast('Sala zapisana')});setTimeout""","""await afterVenue();toast('Sala zapisana')},!r);setTimeout""")
rep("if(!r||!confirm(`Usunąć salę „${r.name}”?${t.length?`\\nStoliki z tej sali (${t.length}) też zostaną usunięte.`:''}`))return;",
"if(!r||!confirm(`Czy na pewno chcesz usunąć salę „${r.name}”${t.length?` i wszystkie przypisane do niej stoliki (${t.length}: ${t.map(x=>x.label).join(', ')})`:''}?\\n\\nTej operacji nie można cofnąć.`))return;")
# 2: stolik – Usuń obok Zapisz
rep("""${r?`<button type="button" class="danger" style="margin-top:10px" onclick="deleteTable('${r.id}')">Usuń stolik</button>`:''}`,async()=>{const p={room_id""",
"""${r?`<div class="shiftModalActions"><button type="button" class="danger" onclick="deleteTable('${r.id}')">Usuń stolik</button><button type="submit" class="primary">Zapisz</button></div>`:''}`,async()=>{const p={room_id""")
rep("""await afterVenue();toast('Stolik zapisany')});setTimeout""","""await afterVenue();toast('Stolik zapisany')},!r);setTimeout""")
rep("if(!t||!confirm(`Usunąć stolik „${t.label}”?`))return;","if(!t||!confirm(`Czy na pewno chcesz usunąć stolik „${t.label}”?\\n\\nTej operacji nie można cofnąć.`))return;")
rep('Cafe Strych Manager <span>V5.0.3</span>','Cafe Strych Manager <span>V5.0.4</span>')
rep('Cafe Strych Manager <b>V5.0.3</b>','Cafe Strych Manager <b>V5.0.4</b>')
open(p,'w',encoding='utf-8').write(s); print('ok')
