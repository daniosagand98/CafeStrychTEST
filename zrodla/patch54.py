# V4.9 – zgłoszenia z 25.10: planowanie aktualności, czytelna lista rachunków, prostszy pulpit,
#        znaczek zgłoszeń przy „D” + powiadomienia push, ukrywanie kwot z menu konta, utarg dnia dla pracownika
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:120]!r}')
    s = s.replace(old, new)

# ---- stopka (bez wspominania o ukrywaniu kwot)
rep('<b>Cafe Strych Manager <span>V4.8</span></b>', '<b>Cafe Strych Manager <span>V4.9</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • Ukrywanie kwot dla administratora, podgląd na iPhonie i iPadzie</small>',
    '<small>Aktualizacja: 26.10.2026 • Planowanie aktualności, utarg dnia dla zespołu, powiadomienia o zgłoszeniach</small>')
rep('<p>Cafe Strych Manager <b>V4.8</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.9</b> • 26.10.2026</p>')

# ---- pulpit: bez „Pracownicy” i bez „Następna zmiana”
rep("""${P.schedule?`<div class="panel nextShiftPanel" style="margin-bottom:12px"><small class="muted">Następna zmiana</small><b>${nextShiftText()}</b></div>`:''}""", "")
rep("""<button class="kpi" onclick="employeesView()"><span>Pracownicy</span><strong>${state.employees.length}</strong><small>aktywnych</small></button>""", "")

# ---- lista otwartych rachunków: nazwa, numer, godzina i liczba sztuk jedno pod drugim
rep("""<button class="order" onclick="openOrder('${o.id}')"><div><b>${esc(o.customer_name||state.tables.find(t=>t.id===o.table_id)?.label||'Na wynos')}</b><small>${esc(o.order_no||'Rachunek')}</small><span class="statusPill">${statusLabel(o.status)}</span>${orderDiscount(o.id)?`<span class="statusPill discPill">−${pctTxt(orderDiscount(o.id))}</span>`:''}</div><strong>${money(orderTotal(o.id))}</strong></button>""",
    """<button class="order openOrderCard" onclick="openOrder('${o.id}')"><div class="ordTop"><b>${esc(o.customer_name||state.tables.find(t=>t.id===o.table_id)?.label||'Na wynos')}</b><small>${esc((o.order_no||'Rachunek').replace(/^\\d{1,2}\\.\\d{1,2}\\.\\d{4}\\s*•\\s*/,''))}${o.customer_name&&o.table_id&&state.tables.find(t=>t.id===o.table_id)?' • '+esc(state.tables.find(t=>t.id===o.table_id).label):''}</small></div><div class="ordMeta"><span>🕒 ${new Date(o.created_at).toLocaleTimeString('pl-PL',{hour:'2-digit',minute:'2-digit'})}</span><span>${orderItems(o.id).reduce((n,i)=>n+Number(i.qty||0),0)} szt.</span>${orderDiscount(o.id)?`<span class="discPill">−${pctTxt(orderDiscount(o.id))}</span>`:''}</div><strong>${money(orderTotal(o.id))}</strong></button>""")

# ---- utarg dnia: przycisk dla wszystkich, pracownik – dziś/wczoraj z bazy (do raportu)
rep("""${canManage()?'<button class="ghost" onclick="salesReport()">Utarg</button><button class="ghost" onclick="orderHistory()">Historia</button>':''}""",
    """<button class="ghost" onclick="salesReport()">Utarg</button>${canManage()?'<button class="ghost" onclick="orderHistory()">Historia</button>':''}""")
