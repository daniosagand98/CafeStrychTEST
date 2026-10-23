# V4.8 – admin może ukryć kwoty na swoim koncie (••• zł), przełącznik w Ustawienia → Przegląd → Prywatność
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'Expected {count} got {n}: {old[:120]!r}')
    s = s.replace(old, new)
rep('<b>Cafe Strych Manager <span>V4.7</span></b>', '<b>Cafe Strych Manager <span>V4.8</span></b>')
rep('<small>Aktualizacja: 23.10.2026 • Podgląd aplikacji na iPhonie i iPadzie (prezentacja), POS offline</small>',
    '<small>Aktualizacja: 23.10.2026 • Ukrywanie kwot dla administratora, podgląd na iPhonie i iPadzie</small>')
rep('<p>Cafe Strych Manager <b>V4.7</b> • 23.10.2026</p>', '<p>Cafe Strych Manager <b>V4.8</b> • 23.10.2026</p>')

rep("const money=v=>Number(v||0).toLocaleString('pl-PL',{minimumFractionDigits:2,maximumFractionDigits:2})+' zł';",
    "const hideMoney=()=>state.profile?.role==='admin'&&!!state.user?.user_metadata?.hide_money;\n"
    "const money=v=>hideMoney()?'••• zł':Number(v||0).toLocaleString('pl-PL',{minimumFractionDigits:2,maximumFractionDigits:2})+' zł';")

rep("${modulesHtml()}${IN_FRAME?'':devicesHtml()}`;", "${privacyHtml()}${modulesHtml()}${IN_FRAME?'':devicesHtml()}`;")
rep("function adminOverview(p){", r"""function privacyHtml(){if(state.profile?.role!=='admin')return '';const on=hideMoney();return `<section class="setting modSetting"><h3>Prywatność</h3><div class="modRow ${on?'':'off'}"><span class="modIc">🙈</span><div class="grow"><b>Ukryj kwoty na moim koncie</b><small>${on?'Kwoty (ceny, rachunki, utarg) widzisz jako ••• zł. Wyłącz na chwilę, gdy trzeba coś sprawdzić.':'Włącz, jeśli nie chcesz widzieć cen, rachunków ani utargu. Działa tylko na Twoim koncie – inni widzą kwoty normalnie.'}</small></div><button type="button" class="modSwitch ${on?'on':''}" role="switch" aria-checked="${on}" aria-label="Ukryj kwoty" onclick="toggleHideMoney()"><i></i></button></div></section>`}
window.toggleHideMoney=async()=>{if(state.profile?.role!=='admin')return;const val=!hideMoney();if(netDown||!navigator.onLine)return alert('Brak internetu – tę opcję można zmienić po powrocie połączenia.');
 const r=await sb.auth.updateUser({data:{hide_money:val}});if(r.error)return alert('Nie udało się zapisać:\n'+r.error.message);
 if(r.data?.user)state.user=r.data.user;else state.user={...state.user,user_metadata:{...(state.user?.user_metadata||{}),hide_money:val}};
 scheduleCache();toast(val?'Kwoty ukryte na Twoim koncie':'Kwoty widoczne');admin('overview')};
function adminOverview(p){""")
# kopia offline pamięta też to ustawienie
rep("user:{id:state.user.id,email:state.user.email},", "user:{id:state.user.id,email:state.user.email,user_metadata:{hide_money:!!state.user.user_metadata?.hide_money}},")
rep('<div class="barList ${keys.length>10?\'clip\':\'\'}">','<div class="barList ${keys.length>10?\'clip\':\'\'} ${hideMoney()?\'noBars\':\'\'}">')
rep("const ck=JSON.stringify(SP)+':'+state.payments.length;","const ck=JSON.stringify(SP)+':'+state.payments.length+':'+hideMoney();")
rep('</style></head>','\n.barList.noBars .barRow i{visibility:hidden}\n</style></head>')
open(dst, 'w', encoding='utf-8').write(s); print('OK', len(s))
