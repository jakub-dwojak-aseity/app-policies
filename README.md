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
że plik istnieje.

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

Generator nie zapisuje niczego, dopóki nie przejdzie wszystkich:

1. każdy dokument prawny, do którego strona linkuje, **istnieje na dysku**;
2. każdy link wewnętrzny prowadzi do pliku, który istnieje albo powstanie;
3. każda strona ma tytuł, `<meta name="description">` do 160 znaków, `<html lang>`
   i adres kanoniczny;
4. tekst własny generatora nie zawiera pauzy `—` (§21.Z: półpauza);
5. nazwy aplikacji się nie dublują;
6. `sitemap.xml` wymienia dokładnie te strony, które generator zapisuje.

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
| Kaname: Gramatyka japońska 要 | [pl](https://jakub-dwojak-aseity.github.io/app-policies/apps/kaname/) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/apps/kaname/) | [pl](https://jakub-dwojak-aseity.github.io/app-policies/kaname/1.2/privacy.html) · [en](https://jakub-dwojak-aseity.github.io/app-policies/kaname/1.2/en/privacy.html) |
| Bunmyaku — Japoński w zdaniu 文脈 | [pl](https://jakub-dwojak-aseity.github.io/app-policies/apps/bunmyaku/) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/apps/bunmyaku/) | [pl](https://jakub-dwojak-aseity.github.io/app-policies/bunmyaku/1.2/privacy.html) · [en](https://jakub-dwojak-aseity.github.io/app-policies/bunmyaku/1.2/en/privacy.html) |
| Katsuyokei: Odmiana japońska 活用形 | [pl](https://jakub-dwojak-aseity.github.io/app-policies/apps/katsuyokei/) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/apps/katsuyokei/) | [pl](https://jakub-dwojak-aseity.github.io/app-policies/katsuyokei/privacy.html) · [en](https://jakub-dwojak-aseity.github.io/app-policies/katsuyokei/en/privacy.html) |
| Joshi: Partykuły japońskie 助詞 | [pl](https://jakub-dwojak-aseity.github.io/app-policies/apps/joshi/) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/apps/joshi/) | [pl](https://jakub-dwojak-aseity.github.io/app-policies/joshi/privacy.html) · [en](https://jakub-dwojak-aseity.github.io/app-policies/joshi/en/privacy.html) |
| Kazoekata: Liczniki japońskie 数え方 | [pl](https://jakub-dwojak-aseity.github.io/app-policies/apps/kazoekata/) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/apps/kazoekata/) | [pl](https://jakub-dwojak-aseity.github.io/app-policies/kazoekata/privacy.html) · [en](https://jakub-dwojak-aseity.github.io/app-policies/kazoekata/en/privacy.html) |
| Kuzushi: Mowa potoczna 崩し | [pl](https://jakub-dwojak-aseity.github.io/app-policies/apps/kuzushi/) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/apps/kuzushi/) | [pl](https://jakub-dwojak-aseity.github.io/app-policies/kuzushi/pl/privacy.html) · [en](https://jakub-dwojak-aseity.github.io/app-policies/kuzushi/privacy.html) |
| Shindan: Poziom japońskiego 診断 *(przed wydaniem)* | [pl](https://jakub-dwojak-aseity.github.io/app-policies/apps/shindan/) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/apps/shindan/) | [pl](https://jakub-dwojak-aseity.github.io/app-policies/shindan/1.0/privacy.html) · [en](https://jakub-dwojak-aseity.github.io/app-policies/shindan/1.0/en/privacy.html) |
| Keigo: Grzeczność japońska 敬語 *(przed wydaniem)* | [pl](https://jakub-dwojak-aseity.github.io/app-policies/apps/keigo/) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/apps/keigo/) | [pl](https://jakub-dwojak-aseity.github.io/app-policies/keigo/1.0/privacy.html) · [en](https://jakub-dwojak-aseity.github.io/app-policies/keigo/1.0/en/privacy.html) |
| Kifuku: Akcent japoński 起伏 *(przed wydaniem)* | [pl](https://jakub-dwojak-aseity.github.io/app-policies/apps/kifuku/) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/apps/kifuku/) | [pl](https://jakub-dwojak-aseity.github.io/app-policies/kifuku/1.0/privacy.html) · [en](https://jakub-dwojak-aseity.github.io/app-policies/kifuku/1.0/en/privacy.html) |
| Onomatope: Japońskie dźwięki オノマトペ *(przed wydaniem)* | [pl](https://jakub-dwojak-aseity.github.io/app-policies/apps/onomatope/) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/apps/onomatope/) | [pl](https://jakub-dwojak-aseity.github.io/app-policies/onomatope/1.0/privacy.html) · [en](https://jakub-dwojak-aseity.github.io/app-policies/onomatope/1.0/en/privacy.html) |
| SpoolCalc – kalkulator pojemności szpuli | – | [en](https://jakub-dwojak-aseity.github.io/app-policies/spoolcalc/privacy.html) |

Mapa rodziny: [pl](https://jakub-dwojak-aseity.github.io/app-policies/) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/). Spis dokumentów: [pl](https://jakub-dwojak-aseity.github.io/app-policies/dokumenty.html) · [en](https://jakub-dwojak-aseity.github.io/app-policies/en/documents.html).
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
