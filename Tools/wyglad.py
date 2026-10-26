"""Wygląd rodziny na witrynie: kolory apek, neutralne i Kinako — z `Tools/wyglad.json`.

Kopię zakłada `Tools/wyglad-z-ui.py` z zacommitowanego stanu `japanese-ui`; ten moduł
tylko ją czyta. Nazwa bez łącznika, bo importuje go generator (tak jak `metadane`).

**Kolor apki jedzie zmiennymi, nie klasą na apkę.** Element w kolorze apki dostaje
`style="--cl:…;--cal:…;--cd:…;--cad:…"`, a arkusz wybiera parę jasną albo ciemną
przez `prefers-color-scheme`. Szesnaście klas po cztery reguły byłoby drugą kopią
tokenów w CSS — a tak jedyną kopią jest `wyglad.json`.

**Kinako jest rysowany ścieżkami, po jednej na kolor palety.** Makieta stawiała
prostokąt na piksel: ~1300 `<rect>` na pozę, ~90 KB na stronę z dwoma kotkami.
Tu sąsiednie piksele w wierszu sklejają się w odcinek, a każda poza stoi na stronie
raz, jako `<symbol>`, i jest wołana przez `<use>`. Obroża (`a` w palecie) bierze
`--c`, więc kotek na stronie Joshiego nosi fiolet Joshiego, bez osobnego rysunku.
"""
import json
from pathlib import Path

PLIK = Path(__file__).resolve().parent / "wyglad.json"
DANE = json.loads(PLIK.read_text(encoding="utf-8"))

#: Kolor rodziny, gdy strona nie należy do żadnej apki. Kaname, bo to jego czerwień
#: niesie znak witryny i karta podglądu rodziny.
DOMYSLNA = "kaname"

#: Nazwy zmiennych CSS dla neutralnych tokenów — te same, co w makietach (`default.css`).
NEUTRALNE = {"background": "--bg", "surface": "--surface", "surface2": "--surface-2",
             "line": "--line", "text": "--text", "textMuted": "--text-muted"}


def ma_kolor(slug: str) -> bool:
    return slug in DANE["apki"]


def zmienne(slug: str) -> str:
    """Wartość atrybutu `style` z parą kolorów apki (bez cudzysłowów)."""
    w = DANE["apki"].get(slug) or DANE["apki"][DOMYSLNA]
    return (f'--cl:{w["band"]["light"]};--cal:{w["accentText"]["light"]};'
            f'--cd:{w["band"]["dark"]};--cad:{w["accentText"]["dark"]}')


def kolor(slug: str) -> str:
    """Gotowy atrybut ` style="…"` dla elementu w kolorze apki."""
    return f' style="{zmienne(slug)}"'


def css_neutralne() -> str:
    """Neutralne tokeny jako zmienne `:root` — jasne i ciemne."""
    n = DANE["neutralne"]
    jasne = "; ".join(f'{NEUTRALNE[k]}:{n[k]["light"]}' for k in NEUTRALNE)
    ciemne = "; ".join(f'{NEUTRALNE[k]}:{n[k]["dark"]}' for k in NEUTRALNE)
    domyslna = zmienne(DOMYSLNA)
    return (f":root {{ color-scheme: light dark; {jasne}; {domyslna}; --ko:{DANE['kinako']['paleta']['O']}; }}\n"
            f"@media (prefers-color-scheme: dark) {{\n"
            f"  :root {{ {ciemne}; --ko:{DANE['kinako']['paleta_ciemna']['O']}; }}\n"
            f"}}\n")


def _sciezki(siatka: list[str], akcent: str | None = None) -> str:
    """Ścieżki pozy. Bez `akcentu` obroża i kontur idą zmiennymi CSS (strona);
    z `akcentem` wszystko jest literałem — dla `rsvg-convert`, który zmiennych nie zna."""
    paleta = DANE["kinako"]["paleta"]
    odcinki: dict[str, list[str]] = {}
    for y, wiersz in enumerate(siatka):
        x = 0
        while x < len(wiersz):
            znak = wiersz[x]
            if znak == ".":
                x += 1
                continue
            koniec = x
            while koniec < len(wiersz) and wiersz[koniec] == znak:
                koniec += 1
            odcinki.setdefault(znak, []).append(f"M{x} {y}h{koniec - x}v1h-{koniec - x}z")
            x = koniec
    czesci = []
    for znak in sorted(odcinki):
        wartosc = paleta[znak]
        if wartosc == "akcent":
            wypelnienie = f"fill:{akcent}" if akcent else "fill:var(--c,#C4525A)"
        elif akcent:
            wypelnienie = f"fill:{wartosc}"
        elif znak == "O":
            wypelnienie = f"fill:var(--ko,{wartosc})"
        else:
            wypelnienie = f"fill:{wartosc}"
        czesci.append(f'<path style="{wypelnienie}" d="{"".join(odcinki[znak])}"/>')
    return "".join(czesci)


POZY = tuple(sorted(DANE["kinako"]["emocje"]))


def symbole(pozy) -> str:
    """Definicje póz użytych na stronie — jeden niewidoczny `<svg>` na początku `<body>`."""
    if not pozy:
        return ""
    r = DANE["kinako"]["rozmiar"]
    wnetrze = "".join(
        f'<symbol id="kinako-{p}" viewBox="0 0 {r} {r}">'
        f'{_sciezki(DANE["kinako"]["emocje"][p])}</symbol>'
        for p in sorted(pozy))
    return (f'<svg class="symbole" width="0" height="0" aria-hidden="true" '
            f'focusable="false">{wnetrze}</svg>')


def kinako(poza: str = "standard", px: int = 96, klasa: str = "") -> str:
    """Kinako na stronie. Ozdoba, więc `aria-hidden`: mówi dymek obok, nie obrazek."""
    if poza not in POZY:
        raise KeyError(f"Kinako nie ma pozy {poza!r} (są: {', '.join(POZY)})")
    k = f"kinako {klasa}".strip()
    return (f'<svg class="{k}" width="{px}" height="{px}" aria-hidden="true" '
            f'focusable="false"><use href="#kinako-{poza}"/></svg>')


def uzyte_pozy(tekst: str) -> list[str]:
    return [p for p in POZY if f'href="#kinako-{p}"' in tekst]


def znak_svg(tlo: str = "#A34F5A", bok: int = 180, poza: str = "standard") -> str:
    """Znak jd-japanese: Kinako na tle marki, obroża w kolorze tła (awatar z 26.10.2026).

    Kadr: **głowa na środku** (Jakub 26.10) — głowa zajmuje w siatce kolumny 0–36
    i wiersze 0–26, więc środek (18, 13) stoi w środku okna 46×46; ogon mieści się
    w całości, tułów jest przycięty. Rysowany z tych
    samych siatek co kotek na stronach, więc zmiana Kinako w pakiecie zmienia też znak.
    """
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{bok}" height="{bok}" viewBox="0 0 {bok} {bok}">'
            f'<rect width="{bok}" height="{bok}" rx="{bok * 2 // 9}" fill="{tlo}"/>'
            f'<svg x="0" y="0" width="{bok}" height="{bok}" viewBox="-5 -10 46 46" shape-rendering="crispEdges">'
            f'{_sciezki(DANE["kinako"]["emocje"][poza], akcent=tlo)}</svg></svg>\n')
