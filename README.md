# app-policies

Strony prawne aplikacji, hostowane na GitHub Pages.

Apple wymaga, żeby adres polityki prywatności i adres wsparcia **działały publicznie**
w momencie recenzji i **nie wymagały logowania** — dlatego to repozytorium jest publiczne
i odseparowane od prywatnych repozytoriów z kodem.

## Adresy

| Aplikacja | Dokument | Adres |
|---|---|---|
| Kaname | Polityka prywatności | https://jakub-dwojak-aseity.github.io/app-policies/kaname/privacy.html |
| Kaname | Wsparcie | https://jakub-dwojak-aseity.github.io/app-policies/kaname/support.html |
| Kaname | Warunki korzystania | https://jakub-dwojak-aseity.github.io/app-policies/kaname/terms.html |
| Katsuyokei | Polityka prywatności | https://jakub-dwojak-aseity.github.io/app-policies/katsuyokei/privacy.html |
| Katsuyokei | Wsparcie | https://jakub-dwojak-aseity.github.io/app-policies/katsuyokei/support.html |
| Katsuyokei | Warunki korzystania | https://jakub-dwojak-aseity.github.io/app-policies/katsuyokei/terms.html |
| Joshi | Polityka prywatności | https://jakub-dwojak-aseity.github.io/app-policies/joshi/privacy.html |
| Joshi | Wsparcie | https://jakub-dwojak-aseity.github.io/app-policies/joshi/support.html |
| Joshi | Warunki korzystania | https://jakub-dwojak-aseity.github.io/app-policies/joshi/terms.html |
| Kazoekata | Polityka prywatności | https://jakub-dwojak-aseity.github.io/app-policies/kazoekata/privacy.html |
| Kazoekata | Wsparcie | https://jakub-dwojak-aseity.github.io/app-policies/kazoekata/support.html |
| Kazoekata | Warunki korzystania | https://jakub-dwojak-aseity.github.io/app-policies/kazoekata/terms.html |
| Bunmyaku | Privacy Policy | https://jakub-dwojak-aseity.github.io/app-policies/bunmyaku/privacy.html |
| Bunmyaku | Support | https://jakub-dwojak-aseity.github.io/app-policies/bunmyaku/support.html |
| Bunmyaku | Terms of Use | https://jakub-dwojak-aseity.github.io/app-policies/bunmyaku/terms.html |
| Kuzushi | Strona aplikacji (adres marketingowy) | https://jakub-dwojak-aseity.github.io/app-policies/kuzushi/ |
| Kuzushi | Privacy Policy | https://jakub-dwojak-aseity.github.io/app-policies/kuzushi/privacy.html |
| Kuzushi | Support | https://jakub-dwojak-aseity.github.io/app-policies/kuzushi/support.html |
| Kuzushi | Terms of Use | https://jakub-dwojak-aseity.github.io/app-policies/kuzushi/terms.html |
| SpoolCalc | Privacy Policy | https://jakub-dwojak-aseity.github.io/app-policies/spoolcalc/privacy.html |
| SpoolCalc | Support | https://jakub-dwojak-aseity.github.io/app-policies/spoolcalc/support.html |
| SpoolCalc | Terms of Use | https://jakub-dwojak-aseity.github.io/app-policies/spoolcalc/terms.html |

## Konfiguracja GitHub Pages

Settings → Pages → Source: **Deploy from a branch**, gałąź `main`, katalog `/ (root)`.
Publikacja zajmuje zwykle około minuty.

## Struktura

```
index.html          spis dokumentów
kaname/             Kaname — gramatyka japońska (JLPT N5–N3)
  privacy.html
  support.html
  terms.html
katsuyokei/         Katsuyokei — japońska odmiana czasowników i przymiotników
  privacy.html
  support.html
  terms.html
joshi/              Joshi — japońskie partykuły
  privacy.html
  support.html
  terms.html
kazoekata/          Kazoekata — japońskie liczniki
  privacy.html
  support.html
  terms.html
bunmyaku/           Bunmyaku — japoński w zdaniu (czytanie)
  privacy.html
  support.html
  terms.html
kuzushi/            Kuzushi — japońska mowa potoczna
  index.html          strona aplikacji — jedyna taka, patrz niżej
  privacy.html
  support.html
  terms.html
spoolcalc/          SpoolCalc — kalkulator pojemności szpuli (wędkarstwo)
  privacy.html
  support.html
  terms.html
```

Kolejne aplikacje dostają własny katalog obok `kaname/`.

**Kuzushi ma w katalogu dodatkowe `index.html` i jest w tym jedyne.** Powód jest
wąski: jako jedyna aplikacja ma wypełnione pole *Marketing URL* w App Store
Connect, a wskazywało ono na sam katalog — czyli na 404, bo GitHub Pages nie
wystawia spisu plików. Strona jest odpowiedzią na to pole. Pozostałe pięć trzyma
Marketing URL pustym, tak jak Bunmyaku, i katalogu z `index.html` nie potrzebuje.

## Skąd pochodzi treść

Strony każdej aplikacji są kopią plików z `docs/app-store/` w repozytorium tej aplikacji.
**Przy zmianie treści aktualizuj obie kopie**, żeby nie rozjechały się z tym,
co aplikacja faktycznie robi.

Strony są samodzielne: styl jest wpisany w plik, nie ma zależności zewnętrznych,
nie ma skryptów i nie ma żadnego śledzenia.

## Język

Zasada jest jedna: **dokument prawny jest w tym języku, w którym recenzent Apple
widzi aplikację** — czyli w jej `primaryLocale` w App Store Connect, a nie w tym,
ile lokalizacji aplikacja wozi w środku.

Strony Kaname, Katsuyokei, Joshi i Kazoekaty są po polsku, bo te aplikacje mają
polski jako podstawowy. Strony Bunmyaku i Kuzushi są po angielsku, choć obie
aplikacje są dwujęzyczne (`en` + `pl`): ich `primaryLocale` to `en-US`. Strony
SpoolCalc są po angielsku, bo wersja 1.0 tej aplikacji jest anglojęzyczna.

Gdy któraś z anglojęzycznych przełączy się na polski jako podstawowy, dołóż
wersje `pl` — nie zamieniaj istniejących.
