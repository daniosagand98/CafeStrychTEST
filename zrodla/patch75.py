import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
rep("Uwagi / telefon","Uwagi")
rep("""${r?`<button type="button" class="danger" style="margin-top:10px" onclick="deleteBooking('${r.id}')">Usuń rezerwację</button>`:''}`""",
    """${r?`<div class="bookActs"><button type="submit" class="primary">Zapisz</button><button type="button" class="ghost" onclick="smsFromForm()">📱 Wyślij SMS</button><button type="button" class="danger" onclick="deleteBooking('${r.id}')">Usuń</button></div>`:''}`""")
rep("setTimeout(()=>smsOffer(nb.id),250)});","setTimeout(()=>smsOffer(nb.id),250)},!r);")
rep("window.smsOffer=id=>{","""window.smsFromForm=()=>{const tel=$('#bookPhone')?.value.trim(),num=smsNumber(tel);if(num.replace(/\\D/g,'').length<9){alert('Wpisz numer telefonu gościa.');$('#bookPhone')?.focus();return}const a=new Date(`${$('#bookDate').value}T${$('#bookHour').value}`);if(isNaN(a))return alert('Wybierz datę i godzinę.');const pl=state.places.find(x=>x.id===$('#bookPlace')?.value);location.href=smsHref(num,smsText({start_at:a.toISOString(),guests_count:+$('#bookGuests').value||0,whole_room:!!$('#bookWhole')?.checked,place_name:pl?.name||null}))};
window.smsOffer=id=>{""")
rep("</style></head>",""".bookActs{display:grid;grid-template-columns:1.3fr 1.2fr 1fr;gap:8px;margin-top:14px}.bookActs button{min-height:50px;margin:0}
@media(max-width:420px){.bookActs{grid-template-columns:1fr 1fr}.bookActs button:first-child{grid-column:1/-1}}
</style></head>""")
rep('Cafe Strych Manager <span>V5.5</span>','Cafe Strych Manager <span>V5.5.1</span>')
rep('Cafe Strych Manager <b>V5.5</b> • 06.11.2026','Cafe Strych Manager <b>V5.5.1</b> • 06.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
