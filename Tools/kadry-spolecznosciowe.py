#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kadry do wystawiania pojedynczych haseł — z tego, co już przejrzane.

    python3 Tools/kadry-spolecznosciowe.py                 # wszystkie, SVG
    python3 Tools/kadry-spolecznosciowe.py --apka joshi    # jedna apka
    python3 Tools/kadry-spolecznosciowe.py --limit 5 --png # próbka, z konwersją
    python3 Tools/kadry-spolecznosciowe.py --katalog /tmp/kadry

Po co to istnieje
=================

Poz. 113 backlogu rodziny („wizytówka poza witryną") jest **zobowiązaniem
cyklicznym**, a nie jednorazowym wystawieniem strony: konto, na które nie ma co
wrzucać co tydzień, umiera po trzech wpisach i robi to publicznie, obok
aplikacji. Rozstrzygnięcie Jakuba z 13.09.2026: **konta nie zakładamy, ale potok
przygotowujemy** — żeby w dniu decyzji materiał na pół roku już był.

**Nie pisze ani jednego nowego zdania.** Kadr składa się z hasła, jego nazwy,
glosy i jednego zdania przykładowego — wszystkiego z `docs/www/eksport.json`
sióstr, czyli z jednostek **darmowych, zielonych we wszystkich soczewkach
i z aktualnym odciskiem**. Ta sama reguła, co na stronach tematycznych: na zewnątrz
nie wychodzi nic, czego nikt nie sprawdził.

Czego to narzędzie **nie** robi
===============================

**Nie stawia furigany.** SVG nie ma rubinu, a ręczne pozycjonowanie czytań nad
znakami to osobna maszyneria — notacja jest tu więc zdejmowana, a nie zgadywana.
Na stronie furigana zostaje; kadr pokazuje zapis, który i tak stoi w japońskim
tekście.

**Nie publikuje.** Pliki lądują w katalogu roboczym (domyślnie `kadry-social/`,
poza gitem i poza witryną): to materiał do ręki człowieka, a nie część strony.

**Nie wymyśla kolejności.** Hasła idą w kolejności eksportu, czyli w kolejności
katalogu, czyli w kolejności nauki.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

NARZEDZIA = Path(__file__).resolve().parent
KORZEN = NARZEDZIA.parent
#: Korzeń drzew rodziny. Na Macu rozwija się dokładnie w to, co stało tu wpisane
#: na sztywno, więc zmiana jest bezobjawowa po tamtej stronie. Absolut macowy czynił
#: to narzędzie nieuruchamialnym na maszynie windowsowej — a jest ono neutralne
#: platformowo. Ten sam kształt stoi w `japanese-tools/lib/rodzina.py`.
ZRODLA = Path(os.environ.get("ASEITY_ROOT") or Path.home() / "aseity")
sys.path.insert(0, str(NARZEDZIA))

from napisy import NAPISY  # noqa: E402

EKSPORT_PLIK = Path("docs") / "www" / "eksport.json"

# Kadr pionowy 4:5 — najbezpieczniejszy kształt na kanałach obrazkowych: mieści
# się w kwadracie z obcięciem u góry i u dołu, a nie w poprzek treści.
SZEROKOSC, WYSOKOSC = 1080, 1350
MARGINES = 96

# Paleta ciemna witryny, co do wartości (`STYL` w `generuj-strony.py`). Kadr ma
# wyglądać jak strona, z której pochodzi — druga paleta byłaby drugą marką.
TLO, TEKST, CICHY, AKCENT, LINIA = "#131315", "#ececef", "#9a9aa0", "#e08a94", "#2c2c30"

# Rodzina krojów z japońskim na pierwszym miejscu: bez niej `rsvg-convert`
# podstawia krój bez kany i kadr wychodzi w prostokątach zastępczych.
KROJE = "Hiragino Sans, Hiragino Kaku Gothic ProN, Noto Sans JP, -apple-system, sans-serif"

CZYTANIA = re.compile(r"\[[^\]]*\]")


def bez_czytan(tekst):
    """`見[み]る` → `見る`. Notacja zdejmowana, nie interpretowana."""
    return CZYTANIA.sub("", tekst or "")


def szerokosc_znaku(znak):
    """Przybliżona szerokość w em. Znak CJK zajmuje pełny firet, łacina połowę —
    bez tego rozróżnienia zawijanie tnie japońskie zdania w połowie wiersza."""
    return 1.0 if ord(znak) > 0x2E7F else 0.5


def zawin(tekst, rozmiar, szerokosc=SZEROKOSC - 2 * MARGINES):
    """Ręczne zawijanie, bo SVG nie zawija samo.

    Łamiemy po spacji tam, gdzie spacje są, i po znaku tam, gdzie ich nie ma —
    japońskie zdanie bywa jednym „słowem" i próba łamania po spacjach zostawiłaby
    je poza kadrem.
    """
    limit = szerokosc / rozmiar
    wiersze, biezacy, szer = [], "", 0.0
    for kawalek in re.findall(r"\S+\s*|\s+", tekst):
        w = sum(szerokosc_znaku(z) for z in kawalek)
        if biezacy and szer + w > limit:
            wiersze.append(biezacy.rstrip())
            biezacy, szer = "", 0.0
        if w > limit:                      # jeden długi ciąg bez spacji
            for znak in kawalek:
                zz = szerokosc_znaku(znak)
                if szer + zz > limit:
                    wiersze.append(biezacy.rstrip())
                    biezacy, szer = "", 0.0
                biezacy += znak
                szer += zz
            continue
        biezacy += kawalek
        szer += w
    if biezacy.strip():
        wiersze.append(biezacy.rstrip())
    return wiersze


def e(tekst):
    return (tekst.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def blok(tekst, y, rozmiar, kolor, waga="400", odstep=1.35):
    """Akapit jako ciąg `<text>` — zwraca `(html, następne y)`."""
    czesci = []
    for wiersz in zawin(tekst, rozmiar):
        czesci.append(
            f'<text x="{MARGINES}" y="{y:.0f}" font-family="{KROJE}" '
            f'font-size="{rozmiar}" fill="{kolor}" font-weight="{waga}">'
            f"{e(wiersz)}</text>")
        y += rozmiar * odstep
    return "".join(czesci), y


def do_zdania(tekst, limit=190):
    """Ucięcie **na granicy zdania**, a nie na granicy znaku.

    Pierwsza wersja brała `[:180]` i zostawiała na kadrze wiszące „która" —
    urwane w połowie zdania wygląda nie na skrót, tylko na zepsuty plik.
    Szukamy więc ostatniej kropki w limicie, a gdy jej nie ma, ostatniej spacji
    i dokładamy wielokropek.
    """
    tekst = tekst.strip()
    if len(tekst) <= limit:
        return tekst
    okno = tekst[:limit]
    for koniec in ("。", ". ", "! ", "? ", "; "):
        ciecie = okno.rfind(koniec)
        if ciecie > limit // 3:
            return okno[:ciecie + len(koniec)].strip()
    ciecie = okno.rfind(" ")
    return (okno[:ciecie] if ciecie > limit // 3 else okno).rstrip() + "…"


def kadr(jednostka, jezyk, nazwa_apki):
    """Jeden kadr: hasło, nazwa, glosa, jedno zdanie. Nic ponadto."""
    termin = bez_czytan(jednostka.get("termin") or "")
    nazwa = bez_czytan(jednostka["nazwa"][jezyk])
    # **Notacja zdejmowana ze WSZYSTKIEGO, nie tylko z terminu.** Keigo trzyma
    # wyjaśnienia w wersji z czytaniami (`explanationRuby`), więc na kadr wchodziło
    # `お願[ねが]いします` z nawiasami — widoczne dopiero na obrazku, bo w JSON-ie
    # wygląda to jak poprawna treść.
    glosa = bez_czytan(jednostka["glosa"][jezyk] or (
        jednostka["wyjasnienie"][jezyk].split("\n\n")[0] if jednostka["wyjasnienie"][jezyk] else ""))

    czesci = [f'<rect width="{SZEROKOSC}" height="{WYSOKOSC}" fill="{TLO}"/>']
    y = MARGINES + 150

    if termin:
        html, y = blok(termin, y, 130, TEKST, waga="600", odstep=1.15)
        czesci.append(html)
        y += 30
    if nazwa:
        html, y = blok(nazwa, y, 46, AKCENT if termin else TEKST,
                       waga="600" if not termin else "400")
        czesci.append(html)
        y += 26
    if glosa:
        html, y = blok(do_zdania(glosa), y, 34, CICHY)
        czesci.append(html)

    przyklady = jednostka.get("przyklady") or []
    if przyklady:
        p = przyklady[0]
        # Zdanie **tuż pod glosą**, nie przyklejone do dołu. Kotwiczenie go
        # u spodu dawało przy krótkich hasłach pas pustki przez pół kadru —
        # wyglądało jak brak treści, a nie jak oddech.
        y += 100
        czesci.append(f'<line x1="{MARGINES}" y1="{y - 50:.0f}" '
                      f'x2="{SZEROKOSC - MARGINES}" y2="{y - 50:.0f}" stroke="{LINIA}"/>')
        html, y = blok(bez_czytan(p["jp"]), y, 44, TEKST)
        czesci.append(html)
        if p.get(jezyk):
            y += 12
            html, y = blok(bez_czytan(p[jezyk]), y, 30, CICHY)
            czesci.append(html)

    stopka = f"{nazwa_apki} · jd-japanese.pl"
    czesci.append(
        f'<text x="{MARGINES}" y="{WYSOKOSC - MARGINES + 20}" font-family="{KROJE}" '
        f'font-size="26" fill="{CICHY}">{e(stopka)}</text>')

    return ('<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{SZEROKOSC}" height="{WYSOKOSC}" '
            f'viewBox="0 0 {SZEROKOSC} {WYSOKOSC}">' + "".join(czesci) + "</svg>\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apka", help="tylko ta aplikacja (slug)")
    parser.add_argument("--jezyk", choices=("pl", "en"), default="pl")
    parser.add_argument("--limit", type=int, help="ile kadrów na aplikację")
    parser.add_argument("--png", action="store_true",
                        help="przepuść przez rsvg-convert (musi być zainstalowany)")
    parser.add_argument("--katalog", default=str(KORZEN / "kadry-social"))
    args = parser.parse_args()

    manifest = json.loads((NARZEDZIA / "apps.json").read_text(encoding="utf-8"))
    cel = Path(args.katalog)
    zrobione, bez_eksportu = 0, []

    for wpis in sorted(manifest["aplikacje"], key=lambda a: a["kolejnosc"]):
        if args.apka and wpis["slug"] != args.apka:
            continue
        plik = ZRODLA / wpis["repo"] / EKSPORT_PLIK
        if not plik.is_file():
            bez_eksportu.append(wpis["slug"])
            continue
        eksport = json.loads(plik.read_text(encoding="utf-8"))
        nazwa_apki = wpis["slug"].capitalize()
        katalog = cel / wpis["slug"] / args.jezyk
        katalog.mkdir(parents=True, exist_ok=True)
        jednostki = eksport.get("jednostki", [])
        if args.limit:
            jednostki = jednostki[:args.limit]
        for jednostka in jednostki:
            nazwa_pliku = re.sub(r"[^A-Za-z0-9._-]+", "-", jednostka["id"]).strip("-")
            sciezka = katalog / f"{nazwa_pliku}.svg"
            sciezka.write_text(kadr(jednostka, args.jezyk, nazwa_apki), encoding="utf-8")
            if args.png:
                subprocess.run(["rsvg-convert", "-o", str(sciezka.with_suffix(".png")),
                                str(sciezka)], check=True)
            zrobione += 1
        print("%-12s %3d kadrów → %s" % (wpis["slug"], len(jednostki), katalog))

    print("razem: %d kadrów (%s)" % (zrobione, "SVG + PNG" if args.png else "SVG"))
    if bez_eksportu:
        print("bez eksportu, więc bez kadrów: %s" % ", ".join(bez_eksportu),
              file=sys.stderr)


if __name__ == "__main__":
    main()
