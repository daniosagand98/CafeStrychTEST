import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
# administrator przypięty na górze listy wiadomości prywatnych
rep("const ppl=chatPeople().map(p=>({p,ch:dmCh(p.id),t:last(dmCh(p.id))?.created_at||''})).sort((a,b)=>b.t.localeCompare(a.t)||String(a.p.full_name).localeCompare(String(b.p.full_name),'pl'));",
    "const isSup=p=>String(p.email||'').toLowerCase()===SUPPORT_EMAIL,sup=chatPeople().filter(isSup),ppl=chatPeople().filter(p=>!isSup(p)).map(p=>({p,ch:dmCh(p.id),t:last(dmCh(p.id))?.created_at||''})).sort((a,b)=>b.t.localeCompare(a.t)||String(a.p.full_name).localeCompare(String(b.p.full_name),'pl'));")
rep("""<h3 class="chatSec">Wiadomości prywatne</h3>""","""${sup.length?`<h3 class="chatSec">Administrator aplikacji</h3><section class="panel chatList supList">${sup.map(p=>row(dmCh(p.id),'🛠️',`${p.full_name||'Administrator'} • Administrator`,'Pytania, problemy z aplikacją, pomysły – napisz')).join('')}</section>`:''}<h3 class="chatSec">Wiadomości prywatne</h3>""")
rep("function chatTitle(ch){if(ch==='general')return 'Czat ogólny';const o=ch.replace(/^dm:/,'').split(':').find(x=>x!==meId());return personName(o)||'Rozmowa'}",
    "const SUPPORT_EMAIL='daniosagand@gmail.com';\nfunction chatTitle(ch){if(ch==='general')return 'Czat ogólny';const o=ch.replace(/^dm:/,'').split(':').find(x=>x!==meId()),p=state.profiles.find(x=>x.id===o);return (personName(o)||'Rozmowa')+(String(p?.email||'').toLowerCase()===SUPPORT_EMAIL?' • Administrator':'')}")
rep("</style></head>",".supList .chatAv{background:#7fa6ff26;color:#bcd3ff}.supList b{color:#bcd3ff}\n</style></head>")
rep('Cafe Strych Manager <span>V5.5.1</span>','Cafe Strych Manager <span>V5.5.2</span>')
rep('Cafe Strych Manager <b>V5.5.1</b> • 06.11.2026','Cafe Strych Manager <b>V5.5.2</b> • 06.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
