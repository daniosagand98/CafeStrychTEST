# V5.8.2: sprawdzanie nowej wersji aplikacji (bez wyłączania appki) + licznik nieprzeczytanych na ikonie
import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
rep("function updateChatBadge(){navBadge('chat',chatChannels().reduce((n,c)=>n+chatUnread(c),0))}",
    "function updateChatBadge(){const n=chatChannels().reduce((n,c)=>n+chatUnread(c),0);navBadge('chat',n);try{if(navigator.setAppBadge)(n?navigator.setAppBadge(n):navigator.clearAppBadge()).catch(()=>{})}catch(_){}}")
rep("function openFromUrl(url){",
r"""/* V5.8.2: nowa wersja aplikacji bez wyłączania – sprawdza co 5 min i po powrocie do aplikacji */
(()=>{const RX=/Cafe Strych Manager <span>(V[\d.]+)<\/span>/,cur=(document.documentElement.innerHTML.match(RX)||[])[1];if(!cur||location.protocol==='file:')return;let newer=null,last=0;
 const idle=()=>!outbox.length&&!$('#modal').open&&!document.activeElement?.matches?.('input,textarea,select');
 const offer=()=>{if($('#updBar'))return;const b=document.createElement('div');b.id='updBar';b.className='updBar';b.innerHTML=`<span>Jest nowa wersja aplikacji <b>${esc(newer)}</b></span><button class="primary" onclick="appUpdate()">Odśwież</button>`;document.body.appendChild(b)};
 const check=async force=>{if(!navigator.onLine||document.hidden||(!force&&Date.now()-last<240000))return;last=Date.now();try{const r=await fetch('index.html?v='+Date.now(),{cache:'no-store'});if(!r.ok)return;const v=((await r.text()).match(RX)||[])[1];if(v&&v!==cur){newer=v;offer()}}catch(_){}};
 window.appUpdate=()=>{if(outbox.length){flushOutbox();return alert('Najpierw muszą się wysłać zmiany z POS (brak internetu). Spróbuj za chwilę.')}if($('#modal').open&&!confirm('Masz otwarte okno – niezapisane zmiany przepadną. Odświeżyć?'))return;location.reload()};
 document.addEventListener('visibilitychange',()=>{if(document.hidden)return;if(newer&&idle())return location.reload();check()});
 setInterval(()=>check(),300000);setTimeout(()=>check(true),20000)})();
function openFromUrl(url){""")
rep(".ticketActions .primary,.ticketActions .cancelBtn{",
    ".updBar{position:fixed;left:50%;transform:translateX(-50%);top:calc(env(safe-area-inset-top,0px) + 10px);z-index:9999;display:flex;align-items:center;gap:12px;padding:8px 8px 8px 16px;border-radius:999px;background:#2b1a10;border:1px solid #e0ad6766;box-shadow:0 10px 30px #0009;color:#f6e7cf;font-size:14px;max-width:calc(100vw - 20px)}.updBar button{padding:8px 14px;border-radius:999px;white-space:nowrap}\n.ticketActions .primary,.ticketActions .cancelBtn{")
rep('Cafe Strych Manager <span>V5.8.1</span>','Cafe Strych Manager <span>V5.8.2</span>')
rep('Cafe Strych Manager <b>V5.8.1</b> • 20.11.2026','Cafe Strych Manager <b>V5.8.2</b> • 20.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