rep("window.salesReport=(date=iso(new Date()))=>{if(!canManage())return;", "window.salesReport=(date=iso(new Date()))=>{if(!canManage())return employeeSales(date);")
rep("const loadedDays=new Set();", r"""const PAY_L={card:'Karta',cash:'Gotówka',blik:'BLIK',transfer:'Przelew'};
window.employeeSales=async(date=iso(new Date()))=>{const td=iso(new Date()),yd=iso(new Date(Date.now()-864e5));if(![td,yd].includes(date))date=td;
 content().innerHTML=`<div class="toolbar inline"><div><button class="ghost" onclick="pos()">← POS</button><h2>Utarg dnia</h2><small class="muted">Do raportu na koniec zmiany</small></div></div><div class="segTabs"><button type="button" class="${date===td?'active':''}" onclick="employeeSales('${td}')">Dziś</button><button type="button" class="${date===yd?'active':''}" onclick="employeeSales('${yd}')">Wczoraj</button></div><div id="empSales"><div class="empty">Wczytuję…</div></div>`;
 const r=await sb.rpc('sales_day',{p_day:date}),box=$('#empSales');if(!box)return;
 if(r.error)return box.innerHTML=`<div class="empty">${/PGRST202|function|schema cache/i.test((r.error.code||'')+' '+r.error.message)?'Utarg dla zespołu będzie dostępny po aktualizacji bazy (sql/supabase_v4_7.sql).':isNetErr(r.error)?'Brak internetu – utarg wczyta się po powrocie połączenia.':esc(r.error.message)}</div>`;
 const rows=r.data||[],ok=rows.filter(p=>p.order_status!=='cancelled'),canc=rows.filter(p=>p.order_status==='cancelled'),sum=l=>l.reduce((n,p)=>n+Number(p.amount||0),0),by=m=>sum(ok.filter(p=>p.method===m)),dayTxt=cap(new Date(date+'T12:00').toLocaleDateString('pl-PL',{weekday:'long',day:'numeric',month:'long',year:'numeric'}));
 window._empReport=[`UTARG – ${dayTxt}`,`Razem: ${money(sum(ok))} (${ok.length} płatności)`,...Object.entries(PAY_L).map(([k,l])=>`${l}: ${money(by(k))}`),canc.length?`Anulowane (nie liczone): ${canc.length} • ${money(sum(canc))}`:'',`Wygenerowano: ${new Date().toLocaleString('pl-PL')} • ${state.profile?.full_name||''}`].filter(Boolean).join('\n');
 box.innerHTML=`<p class="muted" style="margin:0 0 8px">${dayTxt}</p><div class="salesKpis"><div class="kpi"><span>Razem</span><strong>${money(sum(ok))}</strong><small>${ok.length} płatności${canc.length?` • bez ${canc.length} anulowanych`:''}</small></div>${Object.entries(PAY_L).map(([k,l])=>`<div class="kpi"><span>${l}</span><strong>${money(by(k))}</strong></div>`).join('')}</div><div class="repBtns"><button class="ghost" onclick="copyEmpReport()">📋 Kopiuj raport</button><button class="ghost" onclick="print()">🖨 Drukuj</button></div><section class="panel" style="margin-top:12px"><h3>Płatności</h3><div class="salesTable">${rows.map(p=>`<div class="salesRow ${p.order_status==='cancelled'?'cancelled':''}"><div><b>${esc(p.order_name||'Rachunek')}${p.order_status==='cancelled'?' <span class="cancelPill">ANULOWANY</span>':''}</b><small class="muted">${new Date(p.created_at).toLocaleTimeString('pl-PL',{hour:'2-digit',minute:'2-digit'})} • ${PAY_L[p.method]||esc(p.method)}${Number(p.discount_pct)>0?` • rabat ${pctTxt(p.discount_pct)}`:''}</small></div><strong>${money(p.amount)}</strong></div>`).join('')||'<div class="empty">Brak płatności w tym dniu.</div>'}</div></section>`};
window.copyEmpReport=async()=>{try{await navigator.clipboard.writeText(window._empReport||'');toast('Raport skopiowany – wklej go np. w SMS lub e-mail')}catch{prompt('Skopiuj raport:',window._empReport||'')}};
const loadedDays=new Set();""")

# ---- znaczek liczby zgłoszeń na „D” + przycisk ukrywania kwot w menu konta
rep('<button id="adminMenu" class="hide" onclick="admin(\'overview\')">⚙️ Ustawienia</button>',
    '<button id="adminMenu" class="hide" onclick="admin(\'overview\')">⚙️ Ustawienia</button><button id="bugsMenu" class="hide" onclick="admin(\'bugs\')">🐞 Zgłoszenia błędów</button><button id="moneyMenu" class="hide" onclick="toggleHideMoney()">🙈 Ukryj kwoty</button>')
rep("function applyRole(){", r"""function updateBugBadge(){const real=state.profile?.role==='admin',n=real?state.bugs.filter(b=>bugStatus(b)!=='done').length:0,b=$('#menuBtn');if(b){if(n)b.dataset.bugs=n>99?'99+':n;else delete b.dataset.bugs}
 const bm=$('#bugsMenu');if(bm){bm.classList.toggle('hide',!real);bm.innerHTML=`🐞 Zgłoszenia błędów${n?` <em class="menuBadge">${n}</em>`:''}`}
 const mm=$('#moneyMenu');if(mm){mm.classList.toggle('hide',!real);mm.textContent=hideMoney()?'👁 Pokaż kwoty':'🙈 Ukryj kwoty'}}
function applyRole(){updateBugBadge();""")
rep("scheduleCache();toast(val?'Kwoty ukryte na Twoim koncie':'Kwoty widoczne');admin('overview')};",
    "scheduleCache();toast(val?'Kwoty ukryte na Twoim koncie':'Kwoty widoczne');$('#userMenu')?.classList.add('hide');updateBugBadge();if(state.inAdmin)admin(state.adminTab||'overview');else if(state.page)state.page();else view($('[data-view].active')?.dataset.view||'home')};")
# kliknięcie powiadomienia o zgłoszeniu → lista zgłoszeń
rep("function openFromUrl(url){try{const u=new URL(url,location.href),ds=u.searchParams.get('day');if(!ds||!state.user)return;",
    "function openFromUrl(url){try{const u=new URL(url,location.href),ds=u.searchParams.get('day');if(u.searchParams.get('bugs')&&state.user&&state.profile?.role==='admin')return admin('bugs');if(!ds||!state.user)return;")
rep("function handleLaunchUrl(){if(new URLSearchParams(location.search).get('day')){",
    "function handleLaunchUrl(){const q=new URLSearchParams(location.search);if(q.get('day')||q.get('bugs')){")

