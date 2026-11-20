# V5.8.3: sprawdzanie wersji lżejsze (HEAD zamiast pobierania całej aplikacji), bez samoczynnego odświeżania przy POS
import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
rep(""" const idle=()=>!outbox.length&&!$('#modal').open&&!document.activeElement?.matches?.('input,textarea,select');""",
""" let tag=null,hiddenAt=0;
 const idle=()=>!outbox.length&&!posBusy&&!$('#modal').open&&!document.activeElement?.matches?.('input,textarea,select')&&!['pos','bookings','shopping'].includes($('[data-view].active')?.dataset.view)&&Date.now()-hiddenAt>600000;""")
rep(""" const check=async force=>{if(!navigator.onLine||document.hidden||(!force&&Date.now()-last<240000))return;last=Date.now();try{const r=await fetch('index.html?v='+Date.now(),{cache:'no-store'});if(!r.ok)return;const v=((await r.text()).match(RX)||[])[1];if(v&&v!==cur){newer=v;offer()}}catch(_){}};""",
""" // najpierw lekkie zapytanie HEAD (kilkaset bajtów); całą stronę pobiera tylko, gdy plik na serwerze się zmienił
 const check=async force=>{if(newer||!navigator.onLine||document.hidden||posBusy||(!force&&Date.now()-last<240000))return;last=Date.now();try{const u='index.html?v='+Date.now();
  if(tag&&!force){const h=await fetch(u,{method:'HEAD',cache:'no-store'});const t=h.headers.get('etag')||h.headers.get('last-modified');if(!h.ok||!t||t===tag)return}
  const r=await fetch(u,{cache:'no-store'});if(!r.ok)return;tag=r.headers.get('etag')||r.headers.get('last-modified');const v=((await r.text()).match(RX)||[])[1];if(v&&v!==cur){newer=v;offer()}}catch(_){}};""")
rep(""" document.addEventListener('visibilitychange',()=>{if(document.hidden)return;if(newer&&idle())return location.reload();check()});""",
    """ document.addEventListener('visibilitychange',()=>{if(document.hidden){hiddenAt=Date.now();return}if(newer&&idle())return location.reload();check()});""")
rep('Cafe Strych Manager <span>V5.8.2</span>','Cafe Strych Manager <span>V5.8.3</span>')
rep('Cafe Strych Manager <b>V5.8.2</b> • 20.11.2026','Cafe Strych Manager <b>V5.8.3</b> • 20.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
