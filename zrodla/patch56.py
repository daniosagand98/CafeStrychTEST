# V5.0 – „Galeria strony”: kierownik/admin sam dodaje zdjęcia (kilka naraz), opisy, kolejność, ukrywanie, usuwanie
#   wymaga sql/supabase_v4_8.sql
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:120]!r}')
    s = s.replace(old, new)
rep('<b>Cafe Strych Manager <span>V4.9.1</span></b>', '<b>Cafe Strych Manager <span>V5.0</span></b>')
rep('<p>Cafe Strych Manager <b>V4.9.1</b> • 26.10.2026</p>', '<p>Cafe Strych Manager <b>V5.0</b> • 26.10.2026</p>')

# dane
rep("state.social=await safe('site_social_posts',q=>q.select('*').order('created_at',{ascending:false}).limit(60));",
    "state.social=await safe('site_social_posts',q=>q.select('*').order('created_at',{ascending:false}).limit(60));state.gallery=await safe('site_gallery',q=>q.select('*').order('sort_order').order('created_at'));")
rep("'site_social_posts','cafe_settings'].forEach(t=>sb.channel(", "'site_social_posts','cafe_settings','site_gallery'].forEach(t=>sb.channel(")
rep("const DB_TABLES=['site_social_posts',", "const DB_TABLES=['site_gallery','site_social_posts',")

# wejścia: zakładka w Ustawieniach + menu konta (kierownik)
rep("['news','📰','Aktualności www'],", "['news','📰','Aktualności www'],['gallery','🖼️','Galeria strony'],")
rep("news:()=>newsCenter(),", "news:()=>newsCenter(),gallery:()=>galleryAdmin(),")
rep("news:`${state.news.filter(n=>n.published).length} na stronie`,", "news:`${state.news.filter(n=>n.published).length} na stronie`,gallery:`${(state.gallery||[]).filter(g=>g.published).length} zdjęć na stronie`,")
rep('<button id="newsMenu" class="hide" onclick="newsCenter()">📰 Aktualności (strona)</button>',
    '<button id="newsMenu" class="hide" onclick="newsCenter()">📰 Aktualności (strona)</button><button id="galleryMenu" class="hide" onclick="galleryAdmin()">🖼️ Galeria (strona)</button>')
rep("$('#newsMenu').classList.toggle('hide',!canManage());", "$('#newsMenu').classList.toggle('hide',!canManage());$('#galleryMenu').classList.toggle('hide',!canManage());")

