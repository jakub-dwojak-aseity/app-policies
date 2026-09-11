# TERAZ — witryna `jd-japanese.pl`, SEO i dokumenty prawne

**Ten plik jest NADPISYWANY.** Jedno wejście do toru witrynowego, bez datowanych następców:
nie zakładaj `PRZEKAZANIE_<data>.md` ani „TERAZ_2" — osusz ten plik, historia zostaje w `git log`.
Pomiary i uzasadnienia: `jp-grammar/docs/PLAN_SEO_AEO.md` §11–§12. Otwarte pozycje backlogu
rodziny dla tego toru: **82** (SEO/AEO jako robota stała), **84** (adres kontaktowy),
**112** (zapowiadanie apek), **113** (wizytówka poza witryną).

## Od czego zacząć

**Witryna stoi i jest zrobiona od środka.** Domena przełączona 09.09.2026 (`CNAME` w repo, cztery
`A` GitHub Pages, HTTPS), dziesięć podstron w dwóch językach plus mapa rodziny, spis dokumentów,
strona o autorze i własna 404. `robots.txt` z robotami AI z nazwy, `sitemap.xml` (26 adresów),
`llms.txt`, `schema.org`, karty `og:image`, kadry w WebP, poczta rodziny na własnej domenie.
Bramki generatora: **zielone, 32 pliki, 10 aplikacji** (pomiar `--sprawdz`, 11.09).

**Tor witrynowy jedzie równolegle do wydań** i nie zjada miejsc w turze apek (§12 planu SEO).
Wchodząc tu, bierzesz albo **pozycję z kolejki niżej**, albo **obowiązkowy powrót po wydaniu apki**:
`marketingUrl` (§21.AB) · `wSklepie` przy premierze · przeliczenie stron po zmianie metadanych ·
import kadrów po zmianie zrzutów · **porównanie `<title>` na żywym adresie z repo**.

Kolejka toru, w kolejności taniości: (1) domknięcie poz. 84 — 16 plików prozy i stare adresy
w dwóch martwych drzewach, część to historia i **ma zostać**; (2) Search Console (Jakub);
(3) nazwy i opisy 42 zakupów w ASC; (4) 12 pól `marketingUrl`, łapanych przy składaniu apek;
(5) **strony tematyczne z katalogów** — materiał przejrzany (6 482 zielone werdykty z odciskiem),
wycena „miesiące" obalona; miny: dwa schematy `review.json`, brak go w Kifuku i Shindanie,
CC BY-SA w `kifuku/Vendor/tofugu`.

## Czeka na decyzję Jakuba

1. **Search Console — jedyna pętla zwrotna, jaką mamy.** Klucz ASC oddaje `403` na
   `analyticsReportRequests`, więc fraz z App Store nie zobaczy żaden skrypt. Do wyklikania:
   mapa ma **26 adresów, GSC znał 24**; powtórka prośby o zaindeksowanie dla **shindan, keigo,
   kifuku, onomatope** (pierwsze prośby mogły pójść **przed** przestawieniem `wSklepie`, czyli
   Google ma wersję ze znacznikiem „wkrótce" nad apką do kupienia); ewentualna druga własność
   „Prefiks URL", bo własność „Domena" obejmuje też `api.` i `admin.`.
2. **Poz. 112 — czy zapowiadać apki, których jeszcze nie ma.** Mechanizm „wkrótce w App Store"
   **już działa** dla `wSklepie: false`; otwarte jest tylko, czy objąć nim pozycje 62–69. Zapowiedź
   to obietnica z datą, której nie mamy. Wariant pośredni: dziedziny bez dat i bez kart.
3. **Poz. 113 — wizytówka poza witryną.** Zobowiązanie **cykliczne**, nie jednorazowe: koszt leży
   w rytmie publikowania, nie w treści (materiał jest) — kto prowadzi i jak często.
4. **Bunmyaku ma pauzę w nazwie** jako jedyna z dziesięciu — jedno wywołanie, ale **decyzja
   redakcyjna, nie porządek techniczny** (§21.X przyjmuje też w kolejce).

## Świeże miny

- **Strona wyliczana psuje się w ŹRÓDLE, nie w wytworze.** 09.09 metadane zmieniły się o 14:15,
  strony stały przeliczone o 10:35 i **dziesięć stron z dwudziestu czterech niosło stare tytuły
  przez pół dnia** — bramki mierzą wytwór, nie to, czy ktoś generator uruchomił.
- **Bramka 10 świeci dziś 5 rozjazdów** (Bunmyaku `terms.html` i `support.html` wobec
  `bunmyaku-n2/docs/app-store/`) — **nazwane, nieblokujące**, bo kopie leżą w cudzym repo.
  Dokumenty zmienia się **po obu stronach naraz**; podmiana po jednej topi prawdziwy sygnał.
- **Generator nie dotyka dokumentów prawnych.** Piszą w nie tylko `Tools/landmark-main.py`
  i `Tools/glowy_dokumentow.py` — **bez jednego renderowanego znaku zmiany**, i odmawiają pracy
  na pliku o innym kształcie. Przestarzałe wersje dostają `noindex, follow`, **nigdy `canonical`
  na nowszą** — to nie jest ta sama treść.
- **`docs/DOMENA.md` opisuje stan sprzed przełączenia** („nic z tego nie zostało wykonane").
  Kroki 1–10 są zrobione; czytaj go jak historię, nie jak instrukcję.
- **Klienta ASC `asc.py` to repo pożycza z `../kifuku/Tools`** — publiczne repozytorium świadomie
  nie ma go u siebie, tak jak nie ma klucza ani `ASC_ISSUER_ID`.

## Jak zmierzyć stan

```sh
cd ~/aseity/app-policies
python3 Tools/generuj-strony.py --sprawdz        # jedenaście bramek, bez zapisu
python3 Tools/generuj-strony.py                  # przelicz
python3 Tools/generuj-strony.py --powtarzalnie   # dwa przebiegi, bit w bit
python3 Tools/generuj-strony.py --sprawdz-sklep  # manifest kontra pięć witryn App Store (sieć)
python3 Tools/generuj-strony.py --zrzuty         # import kadrów z repo apek
python3 Tools/glowy_dokumentow.py --sprawdz      # canonical i noindex w dokumentach
python3 Tools/asc-marketing-url.py --apka <slug> # bez --zapisz: przebieg na sucho

# ZAWSZE po przeliczeniu — pomiar na żywym adresie, nie na plikach:
for u in kaname bunmyaku katsuyokei joshi kazoekata kuzushi shindan keigo kifuku onomatope; do
  curl -sS -L "https://jd-japanese.pl/apps/$u/" | grep -o '<title>[^<]*'
done
```

**Zielony komunikat narzędzia nie jest dowodem, że czynność zaszła.** Publikacja idzie z `main`
przez GitHub Pages i zajmuje około minuty — dopóki nie odpowie żywy adres, nic nie jest wydane.
