# TERAZ — witryna `jd-japanese.pl`, SEO i dokumenty prawne

**Ten plik jest NADPISYWANY.** Jedno wejście do toru witrynowego, bez datowanych następców:
nie zakładaj `PRZEKAZANIE_<data>.md` ani „TERAZ_2" — osusz ten plik, historia zostaje w `git log`.
Pomiary i uzasadnienia: `jp-grammar/docs/PLAN_SEO_AEO.md` §11–§12. Otwarte pozycje backlogu
rodziny dla tego toru: **82** (SEO/AEO jako robota stała), **84** (adres kontaktowy),
**112** (zapowiadanie apek), **113** (wizytówka poza witryną), **189** (strony tematyczne).

## Od czego zacząć

**Witryna mówi już o japońskim, a nie tylko o aplikacjach.** W nocy z 13 na 14.09.2026 doszło
**osiem tematów, z czego cztery rozpisane na sekcje**; 15.09 doszedł podział onomatopei
i mosty między tematami — mapa witryny **26 → 84 adresy**, dwadzieścia sekcji. Wcześniej wszystko, co tu stało, mówiło wyłącznie o dziesiątce apek,
a nikt nie wpisuje w Google „Kazoekata": wpisuje „jaki licznik do butelek" albo „は czy が".

| adres | z czego | ile |
|---|---|---|
| `/nauka/partykuly-japonskie/` | Joshi | 14 ról w 6 partykułach, 56 zdań |
| `/nauka/formy-czasownika/` | Katsuyokei | 14 form |
| `/nauka/liczniki-japonskie/` | Kazoekata | 22 liczniki, 44 zdania |
| `/nauka/mowa-potoczna/` + 5 sekcji | Kuzushi | 34 wzorce wg rodzaju skrótu, 61 par zdań |
| `/nauka/keigo/` + 2 sekcje | Keigo | 13 sytuacji, 19 słów |
| `/nauka/mylace-pary/` | Kaname | 13 par N5, 22 zdania z sytuacją i powodem |
| `/nauka/onomatopeje/` + 6 sekcji | Onomatope | 66 haseł, 132 zdania |
| `/nauka/gramatyka-n5/` + 7 grup | Kaname | 60 punktów N5, 123 zdania |
| `/nauka/` i `/en/learn/` | rozdroże | żeby strony nie były sierotami |

Poza tym bez zmian: domena przełączona 09.09, dziesięć podstron produktowych w dwóch językach,
mapa rodziny, spis dokumentów, strona o autorze, własna 404, `robots.txt` z robotami AI
z nazwy, `llms.txt`, `schema.org`, karty `og:image`, kadry w WebP, poczta na własnej domenie.
**Bramki generatora: zielone, 94 pliki, 10 aplikacji + 6 zapowiedzianych** (pomiar 15.09) —
bramek jest dziś **dwadzieścia**: trzy doszły przy podziale onomatopei, dwudziesta
przy zapowiedzianych.

**Od 15.09 witryna pokazuje też to, czego jeszcze nie ma.** Sekcja **„Co dojdzie do rodziny"**
pod dziesiątką: sześć kart z ikoną, nazwą i jednym zdaniem, plakietka **„W przygotowaniu"** —
świadomie inna niż „Wkrótce w App Store", bo tamta znaczy tu „czeka na recenzję Apple".
**Trzeci stan w manifeście (`zapowiedziane`), nie przeciążenie `wSklepie`:** tamta ścieżka
buduje pełną stronę produktową i wymaga kompletu metadanych oraz dokumentów prawnych.
Zapowiedziane **nie mają stron produktowych ani wpisów w mapie witryny** — pomiar po
przeliczeniu: 90 plików bez zmian, mapa dalej 84 adresy, ikon 16. Pilnuje **bramka 20**.
Rozstrzygnięcie i to, czego nie wybrano: poz. 112; tożsamość szóstki: poz. 62–67.

