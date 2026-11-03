import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
# --- odczyty czatu: wszyscy uczestnicy
rep("safe('chat_reads',q=>q.select('*').eq('user_id',state.user.id))","safe('chat_reads',q=>q.select('*'))")
rep("state.chatReads=Object.fromEntries(r.map(x=>[x.channel,x.last_read_at]));",
    "state.chatReadsAll=r;state.chatReads=Object.fromEntries(r.filter(x=>x.user_id===state.user.id).map(x=>[x.channel,x.last_read_at]));state.profiles=state.profiles.filter(p=>!p.deleted_at);")
rep("async function chatMarkRead(ch){const at=new Date().toISOString();state.chatReads[ch]=at;updateChatBadge();",
    "async function chatMarkRead(ch){const at=new Date().toISOString();state.chatReads[ch]=at;chatReadSet({user_id:meId(),channel:ch,last_read_at:at});updateChatBadge();")
# --- znaczniki przy wiadomościach
rep("<small class=\"msgTime\">${chatTime(m.created_at)}${m._pending?' • wysyłanie…':''}",
    "<small class=\"msgTime\">${chatTime(m.created_at)}${m._pending?' • wysyłanie…':''}${mine&&!m._pending?`<span class=\"rcpt\" data-r=\"${m.id}\">${chatRcpt(m)}</span>`:''}")
