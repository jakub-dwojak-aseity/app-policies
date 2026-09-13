# TERAZ — witryna `jd-japanese.pl`, SEO i dokumenty prawne

**Ten plik jest NADPISYWANY.** Jedno wejście do toru witrynowego, bez datowanych następców:
nie zakładaj `PRZEKAZANIE_<data>.md` ani „TERAZ_2" — osusz ten plik, historia zostaje w `git log`.
Pomiary i uzasadnienia: `jp-grammar/docs/PLAN_SEO_AEO.md` §11–§12. Otwarte pozycje backlogu
rodziny dla tego toru: **82** (SEO/AEO jako robota stała), **84** (adres kontaktowy),
**112** (zapowiadanie apek), **113** (wizytówka poza witryną), **189** (strony tematyczne).

## Od czego zacząć

**Witryna mówi już o japońskim, a nie tylko o aplikacjach.** W nocy z 13 na 14.09.2026 doszło
**sześć stron tematycznych plus rozdroże, w dwóch językach** — czternaście plików, mapa
witryny **26 → 40 adresów**. Wcześniej wszystko, co tu stało, mówiło wyłącznie o dziesiątce apek,
a nikt nie wpisuje w Google „Kazoekata": wpisuje „jaki licznik do butelek" albo „は czy が".

| adres | z czego | ile |
|---|---|---|
| `/nauka/partykuly-japonskie/` | Joshi | 14 ról w 6 partykułach, 56 zdań |
| `/nauka/formy-czasownika/` | Katsuyokei | 14 form |
| `/nauka/liczniki-japonskie/` | Kazoekata | 22 liczniki, 44 zdania |
| `/nauka/mowa-potoczna/` | Kuzushi | 34 wzorce, 61 par zdań |
| `/nauka/keigo/` | Keigo | 32 pozycje |
| `/nauka/mylace-pary/` | Kaname | 13 par N5, 22 zdania z sytuacją i powodem |
| `/nauka/` i `/en/learn/` | rozdroże | żeby strony nie były sierotami |

Poza tym bez zmian: domena przełączona 09.09, dziesięć podstron produktowych w dwóch językach,
mapa rodziny, spis dokumentów, strona o autorze, własna 404, `robots.txt` z robotami AI
z nazwy, `llms.txt`, `schema.org`, karty `og:image`, kadry w WebP, poczta na własnej domenie.
**Bramki generatora: zielone, 46 plików, 10 aplikacji** (pomiar `--sprawdz`, 14.09).

**Tor witrynowy jedzie równolegle do wydań** i nie zjada miejsc w turze apek (§12 planu SEO).
Wchodząc tu, bierzesz albo **pozycję z kolejki niżej**, albo **obowiązkowy powrót po wydaniu
apki**: `marketingUrl` (§21.AB) · `wSklepie` przy premierze · przeliczenie stron po zmianie
metadanych · import kadrów po zmianie zrzutów · **porównanie `<title>` na żywym adresie
z repo**. Od 14.09 dochodzi szósty: **przeliczenie eksportu po zmianie katalogu** w Joshi,
Katsuyokei, Kazoekacie, Kuzushim, Keigo albo Kaname.

Kolejka toru, w kolejności taniości: (1) domknięcie poz. 84 — 16 plików prozy i stare adresy
w dwóch martwych drzewach, część to historia i **ma zostać**; (2) Search Console (Jakub);
(3) nazwy i opisy 42 zakupów w ASC; (4) **strony tematyczne dla pozostałej czwórki plus 60 punktów N5 Kaname —
poz. 189**, gdzie stoi, co blokuje którą.

**`marketingUrl` zszedł z kolejki 14.09 — pomiarem, nie robotą.** `asc-marketing-url.py`
na sucho oddaje **0 pól do zmiany, 20 już zgodnych**: kolejka mówiła o dwunastu polach na
starym adresie albo pustych, a stan ASC temu przeczy. Zostaje **odruch, nie pozycja**:
przebieg na sucho przy każdym składaniu, bo okno zapisu to `WAITING_FOR_REVIEW` i zamyka
się samo (§21.AB).