**Tor witrynowy jedzie równolegle do wydań** i nie zjada miejsc w turze apek (§12 planu SEO).
Wchodząc tu, bierzesz albo **pozycję z kolejki niżej**, albo **obowiązkowy powrót po wydaniu
apki**: `marketingUrl` (§21.AB) · `wSklepie` przy premierze · przeliczenie stron po zmianie
metadanych · import kadrów po zmianie zrzutów · **porównanie `<title>` na żywym adresie
z repo**. Od 14.09 dochodzi szósty: **przeliczenie eksportu po zmianie katalogu** w Joshi,
Katsuyokei, Kazoekacie, Kuzushim, Keigo albo Kaname.

**Nawigacja ma trzy poziomy** od 14.09: `/nauka/` → temat → sekcja. Powrót w pasku
prowadzi do **rodzica**, nie do mapy aplikacji; strony sekcji mają przejście do
poprzedniej i następnej, bo kolejność sekcji bywa kolejnością nauki.

**Od 15.09 dochodzi czwarte wyjście: „Zobacz też" — most na inny temat.** Deklarowany
w `TEMATY` polem `powiazane`, wypisany z ręki tak jak adresy, ze zdaniem mówiącym, czym
jest strona po drugiej stronie linku. Powód jest zmierzony: **wszystkie 40 stron sekcji
miało zero linków do innego tematu**, a `szkielet-zdania` i `partykuly-japonskie` to dwie
strony pełne は・が・を bez powiedzianej hierarchii. Dziś mostów jest pięć (po dziesięć
stron w dwóch językach); **dokładanie kolejnych to decyzja redakcyjna, nie robota
mechaniczna** — most bez zdania „po co" jest linkiem do niczego.

Kolejka toru, w kolejności taniości: (1) domknięcie poz. 84 — 16 plików prozy i stare adresy
w dwóch martwych drzewach, część to historia i **ma zostać**; (2) Search Console (Jakub);
(3) ~~sekcje bez własnego opisu~~ — **zrobione 15.09, 22 z 22, bramka 19 milczy**;
(4) **przemianowanie 38 zakupów w ASC** — nie 42 i nie „wpisanie brakujących": wszystkie
mają komplet nazw i opisów, a wzorzec z planu mieści się w 30 znakach w 6 nazwach z 38
(propozycja i dziewięć spornych: przekazane Jakubowi 15.09);
(5) **nic z sióstr — wszystko, co się dało, jest wzięte.**
Bunmyaku odpada decyzją Jakuba (318 z 351 haseł to samo znaczenie), Shindan i Kifuku są
zablokowane, Keigo i Kaname mają już swoje — szczegóły w poz. 189.

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

## Search Console — co jeszcze zostało

**Zrobione 14.09.2026 przez Jakuba:** mapa witryny zgłoszona od nowa **oraz** wszystkie
dziesięć adresów z dnia 1 plus ponowne zaindeksowanie `apps/shindan`.

**Tego stanu nie zmierzy żaden skrypt** — klucz ASC oddaje `403` na
`analyticsReportRequests`, a Search Console nie ma tu API w naszym zasięgu. **Ta sekcja jest
jedynym źródłem prawdy o tym, co poszło**, więc odhacza się ją w chwili kliku, nie po tygodniu.

**Uwaga przy najbliższym zgłoszeniu mapy:** jeśli doszły nowe strony po 14.09, mapa wymaga
powtórnego zgłoszenia — sama się nie odświeży w indeksie.

