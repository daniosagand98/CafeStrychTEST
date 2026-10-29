import sys
p='zrodla/strona-szablon.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:80]}')
    s=s.replace(a,b)
rep('<p class="poHours" id="poHours"></p><div class="doneBtns"><button class="btn btn-ghostInk" type="button" data-close>Zamknij</button></div>',
'<p class="poHours" id="poHours"></p><div class="doneBtns"><button class="btn btn-ink" type="button" id="poBack" hidden>← Wróć</button><button class="btn btn-ghostInk" type="button" data-close>Zamknij</button></div>')
rep("$('#poHours').textContent=owner?","$('#poBack').hidden=!(owner&&wwwBookings);$('#poHours').textContent=owner?")
rep("if(!resForm.date.value||resForm.date.value<min||wed)resForm.date.value=isoDay(d);resDlg.showModal()}",
"if(!resForm.date.value||resForm.date.value<min||wed)resForm.date.value=isoDay(d);if(!resDlg.open)resDlg.showModal()}\n$('#poBack').addEventListener('click',()=>openReservation(false,'stolik'));")
rep('Strona v1.8.3 · aktualizacja 29.10.2026','Strona v1.8.4 · aktualizacja 29.10.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
