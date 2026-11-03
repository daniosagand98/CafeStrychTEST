import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
rep("const sb=supabase.createClient(SUPABASE_URL,SUPABASE_KEY,{auth:{persistSession:true}});",
    "const DEV_KEY='cs_company_device',devToken=(()=>{try{return localStorage.getItem(DEV_KEY)||''}catch{return ''}})();\nconst sb=supabase.createClient(SUPABASE_URL,SUPABASE_KEY,{auth:{persistSession:true},...(devToken?{global:{headers:{'x-cs-device':devToken}}}:{})});")
# dostęp: POS / rezerwacje / zakupy tylko na tablecie (pracownik)
rep("function allowed(v){if(v==='home')return true;if(!moduleOn(v)&&!isAdmin())return false;if(canManage())return true;",
    "const TABLET_ONLY=['pos','bookings','shopping'];\nfunction allowed(v){if(v==='home')return true;if(!moduleOn(v)&&!isAdmin())return false;if(canManage())return true;if(TABLET_ONLY.includes(v)&&!state.companyDevice)return false;")
# menu: tablety firmowe (kierownik/admin)
rep('<button id="notifMenu" class="hide" onclick="notificationsView()">🔔 Powiadomienia</button>',
    '<button id="notifMenu" class="hide" onclick="notificationsView()">🔔 Powiadomienia</button><button id="devicesMenu" class="hide" onclick="devicesView()">📱 Tablety firmowe</button>')
rep("$('#notifMenu').classList.remove('hide');","$('#notifMenu').classList.remove('hide');$('#devicesMenu')?.classList.toggle('hide',!canManage());$('#deviceBadge')?.remove();if(state.companyDevice&&state.user){const h=$('header .brand div');if(h)h.insertAdjacentHTML('beforeend',`<button id=\"deviceBadge\" class=\"deviceBadge\" onclick=\"switchUser()\" title=\"Tablet firmowy – wyloguj, aby zalogować inną osobę\">📱 ${esc(state.companyDevice.name)} • ${esc((state.profile?.full_name||'').split(' ')[0])} ⎋</button>`)}")
rep("['system','🛠️','System i logi']","['devices','📱','Tablety firmowe'],['system','🛠️','System i logi']")
rep("system:()=>systemAdmin(pane)}","system:()=>systemAdmin(pane),devices:()=>devicesView(pane)}")
# pracownik na telefonie – informacja na Start
rep("<section class=\"panel\"><h3>Komunikaty</h3><div class=\"cards\">${employeeMessages()",
    "${!state.companyDevice&&TABLET_ONLY.some(v=>moduleOn(v))?'<p class=\"tabletHint\">📱 POS, rezerwacje i zakupy są dostępne na <b>tablecie firmowym</b> w lokalu – zaloguj się tam na swoje konto.</p>':''}<section class=\"panel\"><h3>Komunikaty</h3><div class=\"cards\">${employeeMessages()")
