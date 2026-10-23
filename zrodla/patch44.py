# V4.2 – czytelniejszy układ (Start pracownika, Rezerwacje, Grafik, karty) + utarg: miesiąc, rok, wybrany okres
#   python3 zrodla/patch44.py panel/index.html panel/index.html
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:110]!r}')
    s = s.replace(old, new)

# ---- stopka
rep('<b>Cafe Strych Manager <span>V4.1.1</span></b>', '<b>Cafe Strych Manager <span>V4.2</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • Poprawiony wygląd logowania, reset hasła, usuwanie produktów z menu, kadrowanie zdjęć</small>',
    '<small>Aktualizacja: 23.10.2026 • Czytelniejszy układ ekranów, utarg za miesiąc, rok i wybrany okres</small>')
rep('<p>Cafe Strych Manager <b>V4.1.1</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.2</b> • 23.10.2026</p>')

# ---- START PRACOWNIKA: nagłówek w jednej linii, dwa małe kafelki obok siebie, odstępy między komunikatami
rep("""content().innerHTML=`<div class="toolbar"><div><h2>Cześć, ${esc(state.profile?.full_name||'')}</h2><small class="muted">Panel pracownika</small></div>${moduleOn('schedule')?`<button class="ghost" onclick="${goAvail}">📅 Moja dyspozycyjność</button>`:''}</div><div class="grid two">${moduleOn('schedule')?`<section class="panel"><h3>Najbliższa zmiana</h3>${future[0]?`<strong>${future[0].shift_date}</strong><p>${future[0].start_time.slice(0,5)}–${future[0].end_time.slice(0,5)}</p>`:'<p class="muted">Brak zaplanowanej zmiany.</p>'}</section><section class="panel"><h3>Godziny w miesiącu</h3><strong class="total">${fmtH(h)}</strong></section>`:''}<section class="panel full"><h3>Komunikaty</h3>${employeeMessages().map(a=>employeeMessageCard(a)).join('')||'<p class="muted">Brak komunikatów.</p>'}</section></div>`}""",
    """const nx=future[0],nxDay=nx?shortDay(nx.shift_date):'';content().innerHTML=`<div class="toolbar inline"><div><h2>Cześć, ${esc((state.profile?.full_name||'').split(' ')[0])}</h2><small class="muted">Panel pracownika</small></div>${moduleOn('schedule')?`<button class="ghost btnSm" onclick="${goAvail}">📅 Dyspozycyjność</button>`:''}</div>${moduleOn('schedule')?`<div class="empStats"><button class="statTile" onclick="${allowed('schedule')?"view('schedule')":''}"><span>Najbliższa zmiana</span>${nx?`<b>${nxDay}</b><small>${nx.start_time.slice(0,5)}–${nx.end_time.slice(0,5)}</small>`:'<b class="none">Brak</b><small>nie masz zaplanowanej zmiany</small>'}</button><div class="statTile"><span>Godziny w miesiącu</span><b>${fmtH(h)}</b><small>${cap(m.toLocaleDateString('pl-PL',{month:'long'}))}</small></div></div>`:''}<section class="panel"><h3>Komunikaty</h3><div class="cards">${employeeMessages().map(a=>employeeMessageCard(a)).join('')||'<p class="muted">Brak komunikatów.</p>'}</div></section>`}""")

# ---- REZERWACJE i GRAFIK: tytuł + przycisk w jednej linii, nawigacja i tryb w jednym pasku
rep("""content().innerHTML=`<div class="toolbar"><div><h2>Rezerwacje</h2>""", """content().innerHTML=`<div class="toolbar inline"><div><h2>Rezerwacje</h2>""")
rep("""<button class="primary" onclick="bookingForm()">+ Rezerwacja</button></div><div class="navControls">""",
    """<button class="primary btnSm" onclick="bookingForm()">+ Rezerwacja</button></div><div class="calBar"><div class="navControls">""")
rep("""onclick="bookingMode('month')">Miesiąc</button></div>${state.bookingMode==='week'?""", """onclick="bookingMode('month')">Miesiąc</button></div></div>${state.bookingMode==='week'?""")
rep("""content().innerHTML=`<div class="toolbar"><div><h2>Grafik</h2>""", """content().innerHTML=`<div class="toolbar inline"><div><h2>Grafik</h2>""")
rep("""<div class="actions">${canManage()?'<button class="primary" onclick="shiftForm()">+ Dodaj zmianę</button>':'<button class="primary" onclick="availabilityForm()">+ Moja dyspozycyjność</button>'}</div></div>""",
    """${canManage()?'<button class="primary btnSm" onclick="shiftForm()">+ Zmiana</button>':'<button class="primary btnSm" onclick="availabilityForm()">+ Dyspozycyjność</button>'}</div>""")
