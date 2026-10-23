# V4.6 – POS odporny na brak internetu i zanik prądu
#  • każda zmiana na rachunku (dodanie/±/usunięcie pozycji, nowy rachunek, płatność) trafia najpierw do
#    „skrzynki” w pamięci telefonu (localStorage) i dopiero potem do bazy – nic nie ginie przy zerwaniu sieci,
#    zamknięciu aplikacji ani zaniku prądu; po powrocie internetu wysyła się samo, po kolei;
#  • pasek „📴 Brak internetu – zapisane w pamięci telefonu (N czeka)”;
#  • brak internetu nie czyści danych na ekranie; aplikacja startuje offline z ostatnio zapisanych danych;
#  • service worker zapamiętuje aplikację, więc otwiera się też bez sieci.
#  Pełna ochrona przed podwójnym doliczeniem: sql/supabase_v4_6.sql (bez niego działa w trybie zgodności)
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:120]!r}')
    s = s.replace(old, new)

rep('<b>Cafe Strych Manager <span>V4.5</span></b>', '<b>Cafe Strych Manager <span>V4.6</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • Usuwanie rachunków z historii (admin), prostszy rachunek i rabat</small>',
    '<small>Aktualizacja: 23.10.2026 • POS działa bez internetu (zapis w pamięci telefonu), usuwanie rachunków z historii</small>')
rep('<p>Cafe Strych Manager <b>V4.5</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.6</b> • 23.10.2026</p>')

# ---- pasek stanu sieci
rep('<div id="toast" class="toast">Zapisano</div>', '<div id="netBar" class="netBar hide" role="status" onclick="flushOutbox()"></div><div id="toast" class="toast">Zapisano</div>')

# ---- wykrywanie braku sieci: zapytania bez internetu nie czyszczą danych
rep("async function safe(table,query=q=>q.select('*')){try{const r=await query(sb.from(table));if(r.error){console.warn(table,r.error.message);return []}return r.data??[]}catch(e){console.warn(table,e);return []}}",
    r"""let netFail=false,netDown=false;
const isNetErr=e=>{const m=String(e?.message||e?.details||e||'');return !navigator.onLine||/failed to fetch|networkerror|network error|load failed|network request failed|internet|timed? ?out|aborted|ERR_/i.test(m)};
async function safe(table,query=q=>q.select('*')){try{const r=await query(sb.from(table));if(r.error){if(isNetErr(r.error))netFail=true;console.warn(table,r.error.message);return []}return r.data??[]}catch(e){if(isNetErr(e))netFail=true;console.warn(table,e);return []}}""")
rep("async function loadAll(){const x=await Promise.all([", "async function loadAll(){if(!navigator.onLine){setNet(false);return}netFail=false;const x=await Promise.all([")
rep("safe('bug_reports',q=>q.select('*').order('created_at',{ascending:false}).limit(300))]);\n [state.profiles,",
    "safe('bug_reports',q=>q.select('*').order('created_at',{ascending:false}).limit(300))]);if(netFail){setNet(false);return}\n [state.profiles,")
rep("const settings=await safe('cafe_settings',q=>q.select('*').limit(1));state.settings=settings[0]||{qr_enabled:false};",
    "const settings=await safe('cafe_settings',q=>q.select('*').limit(1));if(!netFail)state.settings=settings[0]||{qr_enabled:false};")
rep("state.social=await safe('site_social_posts',q=>q.select('*').order('created_at',{ascending:false}).limit(60))}",
    "state.social=await safe('site_social_posts',q=>q.select('*').order('created_at',{ascending:false}).limit(60));if(!netFail){setNet(true);scheduleCache()}}")
rep("async function loadPos(){const[o,p]=", "async function loadPos(){if(!navigator.onLine){setNet(false);return}netFail=false;const[o,p]=")
rep("const items=await loadOrderItems(o.map(x=>x.id));state.orders=o;state.payments=p;state.orderItems=items}",
    "const items=await loadOrderItems(o.map(x=>x.id));if(netFail){setNet(false);return}state.orders=o;state.payments=p;state.orderItems=items;setNet(true);scheduleCache()}")
