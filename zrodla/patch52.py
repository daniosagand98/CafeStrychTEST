# V4.7 – „Podgląd na urządzeniach” (admin, komputer): aplikacja w ramce iPhone / iPad do prezentacji
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:120]!r}')
    s = s.replace(old, new)
rep('<b>Cafe Strych Manager <span>V4.6.1</span></b>', '<b>Cafe Strych Manager <span>V4.7</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • POS i rabaty działają bez internetu (zapis w pamięci telefonu)</small>',
    '<small>Aktualizacja: 23.10.2026 • Podgląd aplikacji na iPhonie i iPadzie (prezentacja), POS offline</small>')
rep('<p>Cafe Strych Manager <b>V4.6.1</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.7</b> • 23.10.2026</p>')

# w ramce podglądu: osobna skrzynka offline, żeby dwie kopie aplikacji nie nadpisywały sobie zmian
rep("const OUTBOX_KEY='cs_outbox_v1',", "const IN_FRAME=(()=>{try{return window.self!==window.top}catch{return true}})();if(IN_FRAME)document.documentElement.classList.add('inFrame');\nconst OUTBOX_KEY=IN_FRAME?'cs_outbox_frame_v1':'cs_outbox_v1',")

# sekcja w ustawieniach (Przegląd)
rep("${modulesHtml()}`;", "${modulesHtml()}${IN_FRAME?'':devicesHtml()}`;")
rep("function adminOverview(p){", r"""const DEVICES={iphone:{name:'iPhone',w:393,h:852,ic:'📱',sub:'393 × 852'},ipad:{name:'iPad',w:820,h:1180,ic:'📲',sub:'820 × 1180'}};
function devicesHtml(){return `<section class="setting devSetting"><h3>Podgląd na urządzeniach</h3><p class="muted">Pokaż na komputerze, jak aplikacja wygląda na telefonie i tablecie – np. podczas wideorozmowy. W środku działa prawdziwa aplikacja (Twoje konto, prawdziwe dane): można klikać, przełączać Admin / Kierownik / Pracownik.</p><div class="devPick"><button type="button" class="devBtn" onclick="closeDevice()"><span>💻</span><b>Komputer</b><small>zwykły widok</small></button>${Object.entries(DEVICES).map(([k,d])=>`<button type="button" class="devBtn" onclick="openDevice('${k}')"><span>${d.ic}</span><b>${d.name}</b><small>${d.sub}</small></button>`).join('')}</div></section>`}
let devState={k:null,land:false};
window.openDevice=(k,land=false)=>{const d=DEVICES[k];if(!d)return;devState={k,land};let ov=$('#devOverlay');if(!ov){ov=document.createElement('div');ov.id='devOverlay';document.body.appendChild(ov);addEventListener('resize',fitDevice);addEventListener('keydown',e=>{if(e.key==='Escape'&&$('#devOverlay'))closeDevice()})}
 const w=land?d.h:d.w,h=land?d.w:d.h,src=location.href.split('#')[0].split('?')[0]+'?device='+k,now=new Date().toLocaleTimeString('pl-PL',{hour:'2-digit',minute:'2-digit'});
 ov.innerHTML=`<div class="devBar"><div class="devTabs"><button type="button" onclick="closeDevice()">💻 Komputer</button>${Object.entries(DEVICES).map(([kk,dd])=>`<button type="button" class="${kk===k?'active':''}" onclick="openDevice('${kk}')">${dd.ic} ${dd.name}</button>`).join('')}</div>${k==='ipad'?`<button type="button" class="devTool" onclick="openDevice('ipad',${!land})">⟳ ${land?'Pionowo':'Poziomo'}</button>`:''}<button type="button" class="devTool" onclick="$('#devFrame').src=$('#devFrame').src">↻ Odśwież</button><button type="button" class="devTool devClose" onclick="closeDevice()">✕ Zamknij</button></div>
 <div class="devStage"><div class="devHold" id="devHold"><div class="devBody ${k} ${land?'land':''}" id="devBody" style="--w:${w}px;--h:${h}px"><div class="devScreen"><div class="devStatus"><b>${now}</b>${k==='iphone'?'<i class="island"></i>':''}<span>📶 ◔ 🔋</span></div><iframe id="devFrame" title="Podgląd ${d.name}" src="${src}"></iframe>${k==='iphone'?'<i class="homeBar"></i>':''}</div></div></div></div>`;
 document.body.classList.add('devOpen');fitDevice()};
function fitDevice(){const b=$('#devBody'),h=$('#devHold'),st=$('.devStage');if(!b||!h||!st)return;const bw=b.offsetWidth,bh=b.offsetHeight,sc=Math.min(1,(st.clientWidth-40)/bw,(st.clientHeight-24)/bh);b.style.transform=`scale(${sc})`;h.style.width=bw*sc+'px';h.style.height=bh*sc+'px'}
window.closeDevice=()=>{$('#devOverlay')?.remove();document.body.classList.remove('devOpen');devState={k:null,land:false}};
function adminOverview(p){""")