rep("""<div class="navControls"><button class="ghost" onclick="moveSchedule(-1)">""", """<div class="calBar"><div class="navControls"><button class="ghost" onclick="moveSchedule(-1)">""")
rep("""onclick="scheduleMode('avail')">Dyspozycyjność</button></div>${mode==='week'""", """onclick="scheduleMode('avail')">Dyspozycyjność</button></div></div>${mode==='week'""")

# ---- UTARG: usunięcie starej, nieużywanej wersji (nadpisywanej przez późniejszą z anulowaniami)
a=s.find("window.salesReport=(date=iso(new Date()))=>{if(!canManage())return;const payments=");b=s.find("window.orderHistory=",a)
if a<0 or b<0: raise SystemExit('old salesReport not found')
s=s[:a]+s[b:]
# ---- UTARG: dzień + podsumowanie miesiąca / roku / wybranego okresu
rep("""<h2>Utarg dzienny</h2></div><div><label>Wybierz dzień</label><input type="date" value="${date}" onchange="salesReport(this.value)"></div></div><div class="salesKpis">""",
    """<h2>Utarg</h2></div></div><section class="panel salesPeriod"><div class="sectionHead"><h3>Podsumowanie</h3></div><div class="segTabs">${[['month','Miesiąc'],['year','Rok'],['range','Okres']].map(([k,l])=>`<button type="button" class="${SP.mode===k?'active':''}" onclick="salesPeriodMode('${k}')">${l}</button>`).join('')}</div><div class="periodPick">${SP.mode==='month'?`<input type="month" value="${SP.month}" onchange="SP.month=this.value;loadSalesPeriod()">`:SP.mode==='year'?`<select onchange="SP.year=+this.value;loadSalesPeriod()">${Array.from({length:6},(_,i)=>new Date().getFullYear()-i).map(y=>`<option ${y===SP.year?'selected':''}>${y}</option>`).join('')}</select>`:`<label>Od<input type="date" value="${SP.from}" onchange="SP.from=this.value;loadSalesPeriod()"></label><label>Do<input type="date" value="${SP.to}" onchange="SP.to=this.value;loadSalesPeriod()"></label>`}</div><div id="periodBox"><div class="empty">Liczę…</div></div></section><section class="panel salesDay"><div class="sectionHead"><h3>Dzień</h3><input type="date" value="${date}" onchange="salesReport(this.value)"></div><div class="salesKpis">""")
rep("""<div class="kpi"><span>Przelew</span><strong>${money(method('transfer'))}</strong></div></div><section class="panel"><h3>Płatności z wybranego dnia</h3><div class="salesTable">""",
    """<div class="kpi"><span>Przelew</span><strong>${money(method('transfer'))}</strong></div></div><h3 class="subH">Płatności z wybranego dnia</h3><div class="salesTable">""")