# widok galerii
rep("function newsCenter(){if(!canManage())return home();", r"""const galSrc=u=>/^(https?:|data:|blob:)/.test(u||'')?u:new URL('../'+String(u||'').replace(/^\.?\//,''),location.href).href;
function galleryAdmin(){if(!canManage())return home();const G=state.gallery||[],vis=G.filter(g=>g.published).length;
 content().innerHTML=`<div class="toolbar inline"><div><h2>Galeria strony</h2><small class="muted">${G.length?`${vis} z ${G.length} zdjęć widocznych na stronie • kolejność jak tutaj`:'Zdjęcia z sekcji „Galeria” na stronie www'}</small></div><label class="primary btnSm galAddBtn">+ Dodaj zdjęcia<input type="file" accept="image/*" multiple hidden onchange="galleryUpload(this.files);this.value=''"></label></div>
 <div id="galProgress"></div>
 <div class="galList">${G.map((g,i)=>`<div class="galItem ${g.published?'':'off'}" data-id="${g.id}"><button type="button" class="galThumb" onclick="window.open('${esc(galSrc(g.image_url))}','_blank')" title="Otwórz w pełnym rozmiarze"><img src="${esc(galSrc(g.image_url))}" alt="" loading="lazy"><em>${i+1}</em></button>
  <div class="galBody"><label>Opis zdjęcia</label><input type="text" maxlength="160" value="${esc(g.caption||'')}" placeholder="np. Koncert przy pianinie" onchange="galleryCaption('${g.id}',this.value)">
  <div class="galBtns"><button type="button" class="ghost" ${i?'':'disabled'} onclick="galleryMove('${g.id}',-1)" title="Wyżej">↑</button><button type="button" class="ghost" ${i<G.length-1?'':'disabled'} onclick="galleryMove('${g.id}',1)" title="Niżej">↓</button><button type="button" class="ghost" onclick="galleryToggle('${g.id}')">${g.published?'👁 Widoczne':'🙈 Ukryte'}</button><button type="button" class="danger" onclick="galleryDelete('${g.id}')">Usuń</button></div></div></div>`).join('')||'<div class="empty">Galeria jest pusta. Kliknij „+ Dodaj zdjęcia” – możesz wybrać kilka naraz.</div>'}</div>
 <p class="muted galHint">Opis widać na stronie po najechaniu na zdjęcie i w powiększeniu. Pierwsze zdjęcie jest na stronie największe. Zdjęcia są automatycznie zmniejszane, żeby strona działała szybko.</p>`}
window.galleryAdmin=galleryAdmin;
const galErr=e=>/site_gallery|relation|schema cache/i.test(e?.message||'')?'Najpierw uruchom w Supabase plik sql/supabase_v4_8.sql (galeria strony).':(e?.message||String(e));
window.galleryUpload=async files=>{files=[...(files||[])].filter(f=>/^image\//.test(f.type));if(!files.length)return;if(netDown||!navigator.onLine)return alert('Brak internetu – zdjęcia można dodać po powrocie połączenia.');
 const box=$('#galProgress');let ok=0,maxO=Math.max(0,...(state.gallery||[]).map(g=>g.sort_order||0));
 for(const [i,f] of files.entries()){if(box)box.innerHTML=`<div class="galProg">Wysyłanie ${i+1} z ${files.length}… <i style="--p:${Math.round(i/files.length*100)}%"></i></div>`;
  try{const blob=await shrinkImage(f,1600),path=`gallery/${Date.now()}-${Math.random().toString(36).slice(2,8)}.jpg`,up=await sb.storage.from('site-news').upload(path,blob,{contentType:'image/jpeg',upsert:false});if(up.error)throw up.error;
   const url=sb.storage.from('site-news').getPublicUrl(path).data.publicUrl,cap=f.name.replace(/\.[^.]+$/,'').replace(/[_-]+/g,' ').replace(/^(img|dsc|photo|zdj[eę]cie|image)\s*\d*$/i,'').trim().slice(0,160);
   const r=await sb.from('site_gallery').insert({image_url:url,image_path:path,caption:cap||null,sort_order:(maxO+=10),published:true,created_by:state.user.id});if(r.error){await sb.storage.from('site-news').remove([path]);throw r.error}ok++}
  catch(e){alert(`Nie udało się dodać „${f.name}”:\n`+galErr(e));if(/supabase_v4_8/.test(galErr(e)))break}}
 await loadAll();galleryAdmin();if(ok)toast(`Dodano ${ok} ${ok===1?'zdjęcie':ok<5?'zdjęcia':'zdjęć'} – są już na stronie. Dopisz opisy.`)};
window.galleryCaption=async(id,v)=>{const r=await sb.from('site_gallery').update({caption:v.trim()||null}).eq('id',id);if(r.error)return alert(galErr(r.error));const g=(state.gallery||[]).find(x=>x.id===id);if(g)g.caption=v.trim()||null;toast('Opis zapisany')};
window.galleryToggle=async id=>{const g=(state.gallery||[]).find(x=>x.id===id);if(!g)return;const r=await sb.from('site_gallery').update({published:!g.published}).eq('id',id);if(r.error)return alert(galErr(r.error));g.published=!g.published;galleryAdmin();toast(g.published?'Zdjęcie widoczne na stronie':'Zdjęcie ukryte')};
window.galleryMove=async(id,dir)=>{const G=state.gallery||[],i=G.findIndex(x=>x.id===id),j=i+dir;if(i<0||j<0||j>=G.length)return;[G[i],G[j]]=[G[j],G[i]];G.forEach((g,k)=>g.sort_order=(k+1)*10);galleryAdmin();
 const rs=await Promise.all([G[i],G[j]].map(g=>sb.from('site_gallery').update({sort_order:g.sort_order}).eq('id',g.id)));const e=rs.find(r=>r.error);if(e){alert(galErr(e.error));await loadAll();galleryAdmin()}
 else if(new Set(G.map(g=>g.sort_order)).size!==G.length)await Promise.all(G.map(g=>sb.from('site_gallery').update({sort_order:g.sort_order}).eq('id',g.id)))};
window.galleryDelete=async id=>{const g=(state.gallery||[]).find(x=>x.id===id);if(!g||!confirm(`Usunąć to zdjęcie z galerii strony?${g.caption?`\n\n„${g.caption}”`:''}`))return;const r=await sb.from('site_gallery').delete().eq('id',id);if(r.error)return alert(galErr(r.error));if(g.image_path)await sb.storage.from('site-news').remove([g.image_path]);await loadAll();galleryAdmin();toast('Zdjęcie usunięte z galerii')};
function newsCenter(){if(!canManage())return home();""")
# kolejność zapisywana dla całej listy, żeby zawsze była spójna
rep("const rs=await Promise.all([G[i],G[j]].map(g=>sb.from('site_gallery').update({sort_order:g.sort_order}).eq('id',g.id)));","const rs=await Promise.all(G.map(g=>sb.from('site_gallery').update({sort_order:g.sort_order}).eq('id',g.id)));")
# CSS
rep('</style></head>', '''
/* V5.0 – galeria strony */
.galAddBtn{display:inline-flex;align-items:center;cursor:pointer}
.galList{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:12px}
.galItem{display:flex;gap:12px;padding:10px;border-radius:16px;background:#fff1da0a;border:1px solid #fff1da18}
.galItem.off{opacity:.55}
.galThumb{position:relative;flex:0 0 120px;width:120px!important;height:120px;padding:0!important;border-radius:12px;overflow:hidden;border:0;background:#000}
.galThumb img{width:100%;height:100%;object-fit:cover}.galThumb em{position:absolute;left:6px;top:6px;min-width:22px;padding:1px 6px;border-radius:999px;background:#000b;color:#fff;font:800 11px/20px system-ui;font-style:normal;text-align:center}
.galBody{flex:1;min-width:0;display:flex;flex-direction:column;gap:6px}.galBody label{font-size:11px;color:var(--muted);margin:0}.galBody input{padding:9px 10px}
.galBtns{display:flex;flex-wrap:wrap;gap:6px;margin-top:auto}.galBtns button{width:auto;padding:7px 10px;font-size:13px}
.galProg{margin-bottom:10px;padding:10px 12px;border-radius:12px;background:#e0ad671a;border:1px solid #e0ad6755;font-size:13px}
.galProg i{display:block;height:6px;margin-top:6px;border-radius:9px;background:linear-gradient(90deg,#f0ca80 var(--p),#fff1da18 var(--p))}
.galHint{margin-top:12px;font-size:12px}
@media(max-width:520px){.galList{grid-template-columns:1fr}.galThumb{flex-basis:96px;width:96px!important;height:96px}}
</style></head>''')
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
