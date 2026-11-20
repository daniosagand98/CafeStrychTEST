import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
# 1) pracownik: płatność i zamknięcie rachunku
rep(""":'<p class="muted">Płatność zatwierdza kierownik lub administrator.</p>';""",
    """:`<div class="actions ticketActions"><button class="primary" onclick="pay('${id}')">Płatność</button></div><p class="muted" style="margin-top:6px;font-size:12px">Rabat i anulowanie rachunku – kierownik.</p>`;""")
# 2) aktywacja kont – przez funkcję bazy (kierownik: konta pracowników)
rep("window.toggleAccount=async(id,active)=>{const r=await sb.from('profiles').update({active}).eq('id',id);if(r.error)return alert(r.error.message);await loadAll();admin('accounts')};",
    "window.toggleAccount=async(id,active)=>{let r=await sb.rpc('set_account_active',{p_user:id,p_active:!!active});if(r.error&&/PGRST202|function|schema cache/i.test((r.error.code||'')+r.error.message)){if(!isAdmin())return alert('Uruchom w Supabase plik sql/supabase_v5_7.sql.');r=await sb.from('profiles').update({active}).eq('id',id)}if(r.error)return alert(r.error.message);await loadAll();toast(active?'Konto aktywne':'Konto zablokowane');if(state.inAdmin&&isAdmin())admin('accounts');else if(state.page)state.page()};")
rep("""return `<h3 class="chatSec">Konta w aplikacji</h3><div class="cards">${list.map(p=>`<div class="card"><div class="grow"><b>${esc(p.full_name||'Użytkownik')}</b><small>${esc(p.email||'')} • ${R[p.role]||'Pracownik'}${p.active===false?' • zablokowane':''}</small></div>${canDeleteAccount(p)?`<button class="danger" onclick="deleteAccount('${p.id}')">Usuń konto</button>`:''}</div>`).join('')||'<p class="muted">Nikt poza Tobą nie ma jeszcze konta.</p>'}</div>`}""",
    """const canAct=p=>p.id!==state.user?.id&&p.role!=='admin'&&(isAdmin()||(p.role||'user')==='user');list.sort((a,b)=>(a.active===false?0:1)-(b.active===false?0:1));
 return `<h3 class="chatSec">Konta w aplikacji</h3><div class="cards">${list.map(p=>`<div class="card ${p.active===false?'accPending':''}"><div class="grow"><b>${esc(p.full_name||'Użytkownik')}</b><small>${esc(p.email||'')} • ${R[p.role]||'Pracownik'}${p.active===false?' • <b class="accWait">czeka na aktywację / zablokowane</b>':''}</small></div><div class="accBtns">${canAct(p)?(p.active===false?`<button class="ok" onclick="toggleAccount('${p.id}',true)">✓ Aktywuj</button>`:`<button class="ghost" onclick="toggleAccount('${p.id}',false)">Zablokuj</button>`):''}${canDeleteAccount(p)?`<button class="danger" onclick="deleteAccount('${p.id}')">Usuń konto</button>`:''}</div></div>`).join('')||'<p class="muted">Nikt poza Tobą nie ma jeszcze konta.</p>'}</div>`}""")
rep("</style></head>",".accBtns{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}.accPending{border-color:#e0ad6788!important}.accWait{color:#f0ca80}\n</style></head>")
rep('Cafe Strych Manager <span>V5.6.2</span>','Cafe Strych Manager <span>V5.7</span>')
rep('Cafe Strych Manager <b>V5.6.2</b> • 11.11.2026','Cafe Strych Manager <b>V5.7</b> • 20.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