## Jak działają strony tematyczne — w trzech zdaniach

**Witryna nie liczy odcisków i nie umie ich policzyć.** Każda siostra ma u siebie
`Tools/review-content.py --eksport-www`, który zapisuje `docs/www/eksport.json` z jednostkami
darmowymi, zielonymi we wszystkich soczewkach i z aktualnym odciskiem; generator czyta gotowy
plik. Odwrotność — pięć kopii cudzej logiki hashowania po tej stronie — rozjechałaby się przy
pierwszej zmianie u siostry i zrobiła to **cicho**: strona by nie zniknęła, tylko przestała
odpadać przy rozjeździe.

Format eksportu jest wspólny dla wszystkich sześciu: `schemaVersion`, `zrodlo`
(ścieżka katalogu + jego commit), `grupy`, `jednostki` z `nazwa`/`glosa`/`wyjasnienie`
w obu językach, `przyklady` i `odciski`. Wyjaśnienie wieloakapitowe rozdziela pusta linia.
Przykład ma cztery pola opcjonalne: `jpPelne` (forma pełna przed skrótem, Kuzushi),
`kontekst` i `uwaga` (sytuacja nad zdaniem i powód pod nim, Kaname) oraz `pl`/`en`
(tłumaczenie). Nagłówkiem hasła jest `termin` **albo** `nazwa` — para kontrastowa
krótkiej nazwy nie ma i mieć nie może.

## Czeka na decyzję Jakuba

1. **Czy umorzone zastrzeżenie wpuszcza hasło na stronę** (poz. 189). Dziś **nie** — eksport
   wymaga `ok` wprost. Kosztowało to dwie pozycje Keigo, przy których `--stats` pokazuje zero
   zastrzeżeń. Reguła z poz. 82 brzmi dosłownie „wszystkie soczewki mają `ok`".
2. **Bunmyaku i Onomatope dadzą 351 i 84 hasła** — jedna strona na tyle pozycji jest zła tak
   samo jak 351 stron po jednym słowie. Grupowanie to decyzja redakcyjna.
3. **Search Console — jedyna pętla zwrotna, jaką mamy.** Klucz ASC oddaje `403` na
   `analyticsReportRequests`. Do wyklikania: **mapa ma teraz 38 adresów**, GSC znał 24 —
   zgłosić od nowa; powtórka prośby o zaindeksowanie dla **shindan, keigo, kifuku, onomatope**
   (pierwsze prośby mogły pójść **przed** przestawieniem `wSklepie`); ewentualna druga
   własność „Prefiks URL", bo własność „Domena" obejmuje też `api.` i `admin.`.
4. **Poz. 112 — czy zapowiadać apki, których jeszcze nie ma.** Mechanizm „wkrótce w App Store"
   **już działa** dla `wSklepie: false`; otwarte jest tylko, czy objąć nim pozycje 62–69.
5. **Poz. 113 — wizytówka poza witryną.** Zobowiązanie **cykliczne**: koszt leży w rytmie
   publikowania, nie w treści. **Strony tematyczne zmieniły tu rachunek** — jest teraz
   129 haseł w gotowym kształcie do wystawiania pojedynczo.
6. **Bunmyaku ma pauzę w nazwie** jako jedyna z dziesięciu — decyzja redakcyjna (§21.X).
7. **Przegląd okiem stron tematycznych.** Rozszerzenie Chrome było w nocy odłączone, więc
   układ sprawdzony w znaczniku, nie na ekranie: jasny i ciemny motyw, szerokość telefonu.

## Świeże miny

