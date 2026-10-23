# V4.3 – dyspozycyjność w godzinach, czytelna nawigacja tygodnia/miesiąca, opisy w utargu, szybszy POS
#   python3 zrodla/patch45.py panel/index.html panel/index.html   (szybki POS: sql/supabase_v4_2.sql – bez niego działa po staremu)
import sys, re
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:110]!r}')
    s = s.replace(old, new)

# ---- stopka
rep('<b>Cafe Strych Manager <span>V4.2</span></b>', '<b>Cafe Strych Manager <span>V4.3</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • Czytelniejszy układ ekranów, utarg za miesiąc, rok i wybrany okres</small>',
    '<small>Aktualizacja: 23.10.2026 • Niedostępność w godzinach, czytelna nawigacja tygodni, szybszy POS</small>')
rep('<p>Cafe Strych Manager <b>V4.2</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.3</b> • 23.10.2026</p>')

# =============== 1. DYSPOZYCYJNOŚĆ: niedostępny w wybranych godzinach ===============
rep("""<label>Status</label><select id="avStatus" onchange="$('#avTimes').classList.toggle('hide',this.value!=='available')"><option value="available">Dostępny</option><option value="unavailable" ${a?.status==='unavailable'?'selected':''}>Niedostępny</option></select></div></div><div id="avTimes" class="formGrid timePair ${a?.status==='unavailable'?'hide':''}"><div>${field('avFrom','Od','time',`value="${a?.start_time?.slice(0,5)||'14:00'}"`)}</div><div>${field('avTo','Do','time',`value="${a?.end_time?.slice(0,5)||'23:00'}"`)}</div></div>""",
    """<label>Status</label><select id="avStatus" onchange="avStatusChange(this.value)"><option value="available">Dostępny w godzinach</option><option value="partial" ${avKind(a)==='partial'?'selected':''}>Niedostępny w godzinach</option><option value="unavailable" ${avKind(a)==='unavailable'?'selected':''}>Niedostępny cały dzień</option></select></div></div><p class="avHint muted" id="avHint">${AV_HINT[avKind(a)||'available']}</p><div id="avTimes" class="formGrid timePair ${avKind(a)==='unavailable'?'hide':''}"><div>${field('avFrom','Od','time',`value="${a?.start_time?.slice(0,5)||(avKind(a)==='partial'?'12:00':'14:00')}"`)}</div><div>${field('avTo','Do','time',`value="${a?.end_time?.slice(0,5)||(avKind(a)==='partial'?'16:00':'23:00')}"`)}</div></div>""")
rep("""const e=employee(),ok=$('#avStatus').value==='available',payload={user_id:state.user.id,employee_id:e?.id||null,work_date:$('#avDate').value,start_time:ok?$('#avFrom').value:null,end_time:ok?$('#avTo').value:null,status:$('#avStatus').value};if(!payload.work_date)return alert('Wybierz datę.');""",
    """const e=employee(),k=$('#avStatus').value,ok=k!=='unavailable',payload={user_id:state.user.id,employee_id:e?.id||null,work_date:$('#avDate').value,start_time:ok?$('#avFrom').value:null,end_time:ok?$('#avTo').value:null,status:k==='available'?'available':'unavailable'};if(!payload.work_date)return alert('Wybierz datę.');if(ok&&(!payload.start_time||!payload.end_time))return alert('Wpisz godziny od–do.');if(ok&&payload.start_time===payload.end_time)return alert('Godzina „od” i „do” nie mogą być takie same.');""")
rep("function availText(a){return a?(a.status==='available'?`✓ ${a.start_time?a.start_time.slice(0,5)+'–'+(a.end_time||'').slice(0,5):'cały dzień'}`:'✗ niedostępny'):'–'}",
    """const AV_HINT={available:'Podaj godziny, w których możesz pracować.',partial:'Podaj godziny, w których NIE możesz pracować – poza nimi jesteś dostępny.',unavailable:'Tego dnia nie możesz pracować.'};
function avKind(a){return !a?'':a.status==='available'?'available':a.start_time?'partial':'unavailable'}
window.avStatusChange=v=>{$('#avTimes').classList.toggle('hide',v==='unavailable');$('#avHint').textContent=AV_HINT[v];if(v==='partial'&&$('#avFrom').value==='14:00'&&$('#avTo').value==='23:00'){$('#avFrom').value='12:00';$('#avTo').value='16:00'}};
function availText(a){const t=x=>`${x.start_time.slice(0,5)}–${(x.end_time||'').slice(0,5)}`;return a?(a.status==='available'?`✓ ${a.start_time?t(a):'cały dzień'}`:a.start_time?`✗ niedostępny ${t(a)}`:'✗ niedostępny'):'–'}""")
rep("function availCls(a){return a?(a.status==='available'?'yes':'no'):''}",
    "function availCls(a){return a?(a.status==='available'?'yes':a.start_time?'part':'no'):''}")
