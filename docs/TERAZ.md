# TERAZ — witryna `jd-japanese.pl`, SEO i dokumenty prawne

**Ten plik jest NADPISYWANY.** Jedno wejście do toru witrynowego, bez datowanych następców:
nie zakładaj `PRZEKAZANIE_<data>.md` ani „TERAZ_2" — osusz ten plik, historia zostaje w `git log`.
Pomiary i uzasadnienia: `jp-grammar/docs/PLAN_SEO_AEO.md` §11–§12. Otwarte pozycje backlogu
rodziny dla tego toru: **82** (SEO/AEO jako robota stała), **84** (adres kontaktowy),
**112** (zapowiadanie apek), **113** (wizytówka poza witryną), **189** (strony tematyczne).

## Od czego zacząć

**Witryna mówi już o japońskim, a nie tylko o aplikacjach.** 13.09.2026 doszło
**osiem tematów, z czego cztery rozpisane na sekcje**; 13.09 doszedł podział onomatopei
i mosty między tematami — mapa witryny **26 → 88 adresów**, dwadzieścia sekcji. Wcześniej wszystko, co tu stało, mówiło wyłącznie o dziesiątce apek,
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
**Bramki generatora: zielone, 94 pliki, 10 aplikacji + 6 zapowiedzianych** (pomiar 13.09) —
bramek jest dziś **dwadzieścia**: trzy doszły przy podziale onomatopei, dwudziesta
przy zapowiedzianych.

**Od 13.09 witryna pokazuje też to, czego jeszcze nie ma.** Sekcja **„Co dojdzie do rodziny"**
pod dziesiątką: sześć kart z ikoną, nazwą i jednym zdaniem, plakietka **„W przygotowaniu"** —
świadomie inna niż „Wkrótce w App Store", bo tamta znaczy tu „czeka na recenzję Apple".
**Trzeci stan w manifeście (`zapowiedziane`), nie przeciążenie `wSklepie`:** tamta ścieżka
buduje pełną stronę produktową i wymaga kompletu metadanych oraz dokumentów prawnych.
Zapowiedziane **nie mają stron produktowych ani wpisów w mapie witryny** — pomiar po
przeliczeniu: 90 plików bez zmian, mapa dalej bez nich, ikon 16. Pilnuje **bramka 20**.
Rozstrzygnięcie i to, czego nie wybrano: poz. 112; tożsamość szóstki: poz. 62–67.

**Tor witrynowy jedzie równolegle do wydań** i nie zjada miejsc w turze apek (§12 planu SEO).
Wchodząc tu, bierzesz albo **pozycję z kolejki niżej**, albo **obowiązkowy powrót po wydaniu
apki**: `marketingUrl` (§21.AB) · `wSklepie` przy premierze · przeliczenie stron po zmianie
metadanych · import kadrów po zmianie zrzutów · **porównanie `<title>` na żywym adresie
z repo**. Od 13.09 dochodzi szósty: **przeliczenie eksportu po zmianie katalogu** w Joshi,
Katsuyokei, Kazoekacie, Kuzushim, Keigo albo Kaname.

**Nawigacja ma trzy poziomy** od 13.09: `/nauka/` → temat → sekcja. Powrót w pasku
prowadzi do **rodzica**, nie do mapy aplikacji; strony sekcji mają przejście do
poprzedniej i następnej, bo kolejność sekcji bywa kolejnością nauki.

**Od 13.09 dochodzi czwarte wyjście: „Zobacz też" — most na inny temat.** Deklarowany
w `TEMATY` polem `powiazane`, wypisany z ręki tak jak adresy, ze zdaniem mówiącym, czym
jest strona po drugiej stronie linku. Powód jest zmierzony: **wszystkie 40 stron sekcji
miało zero linków do innego tematu**, a `szkielet-zdania` i `partykuly-japonskie` to dwie
strony pełne は・が・を bez powiedzianej hierarchii. Dziś mostów jest pięć (po dziesięć
stron w dwóch językach); **dokładanie kolejnych to decyzja redakcyjna, nie robota
mechaniczna** — most bez zdania „po co" jest linkiem do niczego.

