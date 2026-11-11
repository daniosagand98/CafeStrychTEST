import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
rep("toast('Rezerwacja odrzucona')};","toast('Rezerwacja odrzucona');setTimeout(()=>smsOffer(id,'reject'),250)};")
# tekst odmowy
rep("function smsHref(num,text){","""function smsRejectText(b){const d=new Date(b.start_at),day=d.toLocaleDateString('pl-PL',{weekday:'long',day:'numeric',month:'long'}),hr=d.toLocaleTimeString('pl-PL',{hour:'2-digit',minute:'2-digit'});
 return `Dzień dobry! Dziękujemy za chęć odwiedzenia Cafe Strych. Niestety na ${day}, godz. ${hr}, nie mamy już wolnych miejsc i nie możemy przyjąć rezerwacji. Bardzo przepraszamy – zapraszamy w innym terminie! W razie pytań: 58 620 30 38. Pozdrawiamy serdecznie, zespół Cafe Strych ☕`}
function smsHref(num,text){""")
rep("window.smsSend=id=>{const b=state.bookings.find(x=>x.id===id);if(!b)return;const num=smsNumber(bookPhoneOf(b));if(num.replace(/\\D/g,'').length<9)return alert('Brak poprawnego numeru telefonu w tej rezerwacji.');location.href=smsHref(num,smsText(b))};",
    "window.smsSend=(id,kind)=>{const b=state.bookings.find(x=>x.id===id);if(!b)return;const num=smsNumber(bookPhoneOf(b));if(num.replace(/\\D/g,'').length<9)return alert('Brak poprawnego numeru telefonu w tej rezerwacji.');location.href=smsHref(num,kind==='reject'?smsRejectText(b):smsText(b))};")
rep("window.smsOffer=id=>{const b=state.bookings.find(x=>x.id===id);if(!b)return;const tel=bookPhoneOf(b);\n modal('✓ Rezerwacja zatwierdzona',",
    "window.smsOffer=(id,kind)=>{const b=state.bookings.find(x=>x.id===id);if(!b)return;const tel=bookPhoneOf(b),rej=kind==='reject';\n modal(rej?'✕ Rezerwacja odrzucona':'✓ Rezerwacja zatwierdzona',")
rep("<div class=\"smsPreview\">${esc(smsText(b))}</div><button class=\"primary smsBtn\" type=\"button\" onclick=\"smsSend('${b.id}')\">📱 Wyślij SMS do ${esc(tel)}</button>",
    "<div class=\"smsPreview\">${esc(rej?smsRejectText(b):smsText(b))}</div><button class=\"primary smsBtn\" type=\"button\" onclick=\"smsSend('${b.id}','${rej?'reject':''}')\">📱 Wyślij SMS ${rej?'o odmowie ':''}do ${esc(tel)}</button>")
# formularz: SMS wg statusu
rep("location.href=smsHref(num,smsText({start_at:a.toISOString(),guests_count:+$('#bookGuests').value||0,whole_room:!!$('#bookWhole')?.checked,place_name:pl?.name||null}))};",
    "const bb={start_at:a.toISOString(),guests_count:+$('#bookGuests').value||0,whole_room:!!$('#bookWhole')?.checked,place_name:pl?.name||null};location.href=smsHref(num,$('#bookStatus')?.value==='rejected'?smsRejectText(bb):smsText(bb))};")
rep('Cafe Strych Manager <span>V5.6</span>','Cafe Strych Manager <span>V5.6.1</span>')
rep('Cafe Strych Manager <b>V5.6</b> • 06.11.2026','Cafe Strych Manager <b>V5.6.1</b> • 11.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
