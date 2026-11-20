import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
# przyciski: Płatność | Rabat + Podziel | Anuluj
rep("""<button class="ghost discBtn" onclick="discountForm('${id}')">％ ${orderDiscount(id)?`Rabat ${pctTxt(orderDiscount(id))}`:'Rabat'}</button><button class="danger" onclick="cancelOrder('${id}')">Anuluj rachunek</button></div>`;""",
    """<button class="ghost discBtn" onclick="discountForm('${id}')">％ ${orderDiscount(id)?`Rabat ${pctTxt(orderDiscount(id))}`:'Rabat'}</button><button class="ghost splitBtn" onclick="splitForm('${id}')">✂ Podziel</button><button class="danger cancelBtn" onclick="cancelOrder('${id}')">Anuluj rachunek</button></div>`;""")
rep(".ticketActions .primary{grid-column:1/-1;text-align:center}",
    ".ticketActions .primary,.ticketActions .cancelBtn{grid-column:1/-1;text-align:center}\n.splitList{display:grid;gap:6px;margin:4px 0 10px}.splitRow{display:grid;grid-template-columns:1fr auto;align-items:center;gap:10px;padding:8px 10px;border:1px solid var(--line,#ddd);border-radius:12px}.splitRow.on{border-color:var(--accent,#c58b3c);background:rgba(197,139,60,.08)}.splitRow small{display:block;opacity:.7}.splitRow .qty{display:flex;align-items:center;gap:8px}.splitRow .qty b{min-width:42px;text-align:center}.splitSum{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:6px 0 2px}.splitSum div{padding:8px 10px;border-radius:12px;background:rgba(127,127,127,.1);text-align:center}.splitSum b{display:block;font-size:18px}")