rep("""}).join('')||'<div class="empty">Brak płatności w tym dniu.</div>'}</div></section>`};""",
    r"""}).join('')||'<div class="empty">Brak płatności w tym dniu.</div>'}</div></section>`;loadSalesPeriod()};
const WD=['Nd','Pn','Wt','Śr','Cz','Pt','Sb'];function shortDay(ds){const d=new Date(ds+'T12:00');return `${WD[d.getDay()]} ${d.getDate()}.${String(d.getMonth()+1).padStart(2,'0')}`}
const SP=window.SP={mode:'month',month:iso(new Date()).slice(0,7),year:new Date().getFullYear(),from:iso(new Date(new Date().getFullYear(),new Date().getMonth(),1)),to:iso(new Date())};
window.salesPeriodMode=m=>{SP.mode=m;salesReport($('.salesDay input[type=date]')?.value||iso(new Date()))};
async function fetchPayments(a,b){let all=[];for(let i=0;;i+=1000){const r=await sb.from('pos_payments').select('amount,method,created_at,order_id,pos_orders(status)').gte('created_at',a.toISOString()).lt('created_at',b.toISOString()).order('created_at').range(i,i+999);if(r.error)throw r.error;all=all.concat(r.data||[]);if((r.data||[]).length<1000)break}return all.filter(p=>(p.pos_orders?.status??state.orders.find(o=>o.id===p.order_id)?.status)!=='cancelled')}
window.loadSalesPeriod=async()=>{const box=$('#periodBox');if(!box)return;let a,b,label,unit;
 if(SP.mode==='month'){const[y,m]=SP.month.split('-').map(Number);if(!y)return;a=new Date(y,m-1,1);b=new Date(y,m,1);label=cap(a.toLocaleDateString('pl-PL',{month:'long',year:'numeric'}));unit='day'}
 else if(SP.mode==='year'){a=new Date(SP.year,0,1);b=new Date(SP.year+1,0,1);label='Rok '+SP.year;unit='month'}
 else{if(!SP.from||!SP.to)return;a=new Date(SP.from+'T00:00');b=new Date(SP.to+'T00:00');b.setDate(b.getDate()+1);if(b<=a)return box.innerHTML='<div class="empty">Data „do” musi być po dacie „od”.</div>';label=`${a.toLocaleDateString('pl-PL')} – ${new Date(b-864e5).toLocaleDateString('pl-PL')}`;unit=(b-a)/864e5>62?'month':'day'}
 box.innerHTML='<div class="empty">Liczę…</div>';let rows;try{rows=await fetchPayments(a,b)}catch(e){return box.innerHTML=`<div class="empty">Nie udało się pobrać płatności: ${esc(e.message||'')}</div>`}
 const sum=l=>l.reduce((n,p)=>n+Number(p.amount||0),0),total=sum(rows),by=m=>sum(rows.filter(p=>p.method===m)),key=p=>unit==='day'?day(p.created_at):day(p.created_at).slice(0,7),groups={};rows.forEach(p=>{const k=key(p);groups[k]=(groups[k]||0)+Number(p.amount||0)});
 const days=new Set(rows.map(p=>day(p.created_at))).size,max=Math.max(1,...Object.values(groups)),keys=Object.keys(groups).sort().reverse();
 const lbl=k=>unit==='day'?shortDay(k):cap(new Date(k+'-15T12:00').toLocaleDateString('pl-PL',{month:'long'}));
 box.innerHTML=`<div class="periodHead"><span>${esc(label)}</span><strong>${money(total)}</strong><small>${rows.length} płatności • ${days} dni ze sprzedażą${days?` • średnio ${money(total/days)} / dzień`:''}</small></div><div class="methodRow">${[['card','Karta'],['cash','Gotówka'],['blik','BLIK'],['transfer','Przelew']].map(([k,l])=>`<div><span>${l}</span><b>${money(by(k))}</b></div>`).join('')}</div>${keys.length?`<h3 class="subH">${unit==='day'?'Dni':'Miesiące'}</h3><div class="barList ${keys.length>10?'clip':''}">${keys.map(k=>`<${unit==='day'?`button type="button" onclick="salesReport('${k}');scrollTo({top:$('.salesDay').offsetTop-10,behavior:'smooth'})"`:'div'} class="barRow"><span>${lbl(k)}</span><i style="--w:${(groups[k]/max*100).toFixed(1)}%"></i><b>${money(groups[k])}</b></${unit==='day'?'button':'div'}>`).join('')}</div>${keys.length>10?`<button type="button" class="ghost moreBtn" onclick="this.previousElementSibling.classList.remove('clip');this.remove()">Pokaż wszystkie (${keys.length})</button>`:''}`:'<div class="empty">Brak sprzedaży w tym okresie.</div>'}`};""")