Kolejka toru, w kolejności taniości: (1) domknięcie poz. 84 — 16 plików prozy i stare adresy
w dwóch martwych drzewach, część to historia i **ma zostać**; (2) **Search Console (Jakub)** — lista do wklejenia stoi w **`docs/SEARCH_CONSOLE.md`**,
komplet 88 adresów w kolejności priorytetu, po dziesięć dziennie;
(3) ~~sekcje bez własnego opisu~~ — **zrobione 13.09, 22 z 22, bramka 19 milczy**;
(4) **przemianowanie 38 zakupów w ASC** — nie 42 i nie „wpisanie brakujących": wszystkie
mają komplet nazw i opisów. **Dziewięć spornych nazw rozstrzygniętych 13.09 jedną regułą:
nazwa produktu nie powtarza słowa, które stoi już w nazwie aplikacji** — po zdjęciu go
38 z 38 mieści się w limicie. `docs/ZAKUPY_NAZWY.md` jest dziś **składem do wpisania**,
nie materiałem do dyskusji; samo wpisanie idzie per apka, do `Config/<App>.storekit`
**i** do ASC, przy jej wydaniu;
(5) **nic z sióstr — wszystko, co się dało, jest wzięte.**
Bunmyaku odpada decyzją Jakuba (318 z 351 haseł to samo znaczenie), Shindan i Kifuku są
zablokowane, Keigo i Kaname mają już swoje — szczegóły w poz. 189.

**`marketingUrl` zszedł z kolejki 13.09 — pomiarem, nie robotą.** `asc-marketing-url.py`
na sucho oddaje **0 pól do zmiany, 20 już zgodnych**: kolejka mówiła o dwunastu polach na
starym adresie albo pustych, a stan ASC temu przeczy. Zostaje **odruch, nie pozycja**:
przebieg na sucho przy każdym składaniu, bo okno zapisu to `WAITING_FOR_REVIEW` i zamyka
się samo (§21.AB).

## Zrobione 13.09 po południu — nie pytać drugi raz

Tura o szóstce zapowiedzianej i przeglądzie witryny. Skutki, nie przebieg:

| co | stan |
|---|---|
| **hreflang w dokumentach prawnych** | 60 par bieżących uzupełnionych, 6 przestarzałych świadomie bez (mają `noindex`), spoolcalc bez pary. Wstawia `glowy_dokumentow.py`, pilnuje **bramka 11** — mierzy **oba adresy osobno**, nie samą obecność słowa |
| **opis mapy rodziny** | przestał być wyliczanką z klamrą; wypadał z niego Shindan, a z nim fraza „test poziomu" |
| **§15 na kartach zapowiedzianych** | `.karta .nazwa::after` dawał niewidzialny cel dotknięcia **także kartom bez linku**. Zawężone do `a.nazwa::after`; kontrpróba na żywo: 10 żywych zachowało cel, 6 straciło |
| **nazwy zakupów** | dziewięć spornych rozstrzygniętych jedną regułą, 38 z 38 w limicie |
| **Search Console** | `docs/SEARCH_CONSOLE.md`, komplet 88 w priorytecie; stara lista rozpisywała 55 |
| **README i miara `NAPISY`** | README mówił o dziewięciu bramkach przy dwudziestu; miara `NAPISY` stała na 92 przy 129 |
| **daty z przyszłości** | 31 wystąpień poprawionych w tym repo — dwie różne daty o dwa i trzy dni w przód, 12 z rokiem i 19 bez. Liczb nie wypisuję tutaj wprost: bramka dat (poz. 210) czyta datę w prozie jako twierdzenie, więc materiał dowodowy trzyma się w `git log`, nie w wejściu roboczym |

**Opis Shindana zmieniony w trzech miejscach naraz** — repo, ASC (wersja w kolejce)
i witryna — bo zdanie „Powyższy opis jest tym samym tekstem, który stoi na karcie
aplikacji w App Store" musi zostać prawdziwe. Przy okazji wyszło, że **„z katalogów
dziewięciu aplikacji" było fałszem już dziś**: arkusz zasila osiem repozytoriów,
Kifuku nie zasila go wcale.

## Miny z tej tury — wszystkie zmierzone, nie przewidziane

1. **PRZEGLĄDARKA POKAZUJE STARY ARKUSZ, GDY `curl` WIDZI JUŻ NOWY.** GitHub Pages oddaje
   `Cache-Control: max-age=600` i nie da się tego zmienić. Kontrpróba zachowania dała
   wynik **odwrotny do prawdziwego** i wyglądała jak regresja, którą sam wprowadziłem.
   Przy pomiarze okiem dokładaj parametr do adresu (`?v=cokolwiek`) — to nowy zasób,
   więc cache nie ma czego podać. Sam `curl` nie jest dowodem: mierzy co innego niż oko.
