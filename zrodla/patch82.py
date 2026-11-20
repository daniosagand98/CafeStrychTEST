# Strona v1.9: polityka prywatności (link w stopce, w banerze cookies i pod formularzem rezerwacji)
import sys
p='zrodla/strona-szablon.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
rep("""<span class="fVer">Strona v1.9 · aktualizacja 20.11.2026<span id="fCkWrap" hidden>""",
    """<span class="fVer">Strona v1.9 · aktualizacja 20.11.2026 · <a href="polityka-prywatnosci.html" class="fPriv">Polityka prywatności</a><span id="fCkWrap" hidden>""")
rep(".fCookies{",".fPriv{color:inherit;opacity:.75}\n.resPriv{font-size:12.5px;color:var(--muted);margin:10px 0 0;text-align:center}.resPriv a{color:inherit}\n.fCookies{")
rep("""      <button class="btn btn-ink" type="submit" id="resBtn">Wyślij prośbę o rezerwację</button>""",
    """      <button class="btn btn-ink" type="submit" id="resBtn">Wyślij prośbę o rezerwację</button>
      <p class="resPriv">Dane z formularza wykorzystamy tylko do obsługi rezerwacji. <a href="polityka-prywatnosci.html" target="_blank">Polityka prywatności</a></p>""")
rep("Bez zgody strona działa tak samo.</p>","Bez zgody strona działa tak samo. <a href=\"polityka-prywatnosci.html\" style=\"color:inherit\">Polityka prywatności</a></p>")
rep("else if(v!=='no')setTimeout(ckBar,900);","else if(v!=='no')setTimeout(ckBar,900);\n  if(location.hash==='#cookies'){history.replaceState(null,'',location.pathname);setTimeout(ckBar,300)}")
open(p,'w',encoding='utf-8').write(s); print('ok')
# (druga część – link w istniejącej zgodzie zamiast osobnego akapitu)
