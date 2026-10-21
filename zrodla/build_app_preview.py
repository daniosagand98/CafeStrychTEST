# Buduje podgląd aplikacji bez logowania (dane demo, nic nie trafia do bazy):
#   python3 build_app_preview.py
# wejście:  panel/index.html + zrodla/podglad-mock.js
# wyjście:  podglad/aplikacja-podglad.html
import base64, io
from PIL import Image, ImageDraw, ImageFont

import os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # katalog repozytorium
app = open(f'{R}/panel/index.html', encoding='utf-8').read()
mock = open(f'{R}/zrodla/podglad-mock.js', encoding='utf-8').read()
poster = open(f'{R}/zrodla/podglad-plakat.txt').read().strip()
logo = 'data:image/webp;base64,' + base64.b64encode(open(f'{R}/panel/logo.webp', 'rb').read()).decode()

# przykładowy „zrzut ekranu” do demo zgłoszenia błędu
im = Image.new('RGB', (520, 300), (28, 16, 12)); d = ImageDraw.Draw(im)
try:
    f1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
    f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
except OSError:
    f1 = f2 = ImageFont.load_default()
d.rounded_rectangle((20, 20, 500, 280), 18, fill=(53, 34, 25), outline=(224, 173, 103))
d.text((44, 48), 'Nowa rezerwacja', font=f1, fill=(255, 242, 220))
d.rounded_rectangle((44, 100, 476, 200), 12, fill=(80, 30, 26), outline=(238, 112, 101))
d.text((62, 116), '⚠ Błąd zapisu', font=f1, fill=(255, 185, 177))
d.text((62, 156), "Could not find the 'place_name' column", font=f2, fill=(255, 210, 200))
d.text((44, 226), 'zrzut ekranu – dane demo', font=f2, fill=(200, 173, 143))
b = io.BytesIO(); im.save(b, 'PNG')
bug_img = 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

mock = mock.replace('POSTER_DATA', poster).replace('BUG_IMG', bug_img)
s = app
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:60], s.count(a)); s = s.replace(a, b)
rep('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>\n', '')
st = s.index('const SUPABASE_URL='); en = s.index('\n', s.index('const sb=supabase.createClient'))
s = s[:st] + mock + s[en:]
rep('src="logo.webp"', f'src="{logo}"', 2)
rep('<title>Cafe Strych</title>', '<title>Cafe Strych – PODGLĄD</title>')
icon = lambda f: 'data:image/png;base64,' + base64.b64encode(open(f'{R}/panel/{f}', 'rb').read()).decode()
rep('<link rel="manifest" href="manifest.webmanifest">', '')
rep('href="favicon-32.png"', f'href="{icon("favicon-32.png")}"')
rep('href="apple-touch-icon.png"', f'href="{icon("apple-touch-icon.png")}"')
rep('<div id="toast" class="toast">Zapisano</div>', '<div id="toast" class="toast">Zapisano</div><div style="position:fixed;z-index:200;right:8px;top:8px;padding:5px 10px;border-radius:999px;background:#e0ad67;color:#27150c;font:800 11px system-ui;pointer-events:none">PODGLĄD • dane demo</div>')
open(f'{R}/podglad/aplikacja-podglad.html', 'w', encoding='utf-8').write(s)
print('ok', len(s))
