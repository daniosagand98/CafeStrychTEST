# V3.8 – anulowanie rachunków zamiast usuwania (nakładane na zbudowany panel/index.html V3.7)
#   python3 zrodla/patch38.py panel/index.html panel/index.html
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        raise SystemExit(f'Expected {count} got {n}: {old[:100]!r}')
    s = s.replace(old, new)

# ---- stopka / wersja
rep('<b>Cafe Strych Manager <span>V3.7</span></b>', '<b>Cafe Strych Manager <span>V3.8</span></b>')
rep('<small>Aktualizacja: 21.10.2026 • Zatwierdzanie nowych kont, rezerwacja całej sali, zabezpieczenia bazy</small>',
    '<small>Aktualizacja: 21.10.2026 • Anulowanie rachunków zamiast usuwania, zatwierdzanie kont, rezerwacja całej sali</small>')
rep('<p>Cafe Strych Manager <b>V3.7</b> • 21.10.2026</p>', '<p>Cafe Strych Manager <b>V3.8</b> • 21.10.2026</p>')

# ---- CSS
rep('</style></head>', '''
/* V3.8: anulowane rachunki */
.cancelledOrder{opacity:.72;border-style:dashed!important}
.cancelledOrder strong{text-decoration:line-through;color:var(--muted)!important}
.cancelPill{display:inline-flex;align-self:flex-start;margin-top:6px;padding:4px 8px;border-radius:999px;background:#ee70651c;color:#ffb9b1;border:1px solid #ee706555;font-size:11px;font-weight:800;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cancelInfo{display:flex;justify-content:space-between;gap:10px;margin:10px 0;padding:12px 14px;border-radius:12px;background:#fff1da0c;border:1px solid #fff1da18}.cancelInfo span{color:#f0ca80;font-weight:800}
.closedNote{padding:10px 12px;border-radius:12px;background:#fff1da0a;color:var(--muted);font-size:13px;line-height:1.5}.closedNote b{color:var(--cream)}
.closedNote.cancelled{background:#ee706514;border:1px solid #ee706544;color:#ffd6d1}
.salesRow.cancelled{opacity:.6}.salesRow.cancelled strong{text-decoration:line-through}
.ticketCancel{width:100%;margin-top:8px;text-align:center}
</style></head>''')

# ---- otwarty rachunek: anulowanie (kierownik), zamknięty: opis + anulowanie opłaconego (admin)
rep('''const actions=closed?`<p class="muted">Rachunek ${statusLabel(o.status).toLowerCase()}.</p>`:canManage()?`<div class="actions ticketActions"><button class="ghost" onclick="orderStatus('${id}','preparing')">Przygotowanie</button><button class="ok" onclick="orderStatus('${id}','ready')">Gotowe</button><button class="primary" onclick="pay('${id}')">Płatność</button></div>`:''',
    '''const actions=closed?closedOrderInfo(o):canManage()?`<div class="actions ticketActions"><button class="ghost" onclick="orderStatus('${id}','preparing')">Przygotowanie</button><button class="ok" onclick="orderStatus('${id}','ready')">Gotowe</button><button class="primary" onclick="pay('${id}')">Płatność</button></div><button class="danger ticketCancel" onclick="cancelOrder('${id}')">Anuluj rachunek</button>`:''')

