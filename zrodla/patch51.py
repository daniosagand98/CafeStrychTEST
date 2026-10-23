# V4.6.1 – rabat działa też bez internetu (zapis w pamięci urządzenia, jak pozycje i płatność)
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:120]!r}')
    s = s.replace(old, new)
rep('<b>Cafe Strych Manager <span>V4.6</span></b>', '<b>Cafe Strych Manager <span>V4.6.1</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • POS działa bez internetu (zapis w pamięci telefonu), usuwanie rachunków z historii</small>',
    '<small>Aktualizacja: 23.10.2026 • POS i rabaty działają bez internetu (zapis w pamięci telefonu)</small>')
rep('<p>Cafe Strych Manager <b>V4.6</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.6.1</b> • 23.10.2026</p>')
rep("""window.saveDiscount=async(id,v)=>{v=Math.round(v*100)/100;const r=await sb.from('pos_orders').update({discount_pct:v,updated_at:new Date().toISOString()}).eq('id',id).select('id,discount_pct').single();if(r.error)return alert(/discount_pct|column|schema/i.test(r.error.message)?'Najpierw uruchom w Supabase plik sql/supabase_v4_3.sql (rabaty).':'Nie udało się zapisać rabatu:\\n'+r.error.message);const o=state.orders.find(x=>x.id===id);if(o)o.discount_pct=v;closeModal();rerenderOrder(id);toast(v?`Rabat ${pctTxt(v)} dodany`:'Rabat usunięty')};""",
    """window.saveDiscount=async(id,v)=>{v=Math.round(v*100)/100;const o=state.orders.find(x=>x.id===id);if(!o)return;o.discount_pct=v;closeModal();rerenderOrder(id);pushOp({type:'discount',oid:id,value:v});toast((v?`Rabat ${pctTxt(v)} dodany`:'Rabat usunięty')+(netDown?' – zapisany offline':''))};""")
rep(" if(op.type==='order'){", """ if(op.type==='discount'){const r=await sb.from('pos_orders').update({discount_pct:op.value,updated_at:op.ts}).eq('id',op.oid).select('id');if(r.error){if(isNetErr(r.error))return r.error;return{message:/zamknięty/i.test(r.error.message)?`rachunek był już zamknięty – rabat ${pctTxt(op.value)} nie został zapisany`:r.error.message}}return null}
 if(op.type==='order'){""")
rep("['saveDiscount','cancelOrder','editOrder','deleteHistoricalOrder','discountForm'].forEach(", "['cancelOrder','editOrder','deleteHistoricalOrder'].forEach(")
rep("Rachunki, dodawanie pozycji i płatności działają offline (zapisują się w pamięci urządzenia), ale rabat, anulowanie, edycja i usuwanie – dopiero po powrocie internetu.",
    "Rachunki, pozycje, rabaty i płatności działają offline (zapisują się w pamięci urządzenia), ale anulowanie, edycja i usuwanie rachunków – dopiero po powrocie internetu.")
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
