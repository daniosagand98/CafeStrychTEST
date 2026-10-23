# V4.1 – reset hasła z ekranu logowania, usuwanie produktów z Menu POS, kadrowanie zdjęć w aktualnościach
#   python3 zrodla/patch42.py panel/index.html panel/index.html     (kadrowanie wymaga sql/supabase_v4_1.sql)
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:110]!r}')
    s = s.replace(old, new)

# ---- stopka
rep('<b>Cafe Strych Manager <span>V4.0</span></b>', '<b>Cafe Strych Manager <span>V4.1</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • Admin włącza/wyłącza moduły i rezerwacje ze strony www</small>',
    '<small>Aktualizacja: 23.10.2026 • Reset hasła przy logowaniu, usuwanie produktów z menu, kadrowanie zdjęć aktualności</small>')
rep('<p>Cafe Strych Manager <b>V4.0</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.1</b> • 23.10.2026</p>')

# ---- 1. RESET HASŁA na ekranie logowania
rep('<input id="loginPassword" type="password" required><button class="primary">Zaloguj</button></form>',
    '<input id="loginPassword" type="password" required autocomplete="current-password"><button class="primary">Zaloguj</button><button type="button" class="linkBtn" id="forgotBtn">Nie pamiętasz hasła?</button></form>'
    '<form id="resetForm" class="hide"><p class="muted resetLead">Wpisz e-mail swojego konta – wyślemy link do ustawienia nowego hasła.</p><label>E-mail</label><input id="resetEmail" type="email" required autocomplete="email"><button class="primary" id="resetBtn">Wyślij link</button><button type="button" class="linkBtn" id="backToLogin">← Wróć do logowania</button></form>')
rep("$('#loginForm').classList.toggle('hide',b.dataset.auth!=='login');",
    "$('#resetForm').classList.add('hide');$('#loginForm').classList.toggle('hide',b.dataset.auth!=='login');")
rep("$('#loginForm').onsubmit=async e=>{e.preventDefault();const r=await sb.auth.signInWithPassword({email:$('#loginEmail').value,password:$('#loginPassword').value});$('#authMsg').textContent=r.error?.message||''};",
    r"""const authPL=m=>!m?'':/invalid login credentials/i.test(m)?'Nieprawidłowy e-mail lub hasło.':/email not confirmed/i.test(m)?'Adres e-mail nie jest jeszcze potwierdzony – kliknij link w mailu od Supabase.':/rate limit|too many|security purposes/i.test(m)?'Za dużo prób w krótkim czasie – spróbuj ponownie za kilka minut.':m;
$('#loginForm').onsubmit=async e=>{e.preventDefault();const r=await sb.auth.signInWithPassword({email:$('#loginEmail').value.trim(),password:$('#loginPassword').value});$('#authMsg').textContent=authPL(r.error?.message)};
$('#forgotBtn').onclick=()=>{$('#authMsg').textContent='';$('#resetEmail').value=$('#loginEmail').value.trim();$('#loginForm').classList.add('hide');$('#resetForm').classList.remove('hide');$('#resetEmail').focus()};
$('#backToLogin').onclick=()=>{$('#authMsg').textContent='';$('#resetForm').classList.add('hide');$('#loginForm').classList.remove('hide')};
$('#resetForm').onsubmit=async e=>{e.preventDefault();const email=$('#resetEmail').value.trim(),btn=$('#resetBtn');if(!email)return;btn.disabled=true;btn.textContent='Wysyłanie…';
 const r=await sb.auth.resetPasswordForEmail(email,{redirectTo:location.origin+location.pathname});btn.disabled=false;btn.textContent='Wyślij link';
 $('#authMsg').textContent=r.error?authPL(r.error.message):`Jeśli konto ${email} istnieje, wysłaliśmy na nie link do zmiany hasła. Sprawdź pocztę (także folder Spam / Oferty) i kliknij link na tym urządzeniu.`};""")

# ---- 2. USUWANIE PRODUKTÓW z Menu POS
rep("""<button class="ghost" onclick="menuForm('${x.id}')">Edytuj</button></div>`).join('')||'<div class="empty">Brak produktów.</div>'}</div>`}""",
    """<button class="ghost" onclick="menuForm('${x.id}')">Edytuj</button><button class="danger" onclick="deleteMenuItem('${x.id}')">Usuń</button></div>`).join('')||'<div class="empty">Brak produktów.</div>'}</div>`}
window.deleteMenuItem=async id=>{const m=state.menu.find(x=>x.id===id);if(!m||!canManage())return;if(!confirm(`Usunąć „${m.name}” z menu POS?\\n\\nStare rachunki z tym produktem zostają bez zmian (nazwa i cena są w nich zapisane). Jeśli chcesz go tylko ukryć na jakiś czas – w „Edytuj” odznacz „Aktywny”.`))return;const r=await removeRow('menu_items',id);if(r.error)return alert('Nie udało się usunąć produktu:\\n'+dbHint(r.error));await loadAll();menuAdmin();toast('Produkt usunięty z menu')};""")