2. **BRAMKA 10 UTOPIŁA WŁASNY SYGNAŁ DRUGI RAZ W TYM SAMYM MIEJSCU.** Po wstawieniu
   `hreflang` skoczyła z 5 rozjazdów na 60 — dokładnie jak 09.09 po wstawieniu głów.
   `bez_glowy_witryny()` jest **rejestrem, nie jednorazową łatką**: każdy nowy znacznik,
   który witryna dokłada do cudzego pliku, trzeba tam dopisać, inaczej bramka przestaje
   mierzyć treść.
3. **MUTACJA NA NIESCOMMITOWANEJ ZMIANIE + `git checkout` = UTRATA ZMIANY.** Kontrpróba
   bramki polegała na zepsuciu pliku i przywróceniu go z gita — a przywróciła wersję
   **sprzed mojej niescommitowanej poprawki**, więc skasowała ją w dwóch plikach.
   Commituj przed mutacją albo mutuj kopię.
4. **AUTOMAT POPRAWIAJĄCY DATY PODMIENIŁ CYTAT STAREJ WARTOŚCI.** W `apps.json` stoi
   zdanie „stało tu `2026-09-15`" — przebieg zamienił je na `2026-09-13` i zdanie zaczęło
   zaprzeczać samo sobie. Ta sama klasa zjadła zdanie „w nocy z 13 na 14.09", robiąc
   z niego „z 13 na 13". **Podmiana hurtem czyta cytat jako twierdzenie.**
5. **ZGŁOSZENIE O BRAKU, KTÓRY ISTNIEJE — DRUGI RAZ.** Na zrzucie telefonu ikony kart
   wyglądały na niezaładowane; pliki odpowiadały 200, a po przybliżeniu ikona była na
   miejscu, tylko ciemna w miniaturze. Przybliż, zanim zgłosisz.

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

**Zrobione 13.09.2026 przez Jakuba:** mapa witryny zgłoszona od nowa **oraz** wszystkie
dziesięć adresów z dnia 1 plus ponowne zaindeksowanie `apps/shindan`.

**Tego stanu nie zmierzy żaden skrypt** — klucz ASC oddaje `403` na
`analyticsReportRequests`, a Search Console nie ma tu API w naszym zasięgu. **Ta sekcja jest
jedynym źródłem prawdy o tym, co poszło**, więc odhacza się ją w chwili kliku, nie po tygodniu.

**Uwaga przy najbliższym zgłoszeniu mapy:** jeśli doszły nowe strony, mapa wymaga
powtórnego zgłoszenia — sama się nie odświeży w indeksie.

**Liczba adresów w Search Console to stan z chwili POBRANIA mapy, nie z teraz.** Zmierzone
13.09: Jakub zgłosił mapę między dwoma wdrożeniami tego samego dnia i GSC pokazał 84, choć
plik na żywo miał już 88. Sprawdzać zawsze u źródła —
`curl -sS https://jd-japanese.pl/sitemap.xml | grep -c '<loc>'` — zanim uzna się rozjazd
za wadę generatora. Ponowne zgłoszenie wymusza pobranie; sam licznik się nie odświeży.

**Rozpisanie adresów przeniesione do `docs/SEARCH_CONSOLE.md`** (13.09.2026) — tu stała
lista pięciu dni, czyli **55 adresów, przy mapie liczącej 88**. Trzydzieści trzy strony,
które doszły po tamtym rozpisaniu, nie były wymienione nigdzie i nikt by ich nie zgłosił.

Nowa lista niesie komplet 88, w kolejności, w jakiej mają iść, i jest sprawdzona przed
wypisaniem: każdy adres oddaje 200, nie przekierowuje i ma własny `canonical`. **Dwóch list
tego samego nie utrzymujemy** — ta sekcja mówi już tylko, co poszło, nie co wkleić.


## Czeka na decyzję Jakuba

