# Search Console — 90 adresów, w kolejności, w jakiej mają iść

## Stan indeksu — odczyt 16.09.2026

**Pierwszy odczyt pokrycia w papierach rodziny.** Wcześniej mierzono wyłącznie, ile adresów
Search Console zna z mapy witryny — nigdy, ile z nich siedzi w indeksie. Właściwość jest typu
**Domena**, więc obejmuje też `http://` i `www`; dane GSC z 14.09.

| | strony |
|---|---|
| **zaindeksowane** | **74** |
| niezaindeksowane | **56**, w czterech powodach |

| powód | `Source` | ile | co to jest |
|---|---|---|---|
| Alternate page with proper canonical tag | Website | 11 | **same warianty `…/index.html`** (`/index.html`, `/en/index.html`, `/en/apps/<slug>/index.html`). Pierwsze wykrycie 15.09 |
| Page with redirect | Website | 1 | **jeden adres: `http://jd-japanese.pl/`** — przekierowanie na `https://` |
| Discovered – currently not indexed | Google systems | 25 | strony tematyczne **2. piętra**, wykryte, `Last crawled: N/A` |
| Crawled – currently not indexed | Google systems | 19 | strony tematyczne **2. piętra**, pobrane 15.09, odłożone bez indeksu |

### Dwa powody z kolumny „Website" są ZAMIERZONE — nie klikamy „Zweryfikuj poprawkę"

Kolumna `Source` mówi, **czyja jest przyczyna**, a nie **jak bardzo boli**. Walidacja poprawki,
której nie ma, kończy się porażką i kosztuje tydzień.

Jedenaście adresów `index.html` to echo [poz. 326] — 1013 odsyłaczy wewnętrznych celowało
w postać plikową do 16.09.2026. Adresy dalej oddają 200, bo **GitHub Pages nie umie przekierowań**,
i poprawnie wskazują kanonikal na postać katalogową, która **jest w indeksie**. Zdjąć się ich
nie da: `noindex` siedziałby w **tym samym pliku** co postać katalogowa i zabrałby z indeksu
także ją. Zmierzone 16.09: w całym `~/aseity` **zero** miejsc budujących adres z `index.html`,
a `Tools/asc-marketing-url.py` celuje w postać katalogową z ukośnikiem — czyli **nic ich już
nie karmi** i licznik osunie się sam, powoli.

`http://jd-japanese.pl/` to „Enforce HTTPS" robiące swoje. Widać go wyłącznie dlatego, że
właściwość jest typu Domena.

**Trzeci adres dołączy do „Alternate page" i to też jest w porządku:** `/kuzushi/` kanonizuje się
na `/en/apps/kuzushi/` świadomie ([poz. 325]) — to adres historyczny pod Marketing URL Kuzushi.
Zniknie dopiero, gdy `Tools/asc-marketing-url.py --zapisz` przestawi pole w ASC.

### Groźne jest to, czego w mejlu Google nie ma

**44 strony tematyczne stoją poza indeksem.** Ze **62 stron 2. piętra**
(`/nauka/<temat>/<grupa>/`, `/en/learn/<topic>/<group>/`) w zgłoszeniu jest 44,
a ze stron 1. piętra i wyżej — **zero**.

Dwie hipotezy obalone pomiarem 16.09, obie w minutę:

```
„są chude"      mediana znaków:  niezaindeksowane 5988  ·  reszta 5849
„to szablon"    nakładanie treści między siostrami: 3,0–7,9%   (tło: 1,4%)
                a najwyższe mają strony ZAINDEKSOWANE: produktowe 11,6%, rozdroża 18,6%
```

Treść jest osobna i zdrowa. Zostaje wiek domeny (treść stoi od 09.09) i priorytet pobierania —
a jedyną dźwignią w GitHub Pages jest **linkowanie wewnętrzne**: dziś każda strona grupy wisi
na **jednym** odsyłaczu ze swojego tematu.

**Czego to nie obiecuje:** „Discovered/Crawled – currently not indexed" nie ma przycisku „napraw".
Linkowanie podnosi priorytet częściowo i przez tygodnie. Gwarancji zaindeksowania nie daje nic.

---

**Sprawdzone przed wypisaniem:** każdy z 88 adresów oddaje **200**, **nie przekierowuje**
i ma **własny `canonical`**. Zgłoszenie adresu, który przekierowuje, marnuje dzienny
limit, więc ta kontrola idzie przed listą, a nie po niej.