rep("async function refreshOrder(oid){if(posBusy)return;const rows=await safe('pos_order_items',q=>q.select('*').eq('order_id',oid));if(posBusy)return;",
    "async function refreshOrder(oid){if(posBusy||netDown)return;netFail=false;const rows=await safe('pos_order_items',q=>q.select('*').eq('order_id',oid));if(posBusy||netFail)return;")
rep("if(posBusy){reloadTimer=null;return live(t)}", "if(posBusy||netDown){livePending=true;return}")

# ---- skrzynka zmian (outbox) + kopia danych na telefonie
rep("function posChange(oid,mid,lineId,delta){localBump(oid,mid,lineId,delta);rerenderOrder(oid);posBusy++;$('#ticket')?.classList.add('syncing');\n enqueue(async()=>{let err=null;try{err=await syncBump(oid,mid,lineId,delta)}catch(e){err=e}posBusy--;if(err)alert('Nie udało się zapisać zmiany na rachunku:\\n'+(err.message||err)+'\\n\\nRachunek zostanie odświeżony.');if(!posBusy||err){await refreshOrder(oid);$('#ticket')?.classList.remove('syncing')}})}",
    r"""function posChange(oid,mid,lineId,delta){localBump(oid,mid,lineId,delta);rerenderOrder(oid);pushOp({type:'bump',oid,mid:mid||null,lineId:mid?null:lineId,delta})}
/* ===== V4.6: zapis offline ===== */
const OUTBOX_KEY='cs_outbox_v1',CACHE_KEY='cs_cache_v1';let outbox=[],flushing=false,opsMode='op',livePending=false,wasOffline=false,cacheTimer;
try{outbox=JSON.parse(localStorage.getItem(OUTBOX_KEY)||'[]')}catch{outbox=[]}
posBusy=outbox.length;
const uuid=()=>crypto.randomUUID?crypto.randomUUID():'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>{const r=Math.random()*16|0;return(c==='x'?r:(r&3|8)).toString(16)});
function saveOutbox(){posBusy=outbox.length;try{localStorage.setItem(OUTBOX_KEY,JSON.stringify(outbox))}catch(e){console.warn('outbox',e)}updateNetBar()}
function pushOp(op){op.id=op.id||uuid();op.ts=new Date().toISOString();op.uid=state.user?.id;outbox.push(op);saveOutbox();scheduleCache();flushOutbox()}
function setNet(ok){if(!ok&&!netDown)wasOffline=true;netDown=!ok;updateNetBar()}
function updateNetBar(){const b=$('#netBar');if(!b)return;const n=outbox.length;b.className='netBar '+(netDown?'off':n?'sync':'hide');
 b.innerHTML=netDown?`<b>📴 Brak internetu</b><span>${n?`Zmiany na rachunkach są zapisane w pamięci tego urządzenia (${n} czeka). Wyślą się same, gdy wróci internet – nie zamykaj rachunków na innym telefonie.`:'Pracujesz na ostatnio zapisanych danych. Zmiany na rachunkach zapiszą się w pamięci urządzenia.'}</span>`:n?`<b>⟳ Wysyłam zapisane zmiany (${n})…</b>`:'';
 $$('#ticket').forEach(t=>t.classList.toggle('syncing',n>0));document.body.classList.toggle('isOffline',netDown)}
function scheduleCache(){clearTimeout(cacheTimer);cacheTimer=setTimeout(saveCache,400)}
function saveCache(){if(!state.user||!state.profile||window.PREVIEW_MODE)return;try{const since=Date.now()-36*3600e3,keep=state.orders.filter(o=>!['paid','cancelled'].includes(o.status)||new Date(o.created_at)>since),ids=new Set(keep.map(o=>o.id));
 localStorage.setItem(CACHE_KEY,JSON.stringify({v:1,ts:Date.now(),uid:state.user.id,user:{id:state.user.id,email:state.user.email},profile:state.profile,settings:state.settings,menu:state.menu,tables:state.tables,rooms:state.rooms,places:state.places,employees:state.employees,permissions:state.permissions,shifts:state.shifts.filter(x=>x.shift_date>=iso(new Date(Date.now()-864e5))),bookings:state.bookings.filter(b=>new Date(b.start_at)>since),orders:keep,orderItems:state.orderItems.filter(i=>ids.has(i.order_id)),payments:state.payments.filter(p=>ids.has(p.order_id))}))}catch(e){console.warn('cache',e)}}
function readCache(){try{return JSON.parse(localStorage.getItem(CACHE_KEY)||'null')}catch{return null}}
function applyCache(c){state.profile=c.profile;['settings','menu','tables','rooms','places','employees','permissions','shifts','bookings','orders','orderItems','payments'].forEach(k=>{if(c[k])state[k]=c[k]})}
const opName=op=>state.orders.find(o=>o.id===op.oid)?.customer_name||state.orders.find(o=>o.id===op.oid)?.order_no||'rachunek';
async function sendOp(op){
 if(op.type==='bump'){if(opsMode==='op'){const r=await sb.rpc('pos_bump_op',{p_op:op.id,p_order:op.oid,p_menu:op.mid,p_item:op.mid?null:op.lineId,p_delta:op.delta});if(!r.error)return null;if(isNetErr(r.error))return r.error;if(/PGRST202|function|schema cache/i.test((r.error.code||'')+' '+r.error.message))opsMode='legacy';else return r.error}return await syncBump(op.oid,op.mid,op.lineId,op.delta)}
 if(op.type==='order'){const r=await sb.from('pos_orders').insert(op.row);return r.error&&!/23505|duplicate/i.test((r.error.code||'')+' '+r.error.message)?r.error:null}
 if(op.type==='pay'){const u=await sb.from('pos_orders').update({status:'paid',closed_at:op.at}).eq('id',op.oid).not('status','in','(paid,cancelled)').select('id');if(u.error)return u.error;
  if(!u.data?.length){const ex=await sb.from('pos_payments').select('id').eq('order_id',op.oid);if(ex.error)return ex.error;if(ex.data.some(p=>p.id===op.payId))return null;
   const st=await sb.from('pos_orders').select('status').eq('id',op.oid).maybeSingle();if(st.error)return st.error;if(!st.data||st.data.status==='cancelled'||ex.data.length){noticeOffline(`Rachunek „${op.name}” został już zamknięty na innym urządzeniu – płatność ${money(op.amount)} zapisana offline NIE została doliczona. Sprawdź go w historii.`);return null}}
  const r=await sb.from('pos_payments').insert({id:op.payId,order_id:op.oid,amount:op.amount,tip_amount:0,method:op.method,created_by:op.uid,created_at:op.at});if(r.error&&!/23505|duplicate/i.test((r.error.code||'')+' '+r.error.message)){if(!isNetErr(r.error))await sb.from('pos_orders').update({status:op.prev,closed_at:null}).eq('id',op.oid);return r.error}return null}
 return null}
const offlineNotes=[];function noticeOffline(t){offlineNotes.push(t)}
window.flushOutbox=async function(){if(flushing||!outbox.length){updateNetBar();return}if(!navigator.onLine){setNet(false);return}flushing=true;let sent=0;const touched=new Set();
 try{while(outbox.length){const op=outbox[0];let err=null;try{err=await sendOp(op)}catch(e){err=e}
  if(err&&isNetErr(err)){setNet(false);break}
  if(err)noticeOffline(`Nie udało się zapisać zmiany na „${opName(op)}”: ${err.message||err}`);
  outbox.shift();saveOutbox();sent++;touched.add(op.oid)}}
 finally{flushing=false}
 if(outbox.length)return;setNet(true);
 if(wasOffline){wasOffline=false;await loadPos();const og=$('#menuGrid')?.dataset.order;if(og)rerenderOrder(og);else if(state.page)state.page();else if(!$('#modal').open)view($('[data-view].active')?.dataset.view||'home');if(sent)toast(`✓ Wysłano zmiany zapisane offline (${sent})`)}
 else{const og=$('#menuGrid')?.dataset.order;if(og&&touched.has(og))await refreshOrder(og)}
 if(offlineNotes.length){const t=offlineNotes.splice(0).join('\n\n');alert(t)}
 if(livePending){livePending=false;live()}};
addEventListener('online',()=>{flushOutbox().then(()=>{if(!outbox.length)live()})});
addEventListener('offline',()=>setNet(false));
setInterval(()=>{if(outbox.length||netDown){if(outbox.length)flushOutbox();else loadPos().then(()=>{if(!netDown){livePending=false;live()}})}},15000);
const ONLINE_ONLY='Brak internetu – ta operacja wymaga połączenia.\n\nRachunki, dodawanie pozycji i płatności działają offline (zapisują się w pamięci urządzenia), ale rabat, anulowanie, edycja i usuwanie – dopiero po powrocie internetu.';""")

