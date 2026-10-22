# V3.9 – posty z Instagrama/TikToka/Facebooka na stronie (nakładane na panel/index.html V3.8)
#   python3 zrodla/patch39.py panel/index.html panel/index.html
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        raise SystemExit(f'Expected {count} got {n}: {old[:100]!r}')
    s = s.replace(old, new)

# ---- stopka / wersja
rep('<b>Cafe Strych Manager <span>V3.8</span></b>', '<b>Cafe Strych Manager <span>V3.9</span></b>')
rep('<small>Aktualizacja: 21.10.2026 • Anulowanie rachunków zamiast usuwania, zatwierdzanie kont, rezerwacja całej sali</small>',
    '<small>Aktualizacja: 22.10.2026 • Posty z Instagrama, TikToka i Facebooka na stronie www</small>')
rep('<p>Cafe Strych Manager <b>V3.8</b> • 21.10.2026</p>', '<p>Cafe Strych Manager <b>V3.9</b> • 22.10.2026</p>')

# ---- dane
rep("state.news=await safe('site_news',q=>q.select('*').order('pinned',{ascending:false}).order('created_at',{ascending:false}).limit(100))}",
    "state.news=await safe('site_news',q=>q.select('*').order('pinned',{ascending:false}).order('created_at',{ascending:false}).limit(100));state.social=await safe('site_social_posts',q=>q.select('*').order('created_at',{ascending:false}).limit(60))}")
rep("'site_news','bug_reports'].forEach(t=>sb.channel(", "'site_news','bug_reports','site_social_posts'].forEach(t=>sb.channel(")
rep("const DB_TABLES=['profiles',", "const DB_TABLES=['site_social_posts','profiles',")
rep("news:`${state.news.filter(n=>n.published).length} na stronie`",
    "news:`${state.news.filter(n=>n.published).length} aktualności • ${(state.social||[]).filter(x=>x.published).length} postów`")

# ---- CSS
rep('</style></head>', '''
/* V3.9 – posty z social mediów na stronie */
.socSection{margin-top:22px}.socSection .toolbar{margin-bottom:10px}
.socCard{align-items:center}.socCard .grow{min-width:0}.socCard .grow small{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.socBadge{width:42px;height:42px;flex:0 0 auto;display:grid;place-items:center;border-radius:12px;color:#fff;font:800 13px system-ui}
.socBadge.instagram{background:linear-gradient(45deg,#f09433,#dc2743 50%,#bc1888)}.socBadge.tiktok{background:#111;border:1px solid #fff3}.socBadge.facebook{background:#1877f2}
.socHelp{margin:8px 0 0;padding:10px 12px;border-radius:12px;background:#fff1da0a;border:1px dashed #e0ad6755;font-size:13px;color:var(--muted);line-height:1.55}
.socDetected{margin-top:8px;font-size:13px;font-weight:800}.socDetected.ok{color:#b9f4c8}.socDetected.bad{color:#ffb9b1}
</style></head>''')

