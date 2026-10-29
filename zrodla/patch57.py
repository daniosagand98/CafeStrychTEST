# V5.0.3 – plakaty (zdjęcia pionowe) w aktualnościach pokazywane w całości; ostrzejsze zdjęcia aktualności (2000 px)
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:120]!r}')
    s = s.replace(old, new)
rep('<b>Cafe Strych Manager <span>V5.0.2</span></b>', '<b>Cafe Strych Manager <span>V5.0.3</span></b>')
rep('<p>Cafe Strych Manager <b>V5.0</b> • 26.10.2026</p>', '<p>Cafe Strych Manager <b>V5.0.3</b> • 29.10.2026</p>')
rep("blob=await shrinkImage(f)", "blob=await shrinkImage(f,2000)")
rep("""function framerHtml(src,pos){return `<div class="framer" id="newsFramer"><img src="${esc(src)}" alt="" draggable="false" style="object-position:${pos}">""",
    """function framerHtml(src,pos){return `<div class="framer" id="newsFramer"><img class="frBg" src="${esc(src)}" alt="" aria-hidden="true"><img class="frMain" src="${esc(src)}" alt="" draggable="false" style="object-position:${pos}" onload="framerKind(this)">""")
rep("function bindFramer(){const box=$('#newsFramer'),img=box?.querySelector('img');",
    """window.framerKind=im=>{const box=im.closest('.framer'),poster=im.naturalHeight>im.naturalWidth*1.05;box.classList.toggle('poster',poster);const h=box.querySelector('.framerHint');if(h)h.textContent=poster?'📄 Plakat – na stronie pokaże się w całości':'✋ Przeciągnij zdjęcie, aby ustawić kadr';const bar=box.nextElementSibling?.querySelector('small');if(bar)bar.textContent=poster?'Pionowe zdjęcie: na stronie widać je w całości, bez przycinania':'Tak zdjęcie będzie przycięte na stronie'};
function bindFramer(){const box=$('#newsFramer'),img=box?.querySelector('img.frMain');""")
rep("box.onpointerdown=e=>{e.preventDefault();", "box.onpointerdown=e=>{if(box.classList.contains('poster'))return;e.preventDefault();")
rep("window.centerFrame=()=>{newsPos='50% 50%';const i=$('#newsFramer img');", "window.centerFrame=()=>{newsPos='50% 50%';const i=$('#newsFramer img.frMain');")
rep('</style></head>', '''
/* V5.0.1 – plakaty */
.framer .frBg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:blur(18px) brightness(.5);transform:scale(1.2);display:none}
.framer .frMain{position:relative}
.framer.poster{aspect-ratio:4/5;max-height:62vh;margin-left:auto;margin-right:auto;cursor:default}
.framer.poster .frBg{display:block}.framer.poster .frMain{object-fit:contain;object-position:50% 50%!important}
</style></head>''')
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