# ---- aktualności: „Pokaż od” / „Pokaż do”
rep("""<div class="formGrid"><div>${field('newsDate','Data wydarzenia (opcjonalnie)','date')}</div>""",
    """<div class="formGrid"><div>${field('newsFrom','Pokaż na stronie od (opcjonalnie)','datetime-local')}</div><div>${field('newsTo','Pokaż na stronie do (opcjonalnie)','datetime-local')}</div></div><p class="muted newsSchedHint">Puste „od” = od razu po zapisaniu. Puste „do” = bez końca. Np. koncert: od poniedziałku 10:00 do soboty 23:59.</p><div class="formGrid"><div>${field('newsDate','Data wydarzenia (opcjonalnie)','date')}</div>""")
rep("pinned:$('#newsPinned').checked,image_url,", "pinned:$('#newsPinned').checked,publish_at:dtIso($('#newsFrom').value),expire_at:dtIso($('#newsTo').value),image_url,")
rep("let z=await save(p);if(z.error&&/image_pos/.test(z.error.message)){",
    "if(p.publish_at&&p.expire_at&&p.expire_at<=p.publish_at)return alert('„Pokaż do” musi być później niż „Pokaż od”.');let z=await save(p);if(z.error&&/publish_at|expire_at/.test(z.error.message)){delete p.publish_at;delete p.expire_at;z=await save(p);if(!z.error)setTimeout(()=>alert('Zapisano, ale bez planowania – uruchom w Supabase plik sql/supabase_v4_7.sql.'),300)}if(z.error&&/image_pos/.test(z.error.message)){")
rep("$('#newsPinned').checked=!!r.pinned}bindFramer()},0)};", "$('#newsPinned').checked=!!r.pinned;$('#newsFrom').value=dtLocal(r.publish_at);$('#newsTo').value=dtLocal(r.expire_at)}bindFramer()},0)};")
rep("function newsCard(n){", r"""const dtIso=v=>v?new Date(v).toISOString():null,dtLocal=v=>{if(!v)return '';const d=new Date(v);return new Date(d-d.getTimezoneOffset()*6e4).toISOString().slice(0,16)},dtTxt=v=>new Date(v).toLocaleString('pl-PL',{weekday:'short',day:'numeric',month:'numeric',hour:'2-digit',minute:'2-digit'});
function newsState(n){const now=new Date();if(!n.published)return['','Ukryte'];if(n.publish_at&&new Date(n.publish_at)>now)return['sched',`⏰ Pojawi się ${dtTxt(n.publish_at)}`];if(n.expire_at&&new Date(n.expire_at)<=now)return['exp',`Zniknęło ${dtTxt(n.expire_at)}`];return['on',`Widoczne na stronie${n.expire_at?` do ${dtTxt(n.expire_at)}`:''}`]}
function newsCard(n){""")
rep("""<span class="newsPill ${n.published?'on':''}">${n.published?'Widoczne na stronie':'Ukryte'}</span>""",
    """<span class="newsPill ${newsState(n)[0]}">${newsState(n)[1]}</span>""")

# ---- CSS
rep('</style></head>', '''
/* V4.9 */
.kpis{grid-template-columns:repeat(auto-fit,minmax(150px,1fr))!important}
.openOrderCard{min-height:118px;gap:8px}.openOrderCard .ordTop b{display:block;font-size:17px;line-height:1.25;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.openOrderCard .ordTop small{display:block;margin-top:2px;font-size:12px;color:var(--muted)!important}
.ordMeta{display:flex;flex-wrap:wrap;gap:6px}.ordMeta span{padding:3px 8px;border-radius:999px;background:#fff1da0f;font-size:11.5px;color:var(--muted)}.ordMeta .discPill{background:#71c98a22;color:#b9f4c8}
.openOrderCard strong{font-size:20px}
#menuBtn{position:relative;overflow:visible}
#menuBtn[data-bugs]::after{content:attr(data-bugs);position:absolute;top:-5px;right:-5px;min-width:19px;height:19px;padding:0 5px;border-radius:10px;background:#e5484d;color:#fff;font:800 11px/19px system-ui;text-align:center;box-shadow:0 0 0 2px #1d100c}
.menuBadge{display:inline-block;margin-left:6px;min-width:18px;padding:0 5px;border-radius:9px;background:#e5484d;color:#fff;font:800 11px/18px system-ui;text-align:center;font-style:normal}
.newsPill.sched{background:#e0ad6726!important;color:#f0ca80!important}.newsPill.exp{background:#fff1da12!important;color:var(--muted)!important}
.newsSchedHint{margin:-4px 0 8px;font-size:12px}
.repBtns{display:flex;gap:8px;margin-top:10px}.repBtns button{flex:1}
@media print{nav,header,footer,.toolbar,.segTabs,.repBtns,#netBar{display:none!important}body,main{background:#fff!important;color:#000!important}.kpi,.panel,.salesRow{border:1px solid #999!important;background:#fff!important;color:#000!important}.kpi strong,.salesRow strong,.salesRow b{color:#000!important}}
</style></head>''')
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
