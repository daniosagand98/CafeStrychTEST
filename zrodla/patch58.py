import sys
p='zrodla/strona-szablon.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:70]}')
    s=s.replace(a,b)
rep("phone:'+48 58 620 30 38'","phone:'+48 58 620 30 38',ownerPhone:'693 971 009'")
rep('<p class="poLead">Obecnie rezerwacje przyjmujemy <b>tylko telefonicznie</b>.</p>','<p class="poLead" id="poLead">Obecnie rezerwacje przyjmujemy <b>tylko telefonicznie</b>.</p>')
rep("function showPhoneOnly(){const tel=CONFIG.phone.replace(/\\s/g,'');$('#poPhone').textContent=CONFIG.phone;$('#poPhone').href='tel:'+tel;$('#poHours').textContent='Zadzwoń w godzinach otwarcia lokalu.';",
"function showPhoneOnly(kind){const owner=kind==='sala'||kind==='lokal',num=owner?CONFIG.ownerPhone:CONFIG.phone,tel=(owner?'+48':'')+num.replace(/\\s/g,'');$('#poPhone').textContent=owner?'+48 '+num:num;$('#poPhone').href='tel:'+tel;$('#poLead').innerHTML=owner?(kind==='sala'?'Rezerwację <b>sali</b> (do 20 osób)':'Rezerwację <b>całego lokalu</b> (do 40 osób)')+' przyjmuje <b>właścicielka – tylko telefonicznie</b>.':'Obecnie rezerwacje przyjmujemy <b>tylko telefonicznie</b>.';$('#poHours').textContent=owner?'Zadzwoń bezpośrednio pod ten numer – obsługa lokalu nie przyjmuje rezerwacji sali ani całego lokalu.':'Zadzwoń w godzinach otwarcia lokalu.';")
rep("$('#resTitle').textContent='Rezerwacje telefoniczne';$('#resDlg .dlgIn').classList.add('isDone')}",
"$('#resTitle').textContent=owner?(kind==='sala'?'Rezerwacja sali':'Rezerwacja całego lokalu'):'Rezerwacje telefoniczne';$('#resDlg .dlgIn').classList.add('isDone')}")
rep("function openReservation(wed=false,kind='stolik'){$('#resPhone').hidden=true;if(!wwwBookings){",
"function openReservation(wed=false,kind='stolik'){$('#resPhone').hidden=true;if(kind==='sala'||kind==='lokal'){$('#newsDlg').open&&$('#newsDlg').close();showPhoneOnly(kind);resDlg.showModal();return}if(!wwwBookings){")
rep('<option value="sala">Sala</option><option value="lokal">Cały lokal (impreza zamknięta)</option>','<option value="sala">Sala (tylko telefonicznie)</option><option value="lokal">Cały lokal (tylko telefonicznie)</option>')
rep("resForm.kind.addEventListener('change',()=>setKind(resForm.kind.value));",
"resForm.kind.addEventListener('change',()=>{const k=resForm.kind.value;if(k==='sala'||k==='lokal'){setKind('stolik');showPhoneOnly(k)}else setKind(k)});")
rep('<p>Osobna sala dla Twojej grupy – na urodziny, imieniny, spotkanie po latach czy firmowe.</p><button class="btn btn-ink btn-sm reserve" type="button" data-type="sala">Zapytaj o salę <span class="arr">→</span></button>',
'<p>Osobna sala dla Twojej grupy (do 20 osób) – na urodziny, imieniny, spotkanie po latach czy firmowe. Rezerwacja tylko telefonicznie u właścicielki.</p><button class="btn btn-ink btn-sm reserve" type="button" data-type="sala">Zadzwoń w sprawie sali <span class="arr">→</span></button>')
rep('<p>Strych tylko dla Was – impreza zamknięta, wesele w kameralnym gronie, event lub sesja zdjęciowa.</p><button class="btn btn-gold btn-sm reserve" type="button" data-type="lokal">Zapytaj o lokal <span class="arr">→</span></button>',
'<p>Strych tylko dla Was (do 40 osób) – impreza zamknięta, wesele w kameralnym gronie, event lub sesja zdjęciowa. Rezerwacja tylko telefonicznie u właścicielki.</p><button class="btn btn-gold btn-sm reserve" type="button" data-type="lokal">Zadzwoń w sprawie lokalu <span class="arr">→</span></button>')
rep('Strona v1.8.1 · aktualizacja 29.10.2026','Strona v1.8.2 · aktualizacja 29.10.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
