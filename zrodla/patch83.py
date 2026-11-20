# V5.8.1: kategoria produktu wybierana z listy (+ nowa kategoria), VAT podpowiadany z kategorii
import sys
p='panel/index.html'; s=open(p,encoding='utf-8').read()
def rep(a,b,c=1):
    global s
    n=s.count(a)
    if n!=c: sys.exit(f'Expected {c} got {n}: {a[:90]}')
    s=s.replace(a,b)
rep("""window.menuForm=(id=null)=>{const r=state.menu.find(x=>x.id===id);modal(r?'Edytuj produkt':'Nowy produkt',`${field('menuName','Nazwa','','required')}${field('menuCat','Kategoria','','required')}""",
"""const menuCats=()=>[...new Set(state.menu.map(x=>(x.category||'').trim()).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'pl'));
const catVat=c=>{const m={};state.menu.filter(x=>x.category===c&&x.tax_rate!=null).forEach(x=>m[x.tax_rate]=(m[x.tax_rate]||0)+1);const k=Object.keys(m).sort((a,b)=>m[b]-m[a])[0];return k==null?null:+k};
window.menuCatPick=()=>{const v=$('#menuCatSel').value,n=v==='__new';$('#menuCatNewWrap').hidden=!n;if(n){setTimeout(()=>$('#menuCat').focus(),0);return}const t=catVat(v);if(t!=null)$('#menuVat').value=t};
window.menuForm=(id=null)=>{const r=state.menu.find(x=>x.id===id),cats=menuCats();if(r&&r.category&&!cats.includes(r.category))cats.push(r.category);
 const catHtml=`<label>Kategoria</label><select id="menuCatSel" onchange="menuCatPick()"><option value="">– wybierz kategorię –</option>${cats.map(c=>`<option value="${esc(c)}">${esc(c)}</option>`).join('')}<option value="__new">＋ Nowa kategoria…</option></select><div id="menuCatNewWrap" hidden>${field('menuCat','Nazwa nowej kategorii','','maxlength="40"')}</div>`;
 modal(r?'Edytuj produkt':'Nowy produkt',`${field('menuName','Nazwa','','required')}${catHtml}""")
rep("""async()=>{const p={name:$('#menuName').value.trim(),category:$('#menuCat').value.trim(),""",
    """async()=>{const sel=$('#menuCatSel').value,cat=sel==='__new'?$('#menuCat').value.trim():sel;if(!$('#menuName').value.trim())return alert('Wpisz nazwę produktu.');if(!cat)return alert(sel==='__new'?'Wpisz nazwę nowej kategorii.':'Wybierz kategorię.');const p={name:$('#menuName').value.trim(),category:cat,""")
rep("""$('#menuCat').value=r.category||'';""","""$('#menuCatSel').value=r.category||'';""")
rep('Cafe Strych Manager <span>V5.8</span>','Cafe Strych Manager <span>V5.8.1</span>')
rep('Cafe Strych Manager <b>V5.8</b> • 20.11.2026','Cafe Strych Manager <b>V5.8.1</b> • 20.11.2026')
open(p,'w',encoding='utf-8').write(s); print('ok')
