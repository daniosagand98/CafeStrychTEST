# V4.0 – admin włącza/wyłącza rezerwacje ze strony www i całe moduły (POS, Grafik, Rezerwacje, Zakupy)
#   python3 zrodla/patch41.py panel/index.html panel/index.html     (wymaga sql/supabase_v4_0.sql)
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:110]!r}')
    s = s.replace(old, new)

# ---- stopka / wersja
rep('<b>Cafe Strych Manager <span>V3.9.1</span></b>', '<b>Cafe Strych Manager <span>V4.0</span></b>')
rep('<small>Aktualizacja: 22.10.2026 • Strona: social media jako ikonki z linkami (bez podglądu postów)</small>',
    '<small>Aktualizacja: 23.10.2026 • Admin włącza/wyłącza moduły i rezerwacje ze strony www</small>')
rep('<p>Cafe Strych Manager <b>V3.9.1</b> • 22.10.2026</p>', '<p>Cafe Strych Manager <b>V4.0</b> • 23.10.2026</p>')

# ---- uprawnienia: wyłączony moduł znika wszystkim poza adminem
rep("function allowed(v){if(v==='home'||canManage())return true;",
    "const MODULES=[['pos','🧾','POS','Rachunki, sprzedaż, utarg dzienny'],['schedule','📅','Grafik','Zmiany i dyspozycyjność pracowników'],['bookings','📖','Rezerwacje','Rezerwacje stolików i sal w aplikacji'],['shopping','🛒','Lista zakupów','Wspólna lista rzeczy do kupienia']];\n"
    "function moduleOn(v){return state.settings?.['module_'+v]!==false}\n"
    "function allowed(v){if(v==='home')return true;if(!moduleOn(v)&&!isAdmin())return false;if(canManage())return true;")
rep("['pos','schedule','bookings','shopping'].forEach(v=>$(`[data-view=\"${v}\"]`).classList.toggle('hide',!allowed(v)))}",
    "['pos','schedule','bookings','shopping'].forEach(v=>{const b=$(`[data-view=\"${v}\"]`);b.classList.toggle('hide',!allowed(v));b.classList.toggle('modOff',isAdmin()&&!moduleOn(v));b.title=isAdmin()&&!moduleOn(v)?'Moduł wyłączony – widzi go tylko administrator':''})}")

# ---- pulpit kierownika: tylko włączone moduły
rep("""<div class="actions"><button class="ghost" onclick="shoppingForm()">+ Dodaj do zakupów</button><button class="primary" onclick="newOrder()">+ Nowy rachunek</button></div></div><div class="panel nextShiftPanel" style="margin-bottom:12px"><small class="muted">Następna zmiana</small><b>${nextShiftText()}</b></div><div class="grid kpis"><button class="kpi" onclick="pos()"><span>Sprzedaż dzisiaj</span><strong>${money(revenue)}</strong><small>${paid.length} rachunków</small></button><button class="kpi" onclick="pos()"><span>Otwarte rachunki</span><strong>${open.length}</strong><small>POS</small></button><button class="kpi" onclick="bookings()"><span>Rezerwacje</span><strong>${res.length}</strong><small>${res.reduce((n,b)=>n+Number(b.guests_count||0),0)} gości</small></button><button class="kpi" onclick="employeesView()"><span>Pracownicy</span><strong>${state.employees.length}</strong><small>aktywnych</small></button></div><div class="grid two"><section class="panel"><div class="sectionHead startOrders"><h3>Aktualne rachunki</h3><button class="ghost startOrdersBtn" onclick="pos()">Otwórz POS</button></div><div class="cards">${open.slice(0,8).map(orderCard).join('')||'<div class="empty">Brak otwartych rachunków.</div>'}</div></section><section class="panel"><h3>Dzisiejsze rezerwacje</h3><div class="cards">${res.map(bookingCard).join('')||'<div class="empty">Brak rezerwacji.</div>'}</div></section></div>`}""",
    """<div class="actions">${P.shopping?'<button class="ghost" onclick="shoppingForm()">+ Dodaj do zakupów</button>':''}${P.pos?'<button class="primary" onclick="newOrder()">+ Nowy rachunek</button>':''}</div></div>${P.schedule?`<div class="panel nextShiftPanel" style="margin-bottom:12px"><small class="muted">Następna zmiana</small><b>${nextShiftText()}</b></div>`:''}<div class="grid kpis">${P.pos?`<button class="kpi" onclick="pos()"><span>Sprzedaż dzisiaj</span><strong>${money(revenue)}</strong><small>${paid.length} rachunków</small></button><button class="kpi" onclick="pos()"><span>Otwarte rachunki</span><strong>${open.length}</strong><small>POS</small></button>`:''}${P.bookings?`<button class="kpi" onclick="bookings()"><span>Rezerwacje</span><strong>${res.length}</strong><small>${res.reduce((n,b)=>n+Number(b.guests_count||0),0)} gości</small></button>`:''}<button class="kpi" onclick="employeesView()"><span>Pracownicy</span><strong>${state.employees.length}</strong><small>aktywnych</small></button></div>${P.pos||P.bookings?`<div class="grid ${P.pos&&P.bookings?'two':''}">${P.pos?`<section class="panel"><div class="sectionHead startOrders"><h3>Aktualne rachunki</h3><button class="ghost startOrdersBtn" onclick="pos()">Otwórz POS</button></div><div class="cards">${open.slice(0,8).map(orderCard).join('')||'<div class="empty">Brak otwartych rachunków.</div>'}</div></section>`:''}${P.bookings?`<section class="panel"><h3>Dzisiejsze rezerwacje</h3><div class="cards">${res.map(bookingCard).join('')||'<div class="empty">Brak rezerwacji.</div>'}</div></section>`:''}</div>`:''}`}""")
