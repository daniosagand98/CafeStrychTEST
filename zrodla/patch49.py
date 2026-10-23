# V4.5 – admin może trwale usunąć rachunek z historii (z ostrzeżeniem o wpływie na utarg)  – wymaga sql/supabase_v4_5.sql
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:110]!r}')
    s = s.replace(old, new)

rep('<b>Cafe Strych Manager <span>V4.4.1</span></b>', '<b>Cafe Strych Manager <span>V4.5</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • Prostszy rachunek i rabat, poprawka usuwania produktów z menu</small>',
    '<small>Aktualizacja: 23.10.2026 • Usuwanie rachunków z historii (admin), prostszy rachunek i rabat</small>')
rep('<p>Cafe Strych Manager <b>V4.4.1</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.5</b> • 23.10.2026</p>')

# historia: opis + przycisk Usuń dla admina (obok Anuluj)
rep('<small class="muted">Opłaconych rachunków się nie usuwa – administrator może je anulować z podaniem powodu</small>',
    '<small class="muted">${isAdmin()?\'Anuluj – rachunek zostaje w historii, bez wpływu na utarg. Usuń – znika na zawsze, także z podsumowań.\':\'Opłacone rachunki może anulować lub usunąć administrator.\'}</small>')
rep("""${!c&&isAdmin()?`<button class="danger historyDelete" onclick="cancelOrder('${o.id}')">Anuluj</button>`:''}</div>`}""",
    """${isAdmin()?`<div class="histBtns">${!c?`<button class="ghost historyDelete" onclick="cancelOrder('${o.id}')">Anuluj</button>`:''}<button class="danger historyDelete" onclick="deleteHistoricalOrder('${o.id}')">Usuń</button></div>`:''}</div>`}""")
rep("window.deleteHistoricalOrder=id=>cancelOrder(id);", r"""window.deleteHistoricalOrder=id=>{if(!isAdmin())return alert('Rachunek z historii może usunąć tylko administrator.');const o=state.orders.find(x=>x.id===id);if(!o)return;const paid=state.payments.filter(p=>p.order_id===id).reduce((n,p)=>n+Number(p.amount||0),0),when=new Date(o.closed_at||o.created_at),name=esc(o.customer_name||state.tables.find(t=>t.id===o.table_id)?.label||o.order_no||'Rachunek');
 modal('⚠️ Usunąć rachunek na zawsze?',`<div class="cancelInfo"><b>${name}</b><span>${money(paid||orderTotal(id))}</span></div><p class="muted" style="margin:4px 0 10px">${when.toLocaleString('pl-PL',{dateStyle:'short',timeStyle:'short'})} • ${statusLabel(o.status)}</p><div class="delWarn"><b>To usunięcie wpłynie na podsumowania.</b><ul><li>Kwota zniknie z utargu dnia, miesiąca i roku${o.status==='paid'?` (−${money(paid||orderTotal(id))})`:''}.</li><li>Wcześniej spisane lub wydrukowane podsumowania (np. raport z kasy fiskalnej, rozliczenie zmiany) mogą się już <b>nie zgadzać</b> z aplikacją.</li><li>Tego nie da się cofnąć. W „System i logi” zostanie wpis, kto i kiedy usunął rachunek.</li></ul>${isCancelled(o)?'':'<p>Jeśli rachunek ma tylko nie liczyć się do utargu, lepiej go <b>anulować</b> – zostanie w historii z powodem.</p>'}</div><label class="check"><input id="delConfirm" type="checkbox"> Rozumiem, usuń ten rachunek</label>`,async()=>{if(!$('#delConfirm').checked)return alert('Zaznacz „Rozumiem, usuń ten rachunek”.');const r=await sb.rpc('pos_delete_order',{p_order:id});if(r.error)return alert(/PGRST202|function|schema cache/i.test((r.error.code||'')+' '+r.error.message)?'Najpierw uruchom w Supabase plik sql/supabase_v4_5.sql (usuwanie rachunków z historii).':'Nie udało się usunąć rachunku:\n'+r.error.message);state.orders=state.orders.filter(x=>x.id!==id);state.payments=state.payments.filter(p=>p.order_id!==id);state.orderItems=state.orderItems.filter(i=>i.order_id!==id);closeModal();orderHistory();toast('Rachunek usunięty z historii')});
 $('#modalSave').textContent='Usuń na zawsze';$('#modalSave').classList.add('dangerSave')};""")
rep("$('#modal').classList.remove('shiftModalCompact','dayModal','discModal');$('#modalSave').textContent='Zapisz';",
    "$('#modal').classList.remove('shiftModalCompact','dayModal','discModal');$('#modalSave').textContent='Zapisz';$('#modalSave').classList.remove('dangerSave');")
rep('</style></head>', '''
/* V4.5 – usuwanie z historii */
.histBtns{position:absolute;right:10px;top:10px;z-index:3;display:flex;flex-direction:column;gap:6px}.histBtns .historyDelete{position:static;width:auto;min-width:76px;padding:7px 10px}.historyOrder:has(.histBtns) .historyOrderContent{padding-right:96px}
.delWarn{padding:12px 14px;border-radius:14px;background:#ee70650f;border:1px solid #ee706555;color:var(--cream);font-size:13.5px;line-height:1.5;margin-bottom:12px}
.delWarn b{color:#ffb9b1}.delWarn ul{margin:6px 0 0;padding-left:18px}.delWarn li{margin:3px 0}.delWarn p{margin:8px 0 0;color:var(--muted)}
#modalSave.dangerSave{background:linear-gradient(135deg,#b4473d,#e0705f)!important;color:#fff!important}
</style></head>''')
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