## Czego ta lista o sobie nie wie

`docs/TERAZ.md` notuje, że poszła już mapa witryny, **dziesięć adresów „dnia 1"**
i powtórka dla `apps/shindan`. **Które dokładnie dziesięć — nie wiadomo**: tamten
dzień nie został wypisany, a dni 2–5 owszem. Dlatego ta lista niesie **komplet 88**,
a nie różnicę.

Rachunek jest niesymetryczny i dlatego tak, a nie inaczej: **powtórzone zgłoszenie
kosztuje jedno miejsce w dziennym limicie, a pominięte — tygodnie niewidoczności.**

**Trzydzieści trzy adresy nie były wymienione nigdzie**, w żadnym dniu — to strony,
które doszły po tamtym rozpisaniu. Stoją w tej liście pierwsze i są jedynymi, co do
których mamy pewność, że nikt ich nie zgłaszał.

Wklejaj po **dziesięć dziennie**: Sprawdzenie URL → Poproś o zindeksowanie.

---

## Dzień 0  ·  2 z 2 na pewno niezgłoszonych — doszły 16.09.2026

Strona „Co dalej" i jej angielska bliźniaczka. Powstały **po** wypisaniu tej listy, więc
nie ma ich w żadnym z dni niżej. Idą pierwsze, bo są jedynymi adresami, o których wiadomo
na pewno, że nigdy nie poszły — i bo są kanałem zwrotnym z [poz. 295], czyli im szybciej
w indeksie, tym wcześniej zaczną zbierać odpowiedzi.

```
https://jd-japanese.pl/co-dalej/
https://jd-japanese.pl/en/whats-next/
```

**Mapa witryny jest już zgłoszona i odczytana** — 16.09.2026, `Success`, **90 adresów**
(odczytane w GSC → Mapy witryny, nie z prozy). Sprawdzone przed wypisaniem, tą samą miarą
co reszta listy: oba adresy oddają **200**, **nie przekierowują**, mają **własny `canonical`**
i **wzajemne `hreflang`**. Sprawdzone też, że **wszystkie 90 adresów mapy oddaje dziś 200**,
**żaden nie przekierowuje** i **każdy ma kanonikal na siebie co do znaku** — zero wyjątków.

## Dzień 1  ·  7 z 10 na pewno niezgłoszonych

```
https://jd-japanese.pl/apps/keigo/
https://jd-japanese.pl/apps/kifuku/
https://jd-japanese.pl/apps/onomatope/
https://jd-japanese.pl/
https://jd-japanese.pl/en/
https://jd-japanese.pl/apps/bunmyaku/
https://jd-japanese.pl/apps/joshi/
https://jd-japanese.pl/apps/kaname/
https://jd-japanese.pl/apps/katsuyokei/
https://jd-japanese.pl/apps/kazoekata/
```

## Dzień 2  ·  10 z 10 na pewno niezgłoszonych

```
https://jd-japanese.pl/apps/kuzushi/
https://jd-japanese.pl/apps/shindan/
https://jd-japanese.pl/en/apps/bunmyaku/
https://jd-japanese.pl/en/apps/joshi/
https://jd-japanese.pl/en/apps/kaname/
https://jd-japanese.pl/en/apps/katsuyokei/
https://jd-japanese.pl/en/apps/kazoekata/
https://jd-japanese.pl/en/apps/keigo/
https://jd-japanese.pl/en/apps/kifuku/
https://jd-japanese.pl/en/apps/kuzushi/
```

## Dzień 3  ·  10 z 10 na pewno niezgłoszonych

```
https://jd-japanese.pl/en/apps/onomatope/
https://jd-japanese.pl/en/apps/shindan/
https://jd-japanese.pl/nauka/
https://jd-japanese.pl/nauka/formy-czasownika/
https://jd-japanese.pl/nauka/gramatyka-n5/
https://jd-japanese.pl/nauka/keigo/
https://jd-japanese.pl/nauka/liczniki-japonskie/
https://jd-japanese.pl/nauka/mowa-potoczna/
https://jd-japanese.pl/nauka/mylace-pary/
https://jd-japanese.pl/nauka/partykuly-japonskie/
```

## Dzień 4  ·  6 z 10 na pewno niezgłoszonych