rep("function home(){if(!canManage())return employeeHome();const today=iso(new Date()),",
    "function home(){if(!canManage())return employeeHome();const P={pos:allowed('pos'),schedule:allowed('schedule'),bookings:allowed('bookings'),shopping:allowed('shopping')},today=iso(new Date()),")

# ---- start pracownika: bez grafiku nie pokazujemy zmian ani dyspozycyjności
rep("""<small class="muted">Panel pracownika</small></div><button class="ghost" onclick="${goAvail}">📅 Moja dyspozycyjność</button></div><div class="grid two"><section class="panel"><h3>Najbliższa zmiana</h3>${future[0]?`<strong>${future[0].shift_date}</strong><p>${future[0].start_time.slice(0,5)}–${future[0].end_time.slice(0,5)}</p>`:'<p class="muted">Brak zaplanowanej zmiany.</p>'}</section><section class="panel"><h3>Godziny w miesiącu</h3><strong class="total">${fmtH(h)}</strong></section>""",
    """<small class="muted">Panel pracownika</small></div>${moduleOn('schedule')?`<button class="ghost" onclick="${goAvail}">📅 Moja dyspozycyjność</button>`:''}</div><div class="grid two">${moduleOn('schedule')?`<section class="panel"><h3>Najbliższa zmiana</h3>${future[0]?`<strong>${future[0].shift_date}</strong><p>${future[0].start_time.slice(0,5)}–${future[0].end_time.slice(0,5)}</p>`:'<p class="muted">Brak zaplanowanej zmiany.</p>'}</section><section class="panel"><h3>Godziny w miesiącu</h3><strong class="total">${fmtH(h)}</strong></section>`:''}""")

# ---- link z powiadomienia o rezerwacji
rep("view('bookings');if(canManage()||allowed('bookings'))", "if(!allowed('bookings'))return view('home');view('bookings');if(allowed('bookings'))")

# ---- na żywo: zmiana ustawień od razu u wszystkich
rep("reloadTimer=setTimeout(async()=>{await loadAll();refreshNext();",
    "reloadTimer=setTimeout(async()=>{await loadAll();refreshNext();applyRole();const av=$('[data-view].active')?.dataset.view;if(av&&!allowed(av)){state.page=null;state.inAdmin=false;return view('home')}")
rep("'site_news','bug_reports','site_social_posts'].forEach(t=>sb.channel(", "'site_news','bug_reports','site_social_posts','cafe_settings'].forEach(t=>sb.channel(")

# ---- ustawienia admina: przełączniki
rep("if(r.error)return alert(r.error.message);state.settings=p;admin('overview')",
    "if(r.error)return alert(r.error.message);state.settings={...state.settings,...p};admin('overview')")