rep('</style></head>', '''
/* V4.7 – podgląd na urządzeniach */
.devPick{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:10px}
.devBtn{display:flex;flex-direction:column;align-items:center;gap:2px;padding:14px 8px!important;border-radius:14px;background:#fff1da0a;border:1px solid #fff1da18;color:var(--cream)}
.devBtn span{font-size:26px}.devBtn small{font-size:11px;color:var(--muted)}.devBtn:hover{border-color:#e0ad6788}
html.inFrame .devSetting{display:none}
body.devOpen{overflow:hidden}
#devOverlay{position:fixed;inset:0;z-index:200;display:flex;flex-direction:column;background:radial-gradient(circle at 50% 30%,#3a2419,#120a07 70%)}
.devBar{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:8px;padding:12px 16px}
.devTabs{display:flex;padding:4px;border-radius:14px;background:#0006;border:1px solid #fff1da22}
.devTabs button{width:auto;padding:8px 14px;border:0;background:transparent;color:var(--muted);border-radius:10px;font-weight:700}
.devTabs .active{background:#e0ad6730;color:var(--cream)}
.devTool{width:auto!important;padding:8px 12px!important;border-radius:12px;background:#0006!important;border:1px solid #fff1da22!important;color:var(--cream)}
.devClose{border-color:#ee706577!important;color:#ffb9b1}
.devStage{flex:1;display:grid;place-items:center;overflow:hidden;min-height:0}
.devHold{position:relative}.devBody{position:absolute;left:0;top:0;transform-origin:0 0;padding:14px;border-radius:64px;background:linear-gradient(145deg,#2c2c30,#0d0d10);box-shadow:0 0 0 2px #55555c,0 30px 80px #000c,inset 0 0 0 2px #000}
.devBody.ipad{padding:24px;border-radius:44px}.devBody.ipad.land{padding:24px}
.devScreen{position:relative;width:var(--w);height:var(--h);border-radius:50px;overflow:hidden;background:#140b08;display:flex;flex-direction:column}
.devBody.ipad .devScreen{border-radius:22px}
.devStatus{position:relative;flex:0 0 auto;height:47px;display:flex;align-items:center;justify-content:space-between;padding:0 30px 0 34px;color:#fff;font:600 15px system-ui;background:#140b08}
.devBody.ipad .devStatus{height:28px;padding:0 22px;font-size:12px}
.devStatus span{font-size:12px;letter-spacing:2px}
.devStatus .island{position:absolute;left:50%;top:11px;transform:translateX(-50%);width:122px;height:35px;border-radius:20px;background:#000}
.devScreen iframe{flex:1;width:100%;border:0;background:#140b08}
.homeBar{position:absolute;left:50%;bottom:8px;transform:translateX(-50%);width:136px;height:5px;border-radius:3px;background:#fffc;pointer-events:none}
@media(max-width:900px){.devSetting{display:none}}
</style></head>''')
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