1. **Czy umorzone zastrzeżenie wpuszcza hasło na stronę** (poz. 189). Dziś **nie** — eksport
   wymaga `ok` wprost. Kosztowało to dwie pozycje Keigo, przy których `--stats` pokazuje zero
   zastrzeżeń. Reguła z poz. 82 brzmi dosłownie „wszystkie soczewki mają `ok`".
2. **~~Bunmyaku i Onomatope~~ — Onomatope rozstrzygnięte 13.09**: sześć sekcji, oś wybrana
   pomiarem i opisana w poz. 189. Zostaje Bunmyaku (351 haseł), odłożone decyzją Jakuba.
   Otwarte przy onomatopejach zostaje jedno: **dwie strony par mają 44,6 i 52,6 KB i są
   dwiema najcięższymi stronami witryny** (następna ma 33,9 KB). Trójpodziału katalog nie
   unosi — żadna trzecia oś nie jest stała w parze — więc gdyby miał powstać, **musi go
   nazwać autor treści**, nie wyliczyć narzędzie.
3. **Search Console — jedyna pętla zwrotna, jaką mamy.** Klucz ASC oddaje `403` na
   `analyticsReportRequests`. **Lista do wklejenia jest gotowa: `docs/SEARCH_CONSOLE.md`** —
   komplet 88 adresów w kolejności priorytetu, po dziesięć dziennie, sprawdzone przed
   wypisaniem (88 × 200, zero przekierowań, każdy z własnym `canonical`). Zostaje ewentualna
   druga własność „Prefiks URL", bo własność „Domena" obejmuje też `api.` i `admin.`.
4. **~~Poz. 112~~ — rozstrzygnięte 13.09:** zapowiadamy, osobnym blokiem „Co dojdzie do
   rodziny" pod dziesiątką, bez dat i bez stron produktowych. Szóstka stoi na witrynie.
5. **Poz. 113 — wizytówka poza witryną.** Zobowiązanie **cykliczne**: koszt leży w rytmie
   publikowania, nie w treści. **Strony tematyczne zmieniły tu rachunek** — jest teraz
   189 haseł w gotowym kształcie do wystawiania pojedynczo.
6. **~~Bunmyaku ma pauzę w nazwie~~ — zamknięte pomiarem 13.09 (poz. 75).** Odczyt nazw
   z ASC: **dziesięć z dziesięciu ma dwukropek**, Bunmyaku też (`Bunmyaku: Japoński
   w zdaniu`). Pozycja opisywała stan, którego już nie ma.
7. **Przegląd okiem — zrobiony częściowo 13.09.** Obejrzane na szerokości telefonu
   (430 px, motyw ciemny): mapa rodziny, strona produktowa, strona tematyczna z sekcjami.
   Wynik: jedna realna wada (§15 na kartach zapowiedzianych, naprawiona) i jeden fałszywy
   alarm. **Nieobejrzane zostają: motyw jasny, szerokość biurkowa i dwie najcięższe strony
   par.** Przy powrocie pamiętaj o `?v=` w adresie — bez tego mierzysz poprzednie wdrożenie.

   Jedna rzecz do rozstrzygnięcia z tego, co widziałem: **spis sekcji pod nagłówkiem
   „Opis ze sklepu" i pod opisem tematu nie ma własnej etykiety** — cztery podkreślone
   linie wielkimi literami lecą od razu po tekście i czytają się jak treść, nie jak spis.
   Czytnik ekranu wie (`aria-label`), oko nie.

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
  stare tytuły przez pół dnia**. Od 13.09 pilnuje tego przy eksportach **bramka 13**:
  porównuje commit katalogu zapisany w eksporcie z bieżącym stanem repo siostry. Uwaga
  nazwana, nieblokująca — katalog leży w cudzym drzewie.
- **Bramka 12 i 13 sprawdzone MUTACJĄ, nie zielenią.** Podstawiony zerowy commit, pusta nazwa
  angielska i hasło bez odcisku dały trzy komunikaty i kod 1. Zielony zestaw nic nie dowodzi,
  dopóki nie wiadomo, co go wywala.
- **Bramka 10 świeci dalej 5 rozjazdów** (Bunmyaku `terms.html` i `support.html` wobec
  `bunmyaku-n2/docs/app-store/`) — **nazwane, nieblokujące**, bo kopie leżą w cudzym repo.
  Dokumenty zmienia się **po obu stronach naraz**; podmiana po jednej topi prawdziwy sygnał.
