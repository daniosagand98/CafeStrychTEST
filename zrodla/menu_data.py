import re
# Jedno źródło menu Cafe Strych (przepisane z karty, październik 2026).
# Każda sekcja: id, nazwa, grupa zakładki na stronie, nagłówki rozmiarów, VAT, notatka, pozycje.
# Pozycja: (nazwa, opis, [ceny w kolejności rozmiarów; None = brak]) lub z własnym VAT jako 4. element.

T = [
 # ---------- KAWA I CZEKOLADA ----------
 dict(id='kawa', name='Kawa', tab='kawa', sizes=[''], vat=23, sketch='szkic-kawiarka',
  note='Do wyboru: mleko zwykłe / bez laktozy', items=[
  ('Kawa aromatyzowana', 'podawana tradycyjnie w kawiarce · smaki: czekoladowo-migdałowa, kokosowa, marcepanowa, karmelowa, śliwka z cynamonem, cynamonowa, orzechowo-kremowa', [17]),
  ('Kawa czarna', 'do wyboru: z ekspresu / mielona / rozpuszczalna', [13]),
  ('Flat White (kawa biała)', '', [16]),
  ('Cappuccino', '', [16]),
  ('Latte Macchiato', '', [17]),
  ('Kawa z bitą śmietaną', '', [22]),
  ('Espresso, woda', '', [13]),
  ('Podwójne espresso', '', [20]),
  ('Espresso z tonikiem i cytryną', '', [20]),
  ('Kawa mrożona', '', [18]),
  ('Kawa mrożona z mlekiem i bitą śmietaną 0,4 l', '', [25]),
  ('Syrop do kawy', 'dyniowy, kokosowy, migdałowy, orzechowy, karmelowy, waniliowy, miętowy, różany, czarny bez, czekoladowy, cynamonowy', [3]),
 ]),
 dict(id='czekolada', name='Czekolada', tab='kawa', sizes=[''], vat=8, items=[
  ('Gorąca czekolada 0,3 l', '', [17]),
  ('Gorąca czekolada z bitą śmietaną 0,3 l', '', [23]),
  ('Gorąca czekolada z konfiturą i bitą śmietaną 0,3 l', 'smaki: wiśniowa, truskawkowa, malinowa, jagodowa', [26]),
  ('Czekolada mrożona z bitą śmietaną 0,4 l', '', [26]),
  ('Syrop do czekolady', 'dyniowy, kokosowy, migdałowy, orzechowy, karmelowy, różany, czarny bez, miętowy, waniliowy, cynamonowy', [3]),
 ]),
 # ---------- HERBATA ----------
 dict(id='herbata', name='Herbata', tab='herbata', sizes=['0,3 l'], vat=23, sketch='szkic-herbata', items=[
  ('Herbata w torebce', 'do wyboru: Ceylon / Earl Grey / miętowa / zielona / owoce leśne', [13]),
  ('Herbata liściasta', 'zapytaj obsługę o dostępne smaki :)', [17]),
  ('Napar', 'świeża mięta, świeży imbir, cytryna, goździki, miód', [17]),
 ]),
 dict(id='herbata-po-naszemu', name='Herbata po naszemu', tab='herbata', sizes=['0,3 l','0,5 l'], vat=23, items=[
  ('Herbata Rybaka', 'czarna z sokiem malinowym i plasterkiem cytryny lub czarna z sokiem korzennym i plasterkiem pomarańczy', [16,21]),
  ('Herbata Gdyńska', 'czarna z miodem, goździkami, plasterkiem cytryny i pomarańczy', [18,23]),
  ('Herbata Strychowa', 'czarna z imbirem, cynamonem, miodem, jabłkiem i pomarańczą', [18,23]),
  ('Herbata Babuni', 'czarna z konfiturą · smaki: jagodowa, truskawkowa, wiśniowa, malinowa', [18,None]),
 ]),
 # ---------- BEZALKOHOLOWE ----------
 dict(id='napoje', name='Napoje i soki', tab='bezalko', sizes=['0,3 l','1,0 l'], vat=23, items=[
  ('Coca-Cola', '', [10,22]),
  ('Sprite', '', [10,22]),
  ('Tonic', '', [10,22]),
  ('Sok', 'jabłkowy, grejpfrutowy, czarna porzeczka, bananowy, pomarańczowy, ananasowy, winogronowy, pomidorowy', [10,22], 8),
  ('Woda źródlana', 'gazowana Żywiec Zdrój / niegazowana Cisowianka', [7,15]),
  ('Red Bull 0,25 l', '', [15,None]),
 ]),
 dict(id='koktajle-bezalko', name='Koktajle bezalkoholowe', tab='bezalko', sizes=['400 ml'], vat=8, items=[
  ('Wilk Morski', 'syrop Blue Curacao, sok bananowy, sok pomarańczowy', [18]),
  ('Shrek', 'syrop miętowy, sok jabłkowy, sok grejpfrutowy, sok pomarańczowy', [18]),
  ('Czerwony Kapturek', 'syrop Grenadina, cytryna, sok jabłkowy, sok grejpfrutowy', [18]),
  ('Lemoniada', 'zaufaj nam :)', [18]),
 ]),
 dict(id='grzance-bezalko', name='Grzańce bezalkoholowe', tab='bezalko', sizes=[''], vat=8, items=[
  ('Wino czerwone z przyprawami 0,2 l', '', [20]),
  ('Piwo z przyprawami 0,5 l', '', [21]),
 ]),
 dict(id='piwo-bezalko', name='Piwo bezalkoholowe', tab='bezalko', sizes=['0,5 l'], vat=8, items=[
  ('Miłosław IPA 0,0%', '', [17]),
  ('Lech Smakowy 0,0%', '', [17]),
  ('Heineken 0,0%', '', [17]),
  ('Książęce Pszenica 0,0%', '', [17]),
 ]),
 dict(id='wino-bezalko', name='Wino bezalkoholowe', tab='bezalko', sizes=['kieliszek','butelka'], vat=8, items=[
  ('Wino bezalkoholowe', 'zapytaj obsługę :)', [15,80]),
 ]),
 # ---------- PIWO ----------
 dict(id='piwo-beczka', name='Piwo z beczki', tab='piwo', sizes=['0,3 l','0,5 l','1,0 l'], vat=23, sketch='szkic-piwo', items=[
  ('Tyskie Gronie', '', [13,16,30]),
  ('Książęce Złote Pszeniczne', '', [14,17,32]),
 ]),
 dict(id='piwo-butelka', name='Piwo z butelki', tab='piwo', sizes=['0,5 l','1,0 l'], vat=23, items=[
  ('Lech Premium', '', [16,30]),
  ('Perła', '', [16,30]),
  ('Pilsner Urquell', '', [17,32]),
  ('Heineken', '', [17,32]),
  ('Kozel Ciemny', '', [17,32]),
  ('Piwo kraftowe', 'zapytaj obsługę', [22,37]),
 ]),
 dict(id='syropy-piwo', name='Syropy do piwa', tab='piwo', sizes=['0,3 l','0,5 l','1,0 l'], vat=23,
  note='Smaki: malinowy, wiśniowy, kokosowy, czarny bez, arbuzowy, marakuja, miętowy, korzenny, imbirowy, migdałowy, karmelowy', items=[
  ('Syrop do piwa', '', [2,3,4]),
 ]),
 # ---------- WINO ----------
 dict(id='wino', name='Wino', tab='wino', sizes=['kieliszek','butelka'], vat=23, items=[
  ('Winiarnia Zamojska', 'polskie wino różowe półsłodkie – lekka czerwona porzeczka', [14,80]),
  ('Luna Argenta Moscato', 'białe włoskie półwytrawne, intensywny bukiet egzotycznych owoców, nuty kwiatowe i miód', [15,90]),
  ('Beauvillion', 'białe francuskie półwytrawne, delikatne, o świeżym owocowym bukiecie', [14,85]),
  ('Cono Sur', 'białe chilijskie wytrawne, orzeźwiające, o owocowym aromacie', [14,80]),
  ('Sheep Dreams Sauvignon Blanc', 'białe nowozelandzkie wytrawne, owoce tropikalne, nuta agrestu i brzoskwini', [17,110]),
  ('Los Pagos', 'czerwone chilijskie wytrawne o przyjemnym owocowym aromacie', [14,80]),
  ('Primitivo Puglia', 'czerwone włoskie półwytrawne, aromatyczne i pikantne', [14,80]),
  ('Primitivo di Manduria', 'czerwone włoskie wytrawne, aromaty śliwek i wiśni', [16,110]),
  ('Wino spod lady', 'zapytaj obsługę, co ciekawego trzymamy na barze :)', [15,90]),
 ]),
 dict(id='prosecco', name='Prosecco', tab='wino', sizes=['kieliszek','butelka'], vat=23, items=[
  ('Martini Prosecco', 'białe włoskie musujące wytrawne', [15,90]),
 ]),
 dict(id='wermuty', name='Wermuty', tab='wino', sizes=[''], vat=23, items=[
  ('Martini Bianco', 'białe włoskie słodkie, nuta wanilii i aromat ziół', [14]),
  ('Martini Rosso', 'czerwone włoskie słodkie, nuta karmelu i aromat ziół', [14]),
 ]),
 # ---------- DRINKI ----------
 dict(id='drinki', name='Drinki tradycyjne', tab='drinki', sizes=[''], vat=23, sketch='szkic-koktajle', items=[
  ('Cuba Libre', 'rum Bacardi, Coca-Cola, limonka lub cytryna', [26]),
  ('Whisky Sour', 'whisky Jim Beam, sok z cytryny, syrop cukrowy, białko', [32]),
  ('Mojito', 'rum Bacardi, mięta, limonka, cukier, Sprite', [32]),
  ('Aperol Spritz', 'likier Aperol, Martini Prosecco, woda gazowana, plasterek pomarańczy', [30]),
  ('Margarita', 'tequila złota Olmeca, sok z limonki, likier Triple Sec, sól', [28]),
  ('Caipiroska', 'wódka, limonka, cukier trzcinowy', [27]),
  ('Krwawa Mary', 'wódka, sok pomidorowy, przyprawy', [28]),
  ('Sex on the Beach', 'wódka, likier Archers brzoskwiniowy, sok pomarańczowy, syrop Grenadina', [28]),
  ('Tequila Sour', 'tequila Olmeca, sok z limonki, sok z cytryny, cukier, białko', [30]),
  ('Negroni', 'gin, Campari, Martini Rosso', [30]),
  ('Hugo', 'Martini Prosecco, woda gazowana, syrop z czarnego bzu, świeża limonka, świeża mięta', [27]),
 ]),
 dict(id='nasze-drinki', name='Nasze pomysły na drinka', tab='drinki', sizes=[''], vat=23, items=[
  ('Początek', 'Martini Bianco, Sprite, cytryna', [24]),
  ('Wspomnienie', 'likier Campari, sok pomarańczowy', [24]),
  ('Przytulny Kącik', 'wódka żurawinowa, syrop Grenadina, sok pomarańczowy', [25]),
  ('Rok 1926', 'wódka Żubrówka trawiasta, sok jabłkowy', [25]),
  ('Strychowy', 'likier Blue Curacao, wódka, Sprite, sok z cytryny', [26]),
  ('Samotna Dziewczyna', 'likier bananowy, wódka, syrop Blue Curacao, sok ananasowy', [26]),
  ('Marzenie', 'likier Passoa, wódka, sok pomarańczowy', [27]),
  ('Satyra', 'likier Jagermeister, sok z cytryny, sok jabłkowy', [27]),
  ('Stały Bywalec', 'likier Carambola, nalewka cytrynowa, sok grejpfrutowy, syrop Blue Curacao', [27]),
  ('Poezja', 'likier melonowy, wódka, sok winogronowy, woda, sok z cytryny', [27]),
  ('Ojciec Chrzestny', 'rum Malibu, wódka, sok z czarnej porzeczki, sok pomarańczowy', [27]),
  ('Zachód Słońca', 'wódka, sok pomarańczowy, cytryna, syrop Grenadina', [27]),
  ('Miętowy Lodowiec', 'nalewka cytrynowa, sok grejpfrutowy, syrop Blue Curacao', [28]),
  ('Zazdrosna Żona', 'tequila Olmeca, likier Blue Curacao, sok grejpfrutowy', [30]),
  ('Melancholia', 'whisky Johnnie Walker, Martini Bianco, sok grejpfrutowy', [32]),
  ('Krwawy Zdzisiu', 'rum czarny Bacardi, likier Campari, sok pomarańczowy, syrop marakuja', [32]),
  ('Na Pożegnanie', 'tequila srebrna, rum Malibu, sok pomarańczowy', [32]),
 ]),
 dict(id='shoty', name='Shoty', tab='drinki', sizes=['40 ml'], vat=23, items=[
  ('Wściekły Pies', 'wódka, sok malinowy, Tabasco', [12]),
  ('Małpi Mózg', 'likier Archers, krem Bailey’s, syrop Grenadina', [13]),
  ('Kamikadze – set 4 shoty', 'wódka, sok z cytryny, likier Blue Curacao', [34]),
  ('Tequila złota', 'tequila Olmeca, pomarańcza, cynamon', [15]),
  ('Tequila srebrna', 'tequila Olmeca, cytryna, sól', [15]),
 ]),
 # ---------- ALKOHOLE ----------
 dict(id='wodka', name='Wódka', tab='alkohole', sizes=['40 ml','butelka 0,5 l'], vat=23, items=[
  ('Luksusowa', '', [10,100]), ('Finlandia', '', [11,115]), ('Biały Bocian', '', [11,115]),
 ]),
 dict(id='wodki-smakowe', name='Wódki smakowe', tab='alkohole', sizes=['40 ml'], vat=23, items=[
  ('Żurawinowa', '', [10]), ('Wiśniówka', '', [10]), ('Malinówka', '', [10]), ('Pigwówka', '', [10]), ('Żubrówka Trawiasta', '', [10]),
 ]),
 dict(id='nalewki', name='Nalewki spod lady', tab='alkohole', sizes=['40 ml'], vat=23, items=[
  ('Kieliszek nalewki', 'zapytaj obsługę o dostępne smaki :)', [13]),
 ]),
 dict(id='whisky', name='Whisky', tab='alkohole', sizes=['40 ml','butelka 0,7 l'], vat=23, items=[
  ("Ballantine's", '', [16,220]), ('Johnnie Walker', '', [16,220]), ('Jameson Irish', '', [17,240]),
  ('Jim Beam White Bourbon', '', [16,None]), ("Jack Daniel's", '', [18,260]), ('Chivas Regal', '', [20,None]),
 ]),
 dict(id='likiery', name='Likiery', tab='alkohole', sizes=['40 ml'], vat=23, items=[
  ('Blue Curacao','',[14]),('Melon','',[14]),('Banan','',[14]),('Amaretto','',[14]),('Kahlua','',[15]),('Passoa','',[14]),
  ('Archers','',[15]),('Triple Sec','',[14]),('Jagermeister','',[14]),('Fernet Blanca','',[16]),('Campari','',[15]),
 ]),
 dict(id='kremy', name='Kremy', tab='alkohole', sizes=['40 ml'], vat=23, items=[('Baileys','',[16]),('Advocaat','',[10])]),
 dict(id='gin', name='Gin', tab='alkohole', sizes=['40 ml'], vat=23, items=[("Seagram's",'',[14]),('Lubuski','',[14])]),
 dict(id='rum', name='Rum', tab='alkohole', sizes=['40 ml'], vat=23, items=[
  ('Bacardi', 'białe lub czarne', [16]), ('Havana Club', 'brązowy', [16]), ('Captain Morgan', 'brązowy', [16]),
 ]),
 dict(id='brandy', name='Brandy', tab='alkohole', sizes=['40 ml'], vat=23, items=[('Stock 84','',[17])]),
 # ---------- JEDZENIE ----------
 dict(id='na-slodko', name='Na słodko', tab='jedzenie', sizes=[''], vat=8, items=[
  ('Ciasto domowej roboty', 'podawane z porcją bitej śmietany · do wyboru: sernik / jabłecznik', [21]),
  ('Ciasto spod lady', 'skuś się, bo warto :)', [24]),
  ('Lody w pucharku', '3 gałki, bita śmietana, polewa', [28]),
 ]),
 dict(id='przekaski', name='Przekąski', tab='jedzenie', sizes=[''], vat=8, sketch='szkic-nachos', items=[
  ('Paluszki Lajkonik','',[16]),('Orzeszki solone','',[16]),('Chipsy','paprykowe / solone',[16]),('Nachos z sosem serowym','',[23]),
 ]),
 dict(id='zakaski', name='Zakąski', tab='jedzenie', sizes=[''], vat=8, items=[
  ('Pajda chleba', '2 kromki chleba z domowym smalcem i ogórkiem', [17]),
  ('Domowe tosty na ciepło', 'zapiekane 4 trójkąty', [17]),
  ('Panini', 'do wyboru: szynka / mozzarella / sałata rzymska lub pomidor / mozzarella / pesto', [18]),
  ('Krokiety na ciepło (2 szt.)', 'zapytaj obsługę, co dziś mamy', [17]),
  ('Łazanki na ciepło', 'z kapustą i grzybami', [18]),
  ('Deska rozmaitości dla 2 osób', 'do wyboru: deska serów / deska wędlin', [38]),
 ]),
]