# ---- 3. KADROWANIE ZDJĘCIA w aktualnościach
rep("window.newsImagePreview=input=>{const f=input.files?.[0],box=$('#newsImgBox');if(!box)return;box.innerHTML=f?`<img class=\"newsPreviewImg\" src=\"${URL.createObjectURL(f)}\" alt=\"\">`:''};",
    r"""let newsPos='50% 50%';
function framerHtml(src,pos){return `<div class="framer" id="newsFramer"><img src="${esc(src)}" alt="" draggable="false" style="object-position:${pos}"><span class="framerHint">✋ Przeciągnij zdjęcie, aby ustawić kadr</span></div><div class="framerBar"><small class="muted">Tak zdjęcie będzie przycięte na stronie</small><button type="button" class="ghost" onclick="centerFrame()">Wyśrodkuj</button></div>`}
function bindFramer(){const box=$('#newsFramer'),img=box?.querySelector('img');if(!img)return;let drag=null;const parse=()=>newsPos.split(' ').map(parseFloat);
 box.onpointerdown=e=>{e.preventDefault();box.setPointerCapture(e.pointerId);const [x,y]=parse();drag={sx:e.clientX,sy:e.clientY,x,y};box.classList.add('drag')};
 box.onpointermove=e=>{if(!drag||!img.naturalWidth)return;const bw=box.clientWidth,bh=box.clientHeight,k=Math.max(bw/img.naturalWidth,bh/img.naturalHeight),ox=img.naturalWidth*k-bw,oy=img.naturalHeight*k-bh,cl=v=>Math.round(Math.min(100,Math.max(0,v)));
  const x=ox>1?cl(drag.x-(e.clientX-drag.sx)/ox*100):50,y=oy>1?cl(drag.y-(e.clientY-drag.sy)/oy*100):50;newsPos=`${x}% ${y}%`;img.style.objectPosition=newsPos};
 box.onpointerup=box.onpointercancel=()=>{drag=null;box.classList.remove('drag')}}
window.centerFrame=()=>{newsPos='50% 50%';const i=$('#newsFramer img');if(i)i.style.objectPosition=newsPos};
window.newsImagePreview=input=>{const f=input.files?.[0],box=$('#newsImgBox');if(!box)return;newsPos='50% 50%';box.innerHTML=f?framerHtml(URL.createObjectURL(f),newsPos):'';bindFramer()};""")
rep("""<div id="newsImgBox">${r?.image_url?`<img class="newsPreviewImg" src="${esc(r.image_url)}" alt="">`:''}</div>""",
    """<div id="newsImgBox">${r?.image_url?framerHtml(r.image_url,newsPos=r.image_pos||'50% 50%'):(newsPos='50% 50%','')}</div>""")
rep("image_url,image_path,updated_at:new Date().toISOString()},z=await(r?sb.from('site_news').update(p).eq('id',r.id):sb.from('site_news').insert({...p,created_by:state.user.id}));",
    "image_url,image_path,image_pos:image_url?newsPos:null,updated_at:new Date().toISOString()},save=q=>r?sb.from('site_news').update(q).eq('id',r.id):sb.from('site_news').insert({...q,created_by:state.user.id});let z=await save(p);if(z.error&&/image_pos/.test(z.error.message)){delete p.image_pos;z=await save(p);if(!z.error)setTimeout(()=>alert('Zapisano, ale bez kadru zdjęcia – uruchom w Supabase plik sql/supabase_v4_1.sql.'),300)}")
rep("$('#newsPublished').checked=r.published!==false;$('#newsPinned').checked=!!r.pinned}},0)};",
    "$('#newsPublished').checked=r.published!==false;$('#newsPinned').checked=!!r.pinned}bindFramer()},0)};")

# ---- CSS
rep('</style></head>', '''
/* V4.1 */
.linkBtn{width:auto!important;margin:12px auto 0;display:block;padding:6px 8px!important;background:none!important;border:0!important;color:#f0ca80!important;font-weight:700;text-decoration:underline;text-underline-offset:3px;cursor:pointer}
.resetLead{margin:0 0 10px;font-size:13px}#resetForm .primary{margin-top:14px}
.framer{position:relative;margin-top:10px;aspect-ratio:16/10;border-radius:14px;overflow:hidden;border:1px solid #e0ad6755;cursor:grab;touch-action:none;user-select:none;-webkit-user-select:none;background:#000}
.framer.drag{cursor:grabbing}.framer img{width:100%;height:100%;object-fit:cover;display:block;pointer-events:none}
.framerHint{position:absolute;left:50%;bottom:10px;transform:translateX(-50%);padding:6px 11px;border-radius:999px;background:#000a;color:#fff;font-size:12px;white-space:nowrap;pointer-events:none;transition:opacity .2s}.framer.drag .framerHint{opacity:0}
.framerBar{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:6px}.framerBar button{width:auto;padding:7px 12px}
</style></head>''')

open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