# przy układaniu zmian: częściowo niedostępny też do wybrania (bez podpowiadania jego „zakazanych” godzin)
rep("""${has?'<span class="statusPill">w grafiku</span>':a?.status!=='unavailable'?`<button type="button" class="ghost" onclick="prefillShift('${e.id}','${(a?.start_time||'').slice(0,5)}','${(a?.end_time||'').slice(0,5)}')">Wybierz</button>`""",
    """${has?'<span class="statusPill">w grafiku</span>':avKind(a)!=='unavailable'?`<button type="button" class="ghost" onclick="prefillShift('${e.id}','${avKind(a)==='available'?(a?.start_time||'').slice(0,5):''}','${avKind(a)==='available'?(a?.end_time||'').slice(0,5):''}')">Wybierz</button>`""")

# =============== 2. NAWIGACJA: ‹ 19–25 paź 2026 › zamiast ‹ Dziś › ===============
rep("""function schedule(){""", r"""function periodLabel(month,w,m){if(month)return cap(m.toLocaleDateString('pl-PL',{month:'long',year:'numeric'}));const e=new Date(w);e.setDate(w.getDate()+6);const mo=d=>d.toLocaleDateString('pl-PL',{month:'short'}).replace('.','');return w.getMonth()===e.getMonth()?`${w.getDate()}–${e.getDate()} ${mo(e)} ${e.getFullYear()}`:`${w.getDate()} ${mo(w)} – ${e.getDate()} ${mo(e)} ${e.getFullYear()}`}
function periodNav(fn,month,w,m){const now=new Date(),cur=month?(m.getFullYear()===now.getFullYear()&&m.getMonth()===now.getMonth()):iso(w)===iso(startWeek(now)),what=month?'miesiąc':'tydzień',dif=month?(m.getFullYear()-now.getFullYear())*12+m.getMonth()-now.getMonth():Math.round((w-startWeek(now))/6048e5),rel=cur?`ten ${what}`:dif===-1?(month?'poprzedni miesiąc':'poprzedni tydzień'):dif===1?(month?'następny miesiąc':'następny tydzień'):'';
 return `<div class="periodNav"><button type="button" class="ghost pnArrow" onclick="${fn}(-1)" aria-label="Poprzedni ${what}">‹</button><div class="pnLabel"><b>${periodLabel(month,w,m)}</b>${rel?`<small>${rel}</small>`:''}${cur?'':`<button type="button" class="pnToday" onclick="${fn}(0)">↺ Dziś</button>`}</div><button type="button" class="ghost pnArrow" onclick="${fn}(1)" aria-label="Następny ${what}">›</button></div>`}
function schedule(){""")
rep("""<div class="calBar"><div class="navControls"><button class="ghost" onclick="moveBookings(-1)">‹</button><button class="ghost" onclick="moveBookings(0)">Dziś</button><button class="ghost" onclick="moveBookings(1)">›</button></div>""",
    """<div class="calBar">${periodNav('moveBookings',state.bookingMode==='month',w,m)}""")
rep("""<div class="calBar"><div class="navControls"><button class="ghost" onclick="moveSchedule(-1)">‹</button><button class="ghost" onclick="moveSchedule(0)">Dziś</button><button class="ghost" onclick="moveSchedule(1)">›</button></div>""",
    """<div class="calBar">${periodNav('moveSchedule',mode==='month',d,state.month)}""")
rep("""<small class="muted">${state.bookingMode==='week'?`Tydzień od ${w.toLocaleDateString('pl-PL')}`:cap(m.toLocaleDateString('pl-PL',{month:'long',year:'numeric'}))} • kliknij dzień, aby go otworzyć</small>""",
    """<small class="muted">Kliknij dzień, aby go otworzyć</small>""")
rep("""<small class="muted">${mode==='week'?'Tydzień':mode==='month'?'Miesiąc':'Dyspozycyjność'} • kliknij dzień, aby go otworzyć</small>""",
    """<small class="muted">Kliknij dzień, aby go otworzyć</small>""")