# ---- nowy rachunek: tworzony od razu na telefonie, wysyłany przez skrzynkę
rep("""r=await sb.from('pos_orders').insert({order_no:no,table_id:$('#orderTable').value||null,customer_name:$('#orderCustomer').value.trim()||null,status:'new',source:'pos',created_by:state.user.id}).select().single();if(r.error)return alert(r.error.message);closeModal();state.orders.unshift(r.data);openOrder(r.data.id)});""",
    """id=uuid(),row={id,order_no:no,table_id:$('#orderTable').value||null,customer_name:$('#orderCustomer').value.trim()||null,status:'new',source:'pos',created_by:state.user.id,created_at:new Date().toISOString()};state.orders.unshift({...row,discount_pct:0});closeModal();openOrder(id);pushOp({type:'order',oid:id,row});if(netDown)toast('Rachunek zapisany offline – wyśle się po powrocie internetu')});""")

# ---- płatność: najpierw dosłane kliknięcia, zapis lokalny + skrzynka
pay_start = s.find("window.pay=id=>modal(");pay_end = s.find("window.orderHistory=", pay_start)
s = s[:pay_start] + r"""window.pay=id=>modal('Płatność',`${orderDiscount(id)?`<p class="payDisc">Suma ${money(orderSubtotal(id))} • rabat ${pctTxt(orderDiscount(id))} (−${money(orderSubtotal(id)-orderTotal(id))})</p>`:''}<div class="total" style="text-align:center">${money(orderTotal(id))}</div><label>Metoda</label><select id="payMethod"><option value="card">Karta</option><option value="cash">Gotówka</option><option value="blik">BLIK</option><option value="transfer">Przelew</option></select>${netDown?'<p class="payOffline">📴 Brak internetu – płatność zapisze się w pamięci tego urządzenia i wyśle sama po powrocie sieci.</p>':''}`,async()=>{const sv=$('#modalSave');if(sv){sv.disabled=true;sv.textContent='Zapisywanie…'}
 if(navigator.onLine&&!netDown){await flushOutbox();if(!outbox.length&&!netDown)await loadPos()}if(sv){sv.disabled=false;sv.textContent='Zapisz'}
 const o=state.orders.find(x=>x.id===id),total=orderTotal(id);if(!o)return alert('Nie znaleziono rachunku.');if(['paid','cancelled'].includes(o.status)){closeModal();pos();return alert('Ten rachunek jest już zamknięty.')}if(total<=0)return alert('Rachunek jest pusty.');
 const at=new Date().toISOString(),payId=uuid(),method=$('#payMethod').value,prev=o.status||'new',name=o.customer_name||o.order_no||'Rachunek';
 o.status='paid';o.closed_at=at;state.payments.unshift({id:payId,order_id:id,amount:total,tip_amount:0,method,created_by:state.user.id,created_at:at});
 closeModal();pos();pushOp({type:'pay',oid:id,payId,amount:total,method,at,prev,name});toast(netDown?'Opłacone – zapisane offline, wyśle się po powrocie internetu':'Rachunek opłacony')});
""" + s[pay_end:]

