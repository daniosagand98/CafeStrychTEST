import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:80]}')
    s=s.replace(a,b)
# 5) grafik całego zespołu dla każdego, własne zmiany wyróżnione
rep("function visibleShifts(){const e=employee();return canManage()?state.shifts:state.shifts.filter(s=>s.employee_id===e?.id)}",
    "function visibleShifts(){return state.shifts}\nfunction mineCls(s){if(canManage())return '';const e=employee();return e&&s.employee_id===e.id?' mine':' others'}")
rep('function shiftHtml(s){return `<div class="shift"','function shiftHtml(s){return `<div class="shift${mineCls(s)}"')
rep("""${rows.slice(0,4).map(x=>`<div class="entry" onclick""","""${rows.slice(0,4).map(x=>`<div class="entry${mineCls(x)}" onclick""")
# 2) rezerwacja bez czasu trwania
rep("""<div><label>Czas trwania</label><select id="bookDur">${[1,2,3,4,5,6].map(h=>`<option value="${h}" ${h===dur?'selected':''}>${h} h</option>`).join('')}</select></div>""","")
rep("end_at:new Date(a.getTime()+(+$('#bookDur').value||2)*3600000).toISOString()","end_at:new Date(a.getTime()+(dur||2)*3600000).toISOString()")
# 3) stolik max 10 osób
rep("if(!(guests>=1))return alert('Podaj liczbę osób.');",
    "if(!(guests>=1))return alert('Podaj liczbę osób.');if(guests>10&&!$('#bookWhole')?.checked)return alert('Stolik można zarezerwować maksymalnie dla 10 osób.\\n\\nWiększa grupa to rezerwacja sali – przyjmuje ją właścicielka telefonicznie (693 971 009).'+(canManage()?'\\n\\nJeśli to rezerwacja sali, wybierz salę i zaznacz „Rezerwacja całej sali”.':''));")
# 6) inny produkt
rep("""<div class="catChips">${cats.map(c=>`<button type="button" data-c="${esc(c)}" onclick="jumpCat(this.dataset.c)">${esc(c)}</button>`).join('')}</div>""",
    """<div class="catChips"><button type="button" class="otherProd" onclick="customItem('${id}')">＋ Inny produkt</button>${cats.map(c=>`<button type="button" data-c="${esc(c)}" onclick="jumpCat(this.dataset.c)">${esc(c)}</button>`).join('')}</div>""")
rep("window.addItem=(oid,mid)=>{","""window.customItem=oid=>{modal('Inny produkt',`${field('ciName','Nazwa','','required maxlength="80" placeholder="np. Tort urodzinowy, korkowe"')}<div class="formGrid"><div>${field('ciPrice','Cena za sztukę (zł)','number','required min="0" step="0.01" inputmode="decimal" placeholder="0,00"')}</div><div>${field('ciQty','Ilość','number','min="1" step="1" value="1" inputmode="numeric"')}</div></div><label>VAT</label><select id="ciVat"><option value="23">23%</option><option value="8">8%</option><option value="5">5%</option><option value="0">0%</option></select><p class="muted" style="font-size:12px">Produkt spoza menu – dopisze się tylko do tego rachunku.</p>`,async()=>{const name=$('#ciName').value.trim(),price=Number(String($('#ciPrice').value).replace(',','.')),qty=Math.max(1,parseInt($('#ciQty').value)||1);if(name.length<2)return alert('Wpisz nazwę produktu.');if(!(price>=0))return alert('Wpisz cenę.');const o=state.orders.find(x=>x.id===oid);if(!o||['paid','cancelled'].includes(o.status))return alert('Rachunek jest już zamknięty.');const row={id:uuid(),order_id:oid,menu_item_id:null,item_name:name,qty,unit_price:Math.round(price*100)/100,tax_rate:+$('#ciVat').value,created_at:new Date().toISOString()};state.orderItems.push(row);closeModal();rerenderOrder(oid);pushOp({type:'custom',oid,row});toast(`+${qty} ${name}`+(netDown?' – zapisane offline':''))});setTimeout(()=>$('#ciName')?.focus(),50)};
window.addItem=(oid,mid)=>{""")
rep("async function sendOp(op){\n","async function sendOp(op){\n if(op.type==='custom'){const r=await sb.from('pos_order_items').insert(op.row);if(!r.error||/23505|duplicate/i.test((r.error.code||'')+' '+r.error.message))return null;if(isNetErr(r.error))return r.error;return{message:/zamknięty/i.test(r.error.message)?`rachunek był już zamknięty – „${op.row.item_name}” nie został dopisany`:r.error.message}}\n")
rep("</style></head>",""".otherProd{background:#e0ad6726!important;border-color:#e0ad6788!important;color:#f0ca80!important;font-weight:800}
.shift.others,.entry.others{opacity:.62;filter:saturate(.6)}
.shift.mine{box-shadow:0 0 0 2px #f0ca80 inset}.entry.mine{background:#a8743e!important;color:#fff}
</style></head>""")
rep('Cafe Strych Manager <span>V5.1.2</span>','Cafe Strych Manager <span>V5.2</span>')
rep('Cafe Strych Manager <b>V5.1.2</b> • 03.11.2026','Cafe Strych Manager <b>V5.2</b> • 03.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