# =============== 3. UTARG: jasne opisy, dzień z dowolnej daty ===============
rep("""<small>${rows.length} płatności • ${days} dni ze sprzedażą${days?` • średnio ${money(total/days)} / dzień`:''}</small>""",
    """<small>${rows.length} płatności${days?` • sprzedaż w ${days} ${days===1?'dniu':'dniach'} • średnio ${money(total/days)} dziennie`:''}</small>""")
rep("""<h3 class="subH">${unit==='day'?'Dni':'Miesiące'}</h3>""",
    """<h3 class="subH">${unit==='day'?'Sprzedaż w poszczególnych dniach':'Sprzedaż w poszczególnych miesiącach'}</h3>${unit==='day'?'<p class="subHint">Kliknij dzień, aby zobaczyć jego płatności poniżej.</p>':''}""")
rep("""<h3 class="subH">Płatności z wybranego dnia</h3>""", """<h3 class="subH">Płatności z tego dnia</h3>""")
# płatności starszych dni dociągane z bazy (na urządzeniu jest tylko ostatnie 500)
rep("""window.salesReport=(date=iso(new Date()))=>{if(!canManage())return;""",
    """const loadedDays=new Set();
async function ensureSalesDay(date){if(loadedDays.has(date))return;loadedDays.add(date);const a=new Date(date+'T00:00'),b=new Date(a);b.setDate(b.getDate()+1);
 const r=await sb.from('pos_payments').select('*,pos_orders(*)').gte('created_at',a.toISOString()).lt('created_at',b.toISOString()).order('created_at');if(r.error){loadedDays.delete(date);return}
 (r.data||[]).forEach(p=>{const o=p.pos_orders;delete p.pos_orders;if(!state.payments.some(x=>x.id===p.id))state.payments.push(p);if(o&&!state.orders.some(x=>x.id===o.id))state.orders.push(o)});
 const ids=(r.data||[]).map(p=>p.order_id).filter(id=>!state.orderItems.some(i=>i.order_id===id));if(ids.length)state.orderItems.push(...await loadOrderItems([...new Set(ids)]));
 if($('.salesDay input[type=date]')?.value===date)salesReport(date)}
window.salesReport=(date=iso(new Date()))=>{if(!canManage())return;{const old=state.payments.reduce((x,p)=>{const d=day(p.created_at);return d<x?d:x},'9999-99-99');if(date<old&&!loadedDays.has(date))ensureSalesDay(date)}""")
# podsumowanie okresu nie liczy się od nowa przy każdym kliknięciu dnia
rep("""window.loadSalesPeriod=async()=>{const box=$('#periodBox');if(!box)return;let a,b,label,unit;""",
    """let periodCache={key:'',html:''};
window.loadSalesPeriod=async()=>{const box=$('#periodBox');if(!box)return;const ck=JSON.stringify(SP)+':'+state.payments.length;if(periodCache.key===ck){box.innerHTML=periodCache.html;return}let a,b,label,unit;""")
rep("""<div class="empty">Brak sprzedaży w tym okresie.</div>'}`};""",
    """<div class="empty">Brak sprzedaży w tym okresie.</div>'}`;periodCache={key:ck,html:box.innerHTML}};""")