# ---- start aplikacji bez internetu
rep("""const r=await sb.from('profiles').select('*').eq('id',state.user.id).maybeSingle();if(r.error||!r.data){alert('Brak profilu użytkownika: '+(r.error?.message||'konto nieaktywne'));await sb.auth.signOut();return}state.profile=r.data;if(state.profile.active===false){alert('Twoje konto czeka na zatwierdzenie przez administratora lub zostało zablokowane.\\n\\nPoproś kierownika o aktywację konta, a potem zaloguj się ponownie.');await sb.auth.signOut();return}await loadAll();""",
    """const r=navigator.onLine?await sb.from('profiles').select('*').eq('id',state.user.id).maybeSingle():{error:{message:'offline'}};
 if(r.error&&isNetErr(r.error)){const c=readCache();if(c&&c.uid===state.user.id){applyCache(c);setNet(false)}else{alert('Brak internetu, a na tym urządzeniu nie ma jeszcze zapisanych danych.\\n\\nPołącz się z internetem i otwórz aplikację ponownie.');bootedId=null;return}}
 else{if(r.error||!r.data){alert('Brak profilu użytkownika: '+(r.error?.message||'konto nieaktywne'));await sb.auth.signOut();return}state.profile=r.data;if(state.profile.active===false){alert('Twoje konto czeka na zatwierdzenie przez administratora lub zostało zablokowane.\\n\\nPoproś kierownika o aktywację konta, a potem zaloguj się ponownie.');await sb.auth.signOut();return}
  if(outbox.length)await flushOutbox();await loadAll();if(netDown){const c=readCache();if(c&&c.uid===state.user.id)applyCache(c)}}""")
