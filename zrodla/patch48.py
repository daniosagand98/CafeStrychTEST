# V4.4.1 – prostszy rachunek: bez Przygotowanie/Gotowe, Rabat obok Anuluj, małe okno rabatu; komunikat przy usuwaniu produktu
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:110]!r}')
    s = s.replace(old, new)

rep('<b>Cafe Strych Manager <span>V4.4</span></b>', '<b>Cafe Strych Manager <span>V4.4.1</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • Rabat procentowy na rachunku, szybszy POS, niedostępność w godzinach</small>',
    '<small>Aktualizacja: 23.10.2026 • Prostszy rachunek i rabat, poprawka usuwania produktów z menu</small>')
rep('<p>Cafe Strych Manager <b>V4.4</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.4.1</b> • 23.10.2026</p>')

# ---- przyciski rachunku: Płatność na całą szerokość, pod nią Rabat | Anuluj
rep("""<div class="actions ticketActions"><button class="ghost" onclick="orderStatus('${id}','preparing')">Przygotowanie</button><button class="ok" onclick="orderStatus('${id}','ready')">Gotowe</button><button class="primary" onclick="pay('${id}')">Płatność</button></div><button class="ghost discBtn" onclick="discountForm('${id}')">％ ${orderDiscount(id)?`Rabat ${pctTxt(orderDiscount(id))} – zmień`:'Dodaj rabat'}</button><button class="danger ticketCancel" onclick="cancelOrder('${id}')">Anuluj rachunek</button>`:'<p class="muted">Zmianę statusu i płatność zatwierdza kierownik lub administrator.</p>'""",
    """<div class="actions ticketActions"><button class="primary" onclick="pay('${id}')">Płatność</button><button class="ghost discBtn" onclick="discountForm('${id}')">％ ${orderDiscount(id)?`Rabat ${pctTxt(orderDiscount(id))}`:'Rabat'}</button><button class="danger" onclick="cancelOrder('${id}')">Anuluj rachunek</button></div>`:'<p class="muted">Płatność zatwierdza kierownik lub administrator.</p>'""")

# ---- okno rabatu: tylko pole z %
old = s[s.find("window.discountForm=id=>{"):s.find("window.saveDiscount=")]
if not old: raise SystemExit('discountForm not found')
s = s.replace(old, r"""window.discountForm=id=>{const o=state.orders.find(x=>x.id===id);if(!o||!canManage())return;if(['paid','cancelled'].includes(o.status))return alert('Rachunek jest zamknięty.');const cur=orderDiscount(id),sub=orderSubtotal(id);
 modal('Rabat',`<label>Rabat w %</label><input id="discPct" type="number" inputmode="decimal" min="0" max="100" step="0.5" value="${cur||''}" placeholder="np. 10" oninput="discPreview()"><p class="discLine" id="discLine"></p>`,async()=>{const raw=String($('#discPct').value).replace(',','.').trim(),v=raw===''?0:Number(raw);if(!(v>=0&&v<=100))return alert('Rabat musi być od 0 do 100%.');await saveDiscount(id,v)});
 $('#modal').classList.add('discModal');$('#modalSave').textContent=cur?'Zapisz (0 = bez rabatu)':'Zapisz';
 window.discPreview=()=>{const v=Math.min(100,Math.max(0,Number(String($('#discPct').value).replace(',','.'))||0)),t=Math.round(sub*(100-v))/100;$('#discLine').innerHTML=v?`Do zapłaty <b>${money(t)}</b> <span>(−${money(sub-t)})</span>`:`Do zapłaty <b>${money(sub)}</b>`};discPreview();setTimeout(()=>$('#discPct')?.focus(),50)};
""")
rep("$('#modal').classList.remove('shiftModalCompact','dayModal');", "$('#modal').classList.remove('shiftModalCompact','dayModal','discModal');$('#modalSave').textContent='Zapisz';")

# ---- usuwanie produktu: zrozumiały komunikat, gdy baza nie ma jeszcze poprawki v4.4
rep("if(r.error)return alert('Nie udało się usunąć produktu:\\n'+dbHint(r.error));",
    "if(r.error)return alert(/zamknięty/i.test(r.error.message||'')?'Ten produkt był na zamkniętym rachunku i baza nie pozwoliła go odpiąć.\\n\\nUruchom w Supabase plik sql/supabase_v4_4.sql – potem usuwanie zadziała (stare rachunki zostaną bez zmian).\\n\\nNa razie możesz go ukryć: „Edytuj” → odznacz „Aktywny”.':'Nie udało się usunąć produktu:\\n'+dbHint(r.error));")

# ---- CSS
rep('</style></head>', '''
/* V4.4.1 */
.ticketActions .discBtn,.ticketActions .danger{width:100%;margin:0}
#modal.discModal{width:min(92%,360px)}#modal.discModal #discPct{font-size:22px;text-align:center}
.discLine{margin:10px 0 2px;text-align:center;color:var(--muted);font-size:14px}.discLine b{color:#f0ca80;font-size:18px}.discLine span{color:#b9f4c8}
</style></head>''')
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
