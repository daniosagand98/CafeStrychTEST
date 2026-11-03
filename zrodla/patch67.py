import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:80]}')
    s=s.replace(a,b)
rep("if(!isAdmin()&&!(canManage()&&isCancelled(o)))return alert('Kierownik może usunąć tylko anulowany rachunek. Opłacony rachunek usuwa administrator.');",
    "if(!canManage())return alert('Rachunek z historii może usunąć kierownik lub administrator.');")
rep("${isAdmin()||(c&&canManage())?`<div class=\"histBtns\">${!c&&isAdmin()?","${canManage()?`<div class=\"histBtns\">${!c?")
rep("${isAdmin()||(isCancelled(o)&&canManage())?`<button class=\"danger historyDelete\"","${canManage()?`<button class=\"danger historyDelete\"")
rep("${isAdmin()?'Anuluj – rachunek zostaje w historii, bez wpływu na utarg. Usuń – znika na zawsze, także z podsumowań.':(canManage()?'Anulowany rachunek możesz usunąć. Opłacone rachunki anuluje lub usuwa administrator.':'Opłacone rachunki może anulować lub usunąć administrator.')}",
    "${canManage()?'Anuluj – rachunek zostaje w historii, bez wpływu na utarg. Usuń – znika na zawsze, także z podsumowań.':'Opłacone rachunki może anulować lub usunąć kierownik.'}")
rep("${isAdmin()?`<button class=\"danger ticketCancel\" onclick=\"cancelOrder('${o.id}')\">Anuluj opłacony rachunek</button>`:''}",
    "${canManage()?`<button class=\"danger ticketCancel\" onclick=\"cancelOrder('${o.id}')\">Anuluj opłacony rachunek</button>`:''}")
rep("if(paid&&!isAdmin())return alert('Opłacony rachunek może anulować tylko administrator.');if(!paid&&!canManage())return alert('Rachunek może anulować kierownik lub administrator.');",
    "if(!canManage())return alert('Rachunek może anulować kierownik lub administrator.');")
open(p,'w',encoding='utf-8').write(s); print('ok')