```
https://jd-japanese.pl/nauka/gramatyka-n5/szkielet-zdania/
https://jd-japanese.pl/nauka/keigo/slowa/
https://jd-japanese.pl/dokumenty.html
https://jd-japanese.pl/en/about/
https://jd-japanese.pl/en/documents.html
https://jd-japanese.pl/o-autorze/
https://jd-japanese.pl/en/learn/
https://jd-japanese.pl/nauka/onomatopeje/
https://jd-japanese.pl/en/learn/casual-japanese/
https://jd-japanese.pl/en/learn/confusing-pairs/
```

## Dzień 5  ·  0 z 10 na pewno niezgłoszonych

```
https://jd-japanese.pl/en/learn/japanese-counters/
https://jd-japanese.pl/en/learn/japanese-mimetics/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/
https://jd-japanese.pl/en/learn/japanese-particles/
https://jd-japanese.pl/en/learn/keigo/
https://jd-japanese.pl/en/learn/verb-forms/
https://jd-japanese.pl/nauka/gramatyka-n5/checi-i-zaproszenia/
https://jd-japanese.pl/nauka/gramatyka-n5/czas-i-miejsce/
https://jd-japanese.pl/nauka/gramatyka-n5/formy-czasownika/
https://jd-japanese.pl/nauka/gramatyka-n5/powod-i-ton/
```

## Dzień 6  ·  0 z 10 na pewno niezgłoszonych

```
https://jd-japanese.pl/nauka/gramatyka-n5/prosby-i-zakazy/
https://jd-japanese.pl/nauka/gramatyka-n5/przymiotniki/
https://jd-japanese.pl/nauka/keigo/sytuacje/
https://jd-japanese.pl/nauka/mowa-potoczna/opuszczenia/
https://jd-japanese.pl/nauka/mowa-potoczna/sciagniecia/
https://jd-japanese.pl/nauka/mowa-potoczna/udzwiecznienia/
https://jd-japanese.pl/nauka/mowa-potoczna/zlania/
https://jd-japanese.pl/nauka/mowa-potoczna/zlozone/
https://jd-japanese.pl/nauka/onomatopeje/bol/
https://jd-japanese.pl/nauka/onomatopeje/cialo-i-samopoczucie/
```

## Dzień 7  ·  0 z 10 na pewno niezgłoszonych

```
https://jd-japanese.pl/nauka/onomatopeje/drzenie/
https://jd-japanese.pl/nauka/onomatopeje/pary-dzwieczne-ta-ho/
https://jd-japanese.pl/nauka/onomatopeje/pary-dzwieczne/
https://jd-japanese.pl/nauka/onomatopeje/pary-dzwiekowe-ko-to/
https://jd-japanese.pl/nauka/onomatopeje/pary-dzwiekowe/
https://jd-japanese.pl/nauka/onomatopeje/zmeczenie/
https://jd-japanese.pl/en/learn/casual-japanese/contractions/
https://jd-japanese.pl/en/learn/casual-japanese/fusions/
https://jd-japanese.pl/en/learn/casual-japanese/layered/
https://jd-japanese.pl/en/learn/casual-japanese/omissions/
```

## Dzień 8  ·  0 z 10 na pewno niezgłoszonych

```
https://jd-japanese.pl/en/learn/casual-japanese/voicing/
https://jd-japanese.pl/en/learn/japanese-mimetics/body-and-feeling/
https://jd-japanese.pl/en/learn/japanese-mimetics/pain/
https://jd-japanese.pl/en/learn/japanese-mimetics/shivering/
https://jd-japanese.pl/en/learn/japanese-mimetics/sound-pairs-ko-to/
https://jd-japanese.pl/en/learn/japanese-mimetics/sound-pairs/
https://jd-japanese.pl/en/learn/japanese-mimetics/tiredness/
https://jd-japanese.pl/en/learn/japanese-mimetics/voicing-pairs-ta-ho/
https://jd-japanese.pl/en/learn/japanese-mimetics/voicing-pairs/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/adjectives/
```

## Dzień 9  ·  0 z 10 na pewno niezgłoszonych

```
https://jd-japanese.pl/en/learn/japanese-n5-grammar/reason-and-tone/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/requests-and-prohibitions/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/sentence-skeleton/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/time-and-place/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/verb-forms/
https://jd-japanese.pl/en/learn/japanese-n5-grammar/wishes-and-invitations/
https://jd-japanese.pl/en/learn/keigo/situations/
https://jd-japanese.pl/en/learn/keigo/words/
```

---

Po ostatnim dniu **zgłoś mapę witryny jeszcze raz** — sama się nie odświeży,
a licznik adresów w Search Console to stan z chwili jej pobrania, nie z teraz.
