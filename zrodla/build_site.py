# Buduje strone: python3 build_site.py  (menu z menu_data.py -> do-wgrania/strona/index.html + podglad/strona-podglad.html)
R='/home/claude/CafeStrych'
import json,base64,re,sys
sys.path.insert(0,R+'/zrodla')
from menu_data import T,TABS
S=R+'/zrodla/'
src=open(R+'/zrodla/strona-szablon.html',encoding='utf-8').read()
menu=[dict(id=s['id'],name=s['name'],tab=s['tab'],sizes=s['sizes'],note=s.get('note',''),items=[[i[0],i[1],i[2]] for i in s['items']]) for s in T]
out=src.replace('__MENU__',json.dumps(menu,ensure_ascii=False)).replace('__TABS__',json.dumps(TABS,ensure_ascii=False))
open(R+'/do-wgrania/strona/index.html','w',encoding='utf-8').write(out)
# preview: images inline, demo news, no supabase
pv=out
from PIL import Image
import io,os
def b64(p):
    im=Image.open(p);im.thumbnail((1100,1100))
    b=io.BytesIO();im.save(b,'WEBP',quality=58 if im.mode=='RGB' else 85,method=6)
    return 'data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()
names=[f[:-5] for f in os.listdir(R+'/do-wgrania/strona/img') if f.endswith('.webp')]
# JS builds paths like 'img/'+name+'.webp' -> provide map
imgs={n:b64(R+f'/do-wgrania/strona/img/{n}.webp') for n in sorted(names) if __import__('os').path.exists(R+f'/do-wgrania/strona/img/{n}.webp')}
for n,d in imgs.items(): pv=pv.replace(f'img/{n}.webp',d)
pv=pv.replace("'img/'+","IMG(").replace("+'.webp'",")")
poster=open(S+'podglad-plakat.txt').read()
demo=f"""<script>window.STRYCH_IMG={json.dumps(imgs)};function IMG(n){{return window.STRYCH_IMG[n]||''}}
(function(){{var d=function(o){{var x=new Date();x.setDate(x.getDate()+o);return x.toISOString().slice(0,10)}};
window.STRYCH_PREVIEW={{news:[
 {{id:'n1',title:'Muzyka na żywo w każdą środę',body:'W październiku grają u nas: Michał Mantaj (nowy muzyk!), Maciej Smycz, Daria Piórek, Tymoteusz Walko i Mateusz Barański-Kledzik.\\n\\nStart o 20:00, wstęp wolny. Stoliki warto rezerwować wcześniej.',image_url:'{poster}',event_date:d((3-new Date().getDay()+7)%7||7),pinned:true,created_at:new Date().toISOString()}},
 {{id:'n2',title:'Wieczór poetycki na Strychu',body:'Przynieś swój ulubiony wiersz albo po prostu posłuchaj. Herbata Strychowa w cenie promocyjnej.',image_url:null,event_date:d(9),pinned:false,created_at:new Date().toISOString()}},
 {{id:'n3',title:'Rozgrzewające grzańce już w karcie',body:'Wróciły grzańce bezalkoholowe: wino czerwone z przyprawami i piwo z przyprawami. Idealne na jesienne wieczory przy piecu.',image_url:IMG('hero-antresola'),event_date:null,pinned:false,created_at:new Date(Date.now()-86400000*2).toISOString()}}
]}}}})();</script>"""
pv=pv.replace('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>',demo)
pv=pv.replace('<title>Cafe Strych – kawiarnia','<title>PODGLĄD – Cafe Strych – kawiarnia')
pv=pv.replace('href="https://fonts.googleapis.com/css2','href="https://fonts.googleapis.com/css2')
open(R+'/podglad/strona-podglad.html','w',encoding='utf-8').write(pv)
print('ok',len(out),len(pv),sorted(imgs))