rep("function adminOverview(p){", r'''window.toggleSetting=async(key,label)=>{if(!isAdmin())return;if(!(key in state.settings))return alert('Najpierw uruchom w Supabase plik sql/supabase_v4_0.sql (SQL Editor → Run), potem odśwież aplikację.');const val=state.settings[key]===false,
 msg=key==='www_bookings'?(val?'Włączyć przyjmowanie rezerwacji ze strony www?':'Wyłączyć rezerwacje ze strony www?\n\nNa stronie po kliknięciu „Rezerwacja” goście zobaczą informację, że rezerwacje przyjmujecie tylko telefonicznie, i numer telefonu.'):(val?`Włączyć moduł „${label}”?`:`Wyłączyć moduł „${label}”?\n\nZniknie z kont pracowników i kierowników (dane zostają w bazie). Ty jako administrator nadal go widzisz.`);
 if(!confirm(msg))return;const r=await sb.from('cafe_settings').update({[key]:val,updated_at:new Date().toISOString()}).eq('id',state.settings.id||1);if(r.error)return alert(/column|schema/i.test(r.error.message)?'Brak kolumn w bazie – uruchom sql/supabase_v4_0.sql.':r.error.message);state.settings={...state.settings,[key]:val};applyRole();toast(`${label}: ${val?'włączone':'wyłączone'}`);admin('overview')};
function switchRow(key,ic,name,desc,extra=''){const on=state.settings[key]!==false;return `<div class="modRow ${on?'':'off'}"><span class="modIc">${ic}</span><div class="grow"><b>${name}</b><small>${desc}</small>${extra}</div><button type="button" class="modSwitch ${on?'on':''}" role="switch" aria-checked="${on}" aria-label="${name}" onclick="toggleSetting('${key}','${name}')"><i></i></button></div>`}
function modulesHtml(){const wwwNote=state.settings.module_bookings===false?'<em class="modWarn">Moduł Rezerwacje jest wyłączony – strona i tak pokazuje tylko telefon.</em>':'';return `<section class="setting modSetting"><h3>Moduły aplikacji</h3><p class="muted">Wyłączony moduł znika z menu u pracowników i kierowników. Dane zostają w bazie – po włączeniu wszystko wraca.</p>${MODULES.map(([k,ic,l,d])=>switchRow('module_'+k,ic,l,d)).join('')}</section><section class="setting modSetting"><h3>Strona www</h3>${switchRow('www_bookings','🌐','Rezerwacje ze strony','Wyłączone: przycisk „Rezerwacja” na stronie pokazuje tylko numer telefonu',wwwNote)}</section>`}
function adminOverview(p){''')
rep("""<button class="${state.settings.qr_enabled?'danger':'primary'}" onclick="toggleQR()">${state.settings.qr_enabled?'Wyłącz':'Włącz'}</button></section>`;""",
    """<button class="${state.settings.qr_enabled?'danger':'primary'}" onclick="toggleQR()">${state.settings.qr_enabled?'Wyłącz':'Włącz'}</button></section>${modulesHtml()}`;""")

# ---- CSS
rep('</style></head>', '''
/* V4.0 – moduły */
nav{grid-template-columns:none!important;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr)}
nav button.modOff{opacity:.45;position:relative}nav button.modOff::after{content:'wył.';position:absolute;top:3px;right:6px;font-size:9px;font-weight:800;color:#ffb9b1}
.modSetting{margin-top:12px}.modSetting h3{margin:0 0 4px}.modSetting>p{margin:0 0 10px;font-size:13px}
.modRow{display:flex;align-items:center;gap:12px;padding:11px 12px;margin-top:8px;border-radius:14px;background:#fff1da08;border:1px solid #e0ad6726;transition:.2s}
.modRow.off{background:#ee70650a;border-color:#ee706540}.modRow.off b{color:var(--muted)}
.modRow .grow{min-width:0;flex:1}.modRow b{display:block}.modRow small{display:block;color:var(--muted);font-size:12px;margin-top:2px}
.modIc{width:38px;height:38px;flex:0 0 auto;display:grid;place-items:center;border-radius:11px;background:#e0ad671c;font-size:19px}
.modWarn{display:block;margin-top:5px;font-style:normal;font-size:12px;color:#ffcf8a}
.modSwitch{position:relative;flex:0 0 auto;width:54px!important;height:30px;padding:0!important;border-radius:999px!important;background:#5a3a2c!important;border:1px solid #e0ad6740!important;cursor:pointer}
.modSwitch i{position:absolute;top:3px;left:3px;width:22px;height:22px;border-radius:50%;background:#e9d8c2;transition:transform .2s}
.modSwitch.on{background:#2f7a49!important;border-color:#71c98a!important}.modSwitch.on i{transform:translateX(24px);background:#fff}
</style></head>''')

open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
