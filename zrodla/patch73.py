import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
rep("</style></head>","""
/* V5.4.1 – wysokość ekranu liczona na żywo (iPhone składany / obrót / klawiatura) */
@media screen{#app,#auth{bottom:auto!important;height:var(--vh,100%)!important}
nav{bottom:auto!important;top:calc(var(--vh,100dvh) - var(--navh,76px) - 8px - env(safe-area-inset-bottom))}
html.kb nav{display:none!important}html.kb .composer,html.kb .propSave{bottom:8px!important}}
</style></head>""")
JS=r"""
/* V5.4.1: wysokość widocznego ekranu – dolny pasek zawsze przy dolnej krawędzi */
(()=>{const root=document.documentElement,vv=window.visualViewport;let timers=[];
 function fit(){const h=Math.round(vv?vv.height:innerHeight),n=document.querySelector('nav');root.style.setProperty('--vh',h+'px');if(n&&n.offsetHeight)root.style.setProperty('--navh',n.offsetHeight+'px');root.classList.toggle('kb',!!vv&&innerHeight-vv.height>140&&/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName||''))}
 function nudge(){fit();const sc=document.getElementById('app');if(sc&&!sc.classList.contains('hide')){const y=sc.scrollTop;sc.scrollTop=y+1;sc.scrollTop=y}if(scrollY)scrollTo(0,0)}
 function later(){timers.forEach(clearTimeout);timers=[0,120,350,800,1500].map(d=>setTimeout(nudge,d))}
 ['resize','orientationchange','pageshow','focus'].forEach(e=>addEventListener(e,later));document.addEventListener('visibilitychange',()=>{if(!document.hidden)later()});
 if(vv){vv.addEventListener('resize',fit);vv.addEventListener('scroll',fit)}document.addEventListener('focusin',()=>setTimeout(fit,300));document.addEventListener('focusout',()=>setTimeout(fit,300));
 if(window.screen?.orientation)screen.orientation.addEventListener?.('change',later);fit();later()})();
"""
rep("\nfunction openFromUrl(url){",JS+"\nfunction openFromUrl(url){")
rep('Cafe Strych Manager <span>V5.4</span>','Cafe Strych Manager <span>V5.4.1</span>')
rep('Cafe Strych Manager <b>V5.4</b> • 03.11.2026','Cafe Strych Manager <b>V5.4.1</b> • 04.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