# =============== 4. POS: natychmiastowa reakcja, mniej zapytań ===============
# 4a. dodawanie / + / − / usuwanie: od razu na ekranie, zapis w tle (jedno zapytanie dzięki SQL v4.2)
old_add = s[s.find("window.addItem=(oid,mid)=>enqueue("):s.find("window.orderStatus=")]
if not old_add or 'window.removeItem' not in old_add: raise SystemExit('POS item functions not found')
s = s.replace(old_add, r"""let posBusy=0,rpcOK=true;
function localBump(oid,mid,lineId,delta){let line=lineId?state.orderItems.find(x=>x.id===lineId):state.orderItems.find(x=>x.order_id===oid&&x.menu_item_id===mid);
 if(line){line.qty=Number(line.qty)+delta;if(line.qty<=0)state.orderItems=state.orderItems.filter(x=>x!==line);return}
 if(delta>0&&mid){const m=state.menu.find(x=>x.id===mid);if(m)state.orderItems.push({id:'tmp-'+Date.now()+'-'+Math.random().toString(36).slice(2,7),order_id:oid,menu_item_id:mid,item_name:m.name,qty:delta,unit_price:m.price,tax_rate:m.tax_rate??23,created_at:new Date().toISOString()})}}
async function syncBump(oid,mid,lineId,delta){
 if(rpcOK){const r=mid?await sb.rpc('pos_bump_item',{p_order:oid,p_menu:mid,p_delta:delta}):await sb.rpc('pos_bump_line',{p_item:lineId,p_delta:delta});if(!r.error)return null;if(/PGRST202|function|schema cache/i.test((r.error.code||'')+' '+(r.error.message||'')))rpcOK=false;else return r.error}
 // bez SQL v4.2 – stary sposób (odczyt + zapis)
 const cur=mid?await sb.from('pos_order_items').select('id,qty').eq('order_id',oid).eq('menu_item_id',mid).limit(1):await sb.from('pos_order_items').select('id,qty').eq('id',lineId).limit(1);if(cur.error)return cur.error;const old=cur.data?.[0];
 if(!old){if(delta<=0||!mid)return null;const m=state.menu.find(x=>x.id===mid);if(!m)return{message:'Tego produktu nie ma już w menu.'};return(await sb.from('pos_order_items').insert({order_id:oid,menu_item_id:mid,item_name:m.name,qty:delta,unit_price:m.price,tax_rate:m.tax_rate??23})).error}
 const q=Number(old.qty)+delta;return(await(q>0?sb.from('pos_order_items').update({qty:q}).eq('id',old.id):sb.from('pos_order_items').delete().eq('id',old.id))).error}
function posChange(oid,mid,lineId,delta){localBump(oid,mid,lineId,delta);rerenderOrder(oid);posBusy++;$('#ticket')?.classList.add('syncing');
 enqueue(async()=>{let err=null;try{err=await syncBump(oid,mid,lineId,delta)}catch(e){err=e}posBusy--;if(err)alert('Nie udało się zapisać zmiany na rachunku:\n'+(err.message||err)+'\n\nRachunek zostanie odświeżony.');if(!posBusy||err){await refreshOrder(oid);$('#ticket')?.classList.remove('syncing')}})}
const lineOf=id=>state.orderItems.find(x=>x.id===id);
window.addItem=(oid,mid)=>{const m=state.menu.find(x=>x.id===mid);if(!m)return;posChange(oid,mid,null,1);toast(`+1 ${m.name}`)};
window.incItem=(itemId,oid)=>{const l=lineOf(itemId);if(!l)return;posChange(oid,l.menu_item_id,l.menu_item_id?null:itemId,1)};
window.decItem=(itemId,oid)=>{const l=lineOf(itemId);if(!l)return;posChange(oid,l.menu_item_id,l.menu_item_id?null:itemId,-1)};
window.removeItem=(itemId,oid)=>{const l=lineOf(itemId);if(!l||!confirm(`Usunąć całą pozycję „${l.item_name}” (${l.qty} szt.)?`))return;posChange(oid,l.menu_item_id,l.menu_item_id?null:itemId,-Number(l.qty))};
""")
rep("async function refreshOrder(oid){const rows=await safe('pos_order_items',q=>q.select('*').eq('order_id',oid));state.orderItems=state.orderItems.filter(x=>x.order_id!==oid).concat(rows);rerenderOrder(oid)}",
    "async function refreshOrder(oid){if(posBusy)return;const rows=await safe('pos_order_items',q=>q.select('*').eq('order_id',oid));if(posBusy)return;state.orderItems=state.orderItems.filter(x=>x.order_id!==oid).concat(rows);if($('#menuGrid')?.dataset.order===oid)rerenderOrder(oid)}")
# 4b. tylko dane POS zamiast całej aplikacji (płatność, nowy rachunek, edycja, zmiany z innych urządzeń)
rep("async function loadOrderItems(ids){const out=[];for(let i=0;i<ids.length;i+=80){out.push(...await safe('pos_order_items',q=>q.select('*').in('order_id',ids.slice(i,i+80))))}return out}",
    "async function loadOrderItems(ids){const parts=[];for(let i=0;i<ids.length;i+=80)parts.push(safe('pos_order_items',q=>q.select('*').in('order_id',ids.slice(i,i+80))));return (await Promise.all(parts)).flat()}\n"
    "async function loadPos(){const[o,p]=await Promise.all([safe('pos_orders',q=>q.select('*').order('created_at',{ascending:false}).limit(400)),canManage()?safe('pos_payments',q=>q.select('*').order('created_at',{ascending:false}).limit(500)):Promise.resolve(state.payments)]);const items=await loadOrderItems(o.map(x=>x.id));state.orders=o;state.payments=p;state.orderItems=items}")
