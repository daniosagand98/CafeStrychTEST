# Strona v1.9: Google Analytics 4 ze zgodą na cookies (ładuje się dopiero po „Akceptuję”)
import sys
p='zrodla/strona-szablon.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
rep("  tiktok:'https://www.tiktok.com/@cafe_strych',          // pusty = ukryte\n",
    "  tiktok:'https://www.tiktok.com/@cafe_strych',          // pusty = ukryte\n  gaId:'',   // Google Analytics 4 – identyfikator pomiaru, np. 'G-ABC123XYZ' (pusty = statystyki wyłączone)\n")
rep(".fBottom .fVer{text-align:center;opacity:.75}",
    """.fBottom .fVer{text-align:center;opacity:.75}
.fCookies{background:none;border:0;color:inherit;font:inherit;text-decoration:underline;cursor:pointer;padding:0;opacity:.75}
.ckBar{position:fixed;left:16px;right:16px;bottom:16px;z-index:200;max-width:560px;margin:0 auto;background:#1c130d;color:#fbf3e4;border:1px solid rgba(251,243,228,.18);border-radius:18px;padding:16px 18px;box-shadow:0 18px 50px rgba(0,0,0,.45);font-size:14px;line-height:1.5;animation:ckIn .35s ease}
.ckBar b{display:block;font-size:15px;margin-bottom:4px}.ckBar p{margin:0 0 12px;opacity:.85}
.ckBtns{display:flex;gap:8px;flex-wrap:wrap}.ckBtns button{flex:1;min-width:130px;border-radius:999px;padding:10px 14px;font:inherit;font-weight:700;cursor:pointer;border:1px solid rgba(251,243,228,.35);background:transparent;color:inherit}.ckBtns .ckYes{background:var(--peach,#e9b872);color:#1c130d;border-color:transparent}
@keyframes ckIn{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}""")
rep("""      <span class="fVer">Strona v1.8.6 · aktualizacja 06.11.2026</span>""",
    """      <span class="fVer">Strona v1.9 · aktualizacja 20.11.2026<span id="fCkWrap" hidden> · <button type="button" class="fCookies" onclick="cookieSettings()">Ustawienia cookies</button></span></span>""")
rep("    $('#doneHello').textContent=`Dziękujemy, ${name.split(' ')[0]}!`;",
    "    track('rezerwacja_wyslana',{rodzaj:f.kind.value||'stolik',osoby:guests});\n    $('#doneHello').textContent=`Dziękujemy, ${name.split(' ')[0]}!`;")
rep("/* ====== MENU (z karty, październik 2026) ====== */",
r"""/* ====== STATYSTYKI (Google Analytics 4) – tylko po zgodzie ====== */
const CK_KEY='cs_cookies_v1';
function ckGet(){try{return localStorage.getItem(CK_KEY)}catch(e){return null}}
function ckSet(v){try{localStorage.setItem(CK_KEY,v)}catch(e){}}
function gaLoad(){const id=CONFIG.gaId;if(!id||window.__gaOn||window.STRYCH_PREVIEW)return;window.__gaOn=1;
  window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};
  gtag('js',new Date());gtag('config',id,{anonymize_ip:true});
  const s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(id);document.head.appendChild(s)}
function track(name,params){try{if(window.__gaOn&&window.gtag)gtag('event',name,params||{})}catch(e){}}
function ckBar(){if(document.querySelector('.ckBar'))return;const b=document.createElement('div');b.className='ckBar';b.setAttribute('role','dialog');b.setAttribute('aria-label','Pliki cookies');
  b.innerHTML='<b>🍪 Pliki cookies</b><p>Za Twoją zgodą używamy Google Analytics, żeby wiedzieć, jak korzystacie ze strony (anonimowe statystyki odwiedzin). Bez zgody strona działa tak samo.</p><div class="ckBtns"><button type="button" class="ckNo">Odrzuć</button><button type="button" class="ckYes">Akceptuję</button></div>';
  b.querySelector('.ckYes').onclick=()=>{ckSet('yes');b.remove();gaLoad()};
  b.querySelector('.ckNo').onclick=()=>{const was=window.__gaOn;ckSet('no');b.remove();if(was){document.cookie.split(';').forEach(c=>{const k=c.split('=')[0].trim();if(/^_ga/.test(k))['',location.hostname,'.'+location.hostname.replace(/^www\./,'')].forEach(d=>document.cookie=k+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/'+(d?';domain='+d:''))});location.reload()}};
  document.body.appendChild(b)}
window.cookieSettings=ckBar;
if(CONFIG.gaId&&!window.STRYCH_PREVIEW){const w=document.getElementById('fCkWrap');if(w)w.hidden=false;const v=ckGet();if(v==='yes')gaLoad();else if(v!=='no')setTimeout(ckBar,900);
  document.addEventListener('click',e=>{const a=e.target.closest&&e.target.closest('a[href^="tel:"],a[href^="mailto:"]');if(a)track(a.href.startsWith('tel:')?'klik_telefon':'klik_email',{numer:a.href.replace(/^(tel|mailto):/,'')})},true)}
/* ====== MENU (z karty, październik 2026) ====== */""")
open(p,'w',encoding='utf-8').write(s); print('ok')
