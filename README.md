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
```

Kolejne aplikacje dostają własny katalog obok `kaname/`.

## Skąd pochodzi treść

Strony Kaname są kopią plików z `docs/app-store/` w repozytorium aplikacji.
**Przy zmianie treści aktualizuj obie kopie**, żeby nie rozjechały się z tym,
co aplikacja faktycznie robi.

Strony są samodzielne: styl jest wpisany w plik, nie ma zależności zewnętrznych,
nie ma skryptów i nie ma żadnego śledzenia.