pay_start = s.find("window.pay=id=>modal(");pay_end = s.find("window.orderHistory=", pay_start)
pay = s[pay_start:pay_end]
if pay.count('await loadAll()') != 3: raise SystemExit('pay(): expected 3 loadAll, got %d' % pay.count('await loadAll()'))
pay = pay.replace("async()=>{await loadAll();", "async()=>{const sv=$('#modalSave');if(sv){sv.disabled=true;sv.textContent='Zapisywanie…'}await posQueue;await loadPos();if(sv){sv.disabled=false;sv.textContent='Zapisz'}", 1).replace("await loadAll()", "await loadPos()")
s = s[:pay_start] + pay + s[pay_end:]
rep("if(r.error)return alert(r.error.message);closeModal();await loadAll();openOrder(r.data.id)});",
    "if(r.error)return alert(r.error.message);closeModal();state.orders.unshift(r.data);openOrder(r.data.id)});")
rep("if(r.error)return alert(r.error.message);closeModal();await loadAll();openOrder(id);toast('Rachunek zaktualizowany')",
    "if(r.error)return alert(r.error.message);closeModal();await loadPos();openOrder(id);toast('Rachunek zaktualizowany')")
# 4c. zmiany z innych urządzeń: przy zmianach w POS pobieramy tylko POS; podczas klikania nie przerywamy
rep("let reloadTimer;function live(){clearTimeout(reloadTimer);reloadTimer=setTimeout(async()=>{await loadAll();",
    "let reloadTimer;const liveDirty=new Set(),POS_T=['pos_orders','pos_order_items','pos_payments'];function live(t){if(typeof t==='string')liveDirty.add(t);else liveDirty.add('*');clearTimeout(reloadTimer);reloadTimer=setTimeout(async()=>{if(posBusy){reloadTimer=null;return live(t)}const onlyPos=[...liveDirty].every(x=>POS_T.includes(x));liveDirty.clear();if(onlyPos)await loadPos();else await loadAll();if(posBusy)return;")
rep("'site_news','bug_reports','site_social_posts','cafe_settings'].forEach(t=>sb.channel('cs-'+t).on('postgres_changes',{event:'*',schema:'public',table:t},live).subscribe());",
    "'site_news','bug_reports','site_social_posts','cafe_settings'].forEach(t=>sb.channel('cs-'+t).on('postgres_changes',{event:'*',schema:'public',table:t},()=>live(t)).subscribe());")

# ---- otwarty rachunek: w dolnym menu podświetlony POS
rep("window.openOrder=id=>{const o=state.orders.find(x=>x.id===id);if(!o)return;","window.openOrder=id=>{const o=state.orders.find(x=>x.id===id);if(!o)return;$$('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view==='pos'));")
# ---- CSS
rep('</style></head>', '''
/* V4.3 */
.calBar{flex-direction:column;align-items:stretch}
.periodNav{display:grid;grid-template-columns:44px minmax(0,1fr) 44px;align-items:center;gap:6px;padding:4px;border-radius:15px;background:#fff1da0a;border:1px solid #fff1da18}
.pnArrow{width:44px!important;height:44px;padding:0!important;font-size:22px;border-radius:12px}
.pnLabel{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:44px;text-align:center;line-height:1.2}
.pnLabel b{font-size:16px}.pnLabel small{font-size:11px;color:var(--muted)}
.pnToday{width:auto!important;margin-top:3px;padding:2px 10px!important;border-radius:999px;background:#e0ad6722!important;border:1px solid #e0ad6755!important;color:#f0ca80;font-size:11px;font-weight:800}
.calBar .mode{width:100%}.calBar .mode button{flex:1}
.av.part,.availRow.part>span:nth-child(2){color:#ffcf8a}.availRow.part{border-color:#ffcf8a44}.av.part{background:#ffcf8a10}
.avHint{margin:2px 0 8px;font-size:12px}
.subHint{margin:-4px 0 8px;font-size:12px;color:var(--muted)}
.ticket.syncing .ticketHead strong::after{content:' ⟳';font-size:12px;opacity:.7}
.salesRow b{margin-right:6px}
</style></head>''')

open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
