import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:80]}')
    s=s.replace(a,b)
# menu konta (kierownik/admin)
rep('<button id="posConfigMenu" class="hide" onclick="posConfiguration()">🍽️ Lokal</button>',
    '<button id="posConfigMenu" class="hide" onclick="posConfiguration()">🍽️ Lokal</button><button id="auditMenu" class="hide" onclick="auditView()">🕓 Historia rachunków</button>')
rep("$('#posConfigMenu').classList.toggle('hide',!canManage());","$('#posConfigMenu').classList.toggle('hide',!canManage());$('#auditMenu')?.classList.toggle('hide',!canManage());")
# zakładka w ustawieniach admina
rep("['menu','🍽️','Menu POS'],","['menu','🍽️','Menu POS'],['audit','🕓','Historia rachunków'],")
rep("menu:()=>menuAdmin(),news:","menu:()=>menuAdmin(),audit:()=>auditView(pane),news:")
# przycisk na rachunku
rep("""${canManage()&&!closed?`<button class="ghost editOrderBtn" onclick="editOrder('${id}')">Edytuj</button>`:''}</div>""",
"""${canManage()?`<button class="ghost auditOrderBtn" title="Historia zmian" onclick="orderAudit('${id}')">🕓</button>`:''}${canManage()&&!closed?`<button class="ghost editOrderBtn" onclick="editOrder('${id}')">Edytuj</button>`:''}</div>""")
JS=r"""
/* ---------------- V5.1: HISTORIA ZMIAN RACHUNKÓW (kierownik/admin) ---------------- */
const AUD={day:null,who:'',kind:'all',rows:[],err:null};
const AUD_ACT={open:['🧾','otwarto rachunek','aOpen'],add:['＋','dodano','aAdd'],remove:['－','usunięto','aDel'],edit:['✎','zmieniono','aEdit'],discount:['％','rabat','aEdit'],paid:['✓','opłacono','aPaid'],cancelled:['✕','anulowano rachunek','aDel'],reopen:['↺','ponownie otwarto','aEdit']};
function audBizDay(d=new Date()){d=new Date(d);if(d.getHours()<6)d.setDate(d.getDate()-1);return iso(d)}
function audRange(ds){const [y,m,d]=ds.split('-').map(Number);return [new Date(y,m-1,d,6).toISOString(),new Date(y,m-1,d+1,6).toISOString()]}
function audOdd(t){const h=new Date(t).getHours();return h>=3&&h<11}
function audQty(n){n=Number(n||0);return (n>0?'+':'')+String(n).replace('.',',')}
function audRow(a,showOrder=true){const [ic,lbl,cls]=AUD_ACT[a.action]||['•',a.action,''],t=new Date(a.created_at),odd=audOdd(a.created_at);
 const what=a.item_name?`<b>${a.qty_delta!=null&&a.action!=='edit'?`${audQty(a.qty_delta)} × `:''}${esc(a.item_name)}</b>${a.unit_price!=null&&a.action!=='edit'?` <small>${money(a.unit_price)}/szt.</small>`:''}`:'';
 return `<div class="audRow ${odd?'audOdd':''}"><span class="audTime">${t.toLocaleTimeString('pl-PL',{hour:'2-digit',minute:'2-digit',second:'2-digit'})}</span><span class="audIc ${cls}">${ic}</span><div class="audMain"><div><span class="audLbl ${cls}">${lbl}</span> ${what}${a.details?` <small class="muted">${esc(a.details)}</small>`:''}</div><small class="muted">👤 <b>${esc(a.user_name||'—')}</b>${showOrder?` • <a href="#" onclick="event.preventDefault();orderAudit('${a.order_id}')">${esc(a.order_label||'Rachunek')}</a>`:''}${odd?' • <span class="audWarn">⚠️ poza godzinami pracy lokalu</span>':''}</small></div></div>`}
async function auditLoad(){const [a,b]=audRange(AUD.day);const r=await sb.from('pos_audit').select('*').gte('created_at',a).lt('created_at',b).order('created_at',{ascending:false}).limit(2000);AUD.err=r.error?r.error.message:null;AUD.rows=r.data||[]}
window.auditView=async(pane=null)=>{if(!canManage())return;if(!AUD.day)AUD.day=audBizDay();const box=pane||content();if(!pane){state.page=()=>auditView();$$('[data-view]').forEach(b=>b.classList.remove('active'))}
 box.innerHTML='<p class="muted">Ładowanie historii…</p>';await auditLoad();auditRender(box,!!pane)};
function auditRender(box,inAdmin){const rows=AUD.rows,people=[...new Set(rows.map(r=>r.user_name||'—'))].sort((a,b)=>a.localeCompare(b,'pl'));if(AUD.who&&!people.includes(AUD.who))AUD.who='';
 const f=rows.filter(r=>(!AUD.who||(r.user_name||'—')===AUD.who)&&(AUD.kind==='all'||(AUD.kind==='remove'?['remove','cancelled','discount','edit'].includes(r.action):audOdd(r.created_at))));
 const nAdd=rows.filter(r=>r.action==='add').length,nDel=rows.filter(r=>r.action==='remove').length,nOdd=rows.filter(r=>audOdd(r.created_at)).length,d=new Date(AUD.day+'T12:00');
 const missing=AUD.err&&/pos_audit|does not exist|schema cache/i.test(AUD.err);
 box.innerHTML=`<div class="toolbar inline"><div><h2>Historia rachunków</h2><small class="muted">Kto i o której dodał lub usunął pozycję • dzień pracy od 6:00 do 6:00</small></div>${inAdmin?'':`<button class="ghost backTop" onclick="state.page=null;view('home')">← Wróć</button>`}</div>
 <div class="audNav"><button class="ghost" onclick="auditShift(-1)">‹</button><input type="date" value="${AUD.day}" max="${audBizDay()}" onchange="AUD.day=this.value||audBizDay();auditView(${inAdmin?"$('#adminPane')":''})"><button class="ghost" onclick="auditShift(1)" ${AUD.day>=audBizDay()?'disabled':''}>›</button></div>
 <p class="audDay">${cap(d.toLocaleDateString('pl-PL',{weekday:'long',day:'numeric',month:'long'}))}</p>
 ${missing?`<div class="dbAlert">Historia zacznie się zapisywać po uruchomieniu w Supabase skryptu <b>supabase_v4_9.sql</b>.</div>`:AUD.err?`<div class="dbAlert">Nie udało się pobrać historii: ${esc(AUD.err)}</div>`:''}
 <div class="grid kpis"><div class="kpi"><span>Dodane pozycje</span><strong>${nAdd}</strong></div><div class="kpi"><span>Usunięte pozycje</span><strong>${nDel}</strong></div><div class="kpi ${nOdd?'audKpiWarn':''}"><span>Poza godzinami</span><strong>${nOdd}</strong></div></div>
 <div class="audFilters"><select onchange="AUD.who=this.value;auditRender(this.closest('#adminPane')||content(),${inAdmin})"><option value="">Wszystkie osoby</option>${people.map(n=>`<option ${n===AUD.who?'selected':''}>${esc(n)}</option>`).join('')}</select><select onchange="AUD.kind=this.value;auditRender(this.closest('#adminPane')||content(),${inAdmin})"><option value="all" ${AUD.kind==='all'?'selected':''}>Wszystkie zmiany</option><option value="remove" ${AUD.kind==='remove'?'selected':''}>Usunięcia, rabaty, anulowania</option><option value="odd" ${AUD.kind==='odd'?'selected':''}>Tylko poza godzinami</option></select></div>
 <section class="panel audList">${f.map(r=>audRow(r)).join('')||'<p class="muted">Brak zmian w tym dniu.</p>'}</section>`}
window.auditShift=n=>{const d=new Date(AUD.day+'T12:00');d.setDate(d.getDate()+n);const v=iso(d);if(v>audBizDay())return;AUD.day=v;auditView(state.inAdmin?$('#adminPane'):null)};
window.orderAudit=async id=>{if(!canManage())return;const o=state.orders.find(x=>x.id===id);modal('Historia rachunku','<p class="muted">Ładowanie…</p>',null,false);$('#modal').classList.add('dayModal');
 const r=await sb.from('pos_audit').select('*').eq('order_id',id).order('created_at',{ascending:true}).limit(1000);const rows=r.data||[];
 const first=rows[0]?new Date(rows[0].created_at):null;
 $('#modalFields').innerHTML=`<p class="muted" style="margin-top:0">${esc(rows.at(-1)?.order_label||o?.customer_name||o?.order_no||'Rachunek')}${first?` • ${first.toLocaleDateString('pl-PL',{weekday:'long',day:'numeric',month:'long'})}`:''}</p>${r.error?`<div class="dbAlert">${/pos_audit|does not exist|schema cache/i.test(r.error.message)?'Uruchom w Supabase skrypt <b>supabase_v4_9.sql</b>.':esc(r.error.message)}</div>`:''}<div class="audList">${rows.map(a=>audRow(a,false)).join('')||'<p class="muted">Brak zapisanych zmian. Historia zapisuje się od uruchomienia skryptu V5.1 – starsze rachunki jej nie mają.</p>'}</div>`};
"""
rep("window.closeAdmin=()=>{state.inAdmin=false;view('home')};","window.closeAdmin=()=>{state.inAdmin=false;view('home')};"+JS)
CSS="""
/* V5.1 historia rachunków */
.audNav{display:grid;grid-template-columns:44px 1fr 44px;gap:8px;margin:4px 0 6px}.audNav input{text-align:center}
.audDay{margin:0 0 10px;color:var(--muted);font-size:13px;text-align:center}
.audFilters{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 0 10px}
@media(max-width:520px){.audFilters{grid-template-columns:1fr}}
.audList{display:flex;flex-direction:column;gap:2px;padding:6px}
.audRow{display:grid;grid-template-columns:auto 30px minmax(0,1fr);gap:10px;align-items:start;padding:10px 8px;border-bottom:1px solid #ffffff10}
.audRow:last-child{border-bottom:0}
.audTime{font:600 12px ui-monospace,Menlo,monospace;color:var(--muted);padding-top:6px}
.audIc{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-weight:800;background:#ffffff10}
.audMain{min-width:0;line-height:1.4}.audMain small{display:block;margin-top:2px}.audMain a{color:#f0ca80}
.audLbl{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.03em}
.aAdd{color:#9fe0b0}.audIc.aAdd{background:#71c98a22}.aDel{color:#ff9d8f}.audIc.aDel{background:#e0605022}
.aPaid{color:#f0ca80}.audIc.aPaid{background:#e0ad6722}.aEdit{color:#bcd3ff}.audIc.aEdit{background:#7fa6ff1f}.aOpen{color:var(--muted)}
.audOdd{background:#e0605014;border-radius:10px}.audWarn{color:#ffb3a8;font-weight:700}
.audKpiWarn strong{color:#ff9d8f!important}
.auditOrderBtn{flex:0 0 auto;width:42px;padding:0!important}
"""
rep("</style></head>",CSS+"</style></head>")
rep('Cafe Strych Manager <span>V5.0.7</span>','Cafe Strych Manager <span>V5.1</span>')
open(p,'w',encoding='utf-8').write(s); print('ok')