- **Strona wyliczana psuje się w ŹRÓDLE, nie w wytworze.** 09.09 metadane zmieniły się
  o 14:15, strony stały przeliczone o 10:35 i **dziesięć stron z dwudziestu czterech niosło
  stare tytuły przez pół dnia**. Od 14.09 pilnuje tego przy eksportach **bramka 13**:
  porównuje commit katalogu zapisany w eksporcie z bieżącym stanem repo siostry. Uwaga
  nazwana, nieblokująca — katalog leży w cudzym drzewie.
- **Bramka 12 i 13 sprawdzone MUTACJĄ, nie zielenią.** Podstawiony zerowy commit, pusta nazwa
  angielska i hasło bez odcisku dały trzy komunikaty i kod 1. Zielony zestaw nic nie dowodzi,
  dopóki nie wiadomo, co go wywala.
- **Bramka 10 świeci dalej 5 rozjazdów** (Bunmyaku `terms.html` i `support.html` wobec
  `bunmyaku-n2/docs/app-store/`) — **nazwane, nieblokujące**, bo kopie leżą w cudzym repo.
  Dokumenty zmienia się **po obu stronach naraz**; podmiana po jednej topi prawdziwy sygnał.
- **Tekst własny witryny urósł z 42 do 61 kluczy `NAPISY`** — tytuł i jedno zdanie na temat,
  i nic ponadto. Ta liczba jest miarą: jeśli rośnie dalej, strona zaczęła mówić od siebie.
- **Generator nie dotyka dokumentów prawnych.** Piszą w nie tylko `Tools/landmark-main.py`
  i `Tools/glowy_dokumentow.py`. Przestarzałe wersje dostają `noindex, follow`, **nigdy
  `canonical` na nowszą** — to nie jest ta sama treść.
- **`docs/DOMENA.md` opisuje stan sprzed przełączenia.** Kroki 1–10 są zrobione; czytaj go
  jak historię, nie jak instrukcję.
- **Klienta ASC `asc.py` to repo pożycza z `../kifuku/Tools`** — publiczne repozytorium
  świadomie nie ma go u siebie, tak jak nie ma klucza ani `ASC_ISSUER_ID`.

## Jak zmierzyć stan

```sh
cd ~/aseity/app-policies
python3 Tools/generuj-strony.py --sprawdz        # czternaście bramek, bez zapisu
python3 Tools/generuj-strony.py                  # przelicz
python3 Tools/generuj-strony.py --powtarzalnie   # dwa przebiegi, bit w bit
python3 Tools/generuj-strony.py --sprawdz-sklep  # manifest kontra pięć witryn App Store (sieć)
python3 Tools/generuj-strony.py --zrzuty         # import kadrów z repo apek
python3 Tools/glowy_dokumentow.py --sprawdz      # canonical i noindex w dokumentach
python3 Tools/asc-marketing-url.py --apka <slug> # bez --zapisz: przebieg na sucho

# eksport przejrzanej treści — w repozytorium siostry, nie tutaj:
cd ~/aseity/<joshi-ios|katsuyokei-ios|kazoekata-ios|kuzushi-ios|keigo-ios|jp-grammar-1.2.5>
python3 Tools/review-content.py --eksport-www

# ZAWSZE po przeliczeniu — pomiar na żywym adresie, nie na plikach:
for u in kaname bunmyaku katsuyokei joshi kazoekata kuzushi shindan keigo kifuku onomatope; do
  curl -sS -L "https://jd-japanese.pl/apps/$u/" | grep -o '<title>[^<]*'
done
for t in partykuly-japonskie mylace-pary formy-czasownika liczniki-japonskie mowa-potoczna keigo; do
  curl -sS -L "https://jd-japanese.pl/nauka/$t/" | grep -o '<title>[^<]*'
done
```

**Zielony komunikat narzędzia nie jest dowodem, że czynność zaszła.** Publikacja idzie z `main`
przez GitHub Pages i zajmuje około minuty — dopóki nie odpowie żywy adres, nic nie jest wydane.