# audyt
rep("reopen:['↺','ponownie otwarto','aEdit']};","reopen:['↺','ponownie otwarto','aEdit'],split:['✂','podzielono rachunek','aEdit']};")
# logika podziału – przed saveDiscount
rep("window.saveDiscount=async(id,v)=>{",
r"""/* V5.8: dzielenie rachunku */
const SPLIT={oid:null,pick:{}};
function splitName(o){const base=o.customer_name||state.tables.find(t=>t.id===o.table_id)?.label||o.order_no||'Rachunek';const root=String(base).replace(/ – część \d+$/,'');let k=2;while(state.orders.some(x=>!['paid','cancelled'].includes(x.status)&&x.customer_name===`${root} – część ${k}`))k++;return `${root} – część ${k}`}
window.splitForm=async id=>{const o=state.orders.find(x=>x.id===id);if(!o)return;if(['paid','cancelled'].includes(o.status))return alert('Rachunek jest zamknięty.');
 if(netDown||!navigator.onLine)return alert('Dzielenie rachunku wymaga internetu. Spróbuj, gdy wróci połączenie.');
 if(outbox.length){toast('Zapisuję ostatnie zmiany…');await flushOutbox();if(outbox.some(op=>op.oid===id))return alert('Nie udało się jeszcze zapisać ostatnich zmian na tym rachunku. Spróbuj za chwilę.')}
 const rows=await safe('pos_order_items',q=>q.select('*').eq('order_id',id));if(netFail)return alert('Brak połączenia – spróbuj za chwilę.');
 state.orderItems=state.orderItems.filter(x=>x.order_id!==id).concat(rows);
 const items=orderItems(id).filter(i=>Number(i.qty)>0).sort((a,b)=>String(a.created_at||'').localeCompare(String(b.created_at||'')));
 if(items.reduce((n,i)=>n+Number(i.qty),0)<2)return alert('Na rachunku jest za mało pozycji, żeby go podzielić.');
 SPLIT.oid=id;SPLIT.pick={};
 modal('Podziel rachunek',`<p class="muted" style="margin-top:0">Zaznacz, co przenieść na nowy rachunek. Reszta zostaje na obecnym.</p><div class="splitList" id="splitList"></div><div class="splitSum" id="splitSum"></div>${field('splitName','Nazwa nowego rachunku','text',`value="${esc(splitName(o))}"`)}`,saveSplit);
 $('#modal').classList.add('dayModal');$('#modalSave').textContent='Podziel';splitRender()};
function splitRender(){const id=SPLIT.oid,d=orderDiscount(id),items=orderItems(id).filter(i=>Number(i.qty)>0).sort((a,b)=>String(a.created_at||'').localeCompare(String(b.created_at||'')));
 $('#splitList').innerHTML=items.map(i=>{const n=SPLIT.pick[i.id]||0;return `<div class="splitRow${n?' on':''}"><div><b>${esc(i.item_name)}</b><small>${money(i.unit_price)} • na rachunku ${i.qty} szt.</small></div><div class="qty"><button type="button" class="ghost" onclick="splitStep('${i.id}',-1)" aria-label="Mniej">−</button><b>${n}/${i.qty}</b><button type="button" class="ghost" onclick="splitStep('${i.id}',1)" aria-label="Więcej">+</button></div></div>`}).join('');
 let moved=0,all=0;items.forEach(i=>{all+=Number(i.qty)*Number(i.unit_price);moved+=(SPLIT.pick[i.id]||0)*Number(i.unit_price)});const f=v=>d?Math.round(v*(100-d))/100:v;
 $('#splitSum').innerHTML=`<div>Nowy rachunek<b>${money(moved)}</b></div><div>Zostaje<b>${money(f(all-moved))}</b>${d?`<small>z rabatem ${pctTxt(d)}</small>`:''}</div>`}
window.splitStep=(iid,dl)=>{const i=state.orderItems.find(x=>x.id===iid);if(!i)return;SPLIT.pick[iid]=Math.min(Number(i.qty),Math.max(0,(SPLIT.pick[iid]||0)+dl));if(!SPLIT.pick[iid])delete SPLIT.pick[iid];splitRender()};
async function saveSplit(){const id=SPLIT.oid,o=state.orders.find(x=>x.id===id);if(!o)return;const items=orderItems(id),pick=Object.entries(SPLIT.pick).filter(([,n])=>n>0);
 if(!pick.length)return alert('Wybierz przynajmniej jedną pozycję do przeniesienia.');
 const left=items.reduce((n,i)=>n+Number(i.qty)-(SPLIT.pick[i.id]||0),0);if(left<=0)return alert('Na obecnym rachunku musi coś zostać.');
 const today=iso(new Date()),no=`${new Date().toLocaleDateString('pl-PL')} • Rachunek ${state.orders.filter(x=>day(x.created_at)===today).length+1}`,nid=uuid(),name=$('#splitName').value.trim()||splitName(o);
 const r=await sb.rpc('pos_split_order',{p_order:id,p_new:nid,p_no:no,p_name:name,p_items:pick.map(([iid,qty])=>({id:iid,qty}))});
 if(r.error){if(isNetErr(r.error))return alert('Brak połączenia – rachunek nie został podzielony. Spróbuj za chwilę.');return alert(/pos_split_order|PGRST202|schema cache/i.test(r.error.message)?'Uruchom w Supabase skrypt sql/supabase_v5_8.sql.':r.error.message)}
 state.orders.unshift({id:nid,order_no:no,table_id:o.table_id,customer_name:name,status:'new',source:'pos',created_by:state.user.id,created_at:new Date().toISOString(),discount_pct:0});
 const rows=await safe('pos_order_items',q=>q.select('*').in('order_id',[id,nid]));if(!netFail)state.orderItems=state.orderItems.filter(x=>x.order_id!==id&&x.order_id!==nid).concat(rows);
 closeModal();openOrder(nid);toast(`Rachunek podzielony – otwarto „${name}”`)}
window.saveDiscount=async(id,v)=>{""")
rep('Cafe Strych Manager <span>V5.7.1</span>','Cafe Strych Manager <span>V5.8</span>')
rep('Cafe Strych Manager <b>V5.7.1</b> • 20.11.2026','Cafe Strych Manager <b>V5.8</b> • 20.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
# (poprawka netFail dopisana ręcznie po patchu)
