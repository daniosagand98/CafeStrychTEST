import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
# --- etat: usunięcie
rep("<small>${esc(e.email||'Brak e-mail')} • ${e.contract_percent||100}% etatu</small>","<small>${esc(e.email||'Brak e-mail')}${e.phone?' • '+esc(e.phone):''}</small>")
rep("""<div>${field('empPct','Etat %','number','min="1" max="100" value="100"')}</div>""","")
rep("async()=>{const pct=+$('#empPct').value||100,p={full_name:","async()=>{const p={full_name:")
rep(",contract_percent:pct,weekly_target_hours:pct*.4,active:true}",",active:true}")
rep(";$('#empPct').value=r.contract_percent||100}},0)}","}},0)}")
rep("${e?`${esc(e.phone||'Brak telefonu')}<br>${e.contract_percent||100}% etatu`:'Konto nie jest połączone z pracownikiem.'}","${e?`${esc(e.phone||'Brak telefonu')}`:'Konto nie jest połączone z pracownikiem.'}")
# --- nawigacja: czat
rep('<button data-view="shopping">🛒<small>Zakupy</small></button></nav>','<button data-view="shopping">🛒<small>Zakupy</small></button><button data-view="chat">💬<small>Czat</small></button></nav>')
rep("({home, pos, schedule, bookings, shopping}[v]||home)()","({home, pos, schedule, bookings, shopping, chat:chatView}[v]||home)()")
rep("['pos','schedule','bookings','shopping'].forEach(v=>{const b=$(`[data-view=\"${v}\"]`);","['pos','schedule','bookings','shopping','chat'].forEach(v=>{const b=$(`[data-view=\"${v}\"]`);")
rep("['shopping','🛒','Lista zakupów','Wspólna lista rzeczy do kupienia']];","['shopping','🛒','Lista zakupów','Wspólna lista rzeczy do kupienia'],['chat','💬','Czat','Czat ogólny i wiadomości prywatne']];")
rep("""<section class="setting modSetting"><h3>Strona www</h3>""","""<section class="setting modSetting"><h3>Grafik</h3>${switchRow('swap_needs_approval','🔁','Zamiany zmian zatwierdza kierownik','Wyłączone: zamiana wchodzi do grafiku od razu, gdy druga osoba ją przyjmie')}</section><section class="setting modSetting"><h3>Strona www</h3>""")
# --- grafik: przyciski
rep("""${canManage()?'<button class="primary btnSm" onclick="shiftForm()">+ Zmiana</button>':'<button class="primary btnSm" onclick="availabilityForm()">+ Dyspozycyjność</button>'}</div><div class="scheduleNext">""",
    """${canManage()?'<button class="primary btnSm" onclick="shiftForm()">+ Zmiana</button>':'<button class="primary btnSm" onclick="availabilityForm()">+ Dyspozycyjność</button>'}</div><div class="schedActs">${canManage()?'<button class="ghost" onclick="scheduleProposal()">✨ Propozycja grafiku</button>':''}<button class="ghost" onclick="swapsView()">🔁 Zamiany <em id="swapCount" class="hide"></em></button></div><div class="scheduleNext">""")
rep("${mode==='week'?weekHtml(d):mode==='month'?monthHtml():availHtml(d)}`}","${mode==='week'?weekHtml(d):mode==='month'?monthHtml():availHtml(d)}`;updateSwapBadge()}")
# --- dzień: zamień / oddaj (własna, przyszła zmiana)
rep("""${canManage()?`<button type="button" class="ghost" onclick="shiftForm('${s.id}','${ds}')">Edytuj</button><button type="button" class="danger" onclick="deleteShift('${s.id}','${ds}')">Usuń</button>`:''}</div>`).join('')||'<div class="empty">Brak zmian tego dnia.</div>'}</div>`;""",
    """${canManage()?`<button type="button" class="ghost" onclick="shiftForm('${s.id}','${ds}')">Edytuj</button><button type="button" class="danger" onclick="deleteShift('${s.id}','${ds}')">Usuń</button>`:s.employee_id===myEmpId()&&ds>=iso(new Date())?(state.swaps.some(w=>w.shift_id===s.id&&['open','accepted'].includes(w.status))?'<span class="statusPill">🔁 prośba wysłana</span>':`<button type="button" class="ghost" onclick="swapForm('${s.id}')">🔁 Zamień / oddaj</button>`):''}</div>`).join('')||'<div class="empty">Brak zmian tego dnia.</div>'}</div>`;""")
# --- powiadomienia: otwieranie czatu / zamian
rep("if(u.searchParams.get('msg')&&state.user){state.page=null;state.inAdmin=false;return view('home')}",
    "if(u.searchParams.get('msg')&&state.user){state.page=null;state.inAdmin=false;return view('home')}const ch=u.searchParams.get('chat');if(ch&&state.user){state.inAdmin=false;return ch==='general'||ch.includes(state.user.id)?chatRoom(ch):chatView()}if(u.searchParams.get('swaps')&&state.user){state.inAdmin=false;$$('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view==='schedule'));return swapsView()}")