# ---- logika
rep("function newsCenter(){if(!canManage())return home();", r'''const SOC_NAMES={instagram:'Instagram',tiktok:'TikTok',facebook:'Facebook'},SOC_SHORT={instagram:'IG',tiktok:'TT',facebook:'f'};
function parseSocialUrl(raw){const u=String(raw||'').trim();let m;
 if(/^https?:\/\/(vm|vt)\.tiktok\.com\//i.test(u)||/tiktok\.com\/t\//i.test(u))return{error:'To skrócony link z aplikacji TikTok. Otwórz go w przeglądarce, a potem skopiuj pełny adres z paska (z „/video/” i numerem).'};
 if((m=/instagram\.com\/(?:[^/?#]+\/)?(p|reel|tv)\/([A-Za-z0-9_-]+)/i.exec(u)))return{platform:'instagram',url:`https://www.instagram.com/${m[1].toLowerCase()==='tv'?'p':m[1].toLowerCase()}/${m[2]}/`};
 if((m=/tiktok\.com\/@([^/?#]+)\/(?:video|photo)\/(\d{8,})/i.exec(u)))return{platform:'tiktok',url:`https://www.tiktok.com/@${m[1]}/video/${m[2]}`};
 if(/^https?:\/\/((www|m|web)\.)?(facebook\.com|fb\.watch)\//i.test(u)){const clean=u.replace(/^https?:\/\/(m|web)\./i,'https://www.').split('#')[0];return{platform:'facebook',url:clean}}
 if(/instagram\.com\//i.test(u))return{error:'To link do profilu Instagrama. Wklej link do konkretnego posta (w aplikacji Instagram: ⋯ → Link / Kopiuj link).'};
 if(/tiktok\.com\//i.test(u))return{error:'To nie jest link do filmiku TikTok. Potrzebny jest pełny link z „/video/” i numerem.'};
 return{error:'Wklej link do posta z Instagrama, filmiku z TikToka albo posta z Facebooka.'}}
function socialCard(x){const d=new Date(x.created_at);return `<div class="card socCard"><span class="socBadge ${x.platform}">${SOC_SHORT[x.platform]||'?'}</span><div class="grow"><b>${SOC_NAMES[x.platform]||x.platform}${x.note?` – ${esc(x.note)}`:''}</b><small>${esc(x.url)}</small><small>dodano ${d.toLocaleDateString('pl-PL')}</small><span class="newsPill ${x.published?'on':''}">${x.published?'Widoczny na stronie':'Ukryty'}</span></div><a class="ghost" style="width:auto;padding:10px 12px;border-radius:13px;text-decoration:none" href="${esc(x.url)}" target="_blank" rel="noopener">Otwórz</a><button class="ghost" onclick="toggleSocial('${x.id}',${!x.published})">${x.published?'Ukryj':'Pokaż'}</button><button class="danger" onclick="deleteSocial('${x.id}')">Usuń</button></div>`}
window.socialCheck=v=>{const r=parseSocialUrl(v),el=$('#socDetected');if(!el)return;if(!String(v).trim()){el.textContent='';el.className='socDetected';return}el.className='socDetected '+(r.error?'bad':'ok');el.textContent=r.error?'⚠ '+r.error:'✓ Rozpoznano: '+SOC_NAMES[r.platform]};
window.socialForm=()=>{if(!canManage())return;modal('Dodaj post na stronę',`<label>Link do posta lub filmiku</label><input id="socUrl" type="url" required placeholder="https://www.instagram.com/p/… lub https://www.tiktok.com/@cafe_strych/video/…" oninput="socialCheck(this.value)"><div id="socDetected" class="socDetected"></div>${field('socNote','Krótki opis dla Ciebie (opcjonalnie)','','maxlength="200" placeholder="np. koncert 15.10"')}<div class="socHelp"><b>Skąd wziąć link?</b><br>📷 <b>Instagram:</b> przy poście ⋯ → „Link” / „Kopiuj link”.<br>🎵 <b>TikTok:</b> otwórz filmik na tiktok.com i skopiuj adres z paska (musi zawierać „/video/” i numer).<br>👍 <b>Facebook:</b> przy poście ⋯ → „Kopiuj link”. Jeśli strona lokalu ma na Facebooku ograniczenie wiekowe (np. alkohol), Facebook nie pozwala pokazać postów na innych stronach.</div>`,async()=>{const r=parseSocialUrl($('#socUrl').value);if(r.error)return alert(r.error);const z=await sb.from('site_social_posts').insert({platform:r.platform,url:r.url,note:$('#socNote').value.trim()||null,published:true,created_by:state.user.id});if(z.error)return alert(/duplicate|unique|23505/i.test(z.error.message+z.error.code)?'Ten post jest już dodany.':'Nie udało się dodać:\n'+dbHint(z.error));closeModal();await loadAll();newsCenter();toast(`Post z ${SOC_NAMES[r.platform]} jest na stronie`)})};
window.toggleSocial=async(id,published)=>{const r=await sb.from('site_social_posts').update({published}).eq('id',id);if(r.error)return alert(r.error.message);await loadAll();newsCenter();toast(published?'Post widoczny na stronie':'Post ukryty')};
window.deleteSocial=async id=>{if(!confirm('Usunąć ten post ze strony? (Na Instagramie/TikToku/Facebooku zostaje bez zmian.)'))return;const r=await sb.from('site_social_posts').delete().eq('id',id);if(r.error)return alert(r.error.message);await loadAll();newsCenter();toast('Post usunięty ze strony')};
function newsCenter(){if(!canManage())return home();''')
rep("""<div class="cards">${state.news.map(newsCard).join('')||'<div class="empty">Brak aktualności. Dodaj pierwszą – np. koncert w środę, nowe ciasto albo zmianę godzin.</div>'}</div>`}""",
    """<div class="cards">${state.news.map(newsCard).join('')||'<div class="empty">Brak aktualności. Dodaj pierwszą – np. koncert w środę, nowe ciasto albo zmianę godzin.</div>'}</div><section class="socSection"><div class="toolbar"><div><h2>Posty z social mediów</h2><small class="muted">Wklej link do posta z Instagrama, filmiku z TikToka lub posta z Facebooka – pokaże się w sekcji „Na bieżąco” na stronie (najnowsze 9)</small></div><button class="primary" onclick="socialForm()">+ Dodaj post</button></div><div class="cards">${(state.social||[]).map(socialCard).join('')||'<div class="empty">Brak postów. Dodaj link do najnowszego posta z Instagrama albo filmiku z TikToka.</div>'}</div></section>`}""")

open(dst, 'w', encoding='utf-8').write(s)
print('OK', len(s))