# ---- „Następna zmiana”: pt 23.10 • 12:00–20:00 zamiast 2026-10-23
rep("return n?`${n.shift_date} • ${n.start_time.slice(0,5)}–${n.end_time.slice(0,5)}`:'Brak zaplanowanej zmiany'}","return n?`${shortDay(n.shift_date)} • ${n.start_time.slice(0,5)}–${n.end_time.slice(0,5)}`:'Brak zaplanowanej zmiany'}")
rep("$('#nextShift').textContent=n?`${n.shift_date} • ","$('#nextShift').textContent=n?`${shortDay(n.shift_date)} • ")
# ---- CSS
rep('</style></head>', '''
/* V4.2 – układ */
.toolbar.inline{flex-direction:row!important;align-items:center!important;justify-content:space-between;flex-wrap:nowrap}
.toolbar.inline>div{min-width:0}.toolbar.inline h2{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.toolbar.inline small{display:block;font-size:12px;line-height:1.35}
.btnSm{width:auto!important;flex:0 0 auto;padding:9px 13px!important;font-size:14px;border-radius:13px;white-space:nowrap}
.calBar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;margin-bottom:12px}
.calBar .navControls{display:flex;gap:5px;margin:0}.calBar .navControls button{width:auto;min-width:40px;height:38px;padding:0 12px}
.calBar .mode{display:flex;gap:0;margin:0;padding:3px;border-radius:13px;background:#fff1da0a;border:1px solid #fff1da18}
.calBar .mode button{width:auto;height:32px;padding:0 12px;border:0!important;background:transparent;border-radius:10px;font-size:14px}
.calBar .mode .active{background:#e0ad6726!important;color:var(--cream)}
.bookingDay .dayHead{margin-bottom:8px}.bookingDay .bookingCard+.bookingCard{margin-top:8px}.bookingDay>p.muted{margin:4px 0 2px}
.cards>.card{margin:0}
.empStats{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px}
.statTile{display:flex;flex-direction:column;align-items:flex-start;gap:2px;padding:12px 13px!important;border-radius:16px;background:#fff1da0a;border:1px solid #fff1da18;text-align:left;color:var(--cream);width:100%}
.statTile span{font-size:12px;color:var(--muted)}.statTile b{font-size:20px;color:#f0ca80;line-height:1.2}.statTile b.none{color:var(--cream);font-size:17px}.statTile small{font-size:12px;color:var(--muted)}
.messageCard .statusPill{grid-row:auto;grid-column:auto}
nav{background:#1d100c!important}
.calBar .mode button{color:var(--muted)}
/* utarg */
.segTabs{display:flex;padding:3px;border-radius:13px;background:#fff1da0a;border:1px solid #fff1da18;margin-bottom:10px}
.segTabs button{flex:1;height:34px;padding:0;border:0!important;background:transparent;border-radius:10px;font-size:14px;color:var(--muted)}.segTabs .active{background:#e0ad6726!important;color:var(--cream)}
.periodPick{display:flex;gap:8px;margin-bottom:12px}.periodPick>*{flex:1;min-width:0}.periodPick label{display:flex;flex-direction:column;gap:4px;font-size:12px;color:var(--muted)}
.periodHead{display:flex;flex-direction:column;gap:2px;padding:14px;border-radius:14px;background:linear-gradient(135deg,#e0ad6722,#e0ad670a);border:1px solid #e0ad6744}
.periodHead span{font-size:13px;color:var(--muted)}.periodHead strong{font-size:30px;color:#f0ca80;line-height:1.15}.periodHead small{font-size:12px;color:var(--muted)}
.methodRow{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:10px}
.methodRow div{padding:10px;border-radius:12px;background:#fff1da0a;border:1px solid #fff1da18}.methodRow span{display:block;font-size:11px;color:var(--muted)}.methodRow b{font-size:14px}
.subH{margin:16px 0 8px;font-size:15px}
.barList{display:grid;gap:4px}
.barRow{position:relative;display:grid;grid-template-columns:96px 1fr auto;align-items:center;gap:10px;width:100%;padding:7px 10px!important;border-radius:10px;background:#fff1da06;border:1px solid transparent;text-align:left;color:var(--cream);font-size:13px}
button.barRow:hover{border-color:#e0ad6744}
.barRow i{height:8px;border-radius:99px;background:#fff1da12;position:relative;overflow:hidden}.barRow i::after{content:'';position:absolute;inset:0;width:var(--w);border-radius:99px;background:linear-gradient(90deg,#c98a4b,#f0ca80)}
.barRow b{color:#f0ca80;font-size:13px;white-space:nowrap}
.barList.clip>.barRow:nth-child(n+11){display:none}.moreBtn{width:100%;margin-top:8px}
.salesDay{margin-top:12px}.salesDay .sectionHead input{width:auto;max-width:170px}.salesDay .salesKpis{margin:4px 0 0}
@media(max-width:700px){.salesDay .salesKpis{grid-template-columns:1fr 1fr}.salesDay .salesKpis .kpi:first-child{grid-column:1/-1}.salesDay .kpi{padding:10px}.salesDay .kpi strong{font-size:17px}
 .methodRow{grid-template-columns:1fr 1fr}.barRow{grid-template-columns:78px 1fr auto}}
</style></head>''')

open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