rep("if(q.get('day')||q.get('bugs')||q.get('msg')){","if(q.get('day')||q.get('bugs')||q.get('msg')||q.get('chat')||q.get('swaps')){")
# --- kod V5.3
js=open('zrodla/v53_client.js',encoding='utf-8').read()
rep("function openFromUrl(url){",js+"\nfunction openFromUrl(url){")
# --- CSS
rep("</style></head>","""
/* V5.3 czat, zamiany, propozycja */
nav button{position:relative}
.navBadge{position:absolute;top:2px;right:calc(50% - 22px);min-width:17px;height:17px;padding:0 4px;border-radius:9px;background:#e05a4a;color:#fff;font:800 10px/17px system-ui;font-style:normal}
.chatList{padding:4px}.chatItem{display:flex;align-items:center;gap:12px;width:100%;padding:12px 10px;border:0;border-bottom:1px solid #ffffff10;background:none;color:inherit;text-align:left;border-radius:12px}
.chatItem:last-child{border-bottom:0}.chatItem .grow{min-width:0}.chatItem small{display:block;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.chatItem.unread b{color:#f0ca80}.chatItem.unread small{color:var(--cream)}
.chatAv{flex:0 0 40px;height:40px;border-radius:50%;display:grid;place-items:center;background:#e0ad6726;color:#f0ca80;font:800 17px system-ui}
.chatMeta{display:flex;flex-direction:column;align-items:flex-end;gap:4px}.chatMeta em{font-style:normal;background:#e05a4a;color:#fff;border-radius:10px;padding:1px 7px;font-size:11px;font-weight:800}
.chatSec{margin:16px 2px 8px;font-size:15px;color:var(--muted)}
.msgs{display:flex;flex-direction:column;gap:2px;padding:4px 0 10px;min-height:40vh}
.msg{max-width:82%;align-self:flex-start;margin-top:8px}.msg.same{margin-top:2px}.msg.mine{align-self:flex-end;text-align:right}
.msgWho{display:block;margin:0 0 3px 10px;color:#f0ca80;font-weight:700;font-size:12px}
.bubble{display:inline-block;text-align:left;padding:9px 13px;border-radius:18px;background:#ffffff12;line-height:1.4;word-break:break-word;white-space:normal}
.msg.mine .bubble{background:linear-gradient(135deg,#b07a42,#8a5a30);color:#fff}
.msgTime{display:block;margin:3px 8px 0;color:var(--muted);font-size:10.5px}.msgTime a{color:var(--muted)}
.mention{color:#f0ca80}.mention.me{background:#f0ca80;color:#2a1a10;border-radius:5px;padding:0 3px}
.composer{position:sticky;bottom:calc(84px + env(safe-area-inset-bottom));display:flex;gap:8px;align-items:flex-end;padding:8px;margin:0 -6px;border-radius:18px;background:#1d100cf2;border:1px solid var(--line);z-index:5}
.composer textarea{flex:1;min-height:42px;max-height:140px;resize:none;margin:0;border-radius:14px}.composer>button{flex:0 0 46px;height:42px;padding:0;font-size:18px}
.mentionBox{position:absolute;left:8px;right:8px;bottom:calc(100% + 6px);display:flex;flex-direction:column;background:#24140f;border:1px solid var(--line);border-radius:14px;overflow:hidden;box-shadow:0 10px 30px #0008}
.mentionBox button{border:0;border-bottom:1px solid #ffffff10;background:none;color:var(--cream);text-align:left;padding:11px 14px;border-radius:0;font-weight:700}
.schedActs{display:flex;gap:8px;margin:-4px 0 10px}.schedActs button{flex:1;position:relative}
.schedActs em{font-style:normal;background:#e05a4a;color:#fff;border-radius:10px;padding:1px 7px;font-size:11px;margin-left:4px}
.swapCard{flex-wrap:wrap;align-items:flex-start}.swapCard small{display:block;margin-top:3px}.swNote{font-style:italic;color:var(--cream)!important}
.swBtns{display:flex;gap:6px;flex-wrap:wrap;width:100%;margin-top:8px}.swBtns button{flex:1;min-width:110px}
.warnPill{background:#e0ad6733!important;color:#f0ca80!important}.badPill{background:#e0605022!important;color:#ffb3a8!important}
.propTpl{padding:12px 14px}.propTpl summary{cursor:pointer}.tplRow{display:grid;grid-template-columns:110px 1fr;gap:8px;align-items:center;margin:6px 0}.tplRow input{margin:0}
.propSum{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;margin:4px 2px 6px}.propSum .bad{color:#ffb3a8;font-weight:700}
.propLoad{display:flex;flex-wrap:wrap;gap:6px 12px;margin:0 2px 10px;font-size:12px;color:var(--muted)}
.propDay{padding:10px 12px;margin-bottom:10px}.propDay h3{margin:0 0 6px;font-size:15px}
.propRow{display:grid;grid-template-columns:28px 92px minmax(0,1fr);gap:8px;align-items:center;padding:6px 0;border-top:1px solid #ffffff10}
.propRow.done{grid-template-columns:120px 1fr;color:var(--muted)}.propRow.none select{border-color:#e0605088}.propRow select{margin:0;font-size:13px}
.pT{font:700 13px ui-monospace,Menlo,monospace}.pChk input{width:20px;height:20px}
.propSave{position:sticky;bottom:calc(84px + env(safe-area-inset-bottom));width:100%;z-index:4;box-shadow:0 10px 30px #000a}
@media(max-width:420px){.propRow{grid-template-columns:24px 1fr}.propRow select{grid-column:1/-1}}
</style></head>""")
rep('Cafe Strych Manager <span>V5.2</span>','Cafe Strych Manager <span>V5.3</span>')
rep('Cafe Strych Manager <b>V5.2</b> • 03.11.2026','Cafe Strych Manager <b>V5.3</b> • 03.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
