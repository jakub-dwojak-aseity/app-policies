# app-policies

Strony rodziny aplikacji do nauki japońskiego: **strony produktowe** i **dokumenty
prawne**, hostowane na GitHub Pages.

Apple wymaga, żeby adres polityki prywatności i adres wsparcia **działały publicznie**
w momencie recenzji i **nie wymagały logowania** — dlatego to repozytorium jest publiczne
i odseparowane od prywatnych repozytoriów z kodem.

## Dwa rodzaje stron i dwa różne sposoby ich utrzymania

| | strony produktowe | dokumenty prawne |
|---|---|---|
| co to | mapa rodziny i podstrona każdej aplikacji | polityka, warunki, wsparcie |
| skąd treść | **generator**, z `docs/app-store/` w repo aplikacji | kopia pliku z repo aplikacji |
| jak zmienić | zmienić metadane w repo aplikacji, puścić generator | poprawić w obu kopiach ręcznie |
| adresy | `/`, `/apps/<slug>/`, `/en/`, `/en/apps/<slug>/` | `<slug>/[<wersja>/][en/]<plik>.html` |

**Dokumentów prawnych generator nie dotyka.** Tylko do nich linkuje — i sprawdza,
że plik istnieje oraz że ma landmark `<main>` (bramka 9).

Jedyne narzędzie, które w te pliki pisze, to `Tools/landmark-main.py`: wstawia sam
znacznik `<main>`, bez jednego renderowanego znaku zmiany, i **odmawia** pracy na
pliku o innym kształcie niż zakłada wstawka. Powstało, bo dokumentów prawnych nie da
się wciągnąć pod generator — to pliki, na które wskazuje `privacyPolicyUrl` w App
Store Connect i które widział App Review; ponowne wyrenderowanie zmieniłoby tekst,
którego nikt nie zamawiał.

```
python3 Tools/landmark-main.py            # wstawia i zapisuje
python3 Tools/landmark-main.py --sprawdz  # nic nie pisze, zgłasza braki, kod wyjścia 1
```

## Generator stron produktowych

```
python3 Tools/generuj-strony.py                  # zapisuje strony
python3 Tools/generuj-strony.py --sprawdz        # tylko bramki, bez zapisu
python3 Tools/generuj-strony.py --powtarzalnie   # dwa przebiegi, porównanie bit w bit
python3 Tools/generuj-strony.py --sprawdz-sklep  # porównuje manifest z App Store (sieć)
```

**Treść stron pochodzi wyłącznie z metadanych sklepowych** — `APP_STORE_METADATA_{PL,EN}.md`
dziewięciu aplikacji i `version-texts.json` Kaname. Opisy w App Store są przejrzane
i zatwierdzone; strona, która mówi coś innego, jest nową obietnicą, której nikt nie
sprawdził. Generator nie pisze zdań o aplikacjach, tylko je przepisuje: cały jego tekst
własny to nawigacja, zebrana w jednej tablicy `NAPISY` w `Tools/generuj-strony.py`.

Czego świadomie **nie** robi: nie pokazuje słów kluczowych (na stronie byłyby listą słów
bez zdania), nie podaje cen zakupów liczbą (cena zależy od sklepu krajowego, więc jedna
liczba jest fałszywa dla większości czytelników) i nie dotyka dokumentów prawnych.

`Tools/apps.json` trzyma **fakty** o aplikacjach — identyfikator w App Store, drzewo
robocze z najświeższymi metadanymi, katalog dokumentów, adres kontaktowy — i **nigdy
kopii tekstu**. Każde pole jest zmierzone, a źródło pomiaru stoi w komentarzu obok.

### Bramki

Generator nie zapisuje niczego, dopóki nie przejdzie wszystkich dziewięciu. Lista
poniżej **miała wcześniej sześć pozycji przy ośmiu bramkach w kodzie** — dwie
dopisane później nie trafiły do dokumentu; są tu jako 6 i 7.

1. każdy dokument prawny, do którego strona linkuje, **istnieje na dysku**;
2. każdy link wewnętrzny prowadzi do pliku, który istnieje albo powstanie;
3. każda strona ma tytuł, `<meta name="description">` do 160 znaków, `<html lang>`
   i adres kanoniczny;
