import sys
p='zrodla/strona-szablon.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:70]}')
    s=s.replace(a,b)
rep(".eventCard p{margin:0 0 8px;color:var(--ink2);flex:1}",
".eventCard p{margin:0 0 8px;color:var(--ink2);flex:1}.evPrice{margin:0 0 6px;padding:14px 16px;border-radius:14px;background:rgba(201,147,86,.12);border:1px dashed rgba(122,74,38,.35)}.evPrice .epTot{display:flex;align-items:baseline;justify-content:space-between;gap:10px;font:600 15px/1.2 var(--sans)}.evPrice .epTot b{font:700 26px/1 var(--serif);color:var(--ink);white-space:nowrap}.evPrice ul{list-style:none;margin:8px 0 0;padding:0;font-size:14px;color:var(--ink2)}.evPrice li{display:flex;justify-content:space-between;gap:10px;padding:3px 0;border-top:1px solid rgba(122,74,38,.12)}.evPrice li span:last-child{font-weight:600;color:var(--ink);white-space:nowrap}.evPrice .epDep{margin-top:6px;font-size:13px;color:var(--ink2)}")
PR=lambda tot,use,fee,dep:f'<div class="evPrice"><div class="epTot"><span>Koszt rezerwacji</span><b>{tot} zł</b></div><ul><li><span>do wykorzystania na barze</span><span>{use} zł</span></li><li><span>opłata za rezerwację</span><span>{fee} zł</span></li></ul><div class="epDep">Zadatek przy rezerwacji: <b>{dep} zł</b> (bezzwrotny)</div></div>'
rep('Rezerwacja tylko telefonicznie u właścicielki.</p><button class="btn btn-ink btn-sm reserve" type="button" data-type="sala">',
'Rezerwacja tylko telefonicznie u właścicielki.</p>'+PR('1200','1000','200','400')+'<button class="btn btn-ink btn-sm reserve" type="button" data-type="sala">')
rep('Rezerwacja tylko telefonicznie u właścicielki.</p><button class="btn btn-gold btn-sm reserve" type="button" data-type="lokal">',
'Rezerwacja tylko telefonicznie u właścicielki.</p>'+PR('5000','4500','500','1000')+'<button class="btn btn-gold btn-sm reserve" type="button" data-type="lokal">')
rep('Strona v1.8.2 · aktualizacja 29.10.2026','Strona v1.8.3 · aktualizacja 29.10.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
