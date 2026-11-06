import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
# pole telefonu w formularzu
rep("""<div>${field('bookGuests','Liczba osób','number','min="1" max="200" required inputmode="numeric"')}</div></div>""",
    """<div>${field('bookGuests','Liczba osób','number','min="1" max="200" required inputmode="numeric"')}</div></div>${field('bookPhone','Telefon gościa (do SMS z potwierdzeniem)','tel','inputmode="tel" maxlength="20" autocomplete="off" placeholder="np. 600 100 200"')}""")
rep('<textarea id="bookNotes" maxlength="600" placeholder="np. tel. 600 100 200, urodziny, krzesełko dla dziecka">','<textarea id="bookNotes" maxlength="600" placeholder="np. urodziny, krzesełko dla dziecka">')
rep("notes:$('#bookNotes').value.trim()||null,booking_status:status};",
    "notes:[$('#bookPhone').value.trim()?'tel. '+$('#bookPhone').value.trim():'',stripTel($('#bookNotes').value)].filter(Boolean).join(' • ')||null,booking_status:status};")
rep("refreshPage();if(ret)bookingDay(iso(a));else closeModal();toast(status==='pending'?'Rezerwacja wysłana do zatwierdzenia':'Rezerwacja zapisana')});",
    "refreshPage();if(ret)bookingDay(iso(a));else closeModal();toast(status==='pending'?'Rezerwacja wysłana do zatwierdzenia':'Rezerwacja zapisana');if(!r&&status==='confirmed'&&z.data?.id&&bookPhoneOf(z.data))setTimeout(()=>smsOffer(z.data.id),250)});")
rep("$('#bookTitle').value=r.title||'';$('#bookTable').value=r.table_label||'';$('#bookNotes').value=r.notes||''}",
    "$('#bookTitle').value=r.title||'';$('#bookTable').value=r.table_label||'';$('#bookPhone').value=bookPhoneOf(r);$('#bookNotes').value=stripTel(r.notes)}")
# po zatwierdzeniu – SMS
rep("if(state.dayReturn&&$('#modal').open)bookingDay(state.dayReturn.ds);toast('Rezerwacja zatwierdzona')};",
    "if(state.dayReturn&&$('#modal').open)bookingDay(state.dayReturn.ds);toast('Rezerwacja zatwierdzona');setTimeout(()=>smsOffer(id),250)};")
JS=r"""
/* ---------- V5.5: SMS z potwierdzeniem rezerwacji ---------- */
const TEL_RE=/tel\.?\s*:?\s*(\+?\d[\d\s-]{6,}\d)/i;
function bookPhoneOf(b){const m=String(b?.notes||'').match(TEL_RE);return m?m[1].trim():''}
function stripTel(t){return String(t||'').replace(/(^|\s*•\s*)tel\.?\s*:?\s*\+?\d[\d\s-]{6,}\d/i,'').replace(/^\s*•\s*/,'').trim()}
function smsNumber(t){let d=String(t||'').replace(/[^\d+]/g,'');if(/^\d{9}$/.test(d))d='+48'+d;else if(/^48\d{9}$/.test(d))d='+'+d;else if(/^00/.test(d))d='+'+d.slice(2);return d}
function smsText(b){const d=new Date(b.start_at),day=d.toLocaleDateString('pl-PL',{weekday:'long',day:'numeric',month:'long'}),hr=d.toLocaleTimeString('pl-PL',{hour:'2-digit',minute:'2-digit'}),n=+b.guests_count||0,os=n===1?'osobę':n>=2&&n<=4?'osoby':'osób';
 return `Dzień dobry! Potwierdzamy rezerwację w Cafe Strych na ${day}, godz. ${hr}, dla ${n} ${os}${b.whole_room&&b.place_name?` (${b.place_name})`:''}. Czekamy na Państwa – Plac Kaszubski 7 (w podwórzu), Gdynia. W razie zmian prosimy o telefon: 58 620 30 38. Pozdrawiamy serdecznie, zespół Cafe Strych ☕`}
function smsHref(num,text){const ios=/iPhone|iPad|iPod|Macintosh/.test(navigator.userAgent)&&'ontouchend' in document;return `sms:${num}${ios?'&':'?'}body=${encodeURIComponent(text)}`}
window.smsSend=id=>{const b=state.bookings.find(x=>x.id===id);if(!b)return;const num=smsNumber(bookPhoneOf(b));if(num.replace(/\D/g,'').length<9)return alert('Brak poprawnego numeru telefonu w tej rezerwacji.');location.href=smsHref(num,smsText(b))};
window.smsOffer=id=>{const b=state.bookings.find(x=>x.id===id);if(!b)return;const tel=bookPhoneOf(b);
 modal('✓ Rezerwacja zatwierdzona',`<div class="cancelInfo"><b>${esc(b.title||'Gość')} • ${b.guests_count||'?'} os.</b><span>${cap(new Date(b.start_at).toLocaleDateString('pl-PL',{weekday:'long',day:'numeric',month:'long'}))}, ${new Date(b.start_at).toLocaleTimeString('pl-PL',{hour:'2-digit',minute:'2-digit'})}</span></div>${tel?`<p class="muted" style="margin:10px 0 6px">Treść SMS-a (możesz ją jeszcze zmienić w telefonie):</p><div class="smsPreview">${esc(smsText(b))}</div><button class="primary smsBtn" type="button" onclick="smsSend('${b.id}')">📱 Wyślij SMS do ${esc(tel)}</button>`:`<p class="muted">W rezerwacji nie ma numeru telefonu – dopisz go w polu „Telefon gościa”, a potem wyślesz SMS z poziomu rezerwacji.</p><button class="ghost smsBtn" type="button" onclick="closeModal();bookingForm('${b.id}')">Dodaj numer telefonu</button>`}`,null,false)};
"""
rep("\nfunction openFromUrl(url){",JS+"\nfunction openFromUrl(url){")
rep("</style></head>",""".smsPreview{padding:12px 14px;border-radius:14px;background:#ffffff0d;border:1px solid var(--line);font-size:14px;line-height:1.45;white-space:pre-wrap}
.smsBtn{width:100%;margin-top:12px;min-height:50px;font-size:16px}
</style></head>""")
rep('Cafe Strych Manager <span>V5.4.2</span>','Cafe Strych Manager <span>V5.5</span>')
rep('Cafe Strych Manager <b>V5.4.2</b> • 06.11.2026','Cafe Strych Manager <b>V5.5</b> • 06.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
