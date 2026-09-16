#!/usr/bin/env python3
"""Czy to, co Google zobaczy na żywo, da się zaindeksować.

    python3 Tools/indeks-witryny.py                 # cała witryna, sześć sprawdzeń
    python3 Tools/indeks-witryny.py --tylko glebokosc
    python3 Tools/indeks-witryny.py --prog-glebokosci 2
    python3 Tools/indeks-witryny.py --baza http://localhost:8000   # wytwór na podglądzie

**Po co to jest, skoro generator ma już jedenaście bramek.** Bo tamte sprawdzają
to, co same złożyły. [poz. 326] przeszła przez komplet zielonych bramek: 1013
odsyłaczy wewnętrznych celowało w `…/index.html`, zero miało postać katalogową,
i nic tego nie zauważyło przez cały czas, bo pytanie brzmiało „czy wytwór zgadza
się z zamiarem”, a nie „co dostanie robot”. Ta bramka nie otwiera repozytorium
w ogóle — pobiera `sitemap.xml` z sieci i chodzi po tym, co oddaje serwer.

To jest ta sama różnica, co §21.W: bramka sprawdza **skutek**, nie zamiar.

**Sześć sprawdzeń.** Pierwsze cztery pilnują higieny, którą dziś trzeba robić
ręcznie przed każdym wklejaniem listy do Search Console (`docs/SEARCH_CONSOLE.md`).
Piąte jest jedyną miarą, która odróżniła 44 strony niezaindeksowane od 74
zaindeksowanych (odczyt 16.09.2026) — objętość treści i podobieństwo do sióstr
**nie odróżniły ich wcale**, a liczba wejść odróżniła je pozornie — wszystko
trzy obalone, rachunek w docstringu `spr_glebokosc`. Szóste pilnuje samego rejestru wyjątków.

    mapa           każdy adres mapy: 200, zero przekierowań, canonical na siebie
    odsylacze      zero odsyłaczy wewnętrznych w postaci niekanonicznej
    mapa-vs-linki  mapa zawiera każdą podlinkowaną stronę indeksowalną i tylko takie
    hreflang       pary wzajemne, żadna nie prowadzi do strony z `noindex`
    glebokosc      ile kliknięć od korzenia dzieli robota od strony z mapy
    wyjatki        czy każdy zapisany wyjątek jeszcze się do czegoś odnosi

**Trzy kody wyjścia, bo „nie wiadomo” nie jest zgodą** (wzorzec z `parytet.py`):

    0  zielono
    1  ZNALAZŁEM — któreś sprawdzenie ma czerwień
    2  NIE SPRAWDZIŁEM — witryna nieosiągalna, mapa pusta albo brak rejestru

Kod 2 różni się od 0 celowo. Bramka, która nad nieosiągalną witryną świeci
zielono, mówi „sprawdzone” o czymś, czego nie otworzyła.

**Wyjątki siedzą w `Tools/indeks-wyjatki.json`, nie w tym pliku.** Wyjątek
w kodzie staje się cudzym założeniem i nie widać go w diffie; wyjątek w danych
widać. Każdy niesie powód i numer pozycji, a sprawdzenie `wyjatki` pilnuje, żeby
przeterminowany wyleciał — uzasadnienie starzeje się osobno od reguły.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlsplit

KORZEN = Path(__file__).resolve().parent.parent
REJESTR = Path(__file__).resolve().parent / "indeks-wyjatki.json"
BAZA = "https://jd-japanese.pl"
CZAS = 25
WATKI = 8

SPRAWDZENIA = ("mapa", "odsylacze", "mapa-vs-linki", "hreflang", "glebokosc", "wyjatki")

ZASOBY = re.compile(r"\.(webp|png|jpg|jpeg|gif|svg|css|js|ico|xml|txt|json|woff2?|pdf)$", re.I)


class Strona:
    """Jedna odpowiedź serwera, rozebrana na to, co decyduje o indeksowaniu."""

    def __init__(self, adres, kod, adres_koncowy, przekierowan, tresc):
        self.adres = adres
        self.kod = kod
        self.adres_koncowy = adres_koncowy
        self.przekierowan = przekierowan
        self.tresc = tresc or ""

    @property
    def kanonikal(self):
        m = re.search(r'<link[^>]*\brel="canonical"[^>]*\bhref="([^"]+)"', self.tresc)
        return m.group(1) if m else None

    @property
    def noindex(self):
        m = re.search(r'<meta[^>]*\bname="robots"[^>]*\bcontent="([^"]+)"', self.tresc, re.I)
        return bool(m and "noindex" in m.group(1).lower())

    @property
    def hreflangi(self):
        pary = re.findall(
            r'<link[^>]*\brel="alternate"[^>]*\bhreflang="([^"]+)"[^>]*\bhref="([^"]+)"',
            self.tresc)
        return {j: a for j, a in pary}

    def odsylacze(self, baza):
        """Adresy HTML, na które ta strona wskazuje — bez zasobów i obcych domen."""
        host = urlsplit(baza).netloc
        wynik = set()
        for cel in re.findall(r'<(?:a|link)\b[^>]*?\bhref="([^"]+)"', self.tresc):
            if cel.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            rozbity = urlsplit(urljoin(self.adres, cel))
            if rozbity.netloc != host or ZASOBY.search(rozbity.path):
                continue
            wynik.add(f"{baza}{rozbity.path}")
        return wynik


def pobierz(adres):
    """Jedno żądanie. Zwraca Stronę albo None, gdy sieć nie odpowiedziała."""
    zadanie = urllib.request.Request(adres, headers={"User-Agent": "indeks-witryny/1.0"})
    przekierowan = 0

    class Licznik(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **kw):
            nonlocal przekierowan
            przekierowan += 1
            return super().redirect_request(*a, **kw)

    try:
        with urllib.request.build_opener(Licznik).open(zadanie, timeout=CZAS) as odp:
            return Strona(adres, odp.status, odp.geturl(), przekierowan,
                          odp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return Strona(adres, e.code, adres, przekierowan, "")
    except Exception:
        return None


def pobierz_wiele(adresy):
    with ThreadPoolExecutor(max_workers=WATKI) as pula:
        return {a: s for a, s in zip(adresy, pula.map(pobierz, adresy))}


def wczytaj_rejestr():
    if not REJESTR.exists():
        return None
    with REJESTR.open(encoding="utf-8") as f:
        return json.load(f)


def pasuje(sciezka, wyjatki, rodzaj):
    """Czy ścieżka (bez bazy, bez wiodącego ukośnika) jest zapisanym wyjątkiem."""
    for w in wyjatki.get(rodzaj, []):
        if re.search(w["wzorzec"], sciezka):
            return w
    return None


# ---------------------------------------------------------------- sprawdzenia


def spr_mapa(strony, mapa, baza, wyjatki):
    """Adres w mapie witryny musi być tym, co Google ma zaindeksować — nie drogą do tego."""
    bledy = []
    for a in mapa:
        s = strony.get(a)
        if s is None:
            return None, f"{a}: sieć nie odpowiedziała"
        if s.kod != 200:
            bledy.append(f"{a}: kod {s.kod}, a mapa go obiecuje")
        if s.przekierowan:
            bledy.append(f"{a}: przekierowuje na {s.adres_koncowy} — zgłoszenie takiego "
                         f"adresu marnuje dzienny limit w Search Console")
        elif s.kanonikal is None:
            bledy.append(f"{a}: brak `canonical`")
        elif s.kanonikal != a:
            bledy.append(f"{a}: canonical wskazuje {s.kanonikal} — adres w mapie ma być "
                         f"kanoniczny, inaczej mapa prosi o zaindeksowanie duplikatu")
        elif s.noindex:
            bledy.append(f"{a}: `noindex`, a stoi w mapie — mapa i meta mówią co innego")
    return bledy, None


def spr_odsylacze(strony, mapa, baza, wyjatki):
    """Regresja [poz. 326]: odsyłacz w postaci plikowej robi Google drugi adres tej samej strony."""
    bledy = []
    for adres, s in sorted(strony.items()):
        if s is None or s.kod != 200:
            continue
        for cel in sorted(s.odsylacze(baza)):
            if cel.endswith("/index.html"):
                bledy.append(f"{adres} → {cel}: postać plikowa zamiast katalogowej "
                             f"(to jest dokładnie wada z [poz. 326])")
    return bledy, None


def spr_mapa_vs_linki(strony, mapa, baza, wyjatki):
    """Mapa ma nieść każdą podlinkowaną stronę indeksowalną — i żadnej innej."""
    bledy = []
    wmapie = set(mapa)
    for adres, s in sorted(strony.items()):
        if s is None or s.kod != 200 or adres in wmapie:
            continue
        sciezka = adres[len(baza):].lstrip("/")
        if s.noindex or (s.kanonikal and s.kanonikal != adres):
            continue  # sama się wyłącza z indeksu — nieobecność w mapie jest zgodna
        if pasuje(sciezka, wyjatki, "poza-mapa-swiadomie"):
            continue
        bledy.append(f"{adres}: podlinkowana, indeksowalna, a nie ma jej w mapie witryny")
    for a in mapa:
        s = strony.get(a)
        if s is None:
            continue
        if s.kanonikal and s.kanonikal != a:
            bledy.append(f"{a}: w mapie, a kanonikal oddaje ją {s.kanonikal}")
    return bledy, None


def spr_hreflang(strony, mapa, baza, wyjatki):
    """Para hreflang wskazująca stronę z `noindex` to polecenie sprzeczne."""
    bledy = []
    for adres, s in sorted(strony.items()):
        if s is None or s.kod != 200 or not s.hreflangi:
            continue
        for jezyk, cel in sorted(s.hreflangi.items()):
            if jezyk == "x-default":
                continue
            druga = strony.get(cel)
            if druga is None or druga.kod != 200:
                bledy.append(f"{adres}: hreflang={jezyk} prowadzi do {cel}, którego nie ma")
                continue
            if druga.noindex:
                bledy.append(f"{adres}: hreflang={jezyk} prowadzi do {cel} z `noindex` "
                             f"— to polecenie sprzeczne")
            if adres not in druga.hreflangi.values():
                bledy.append(f"{adres}: hreflang={jezyk} → {cel}, ale {cel} nie odwzajemnia")
    return bledy, None


def glebokosci(strony, baza):
    """Ile kliknięć od korzenia. Wejściem są obie strony główne, jak u robota."""
    start = [f"{baza}/", f"{baza}/en/"]
    poziom = {a: 0 for a in start if a in strony}
    fala = list(poziom)
    while fala:
        nastepna = []
        for adres in fala:
            s = strony.get(adres)
            if s is None or s.kod != 200:
                continue
            for cel in s.odsylacze(baza):
                if cel not in poziom:
                    poziom[cel] = poziom[adres] + 1
                    nastepna.append(cel)
        fala = nastepna
    return poziom


def spr_glebokosc(strony, mapa, baza, wyjatki, prog=1):
    """Ile kliknięć od korzenia — jedyna miara, która przeżyła kontrpróbę.

    Pomiar 16.09.2026 przeciw temu, co zgłosił Google. Strony tematów i strony grup
    **powstały tego samego dnia, 13.09, w tych samych commitach** (`93b1f30`,
    `ade114b`, `886e9ed`) — wiek jest więc trzymany na stałe:

        powstałe 13.09, 1 kliknięcie od korzenia   18 stron   w indeksie
        powstałe 13.09, 2 kliknięcia od korzenia   44 strony  POZA indeksem

    Zgłoszonych przez Google jest 44 i stron na głębokości 2 jest 44 — co do sztuki.

    **Co zostało obalone po drodze**, żeby nikt nie wracał tą drogą:

        objętość treści     mediana 5988 znaków wobec 5849 — bez różnicy
        podobieństwo sióstr 3–8% przy tle 1,4%, a najwyższe miały ZAINDEKSOWANE
        liczba wejść        mediana 4 po obu stronach — nie odróżnia niczego

    Liczba wejść wyglądała na miarę (zgłoszone miały medianę 4, reszta mapy 12),
    dopóki nie zawęziło się porównania do właściwej klasy: **wśród samych stron
    na głębokości 2** rozkłady są identyczne. Tamta różnica była różnicą między
    piętrami, nie między zaindeksowanymi a nie. Bramka mierzy piętro.

    Próg 1 znaczy: **każda strona z mapy ma być linkowana wprost z korzenia**.
    Rozdroże ani spis treści tego nie załatwią — same leżą na głębokości 1, więc
    to, co linkują, ląduje na 2.
    """
    bledy = []
    poziom = glebokosci(strony, baza)
    for a in mapa:
        g = poziom.get(a)
        if g is None:
            bledy.append(f"{a}: w mapie, a nie prowadzi do niej żaden odsyłacz z korzenia "
                         f"— sierota, do której Google dojdzie wyłącznie z mapy")
        elif g > prog:
            bledy.append(f"{a}: {g} kliknięcia od korzenia (próg {prog}) — tyle miały "
                         f"wszystkie 44 strony, których Google nie zaindeksował")
    return bledy, None


def spr_wyjatki(strony, mapa, baza, wyjatki):
    """Wyjątek, który przestał się do czegokolwiek odnosić, jest nieprawdziwym powodem."""
    bledy = []
    sciezki = [a[len(baza):].lstrip("/") for a, s in strony.items() if s and s.kod == 200]
    for rodzaj, lista in wyjatki.items():
        if rodzaj.startswith("_"):
            continue
        for w in lista:
            if not any(re.search(w["wzorzec"], s) for s in sciezki):
                bledy.append(f"wyjątek `{w['wzorzec']}` ({rodzaj}) nie pasuje już do żadnej "
                             f"strony — powód: {w.get('powod', '?')}. Zdejmij go z rejestru")
    return bledy, None


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--baza", default=BAZA, help=f"domyślnie {BAZA}")
    p.add_argument("--prog-glebokosci", type=int, default=1,
                   help="ile kliknięć od korzenia wolno mieć stronie z mapy (domyślnie 1)")
    p.add_argument("--tylko", choices=SPRAWDZENIA, action="append",
                   help="ogranicz do wybranych sprawdzeń (można powtórzyć)")
    args = p.parse_args()
    baza = args.baza.rstrip("/")

    wyjatki = wczytaj_rejestr()
    if wyjatki is None:
        print(f"NIE SPRAWDZIŁEM: brak rejestru wyjątków {REJESTR}", file=sys.stderr)
        return 2

    mapa_odp = pobierz(f"{baza}/sitemap.xml")
    if mapa_odp is None or mapa_odp.kod != 200:
        print(f"NIE SPRAWDZIŁEM: {baza}/sitemap.xml nieosiągalna", file=sys.stderr)
        return 2
    mapa = re.findall(r"<loc>([^<]+)</loc>", mapa_odp.tresc)
    if not mapa:
        print("NIE SPRAWDZIŁEM: mapa witryny nie ma ani jednego adresu", file=sys.stderr)
        return 2

    print(f"mapa witryny: {len(mapa)} adresów — pobieram i chodzę po odsyłaczach…")
    strony = pobierz_wiele(mapa)
    if any(s is None for s in strony.values()):
        ile = sum(1 for s in strony.values() if s is None)
        print(f"NIE SPRAWDZIŁEM: {ile} adresów nie odpowiedziało", file=sys.stderr)
        return 2

    # Drugi krąg: wszystko, na co mapa wskazuje, a czego w mapie nie ma.
    do_pobrania = set()
    for s in strony.values():
        do_pobrania |= s.odsylacze(baza)
    do_pobrania -= set(strony)
    if do_pobrania:
        strony.update(pobierz_wiele(sorted(do_pobrania)))
    strony = {a: s for a, s in strony.items() if s is not None}
    print(f"stron pobranych łącznie: {len(strony)}\n")

    wybrane = args.tylko or list(SPRAWDZENIA)
    funkcje = {
        "mapa": spr_mapa,
        "odsylacze": spr_odsylacze,
        "mapa-vs-linki": spr_mapa_vs_linki,
        "hreflang": spr_hreflang,
        "glebokosc": lambda *a: spr_glebokosc(*a, prog=args.prog_glebokosci),
        "wyjatki": spr_wyjatki,
    }

    czerwien = False
    for nazwa in SPRAWDZENIA:
        if nazwa not in wybrane:
            continue
        bledy, niepewne = funkcje[nazwa](strony, mapa, baza, wyjatki)
        if niepewne:
            print(f"NIE SPRAWDZIŁEM ({nazwa}): {niepewne}", file=sys.stderr)
            return 2
        if bledy:
            czerwien = True
            print(f"✗ {nazwa} — {len(bledy)}")
            for b in bledy[:25]:
                print(f"    {b}")
            if len(bledy) > 25:
                print(f"    … i jeszcze {len(bledy) - 25}")
        else:
            print(f"✓ {nazwa}")

    return 1 if czerwien else 0


if __name__ == "__main__":
    sys.exit(main())