- **Tekst własny witryny urósł z 42 przez 92 do 129 kluczy `NAPISY`** (pomiar 13.09.2026,
  tyle samo w obu językach) — tytuł i jedno zdanie na temat, plus **nazwy sekcji, których
  katalog nie nazywa** (rodzaje skrótu, rodzaje pozycji Keigo, klasy odmiany). Ta liczba
  jest miarą: jeśli rośnie dalej, strona zaczęła mówić od siebie. **Sama miara też się
  starzeje** — wpis stał na „92" jeszcze po trzydziestu siedmiu kolejnych kluczach, czyli
  dokładnie wtedy, gdy miał ostrzegać. Mierz poleceniem, nie tym zdaniem:
  `python3 -c "import sys; sys.path.insert(0,'Tools'); from napisy import NAPISY; print(len(NAPISY['pl']))"`
- **Generator nie dotyka dokumentów prawnych.** Piszą w nie tylko `Tools/landmark-main.py`
  i `Tools/glowy_dokumentow.py`. Przestarzałe wersje dostają `noindex, follow`, **nigdy
  `canonical` na nowszą** — to nie jest ta sama treść.
- **`docs/DOMENA.md` opisuje stan sprzed przełączenia.** Kroki 1–10 są zrobione; czytaj go
  jak historię, nie jak instrukcję.
- **Klienta ASC `asc.py` to repo pożycza z `../kifuku/Tools`** — publiczne repozytorium
  świadomie nie ma go u siebie, tak jak nie ma klucza ani `ASC_ISSUER_ID`.

## Kto tu był ostatnio

Sesja z 13.09.2026 po południu: szóstka zapowiedziana w narzędziach i papierach rodziny,
przegląd witryny, cztery rozstrzygnięcia Jakuba. **Papiery rodziny (`jp-grammar/docs/`,
`AGENTS.md`, konwencje) pisała wtedy druga sesja** — tu obowiązywał podział: tor witryny
i `app-policies` po tej stronie, hub po tamtej, `Tools/` w hubie punktowo i po zapowiedzi.
Jeśli wchodzisz tu równolegle z kimś, ustal to samo, zanim cokolwiek zapiszesz: jeden
`git commit -a` w cudzym drzewie roboczym zgarnia cudzą pracę w połowie testowania.

## Jak zmierzyć stan

```sh
cd ~/aseity/app-policies
python3 Tools/generuj-strony.py --sprawdz        # dwadzieścia bramek, bez zapisu
python3 Tools/generuj-strony.py                  # przelicz
python3 Tools/generuj-strony.py --powtarzalnie   # dwa przebiegi, bit w bit
python3 Tools/generuj-strony.py --sprawdz-sklep  # manifest kontra pięć witryn App Store (sieć)
python3 Tools/generuj-strony.py --zrzuty         # import kadrów z repo apek
python3 Tools/glowy_dokumentow.py --sprawdz      # canonical, hreflang i noindex w dokumentach
python3 Tools/asc-marketing-url.py --apka <slug> # bez --zapisz: przebieg na sucho

# eksport przejrzanej treści — w repozytorium siostry, nie tutaj:
cd ~/aseity/<joshi-ios|katsuyokei-ios|kazoekata-ios|kuzushi-ios|keigo-ios|jp-grammar-1.2.5>
python3 Tools/review-content.py --eksport-www

# ZAWSZE po przeliczeniu — pomiar na żywym adresie, nie na plikach.
# Do pomiaru OKIEM dokładaj `?v=cokolwiek`: GitHub Pages oddaje max-age=600
# i przeglądarka pokaże stary arkusz, choć curl widzi już nowy.
for u in kaname bunmyaku katsuyokei joshi kazoekata kuzushi shindan keigo kifuku onomatope; do
  curl -sS -L "https://jd-japanese.pl/apps/$u/" | grep -o '<title>[^<]*'
done
for t in partykuly-japonskie mylace-pary formy-czasownika liczniki-japonskie mowa-potoczna keigo; do
  curl -sS -L "https://jd-japanese.pl/nauka/$t/" | grep -o '<title>[^<]*'
done
```

**Zielony komunikat narzędzia nie jest dowodem, że czynność zaszła.** Publikacja idzie z `main`
przez GitHub Pages i zajmuje około minuty — dopóki nie odpowie żywy adres, nic nie jest wydane.
