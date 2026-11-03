import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:80]}')
    s=s.replace(a,b)
rep("notificationsView=async()=>{if(!canManage())return home();const sup=","notificationsView=async()=>{const mgr=canManage(),sup=")
rep("<small class=\"muted\">Nowe rezerwacje prosto na telefon – także gdy aplikacja jest zamknięta</small>",
    "<small class=\"muted\">${mgr?'Nowe rezerwacje i wiadomości':'Wiadomości od kierownika'} prosto na telefon – także gdy aplikacja jest zamknięta</small>")
rep("${on?'Dostaniesz powiadomienie o każdej nowej rezerwacji (ze strony i od zespołu).'",
    "${on?(mgr?'Dostaniesz powiadomienie o każdej nowej rezerwacji (ze strony i od zespołu) oraz o wiadomościach do Ciebie.':'Dostaniesz powiadomienie, gdy kierownik wyśle Ci wiadomość.')")
rep(":'Włącz, żeby dostawać powiadomienia o nowych rezerwacjach.'}",":(mgr?'Włącz, żeby dostawać powiadomienia o nowych rezerwacjach i wiadomościach.':'Włącz, żeby dostawać powiadomienie, gdy kierownik wyśle Ci wiadomość.')}")
rep("$('#notifMenu').classList.toggle('hide',!canManage());","$('#notifMenu').classList.remove('hide');")
rep("if(u.searchParams.get('bugs')&&state.user&&state.profile?.role==='admin')return admin('bugs');",
    "if(u.searchParams.get('bugs')&&state.user&&state.profile?.role==='admin')return admin('bugs');if(u.searchParams.get('msg')&&state.user){state.page=null;state.inAdmin=false;return view('home')}")
rep("if(q.get('day')||q.get('bugs')){","if(q.get('day')||q.get('bugs')||q.get('msg')){")
rep("notify_bookings:true,updated_at:new Date().toISOString()}","notify_bookings:true,notify_messages:true,updated_at:new Date().toISOString()}")
rep('Cafe Strych Manager <span>V5.1</span>','Cafe Strych Manager <span>V5.1.1</span>')
rep('Cafe Strych Manager <b>V5.1</b> • 03.11.2026','Cafe Strych Manager <b>V5.1.1</b> • 03.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
