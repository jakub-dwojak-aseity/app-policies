#!/usr/bin/env python3
"""Dopisuje `canonical` do dokumentów prawnych, a przestarzałym — `noindex`.

    python3 Tools/glowy_dokumentow.py            # dopisuje i zapisuje
    python3 Tools/glowy_dokumentow.py --sprawdz  # nic nie pisze, tylko zgłasza braki

**Po co to istnieje.** Zmierzone 09.09.2026: siedemdziesiąt dokumentów prawnych ma
w `<head>` wyłącznie `<title>` i `lang`. Zero `canonical`, zero `robots`. W mapie
witryny ich nie ma, ale linkuje do nich `dokumenty.html`, który **w mapie jest** —
więc robot po nie sięgnie. Na domenie postawionej tego samego dnia znaczy to, że
pierwszy obchód idzie w siedemdziesiąt cienkich stron zamiast w dwadzieścia
produktowych.

**Dlaczego `canonical`, a nie przekierowanie.** Dokument prawny musi zostać pod
swoim adresem: wskazuje na niego `privacyPolicyUrl` w App Store Connect, widział go
App Review, i krąży w dwudziestu starych adresach `github.io`, które dziś oddają
`301`. Adresu się nie rusza — mówi się tylko wprost, że to jest ten właściwy.

**Dlaczego przestarzałe dostają `noindex`, a nie `canonical` na nowszą wersję.**
Bo `canonical` znaczy „ta sama treść pod dwoma adresami", a to nie jest ta sama
treść: `kaname/privacy.html` różni się od `kaname/1.2/privacy.html` o 34 linie,
`bunmyaku/privacy.html` od swojej nowszej wersji o 273. To są **starsze wersje
polityki, obowiązujące dla starszych wydań aplikacji**, które ktoś ma jeszcze na
telefonie. Muszą zostać osiągalne i nie mają konkurować w wyszukiwarce z bieżącą —
a to jest dokładnie definicja `noindex, follow`. `follow`, bo linki ze stopki takiego
dokumentu prowadzą do reszty witryny i mają być przechodzone.

**Co jest bieżące, a co przestarzałe, mówi `Tools/apps.json`** — ten sam manifest,
z którego generują się strony i mapa witryny. Nie ma tu drugiej listy do utrzymania:
dokument spoza pola `dokumenty` którejkolwiek aplikacji jest z definicji poza
bieżącym obiegiem.

**Nazwa pliku bez łącznika jest celowa.** Bramka 11 w `generuj-strony.py` importuje
ten moduł, żeby „które dokumenty są bieżące" istniało w jednym miejscu, a nie
w dwóch kopiach, które się rozjadą — narzędzia rodziny mają już taką bliznę.
Import wymaga nazwy będącej identyfikatorem Pythona, stąd `glowy_dokumentow`,
tak jak `metadane`, a nie `landmark-main`.

**Dlaczego to nie jest `sed`.** Bo błąd w dokumencie prawnym jest gorszy niż jego
brak. Narzędzie **odmawia** pracy na pliku, który nie wygląda tak, jak zakłada
wstawka, zamiast wstawiać w przypadkowe miejsce.

**Pułapki, na które patrzy:**

- **brak albo więcej niż jeden `<title>`** — nie wiadomo, po której linii wstawiać:
  odmowa;
- **plik, który już ma `canonical`** — pomijany bez skargi, żeby drugie uruchomienie
  nie dokładało drugiego znacznika i żeby przebieg był powtarzalny;
- **`canonical` niezgodny z adresem pliku** — zgłaszany jako błąd, nie nadpisywany
  po cichu; to znaczy, że ktoś wstawił go ręcznie i trzeba na to spojrzeć;
- **`noindex` na dokumencie bieżącym** — błąd. Bieżąca polityka ma być w indeksie;
- **dokument w manifeście, którego nie ma na dysku** — błąd, bo to znaczy, że strona
  linkuje w pustkę.

Kod wyjścia: 0, gdy wszystko przeszło; 1, gdy któryś plik został odrzucony albo
(w `--sprawdz`) gdy którykolwiek dokument nie ma jeszcze kompletnej głowy.
"""

import argparse
import json
import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parent.parent
PLIKI_DOKUMENTU = ("privacy.html", "terms.html", "support.html")
CANONICAL = '<link rel="canonical" href="{adres}">'
NOINDEX = '<meta name="robots" content="noindex, follow">'


