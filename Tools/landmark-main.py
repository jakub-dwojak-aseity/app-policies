#!/usr/bin/env python3
"""Wstawia znacznik `<main>` do dokumentów prawnych — jeden landmark na stronę.

    python3 Tools/landmark-main.py            # wstawia i zapisuje
    python3 Tools/landmark-main.py --sprawdz  # nic nie pisze, tylko zgłasza braki

**Po co to istnieje.** Audyt dostępności (Lighthouse, „One main landmark helps screen
reader users navigate a web page") mówi o czytniku ekranu: bez `<main>` nie ma skoku
do treści z pominięciem nawigacji i stopki. Strony produktowe dostały landmark
z generatora (`generuj-strony.py`), ale **dokumenty prawne nie są generowane** —
to pliki pisane ręcznie, na które wskazuje `privacyPolicyUrl` w App Store Connect
i które widział App Review. Wciągnięcie ich pod generator przepisałoby tekst,
którego nikt nie zamawiał; wstawienie samego znacznika **nie zmienia ani jednego
renderowanego znaku**. Stąd osobne narzędzie zamiast osobnego szablonu.

**Dlaczego to nie jest jednolinijkowy `sed`.** Bo `sed` na pliku o innym kształcie
zrobi cichą zmianę w złym miejscu, a błąd w dokumencie prawnym jest gorszy niż jego
brak. To narzędzie **odmawia** pracy, gdy plik nie wygląda dokładnie tak, jak
zakłada wstawka, zamiast zgadywać.

**Co dokładnie robi:** nową linię `<main>` zaraz po linii z `<body>` i nową linię
`</main>` tuż przed linią z `<footer>`. Nic poza tym — reszta pliku zostaje bajt
w bajt, razem z wcięciami; wstawione linie dostają wcięcie linii, obok której stają.

**Pułapki, na które to narzędzie patrzy:**

- **więcej niż jeden `<body>` albo `<footer>`** — wtedy nie wiadomo, który jest ten
  właściwy, i narzędzie odmawia zamiast wybierać pierwszy z brzegu;
- **`<footer>` przed `<body>`** (plik złożony inaczej, niż zakłada wstawka) — odmowa;
- **coś jeszcze w linii `<body>`** albo **tekst przed `<footer>` w jego linii** —
  wstawka rozcięłaby zdanie na pół, więc też odmowa;
- **plik, który już ma `<main`** — pomijany bez słowa skargi, żeby przebieg był
  powtarzalny i żeby drugie uruchomienie nie dokładało drugiego landmarku;
- **`<h1>` poza `<main>`** — po wstawce nagłówek strony ma być w środku landmarku,
  inaczej czytnik ekranu skacze do treści i mija tytuł. Sprawdzane po zmianie,
  na wytworze, a nie na zamiarze.

Kod wyjścia: 0, gdy wszystko przeszło; 1, gdy któryś plik został odrzucony albo
(w `--sprawdz`) gdy którykolwiek dokument nie ma jeszcze landmarku.
"""

import argparse
import re
import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parent.parent

BODY = re.compile(r"<body\b[^>]*>")
FOOTER = re.compile(r"<footer\b[^>]*>")


def pliki_html(korzen: Path):
    """Wszystkie strony repozytorium, w stałej kolejności i bez wnętrza gita."""
    return sorted(p for p in korzen.rglob("*.html") if ".git" not in p.parts)