# ---- nowe funkcje (przed linią z wrapperami widoków)
CODE = r"""
/* ===================== V3.8: anulowanie rachunków zamiast usuwania ===================== */
function isCancelled(o){return o?.status==='cancelled'}
function personName(uid){return state.profiles.find(p=>p.id===uid)?.full_name||''}
function closedOrderInfo(o){const when=o.cancelled_at||o.closed_at;if(isCancelled(o))return `<div class="closedNote cancelled"><b>Rachunek anulowany</b>${when?` • ${new Date(when).toLocaleString('pl-PL',{dateStyle:'short',timeStyle:'short'})}`:''}${o.cancelled_by&&personName(o.cancelled_by)?` • ${esc(personName(o.cancelled_by))}`:''}${o.cancel_reason?`<br>Powód: ${esc(o.cancel_reason)}`:''}<br>Nie jest liczony do utargu.</div>`;return `<div class="closedNote"><b>Rachunek opłacony</b>${when?` • ${new Date(when).toLocaleString('pl-PL',{dateStyle:'short',timeStyle:'short'})}`:''}</div>${isAdmin()?`<button class="danger ticketCancel" onclick="cancelOrder('${o.id}')">Anuluj opłacony rachunek</button>`:''}`}
window.cancelOrder=id=>{const o=state.orders.find(x=>x.id===id);if(!o)return;if(isCancelled(o))return alert('Ten rachunek jest już anulowany.');const paid=o.status==='paid';if(paid&&!isAdmin())return alert('Opłacony rachunek może anulować tylko administrator.');if(!paid&&!canManage())return alert('Rachunek może anulować kierownik lub administrator.');
 modal('Anuluj rachunek',`<p class="muted">${paid?'Rachunek jest opłacony. Po anulowaniu zostanie w historii z dopiskiem <b>ANULOWANY</b>, a jego kwota nie będzie liczona do utargu. Tej operacji nie można cofnąć.':'Rachunek zostanie zamknięty jako anulowany i zostanie w historii.'}</p><div class="cancelInfo"><b>${esc(o.customer_name||state.tables.find(t=>t.id===o.table_id)?.label||o.order_no||'Rachunek')}</b><span>${money(orderTotal(id))}</span></div><label>Powód anulowania</label><textarea id="cancelReason" required maxlength="300" placeholder="np. pomyłka przy nabijaniu, zwrot dla gościa…"></textarea>`,async()=>{const reason=$('#cancelReason').value.trim();if(reason.length<3)return alert('Wpisz powód anulowania.');const r=await saveRow('pos_orders',{status:'cancelled',cancel_reason:reason,cancelled_at:new Date().toISOString(),cancelled_by:state.user.id,updated_at:new Date().toISOString()},id);if(r.error)return alert('Nie udało się anulować rachunku:\n'+r.error.message);if(!r.data?.length)return alert('Brak uprawnień do anulowania tego rachunku.');closeModal();await loadAll();if(state.page)state.page();else if($('#menuGrid')||$('.ticket'))openOrder(id);else orderHistory();toast('Rachunek anulowany')})};
window.deleteHistoricalOrder=id=>cancelOrder(id);
window.orderHistory=(f=state.histFilter||'all')=>{state.histFilter=f;const rows=state.orders.filter(o=>f==='all'?['paid','cancelled'].includes(o.status):o.status===f).sort((a,b)=>String(b.closed_at||b.created_at).localeCompare(String(a.closed_at||a.created_at)));content().innerHTML=`<div class="toolbar"><div>${state.inAdmin?'':'<button class="ghost" onclick="pos()">← POS</button>'}<h2>Historia rachunków</h2><small class="muted">Opłaconych rachunków się nie usuwa – administrator może je anulować z podaniem powodu</small></div></div><div class="mode">${[['all','Wszystkie'],['paid','Opłacone'],['cancelled','Anulowane']].map(([k,l])=>`<button class="ghost ${f===k?'active':''}" onclick="orderHistory('${k}')">${l}</button>`).join('')}</div><div class="orderGrid">${rows.map(o=>{const c=isCancelled(o);return `<div class="order historyOrder ${c?'cancelledOrder':''}"><button class="historyOrderContent" onclick="openOrder('${o.id}')"><b>${esc(o.customer_name||state.tables.find(t=>t.id===o.table_id)?.label||o.order_no||'Rachunek')}</b><small>${new Date(o.cancelled_at||o.closed_at||o.created_at).toLocaleString('pl-PL',{dateStyle:'short',timeStyle:'short'})}</small>${c?`<span class="cancelPill" title="${esc(o.cancel_reason||'')}">ANULOWANY${o.cancel_reason?' • '+esc(o.cancel_reason):''}</span>`:''}<strong>${money(orderTotal(o.id))}</strong></button>${!c&&isAdmin()?`<button class="danger historyDelete" onclick="cancelOrder('${o.id}')">Anuluj</button>`:''}</div>`}).join('')||'<div class="empty">Brak rachunków.</div>'}</div>`};
window.salesReport=(date=iso(new Date()))=>{if(!canManage())return;const cancelledIds=new Set(state.orders.filter(isCancelled).map(o=>o.id)),all=state.payments.filter(p=>day(p.created_at)===date),payments=all.filter(p=>!cancelledIds.has(p.order_id)),canc=all.filter(p=>cancelledIds.has(p.order_id)),sum=l=>l.reduce((n,p)=>n+Number(p.amount||0),0),method=m=>sum(payments.filter(p=>p.method===m)),label=m=>({card:'Karta',cash:'Gotówka',blik:'BLIK',transfer:'Przelew'}[m]||m);content().innerHTML=`<div class="toolbar"><div><button class="ghost" onclick="pos()">← POS</button><h2>Utarg dzienny</h2></div><div><label>Wybierz dzień</label><input type="date" value="${date}" onchange="salesReport(this.value)"></div></div><div class="salesKpis"><div class="kpi"><span>Razem</span><strong>${money(sum(payments))}</strong><small>${payments.length} płatności${canc.length?` • bez ${canc.length} anulowanych (${money(sum(canc))})`:''}</small></div><div class="kpi"><span>Karta</span><strong>${money(method('card'))}</strong></div><div class="kpi"><span>Gotówka</span><strong>${money(method('cash'))}</strong></div><div class="kpi"><span>BLIK</span><strong>${money(method('blik'))}</strong></div><div class="kpi"><span>Przelew</span><strong>${money(method('transfer'))}</strong></div></div><section class="panel"><h3>Płatności z wybranego dnia</h3><div class="salesTable">${all.map(p=>{const o=state.orders.find(x=>x.id===p.order_id),c=cancelledIds.has(p.order_id);return `<div class="salesRow ${c?'cancelled':''}"><div><b>${esc(o?.customer_name||o?.order_no||'Rachunek')}${c?' <span class="cancelPill">ANULOWANY</span>':''}</b><small class="muted">${new Date(p.created_at).toLocaleTimeString('pl-PL',{hour:'2-digit',minute:'2-digit'})} • ${esc(label(p.method))}${c&&o?.cancel_reason?` • ${esc(o.cancel_reason)}`:''}</small></div><strong>${money(p.amount)}</strong></div>`}).join('')||'<div class="empty">Brak płatności w tym dniu.</div>'}</div></section>`};
"""
marker = "['newsCenter','employeesView','messagesCenter'"
assert s.count(marker) == 1
s = s.replace(marker, CODE.strip() + '\n' + marker)

open(dst, 'w', encoding='utf-8').write(s)
print('OK', len(s))