JS=r"""
state.chatReadsAll=state.chatReadsAll||[];
function chatReadSet(x){const i=state.chatReadsAll.findIndex(r=>r.user_id===x.user_id&&r.channel===x.channel);if(i>=0)state.chatReadsAll[i]={...state.chatReadsAll[i],...x};else state.chatReadsAll.push(x)}
function chatSeen(m){return state.chatReadsAll.filter(r=>r.channel===m.channel&&r.user_id!==m.sender_id&&r.last_read_at>=m.created_at)}
function chatLastMine(ch){return state.chat.filter(x=>x.channel===ch&&x.sender_id===meId()&&!x._pending).at(-1)}
function chatRcpt(m){const seen=chatSeen(m),hm=t=>new Date(t).toLocaleTimeString('pl-PL',{hour:'2-digit',minute:'2-digit'});
 if(m.channel!=='general'){const r=seen[0];return r?` • <b class="seen">✓✓ Wyświetlono ${hm(r.last_read_at)}</b>`:' • ✓ Wysłano'}
 if(!seen.length)return ' • ✓ Nikt jeszcze nie wyświetlił';
 const last=chatLastMine(m.channel)?.id===m.id,names=seen.map(r=>(personName(r.user_id)||'?').split(' ')[0]);
 return ` • <a href="#" class="seen" onclick="event.preventDefault();chatSeenList('${m.id}')">👁 ${last?`Wyświetlili: ${esc(names.slice(0,3).join(', '))}${names.length>3?` +${names.length-3}`:''}`:seen.length}</a>`}
function chatRcptRefresh(){$$('.rcpt').forEach(e=>{const m=state.chat.find(x=>x.id===e.dataset.r);if(m)e.innerHTML=chatRcpt(m)})}
window.chatSeenList=id=>{const m=state.chat.find(x=>x.id===id);if(!m)return;const seen=chatSeen(m),ids=seen.map(r=>r.user_id),notYet=chatPeople().filter(p=>!ids.includes(p.id));
 modal('Kto wyświetlił',`<p class="muted" style="margin-top:0">„${esc(String(m.body).slice(0,80))}”</p><h3 class="chatSec">✓ Wyświetlili (${seen.length})</h3><div class="cards">${seen.sort((a,b)=>a.last_read_at.localeCompare(b.last_read_at)).map(r=>`<div class="card"><div class="grow"><b>${esc(personName(r.user_id)||'Użytkownik')}</b><small>${new Date(r.last_read_at).toLocaleString('pl-PL',{dateStyle:'short',timeStyle:'short'})}</small></div></div>`).join('')||'<p class="muted">Nikt.</p>'}</div><h3 class="chatSec">Jeszcze nie (${notYet.length})</h3><div class="cards">${notYet.map(p=>`<div class="card"><div class="grow"><b>${esc(p.full_name||p.email||'Użytkownik')}</b></div></div>`).join('')||'<p class="muted">Wszyscy wyświetlili.</p>'}</div>`,null,false)};
sb.channel('cs-chat-reads').on('postgres_changes',{event:'*',schema:'public',table:'chat_reads'},p=>{const x=p.new;if(!x?.user_id)return;chatReadSet(x);if(x.user_id===meId()){state.chatReads[x.channel]=x.last_read_at;updateChatBadge()}if(state.chatRoom===x.channel)chatRcptRefresh()}).subscribe();

/* ---------- usuwanie kont ---------- */
function canDeleteAccount(p){if(!p||p.id===state.user?.id||p.role==='admin')return false;return isAdmin()||(canManage()&&(p.role||'user')==='user')}
window.deleteAccount=async id=>{const p=state.profiles.find(x=>x.id===id);if(!canDeleteAccount(p))return;
 if(!confirm(`Usunąć konto „${p.full_name||p.email}”?\n\n• Ta osoba nie zaloguje się już do aplikacji.\n• Jej rachunki, zmiany w grafiku i historia zostają.\n• Tego nie da się cofnąć – może tylko założyć nowe konto.`))return;
 const r=await sb.rpc('admin_delete_account',{p_user:id});if(r.error)return alert(/PGRST202|function|schema cache/i.test((r.error.code||'')+r.error.message)?'Usuwanie kont zacznie działać po uruchomieniu w Supabase pliku sql/supabase_v5_3_1.sql.':r.error.message);
 state.profiles=state.profiles.filter(x=>x.id!==id);await loadAll();toast('Konto usunięte');if(state.page)state.page()};
function accountsSection(){const list=state.profiles.filter(p=>p.id!==state.user?.id).sort((a,b)=>String(a.full_name||'').localeCompare(String(b.full_name||''),'pl'));const R={admin:'Administrator',manager:'Kierownik',user:'Pracownik'};
 return `<h3 class="chatSec">Konta w aplikacji</h3><div class="cards">${list.map(p=>`<div class="card"><div class="grow"><b>${esc(p.full_name||'Użytkownik')}</b><small>${esc(p.email||'')} • ${R[p.role]||'Pracownik'}${p.active===false?' • zablokowane':''}</small></div>${canDeleteAccount(p)?`<button class="danger" onclick="deleteAccount('${p.id}')">Usuń konto</button>`:''}</div>`).join('')||'<p class="muted">Nikt poza Tobą nie ma jeszcze konta.</p>'}</div>`}
"""
rep("\nfunction openFromUrl(url){",JS+"\nfunction openFromUrl(url){")
# --- przyciski: admin (Konta i role) i kierownik (Pracownicy)
rep("""<button class="${x.active===false?'ok':'danger'}" onclick="toggleAccount('${x.id}',${x.active===false})">${x.active===false?'✓ Zatwierdź':'Zablokuj'}</button></div>`).join('')}</div>`}""",
    """<button class="${x.active===false?'ok':'danger'}" onclick="toggleAccount('${x.id}',${x.active===false})">${x.active===false?'✓ Zatwierdź':'Zablokuj'}</button>${canDeleteAccount(x)?`<button class="danger" onclick="deleteAccount('${x.id}')">Usuń konto</button>`:''}</div>`).join('')}</div>`}""")
rep("""<button class="danger" onclick="deleteEmployee('${e.id}')">Usuń</button></div>`).join('')}</div>`}""",
    """<button class="danger" onclick="deleteEmployee('${e.id}')">Usuń</button></div>`).join('')}</div>${canManage()&&!state.inAdmin?accountsSection():''}`;if(!state.inAdmin)state.page=()=>employeesView()}""")
rep(".rcpt",".rcpt",0) if False else None
rep("</style></head>",".msgTime .seen{color:#f0ca80;font-weight:700;text-decoration:none}\n</style></head>")
rep('Cafe Strych Manager <span>V5.3</span>','Cafe Strych Manager <span>V5.3.1</span>')
rep('Cafe Strych Manager <b>V5.3</b> • 03.11.2026','Cafe Strych Manager <b>V5.3.1</b> • 03.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