4. tekst własny generatora nie zawiera pauzy `—` (§21.Z: półpauza);
5. nazwy aplikacji się nie dublują;
6. liczba pytań w sekcji „Częste pytania” zgadza się między `pl` a `en`;
7. każdy kadr na stronie ma podpis w obu językach (`screenshots.json`);
8. `sitemap.xml` wymienia dokładnie te strony, które generator zapisuje;
9. **każda strona ma dokładnie jeden landmark `<main>`** — za `<body>`, przed
   `<footer>`, z `<h1>` w środku. Liczone są oba znaczniki osobno, bo landmark
   niezamknięty jest gorszy niż żaden: obejmuje wtedy także stopkę. Bramka mierzy
   **i dokumenty prawne** (pisane ręcznie, więc bez szablonu, który by ich pilnował),
   **i strony generowane** — te ostatnie trzymały landmark na jednej linii szablonu
   i żadnym teście, więc nowy szablon bez `<main>` przeszedłby bez słowa.

Dziesiąta jest **nazwana, ale nie blokuje**: dokumenty prawne mają bliźniaki
w `<repo>/docs/app-store/**` i bramka mówi, które się rozjechały, parując je
**sumą kontrolną treści**, a nie mapą ścieżek — mapa rozjeżdża się przy pierwszej
przeprowadzce katalogu, a Kaname i Bunmyaku mają po dwa drzewa robocze. Nie blokuje,
bo kopie leżą w cudzych repozytoriach i naprawia je kto inny; bramka blokująca,
której nie da się zazielenić na miejscu, kończy tak, że ktoś ją wyłącza.

`--powtarzalnie` sprawdza dodatkowo, że dwa przebiegi dają ten sam wynik bit w bit.
Ikony są przeskalowane z zasobów aplikacji i powstają **tylko przy zmianie skrótu
źródła** (`assets/ikony/zrodla.json`), bo `sips` nie gwarantuje powtarzalnego bajtu.

### Dopisanie kolejnej aplikacji

Jeden wpis w `Tools/apps.json` i przebieg generatora. Katalog dokumentów wpisuje się
**odczytany z App Store Connect** (`privacyPolicyUrl` per lokalizacja), a nie wyliczony
z metadanych w repo: te dwa źródła potrafią się rozjechać i już się rozjechały.

<!-- ADRESY: sekcja poniżej jest generowana przez Tools/generuj-strony.py, nie edytować ręcznie -->
## Adresy

