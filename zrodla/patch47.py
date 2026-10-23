# V4.4 – rabat procentowy na rachunku (wymaga sql/supabase_v4_3.sql)
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:110]!r}')
    s = s.replace(old, new)

rep('<b>Cafe Strych Manager <span>V4.3.1</span></b>', '<b>Cafe Strych Manager <span>V4.4</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • Prostszy Start pracownika, niedostępność w godzinach, szybszy POS</small>',
    '<small>Aktualizacja: 23.10.2026 • Rabat procentowy na rachunku, szybszy POS, niedostępność w godzinach</small>')
rep('<p>Cafe Strych Manager <b>V4.3.1</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.4</b> • 23.10.2026</p>')

# ---- sumy: przed i po rabacie
rep("function orderTotal(id){return orderItems(id).reduce((n,x)=>n+Number(x.qty||0)*Number(x.unit_price||0),0)}",
    "function orderSubtotal(id){return orderItems(id).reduce((n,x)=>n+Number(x.qty||0)*Number(x.unit_price||0),0)}\n"
    "function orderDiscount(id){const d=Number(state.orders.find(o=>o.id===id)?.discount_pct||0);return d>0&&d<=100?d:0}\n"
    "function orderTotal(id){const sub=orderSubtotal(id),d=orderDiscount(id);return d?Math.round(sub*(100-d))/100:sub}\n"
    "const pctTxt=d=>String(+Number(d).toFixed(2)).replace('.',',')+'%';")

# ---- rachunek: wiersze rabatu + przycisk
rep('<div class="row ticketSum"><span>Razem</span><strong class="total">${money(total)}</strong></div>',
    '${orderDiscount(id)?`<div class="row discRow"><span>Suma</span><span>${money(orderSubtotal(id))}</span></div><div class="row discRow disc"><span>Rabat ${pctTxt(orderDiscount(id))}</span><span>−${money(orderSubtotal(id)-total)}</span></div>`:\'\'}<div class="row ticketSum"><span>Razem${orderDiscount(id)?\' po rabacie\':\'\'}</span><strong class="total">${money(total)}</strong></div>')
rep("""<button class="primary" onclick="pay('${id}')">Płatność</button></div>""",
    """<button class="primary" onclick="pay('${id}')">Płatność</button></div><button class="ghost discBtn" onclick="discountForm('${id}')">％ ${orderDiscount(id)?`Rabat ${pctTxt(orderDiscount(id))} – zmień`:'Dodaj rabat'}</button>""")
# lista rachunków: znaczek rabatu
rep('<span class="statusPill">${statusLabel(o.status)}</span>',
    '<span class="statusPill">${statusLabel(o.status)}</span>${orderDiscount(o.id)?`<span class="statusPill discPill">−${pctTxt(orderDiscount(o.id))}</span>`:\'\'}')
# płatność: pokazuje sumę i rabat
rep('<div class="total" style="text-align:center">${money(orderTotal(id))}</div>',
    '${orderDiscount(id)?`<p class="payDisc">Suma ${money(orderSubtotal(id))} • rabat ${pctTxt(orderDiscount(id))} (−${money(orderSubtotal(id)-orderTotal(id))})</p>`:\'\'}<div class="total" style="text-align:center">${money(orderTotal(id))}</div>')
# utarg dnia: przy płatności widać rabat
rep("${esc(label(p.method))}${c&&o?.cancel_reason?",
    "${esc(label(p.method))}${o&&Number(o.discount_pct)>0?` • rabat ${pctTxt(o.discount_pct)}`:''}${c&&o?.cancel_reason?")

# ---- okno rabatu
rep("window.toggleTicket=", r"""window.discountForm=id=>{const o=state.orders.find(x=>x.id===id);if(!o||!canManage())return;if(['paid','cancelled'].includes(o.status))return alert('Rachunek jest zamknięty.');const cur=orderDiscount(id),sub=orderSubtotal(id);
 modal('Rabat na rachunek',`<p class="muted">Rabat procentowy od całego rachunku. Kwota do zapłaty i utarg będą już po rabacie.</p><div class="discChips">${[5,10,15,20,25,30,50,100].map(p=>`<button type="button" class="ghost ${p===cur?'active':''}" onclick="setDiscPreview(${p})">${p}%</button>`).join('')}</div><label>Rabat w %</label><input id="discPct" type="number" inputmode="decimal" min="0" max="100" step="0.5" value="${cur||''}" placeholder="np. 10" oninput="setDiscPreview(this.value,true)"><div class="discPreview" id="discPreview"></div>${cur?`<button type="button" class="danger" style="margin-top:10px" onclick="saveDiscount('${id}',0)">Usuń rabat</button>`:''}`,async()=>{const v=Number(String($('#discPct').value).replace(',','.'));if(!(v>=0&&v<=100))return alert('Rabat musi być od 0 do 100%.');await saveDiscount(id,v)});
 window.setDiscPreview=(p,typed)=>{const v=Math.min(100,Math.max(0,Number(String(p).replace(',','.'))||0));if(!typed)$('#discPct').value=v;$$('.discChips button').forEach(b=>b.classList.toggle('active',parseFloat(b.textContent)===v));$('#discPreview').innerHTML=v?`<span>Suma ${money(sub)}</span><span>Rabat −${money(sub-Math.round(sub*(100-v))/100)}</span><b>Do zapłaty ${money(Math.round(sub*(100-v))/100)}</b>`:`<span>Bez rabatu: ${money(sub)}</span>`};setDiscPreview(cur||0,true)};
window.saveDiscount=async(id,v)=>{v=Math.round(v*100)/100;const r=await sb.from('pos_orders').update({discount_pct:v,updated_at:new Date().toISOString()}).eq('id',id).select('id,discount_pct').single();if(r.error)return alert(/discount_pct|column|schema/i.test(r.error.message)?'Najpierw uruchom w Supabase plik sql/supabase_v4_3.sql (rabaty).':'Nie udało się zapisać rabatu:\n'+r.error.message);const o=state.orders.find(x=>x.id===id);if(o)o.discount_pct=v;closeModal();rerenderOrder(id);toast(v?`Rabat ${pctTxt(v)} dodany`:'Rabat usunięty')};
window.toggleTicket=""")

# ---- CSS
rep('</style></head>', '''
/* V4.4 – rabat */
.discRow{font-size:13px;color:var(--muted);margin-top:4px}.discRow.disc{color:#b9f4c8}
.discBtn{width:100%;margin-top:8px}
.discPill{background:#71c98a22!important;color:#b9f4c8!important;margin-left:4px}
.discChips{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:10px 0 12px}.discChips button{padding:10px 0}.discChips .active{background:#e0ad6730;border-color:#e0ad67aa}
.discPreview{display:flex;flex-direction:column;gap:3px;margin-top:10px;padding:12px;border-radius:12px;background:#fff1da0a;border:1px solid #fff1da18;font-size:13px;color:var(--muted)}.discPreview b{font-size:17px;color:#f0ca80}
.payDisc{text-align:center;font-size:13px;color:#b9f4c8;margin:0 0 4px}
</style></head>''')
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
