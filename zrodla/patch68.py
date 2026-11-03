import sys
p='zrodla/strona-szablon.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:80]}')
    s=s.replace(a,b)
rep('<div class="cRow"><span class="ico">📞</span><div><b>Telefon</b><a id="cPhone"></a></div></div>',
    '<div class="cRow"><span class="ico">📞</span><div><b>Telefon</b><a id="cPhone"></a></div></div>\n        <div class="cRow"><span class="ico">✉️</span><div><b>E-mail</b><a href="mailto:strychgdynia@op.pl">strychgdynia@op.pl</a></div></div>')
rep('<a class="fLine" id="fPhone"></a>','<a class="fLine" id="fPhone"></a>\n        <a class="fLine" href="mailto:strychgdynia@op.pl">✉️ strychgdynia@op.pl</a>')
rep('<input name="guests" type="number" inputmode="numeric" min="1" max="120" step="1" required placeholder="np. 4">',
    '<input name="guests" type="number" inputmode="numeric" min="1" max="10" step="1" required placeholder="np. 4">')
rep("if(guests>120)return msg.textContent='Dla grup powyżej 120 osób zadzwoń do nas: '+CONFIG.phone;",
    "if(guests>10)return msg.textContent='Stolik rezerwujemy maksymalnie dla 10 osób. Większą grupę zaprosimy do sali – zadzwoń do właścicielki: +48 '+CONFIG.ownerPhone;")
rep('<p>Dla par, rodzin i znajomych. Wybierz dzień i godzinę – potwierdzimy telefonicznie.</p>','<p>Dla par, rodzin i znajomych – do 10 osób. Wybierz dzień i godzinę – potwierdzimy telefonicznie.</p>')
rep('Strona v1.8.4 · aktualizacja 29.10.2026','Strona v1.8.5 · aktualizacja 03.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