| Aplikacja | Strona produktowa | Dokumenty |
|---|---|---|
| Kaname: Gramatyka japońska 要 | [pl](https://jd-japanese.pl/apps/kaname/) · [en](https://jd-japanese.pl/en/apps/kaname/) | [pl](https://jd-japanese.pl/kaname/1.2/privacy.html) · [en](https://jd-japanese.pl/kaname/1.2/en/privacy.html) |
| Bunmyaku: Japoński w zdaniu 文脈 | [pl](https://jd-japanese.pl/apps/bunmyaku/) · [en](https://jd-japanese.pl/en/apps/bunmyaku/) | [pl](https://jd-japanese.pl/bunmyaku/1.2/privacy.html) · [en](https://jd-japanese.pl/bunmyaku/1.2/en/privacy.html) |
| Katsuyokei: Odmiana japońska 活用形 | [pl](https://jd-japanese.pl/apps/katsuyokei/) · [en](https://jd-japanese.pl/en/apps/katsuyokei/) | [pl](https://jd-japanese.pl/katsuyokei/privacy.html) · [en](https://jd-japanese.pl/katsuyokei/en/privacy.html) |
| Joshi: Partykuły japońskie 助詞 | [pl](https://jd-japanese.pl/apps/joshi/) · [en](https://jd-japanese.pl/en/apps/joshi/) | [pl](https://jd-japanese.pl/joshi/privacy.html) · [en](https://jd-japanese.pl/joshi/en/privacy.html) |
| Kazoekata: Liczniki japońskie 数え方 | [pl](https://jd-japanese.pl/apps/kazoekata/) · [en](https://jd-japanese.pl/en/apps/kazoekata/) | [pl](https://jd-japanese.pl/kazoekata/privacy.html) · [en](https://jd-japanese.pl/kazoekata/en/privacy.html) |
| Kuzushi: Mowa potoczna 崩し | [pl](https://jd-japanese.pl/apps/kuzushi/) · [en](https://jd-japanese.pl/en/apps/kuzushi/) | [pl](https://jd-japanese.pl/kuzushi/pl/privacy.html) · [en](https://jd-japanese.pl/kuzushi/privacy.html) |
| Shindan: Poziom japońskiego 診断 | [pl](https://jd-japanese.pl/apps/shindan/) · [en](https://jd-japanese.pl/en/apps/shindan/) | [pl](https://jd-japanese.pl/shindan/1.0/privacy.html) · [en](https://jd-japanese.pl/shindan/1.0/en/privacy.html) |
| Keigo: Grzeczność japońska 敬語 | [pl](https://jd-japanese.pl/apps/keigo/) · [en](https://jd-japanese.pl/en/apps/keigo/) | [pl](https://jd-japanese.pl/keigo/1.0/privacy.html) · [en](https://jd-japanese.pl/keigo/1.0/en/privacy.html) |
| Kifuku: Akcent japoński 起伏 | [pl](https://jd-japanese.pl/apps/kifuku/) · [en](https://jd-japanese.pl/en/apps/kifuku/) | [pl](https://jd-japanese.pl/kifuku/1.0/privacy.html) · [en](https://jd-japanese.pl/kifuku/1.0/en/privacy.html) |
| Onomatope: Dźwięki i wyrażenia オノマトペ | [pl](https://jd-japanese.pl/apps/onomatope/) · [en](https://jd-japanese.pl/en/apps/onomatope/) | [pl](https://jd-japanese.pl/onomatope/1.0/privacy.html) · [en](https://jd-japanese.pl/onomatope/1.0/en/privacy.html) |
| SpoolCalc – kalkulator pojemności szpuli | – | [en](https://jd-japanese.pl/spoolcalc/privacy.html) |

Mapa rodziny: [pl](https://jd-japanese.pl/) · [en](https://jd-japanese.pl/en/). Spis dokumentów: [pl](https://jd-japanese.pl/dokumenty.html) · [en](https://jd-japanese.pl/en/documents.html).
<!-- /ADRESY -->

## Konfiguracja GitHub Pages

Settings → Pages → Source: **Deploy from a branch**, gałąź `main`, katalog `/ (root)`.
Publikacja zajmuje zwykle około minuty.

## Język

**Dokumenty są w tylu językach, w ilu jest interfejs aplikacji** (§6b w
`jp-grammar/docs/FAMILY_CONVENTIONS.md`). Do 02.09.2026 stała tu reguła odwrotna —
„dokument w języku podstawowym aplikacji" — i wystarczała dokładnie tak długo, jak długo
nikt tych dokumentów nie czytał. Recenzent Apple czyta: angielski interfejs otwierał
polski regulamin, a pole *Privacy Policy URL* w App Store Connect **jest per lokalizacja**
i też wskazywało polski.

Strony produktowe mają obie wersje językowe zawsze, niezależnie od `primaryLocale`
aplikacji, i wskazują na siebie przez `hreflang`.

**Adres dokumentu niesie wersję** (`<aplikacja>/<wersja>/…`), a katalog jest **zamrożony**
po wydaniu. Strony są jedne dla wszystkich zainstalowanych buildów, a wydania idą po
kolei: gdy 1.2 stoi w recenzji, w sklepie jest jeszcze 1.1. Bez wersji w adresie każda
zmiana dokumentu musi wybrać, którą aplikację okłamać. Adresy bez wersji **zostają
nietknięte** — linkują je buildy już wydane.

## Skąd pochodzi treść dokumentów prawnych

Dokumenty każdej aplikacji są kopią plików z `docs/app-store/` w repozytorium tej
aplikacji. **Przy zmianie treści aktualizuj obie kopie**, żeby nie rozjechały się z tym,
co aplikacja faktycznie robi.

Wszystkie strony w tym repozytorium są samodzielne: styl jest wpisany w plik, nie ma
zależności zewnętrznych, nie ma skryptów i nie ma żadnego śledzenia.