def manifest() -> dict:
    return json.loads((KORZEN / "Tools" / "apps.json").read_text(encoding="utf-8"))


def biezace(m: dict) -> set[str]:
    """Ścieżki dokumentów, na które wskazuje dziś którakolwiek aplikacja."""
    wynik = set()
    for a in list(m["aplikacje"]) + list(m.get("pozostale", [])):
        for katalog in a["dokumenty"].values():
            wynik |= {f"{katalog}/{plik}" for plik in PLIKI_DOKUMENTU}
    return wynik


def dokumenty_na_dysku() -> list[str]:
    """Wszystkie ręcznie pisane dokumenty prawne, po ścieżkach względem korzenia.

    Generowane strony rozpoznajemy po tym, że leżą w `apps/` albo są jedną
    z czterech stron witryny — generator dopisuje im głowę sam.
    """
    generowane = {"index.html", "404.html", "dokumenty.html",
                  "en/index.html", "en/documents.html"}
    wynik = []
    for sciezka in sorted(KORZEN.rglob("*.html")):
        wzgledna = sciezka.relative_to(KORZEN).as_posix()
        if wzgledna.startswith((".git/", "apps/", "en/apps/", "assets/", "Tools/")):
            continue
        if wzgledna in generowane or wzgledna.endswith("/index.html"):
            continue
        wynik.append(wzgledna)
    return wynik


def wstaw(tresc: str, wiersze_do_wstawienia: list[str]) -> str:
    """Dokłada wiersze zaraz po linii z `<title>`, z jej wcięciem.

    Odmawia, gdy `<title>` nie ma albo jest więcej niż jeden — wtedy nie wiadomo,
    gdzie jest głowa dokumentu, a zgadywanie w pliku prawnym jest gorsze niż brak.
    """
    linie = tresc.split("\n")
    trafienia = [i for i, w in enumerate(linie) if "<title>" in w]
    if len(trafienia) != 1:
        raise ValueError(f"linii z <title>: {len(trafienia)}, oczekiwano jednej")
    i = trafienia[0]
    wciecie = linie[i][: len(linie[i]) - len(linie[i].lstrip())]
    return "\n".join(linie[: i + 1] + [wciecie + w for w in wiersze_do_wstawienia]
                     + linie[i + 1:])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sprawdz", action="store_true",
                        help="nic nie zapisuje; kod 1, gdy czegoś brakuje")
    args = parser.parse_args()

    m = manifest()
    baza = m["bazaAdresu"].rstrip("/")
    aktualne = biezace(m)
    bledy, zmienione, pominiete = [], [], 0

    for wzgledna in sorted(aktualne):
        if not (KORZEN / wzgledna).exists():
            bledy.append(f"{wzgledna}: jest w manifeście, nie ma go na dysku")

    for wzgledna in dokumenty_na_dysku():
        plik = KORZEN / wzgledna
        tresc = plik.read_text(encoding="utf-8")
        adres = f"{baza}/{wzgledna}"
        przestarzaly = wzgledna not in aktualne

        ma_canonical = 'rel="canonical"' in tresc
        ma_noindex = "noindex" in tresc

        if ma_canonical and adres not in tresc:
            bledy.append(f"{wzgledna}: ma canonical na inny adres niż własny")
            continue
        if ma_noindex and not przestarzaly:
            bledy.append(f"{wzgledna}: dokument bieżący ma noindex")
            continue

        potrzebne = []
        if not ma_canonical:
            potrzebne.append(CANONICAL.format(adres=adres))
        if przestarzaly and not ma_noindex:
            potrzebne.append(NOINDEX)
        if not potrzebne:
            pominiete += 1
            continue

        if args.sprawdz:
            zmienione.append(wzgledna)
            continue
        try:
            plik.write_text(wstaw(tresc, potrzebne), encoding="utf-8")
        except ValueError as blad:
            bledy.append(f"{wzgledna}: {blad}")
            continue
        zmienione.append(wzgledna)

    for blad in bledy:
        print(f"  ✗ {blad}")
    czasownik = "bez głowy" if args.sprawdz else "uzupełnione"
    print(f"dokumenty prawne: {czasownik}: {len(zmienione)}, "
          f"kompletne wcześniej: {pominiete}, przestarzałe: "
          f"{len([w for w in dokumenty_na_dysku() if w not in aktualne])}")
    return 1 if bledy or (args.sprawdz and zmienione) else 0


if __name__ == "__main__":
    sys.exit(main())