rep("sb.auth.getSession().then(({data})=>boot(data.session));",
    "sb.auth.getSession().then(({data})=>{if(!data.session&&!navigator.onLine){const c=readCache();if(c?.user)return boot({user:c.user})}boot(data.session)}).catch(()=>{const c=readCache();if(c?.user)boot({user:c.user})});updateNetBar();")

# ---- operacje wymagające internetu
rep("let reloadTimer;", """['saveDiscount','cancelOrder','editOrder','deleteHistoricalOrder','discountForm'].forEach(n=>{const f=window[n];if(typeof f!=='function')return;window[n]=(...a)=>{if(netDown||!navigator.onLine)return alert(ONLINE_ONLY);return f(...a)}});
let reloadTimer;""")

# ---- CSS
rep('</style></head>', '''
/* V4.6 – offline */
.netBar{position:fixed;z-index:90;left:50%;top:calc(8px + env(safe-area-inset-top));transform:translateX(-50%);width:min(94%,640px);display:flex;flex-direction:column;gap:2px;padding:10px 14px;border-radius:14px;font-size:12.5px;line-height:1.4;box-shadow:0 10px 30px #0008;cursor:pointer}
.netBar.hide{display:none}.netBar b{font-size:13.5px}
.netBar.off{background:#4a1f17;border:1px solid #ee7065;color:#ffe2dc}
.netBar.sync{background:#2b2414;border:1px solid #e0ad67;color:#f7e3bf;flex-direction:row;justify-content:center}
body.isOffline .shell{padding-top:calc(86px + env(safe-area-inset-top))}
.payOffline{margin:10px 0 0;padding:9px 11px;border-radius:11px;background:#ee70651a;border:1px solid #ee706555;color:#ffd4cc;font-size:12.5px}
</style></head>''')
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
