import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:80]}')
    s=s.replace(a,b)
rep("</style></head>","""
/* V5.0.6 – dolny pasek nie ucieka przy przewijaniu (Safari na iOS):
   strona przewija się we własnym kontenerze, a nie całe okno */
@media screen{html,body{height:100%;overflow:hidden;overscroll-behavior:none}
#app,#auth{position:fixed;inset:0;overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch;overscroll-behavior-y:contain}
#app.hide,#auth.hide{display:none!important}}
</style></head>""")
rep("sy=scrollY;openOrder(oid);","sc=$('#app'),sy=sc.scrollTop;openOrder(oid);")
rep("filterProductMenu(oid,term)}scrollTo(0,sy)}","filterProductMenu(oid,term)}sc.scrollTop=sy}")
rep("salesReport('${k}');scrollTo({top:$('.salesDay').offsetTop-10,behavior:'smooth'})","salesReport('${k}');$('.salesDay')?.scrollIntoView({behavior:'smooth',block:'start'})")
rep('Cafe Strych Manager <span>V5.0.5</span>','Cafe Strych Manager <span>V5.0.6</span>')
rep('Cafe Strych Manager <b>V5.0.5</b>','Cafe Strych Manager <b>V5.0.6</b>')
open(p,'w',encoding='utf-8').write(s); print('ok')