JS=r"""
/* ---------- V5.4: TABLETY FIRMOWE ---------- */
state.companyDevice=(()=>{try{const n=localStorage.getItem(DEV_KEY+'_name');return devToken&&n?{name:n}:null}catch{return null}})();
let devChecked=false;
async function checkDevice(){if(devChecked||!devToken||!navigator.onLine)return;devChecked=true;const r=await sb.rpc('check_company_device',{p_token:devToken});if(r.error){if(!/PGRST202|function|schema cache/i.test((r.error.code||'')+r.error.message))devChecked=false;return}
 const before=!!state.companyDevice;state.companyDevice=r.data?{name:r.data.name,id:r.data.id}:null;try{if(r.data)localStorage.setItem(DEV_KEY+'_name',r.data.name);else localStorage.removeItem(DEV_KEY+'_name')}catch{}
 if(before!==!!state.companyDevice){applyRole();const av=$('[data-view].active')?.dataset.view;if(av&&!allowed(av))view('home')}}
{const base=loadAll;loadAll=async function(){await base.apply(this,arguments);await checkDevice()}}
window.switchUser=async()=>{if(outbox.length&&!confirm('Na tym tablecie są jeszcze niewysłane zmiany z POS (brak internetu). Wylogować mimo to? Wyślą się po zalogowaniu kolejnej osoby.'))return;if(!confirm(`Wylogować ${state.profile?.full_name||''}?\n\nNa tablecie zaloguje się następna osoba.`))return;await sb.auth.signOut();location.reload()};
window.devicesView=async(pane=null)=>{if(!canManage())return;const box=pane||content();if(!pane){state.page=()=>devicesView();$$('[data-view]').forEach(b=>b.classList.remove('active'))}
 const r=await sb.from('company_devices').select('id,name,created_at,last_seen_at,active').order('created_at'),list=r.data||[],missing=r.error&&/company_devices|does not exist|schema cache/i.test(r.error.message);
 const here=state.companyDevice;
 box.innerHTML=`<div class="toolbar inline"><div><h2>📱 Tablety firmowe</h2><small class="muted">Na nich pracownik ma POS, rezerwacje i zakupy</small></div>${pane?'':`<button class="ghost backTop" onclick="state.page=null;view('home')">← Wróć</button>`}</div>
 ${missing?'<div class="dbAlert">Uruchom w Supabase plik <b>sql/supabase_v5_4.sql</b>.</div>':''}
 <section class="panel devHere ${here?'on':''}"><div class="notifIcon">${here?'📱':'📵'}</div><div class="grow"><b>${here?`To urządzenie to tablet firmowy: ${esc(here.name)}`:'To urządzenie nie jest tabletem firmowym'}</b><small class="muted">${here?'Każdy pracownik po zalogowaniu ma tu POS, rezerwacje i zakupy. Po zmianie: przycisk z imieniem u góry → wyloguj.':'Na swoim telefonie pracownik ma tylko Start (wiadomości), Grafik, Czat i Moje konto (dokumenty).'}</small></div><div class="notifActions">${here?'<button class="danger" onclick="unregisterDevice()">Usuń z tego urządzenia</button>':'<button class="primary" onclick="registerDevice()">Ustaw jako tablet firmowy</button>'}</div></section>
 <section class="panel"><h3>Zarejestrowane tablety</h3><div class="cards">${list.map(d=>`<div class="card"><div class="grow"><b>${esc(d.name)}${here?.id===d.id?' <span class="statusPill okPill">to urządzenie</span>':''}</b><small>${d.active?'aktywny':'wyłączony'} • dodany ${new Date(d.created_at).toLocaleDateString('pl-PL')}${d.last_seen_at?` • ostatnio ${new Date(d.last_seen_at).toLocaleString('pl-PL',{dateStyle:'short',timeStyle:'short'})}`:''}</small></div><button class="danger" onclick="deleteDevice('${d.id}')">Usuń</button></div>`).join('')||'<p class="muted">Brak. Wejdź tutaj na tablecie w lokalu i kliknij „Ustaw jako tablet firmowy”.</p>'}</div></section>
 <section class="panel iosHint"><h3>Jak to ustawić</h3><ol><li>Na tablecie otwórz aplikację (najlepiej dodaj ją do ekranu początkowego).</li><li>Zaloguj się <b>swoim</b> kontem (kierownik lub administrator).</li><li>Menu konta → 📱 Tablety firmowe → <b>Ustaw jako tablet firmowy</b>, nadaj nazwę (np. „Tablet bar”).</li><li>Wyloguj się – od teraz każdy pracownik loguje się tu na swoje konto i ma POS, rezerwacje i zakupy.</li></ol><small class="muted">Usunięcie tabletu z listy od razu odbiera mu dostęp. Wyczyszczenie danych przeglądarki na tablecie wymaga ponownego ustawienia.</small></section>`};
window.registerDevice=async()=>{const name=prompt('Nazwa tabletu (np. „Tablet bar”, „Tablet sala”):','Tablet bar');if(name===null)return;const tok=[...crypto.getRandomValues(new Uint8Array(32))].map(b=>b.toString(16).padStart(2,'0')).join('');
 const r=await sb.rpc('register_company_device',{p_name:name.trim()||'Tablet',p_token:tok});if(r.error)return alert(/PGRST202|function|schema cache/i.test((r.error.code||'')+r.error.message)?'Najpierw uruchom w Supabase plik sql/supabase_v5_4.sql.':r.error.message);
 try{localStorage.setItem(DEV_KEY,tok);localStorage.setItem(DEV_KEY+'_name',name.trim()||'Tablet')}catch{return alert('Ta przeglądarka nie pozwala zapamiętać ustawienia (tryb prywatny?).')}alert('✓ To urządzenie jest teraz tabletem firmowym. Aplikacja się odświeży.');location.reload()};
window.unregisterDevice=async()=>{if(!confirm('Usunąć oznaczenie „tablet firmowy” z tego urządzenia? Pracownicy stracą tu dostęp do POS, rezerwacji i zakupów.'))return;if(state.companyDevice?.id)await sb.from('company_devices').delete().eq('id',state.companyDevice.id);try{localStorage.removeItem(DEV_KEY);localStorage.removeItem(DEV_KEY+'_name')}catch{}location.reload()};
window.deleteDevice=async id=>{if(!confirm('Usunąć ten tablet? Od razu straci dostęp do POS, rezerwacji i zakupów dla pracowników.'))return;const r=await sb.from('company_devices').delete().eq('id',id);if(r.error)return alert(r.error.message);if(state.companyDevice?.id===id){try{localStorage.removeItem(DEV_KEY);localStorage.removeItem(DEV_KEY+'_name')}catch{}location.reload();return}state.page?state.page():devicesView()};
"""
rep("\nfunction openFromUrl(url){",JS+"\nfunction openFromUrl(url){")
rep("</style></head>",""".deviceBadge{display:block;margin-top:2px;padding:3px 9px;border-radius:999px;border:1px solid #e0ad6766;background:#e0ad6722;color:#f0ca80;font-size:11px;font-weight:800;white-space:nowrap;max-width:62vw;overflow:hidden;text-overflow:ellipsis}
.tabletHint{margin:0 0 12px;padding:10px 12px;border-radius:12px;background:#e0ad6714;border:1px dashed #e0ad6766;font-size:13px;line-height:1.45}
.devHere{display:flex;gap:12px;align-items:center;flex-wrap:wrap}.devHere.on{border-color:#71c98a66}
</style></head>""")
rep('Cafe Strych Manager <span>V5.3.2</span>','Cafe Strych Manager <span>V5.4</span>')
rep('Cafe Strych Manager <b>V5.3.2</b> • 03.11.2026','Cafe Strych Manager <b>V5.4</b> • 03.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