def wstaw(tresc: str):
    """Zwraca (nowa_tresc, powod_odmowy). Dokładnie jedno z dwojga jest None."""
    if "<main" in tresc:
        return None, None  # już ma landmark — nie ma czego wstawiać

    if len(BODY.findall(tresc)) != 1:
        return None, f"{len(BODY.findall(tresc))} znaczników <body> zamiast jednego"
    if len(FOOTER.findall(tresc)) != 1:
        return None, f"{len(FOOTER.findall(tresc))} znaczników <footer> zamiast jednego"

    linie = tresc.split("\n")
    i_body = next(i for i, l in enumerate(linie) if BODY.search(l))
    i_stopka = next(i for i, l in enumerate(linie) if FOOTER.search(l))
    if i_stopka <= i_body:
        return None, "<footer> stoi przed <body>"

    reszta = BODY.sub("", linie[i_body], count=1).strip()
    if reszta:
        return None, f"linia z <body> niesie jeszcze treść: {reszta[:40]!r}"
    przed = linie[i_stopka][:FOOTER.search(linie[i_stopka]).start()]
    if przed.strip():
        return None, f"treść przed <footer> w tej samej linii: {przed.strip()[:40]!r}"

    wciecie_body = linie[i_body][:len(linie[i_body]) - len(linie[i_body].lstrip())]
    nowe = list(linie)
    nowe.insert(i_stopka, przed + "</main>")   # najpierw dalsza wstawka,
    nowe.insert(i_body + 1, wciecie_body + "<main>")  # żeby indeksy się nie przesunęły
    return "\n".join(nowe), None


def sprawdz_wytwor(tresc: str):
    """Co musi być prawdą po wstawce. Mierzy plik, nie to, co narzędzie zamierzało."""
    bledy = []
    if tresc.count("<main") != 1 or tresc.count("</main>") != 1:
        bledy.append(f"<main {tresc.count('<main')}, </main> {tresc.count('</main>')}")
        return bledy
    otwarcie, zamkniecie = tresc.index("<main"), tresc.index("</main>")
    body = BODY.search(tresc)
    stopka = FOOTER.search(tresc)
    if body and otwarcie < body.end():
        bledy.append("<main> nie stoi za <body>")
    if stopka and zamkniecie > stopka.start():
        bledy.append("</main> nie stoi przed <footer>")
    for h1 in re.finditer(r"<h1\b", tresc):
        if not otwarcie < h1.start() < zamkniecie:
            bledy.append("<h1> poza <main>")
            break
    return bledy


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--sprawdz", action="store_true",
                        help="nic nie zapisuje; zgłasza braki i wychodzi kodem 1")
    parser.add_argument("sciezki", nargs="*", type=Path,
                        help="pliki albo katalogi (domyślnie całe repozytorium)")
    args = parser.parse_args()

    cele = []
    for s in (args.sciezki or [KORZEN]):
        cele += pliki_html(s) if s.is_dir() else [s]

    braki, odmowy, zmienione, zle = [], [], [], []
    for plik in cele:
        tresc = plik.read_text(encoding="utf-8")
        nowa, powod = wstaw(tresc)
        wzgledna = plik.relative_to(KORZEN) if KORZEN in plik.parents else plik
        if powod:
            odmowy.append(f"{wzgledna}: {powod}")
            continue
        if nowa is None:
            for blad in sprawdz_wytwor(tresc):
                zle.append(f"{wzgledna}: {blad}")
            continue
        braki.append(str(wzgledna))
        if args.sprawdz:
            continue
        po_wstawce = sprawdz_wytwor(nowa)
        if po_wstawce:
            # Wytwór nie przeszedł własnego sprawdzenia — plik zostaje nietknięty.
            zle += [f"{wzgledna}: {blad}" for blad in po_wstawce]
            continue
        plik.write_text(nowa, encoding="utf-8")
        zmienione.append(str(wzgledna))

    for wiersz in odmowy:
        print(f"odmowa: {wiersz}")
    for wiersz in zle:
        print(f"po wstawce nadal źle: {wiersz}")

    if args.sprawdz:
        for wiersz in braki:
            print(f"bez landmarku: {wiersz}")
        print(f"sprawdzono {len(cele)} plików: bez <main> {len(braki)}, "
              f"odmów {len(odmowy)}, wadliwych {len(zle)}")
        return 1 if braki or odmowy or zle else 0

    print(f"sprawdzono {len(cele)} plików: wstawiono <main> w {len(zmienione)}, "
          f"odmów {len(odmowy)}, wadliwych {len(zle)}")
    return 1 if odmowy or zle else 0


if __name__ == "__main__":
    sys.exit(main())