TABS = [('kawa','Kawa i czekolada'),('herbata','Herbata'),('bezalko','Bez procentów'),('piwo','Piwo'),('wino','Wino'),('drinki','Drinki i shoty'),('alkohole','Mocniejsze'),('jedzenie','Do jedzenia')]

# Nazwy kategorii w POS (krótsze, sortowane alfabetycznie w aplikacji)
POS_CAT = {'kawa':'Kawa','czekolada':'Czekolada','herbata':'Herbata','herbata-po-naszemu':'Herbata po naszemu','napoje':'Napoje i soki',
 'koktajle-bezalko':'Koktajle bezalkoholowe','grzance-bezalko':'Grzańce bezalkoholowe','piwo-bezalko':'Piwo bezalkoholowe','wino-bezalko':'Wino bezalkoholowe',
 'piwo-beczka':'Piwo z beczki','piwo-butelka':'Piwo z butelki','syropy-piwo':'Dodatki','wino':'Wino','prosecco':'Wino','wermuty':'Wermuty',
 'drinki':'Drinki','nasze-drinki':'Drinki – nasze','shoty':'Shoty','wodka':'Wódka','wodki-smakowe':'Wódka','nalewki':'Nalewki',
 'whisky':'Whisky','likiery':'Likiery i kremy','kremy':'Likiery i kremy','gin':'Gin, rum, brandy','rum':'Gin, rum, brandy','brandy':'Gin, rum, brandy',
 'na-slodko':'Desery','przekaski':'Przekąski','zakaski':'Zakąski'}

def pos_items():
    out = []
    for sec in T:
        sizes = sec['sizes']
        for it in sec['items']:
            name, desc, prices = it[0], it[1], it[2]
            vat = it[3] if len(it) > 3 else sec['vat']
            cat = POS_CAT[sec['id']]
            if sec['id'] in ('kawa','czekolada') and name.startswith('Syrop'):
                cat = 'Dodatki'
            for size, price in zip(sizes, prices):
                if price is None: continue
                label = name
                if re.search(r'\d,\d+ l|\d+ ml', name):
                    pass
                elif len(sizes) > 1 or (size and size not in ('40 ml','400 ml')):
                    if size: label = f'{name} {size}'
                elif size == '40 ml' and sec['id'] in ('wodka','whisky'):
                    label = f'{name} 40 ml'
                out.append((label, cat, price, vat))
    return out

if __name__ == '__main__':
    items = pos_items()
    print(len(items), 'pozycji POS')
    for x in items[:12]: print(x)