**Zostają trzy strony produktowe do powtórki** (pierwsze prośby mogły pójść, gdy strony
mówiły jeszcze „wkrótce"):
```
https://jd-japanese.pl/apps/keigo/
https://jd-japanese.pl/apps/kifuku/
https://jd-japanese.pl/apps/onomatope/
```

**Dzień 2 — reszta polskich (12)**
```
https://jd-japanese.pl/nauka/gramatyka-n5/checi-i-zaproszenia/
https://jd-japanese.pl/nauka/gramatyka-n5/czas-i-miejsce/
https://jd-japanese.pl/nauka/gramatyka-n5/formy-czasownika/
https://jd-japanese.pl/nauka/gramatyka-n5/powod-i-ton/
https://jd-japanese.pl/nauka/gramatyka-n5/prosby-i-zakazy/
https://jd-japanese.pl/nauka/gramatyka-n5/przymiotniki/
https://jd-japanese.pl/nauka/keigo/sytuacje/
https://jd-japanese.pl/nauka/mowa-potoczna/opuszczenia/
https://jd-japanese.pl/nauka/mowa-potoczna/sciagniecia/
https://jd-japanese.pl/nauka/mowa-potoczna/udzwiecznienia/
https://jd-japanese.pl/nauka/mowa-potoczna/zlania/
https://jd-japanese.pl/nauka/mowa-potoczna/zlozone/
```

**Dzień 3 — angielskie rozdroża i najmocniejsze frazy**
```
https://jd-japanese.pl/en/learn/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/
https://jd-japanese.pl/en/learn/japanese-particles/
https://jd-japanese.pl/en/learn/confusing-pairs/
https://jd-japanese.pl/en/learn/japanese-counters/
https://jd-japanese.pl/en/learn/keigo/
https://jd-japanese.pl/en/learn/casual-japanese/
https://jd-japanese.pl/en/learn/verb-forms/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/sentence-skeleton/
https://jd-japanese.pl/en/learn/keigo/words/
```

**Dzień 4 i 5 — reszta angielskich (12)**
```
https://jd-japanese.pl/en/learn/casual-japanese/contractions/
https://jd-japanese.pl/en/learn/casual-japanese/fusions/
https://jd-japanese.pl/en/learn/casual-japanese/layered/
https://jd-japanese.pl/en/learn/casual-japanese/omissions/
https://jd-japanese.pl/en/learn/casual-japanese/voicing/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/adjectives/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/reason-and-tone/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/requests-and-prohibitions/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/time-and-place/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/verb-forms/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/wishes-and-invitations/
https://jd-japanese.pl/en/learn/keigo/situations/
```

**Dzień 7 — druga tura 15.09: połówki par (4 adresy)**
```
https://jd-japanese.pl/nauka/onomatopeje/pary-dzwieczne-ta-ho/
https://jd-japanese.pl/nauka/onomatopeje/pary-dzwiekowe-ko-to/
https://jd-japanese.pl/en/learn/japanese-mimetics/voicing-pairs-ta-ho/
https://jd-japanese.pl/en/learn/japanese-mimetics/sound-pairs-ko-to/
```

**Dzień 6 — podział onomatopei, 15.09 (8 nowych adresów)**
```
https://jd-japanese.pl/nauka/onomatopeje/bol/
https://jd-japanese.pl/nauka/onomatopeje/drzenie/
https://jd-japanese.pl/nauka/onomatopeje/zmeczenie/
https://jd-japanese.pl/nauka/onomatopeje/pary-dzwiekowe/
https://jd-japanese.pl/en/learn/japanese-mimetics/pain/
https://jd-japanese.pl/en/learn/japanese-mimetics/shivering/
https://jd-japanese.pl/en/learn/japanese-mimetics/tiredness/
https://jd-japanese.pl/en/learn/japanese-mimetics/sound-pairs/
```
**Mapa wymaga ponownego zgłoszenia** — urosła z 76 na **88** adresów. Cztery stare adresy
onomatopei (`cialo-i-samopoczucie`, `pary-dzwieczne` i ich angielskie odpowiedniki)
**żyją dalej i niosą treść** — zgłoszone 14.09 kliki nie poszły na marne.

**Dzień 5 — ósmy temat, dołożony 14.09 po południu**
```
https://jd-japanese.pl/en/learn/japanese-mimetics/
https://jd-japanese.pl/en/learn/japanese-mimetics/body-and-feeling/
https://jd-japanese.pl/en/learn/japanese-mimetics/voicing-pairs/
https://jd-japanese.pl/nauka/onomatopeje/
https://jd-japanese.pl/nauka/onomatopeje/cialo-i-samopoczucie/
https://jd-japanese.pl/nauka/onomatopeje/pary-dzwieczne/
```

## Czeka na decyzję Jakuba

1. **Czy umorzone zastrzeżenie wpuszcza hasło na stronę** (poz. 189). Dziś **nie** — eksport
   wymaga `ok` wprost. Kosztowało to dwie pozycje Keigo, przy których `--stats` pokazuje zero
   zastrzeżeń. Reguła z poz. 82 brzmi dosłownie „wszystkie soczewki mają `ok`".
2. **~~Bunmyaku i Onomatope~~ — Onomatope rozstrzygnięte 15.09**: sześć sekcji, oś wybrana
   pomiarem i opisana w poz. 189. Zostaje Bunmyaku (351 haseł), odłożone decyzją Jakuba.
   Otwarte przy onomatopejach zostaje jedno: **dwie strony par mają 44,6 i 52,6 KB i są
   dwiema najcięższymi stronami witryny** (następna ma 33,9 KB). Trójpodziału katalog nie
   unosi — żadna trzecia oś nie jest stała w parze — więc gdyby miał powstać, **musi go
   nazwać autor treści**, nie wyliczyć narzędzie.
3. **Search Console — jedyna pętla zwrotna, jaką mamy.** Klucz ASC oddaje `403` na
   `analyticsReportRequests`. Do wyklikania: **mapa ma teraz 88 adresów**, GSC znał 24 —
   zgłosić od nowa; powtórka prośby o zaindeksowanie dla **shindan, keigo, kifuku, onomatope**
   (pierwsze prośby mogły pójść **przed** przestawieniem `wSklepie`); ewentualna druga
   własność „Prefiks URL", bo własność „Domena" obejmuje też `api.` i `admin.`.
4. **~~Poz. 112~~ — rozstrzygnięte 15.09:** zapowiadamy, osobnym blokiem „Co dojdzie do
   rodziny" pod dziesiątką, bez dat i bez stron produktowych. Szóstka stoi na witrynie.
5. **Poz. 113 — wizytówka poza witryną.** Zobowiązanie **cykliczne**: koszt leży w rytmie
   publikowania, nie w treści. **Strony tematyczne zmieniły tu rachunek** — jest teraz
   189 haseł w gotowym kształcie do wystawiania pojedynczo.
6. **Bunmyaku ma pauzę w nazwie** jako jedyna z dziesięciu — decyzja redakcyjna (§21.X).
7. **Przegląd okiem stron tematycznych.** Rozszerzenie Chrome było w nocy odłączone, więc
   układ sprawdzony w znaczniku, nie na ekranie: jasny i ciemny motyw, szerokość telefonu.

## Świeże miny

- **Oś podziału mierzona na złym zbiorze wygląda jak oś zła.** Poz. 189 nosiła zapis
  „oś `script` nie pomaga (47/19)" — liczba prawdziwa, tylko z całego eksportu (66 haseł),
  a dzieli się **jedną stronę naraz**. Na samej sekcji par ta sama oś daje 9/9 rodzin.
  Przy następnym podziale: **policz na tym zbiorze, który idzie na stronę.**
- **Oś, na której zbudowana jest strona, jest ostatnią, po której wolno ją dzielić.**
  Dźwięczność w sekcji par dzieli 38 haseł równiutko na 19/19 i jest stała tylko
  w 2 rodzinach na 20 — bo każda para stoi właśnie na tym kontraście.
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
- **Tekst własny witryny urósł z 42 do 92 kluczy `NAPISY`** — tytuł i jedno zdanie na temat,
  plus **nazwy sekcji, których katalog nie nazywa** (rodzaje skrótu, rodzaje pozycji
  Keigo, klasy odmiany). To najgrubszy skok od początku i ma być zauważony. Ta liczba jest miarą: jeśli rośnie dalej, strona zaczęła mówić od siebie.
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
python3 Tools/generuj-strony.py --sprawdz        # dwadzieścia bramek, bez zapisu
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
