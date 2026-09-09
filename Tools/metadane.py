"""Czytanie metadanych sklepowych sióstr — jedno miejsce dla generatora stron.

**Strona ma pochodzić z tego samego pliku co sklep.** To jest cała racja bytu tego
modułu: gdyby generator dostawał tekst wpisany ręcznie, strona rozjechałaby się
z App Store przy pierwszej korekcie opisu — a opisy w sklepie są przejrzane
i zatwierdzone, więc strona mówiąca coś innego jest nową obietnicą, której nikt
nie sprawdził.

Dwa źródła, bo rodzina ma dwa formaty:

- dziewięć sióstr: `docs/app-store/APP_STORE_METADATA_{PL,EN}.md` — bloki ``` pod
  nagłówkami `## Nazwa`, dokładnie tak, jak czyta je `Tools/asc-metadata.py`
  każdej z nich (ten sam wyraz regularny, świadomie skopiowany co do znaku);
- Kaname: `docs/app-store/version-texts.json` — słownik wersji, bo Kaname trzyma
  teksty per wydanie i wozi je do ASC innym narzędziem.

**Nagłówki bywają po polsku.** `katsuyokei-ios` trzyma w pliku PL `## Nazwa`,
`## Podtytuł`, `## Opis` — i nie jest to usterka: jego własny `asc-metadata.py`
czyta te nazwy (`asc-metadata.py:407`). Stąd tablica aliasów zamiast założenia,
że nagłówek jest angielski.
"""

import json
import re
from pathlib import Path

# Nagłówek → pole kanoniczne. Klucz po lewej jest tym, co stoi w pliku; wariant
# polski dokłada Katsuyokei, wariant „What's New” pomijamy świadomie — strona
# produktowa mówi, czym aplikacja jest, a nie co zmieniło się w ostatnim wydaniu.
ALIASY = {
    "Name": "nazwa",
    "Nazwa": "nazwa",
    "Subtitle": "podtytul",
    "Podtytuł": "podtytul",
    "Promotional text": "promo",
    "Tekst promocyjny": "promo",
    "Description": "opis",
    "Opis": "opis",
    "Keywords": "tagi",
    "Słowa kluczowe": "tagi",
    "Support URL": "wsparcie",
    "Adres wsparcia": "wsparcie",
    "Privacy Policy URL": "prywatnosc",
    "Adres polityki prywatności": "prywatnosc",
}

WYMAGANE = ("nazwa", "podtytul", "promo", "opis", "tagi")

# **Rodzina ma dwa różne wzorce nagłówka i to nie jest szczegół.** Wzorzec
# z `kifuku/Tools/asc-metadata.py` (i z ośmiu innych kopii) brzmi
# `^## ([^\n(]+?)(?:\s*\(\d+\))?` — zjada nawias, ale **wyłącznie z samą
# liczbą**. Cztery pliki z osiemnastu piszą `## Keywords (100, przecinki bez
# spacji)` i na tym wzorcu **cała sekcja przepada bez błędu**: Kuzushi (pl i en),
# Bunmyaku (pl i en) oraz Katsuyokei (en). Zmierzone 08.09.2026 przy pisaniu tego
# modułu — pierwsze podejście czytało siedem plików z osiemnastu i milczało.
#
# Dlatego kotwiczymy na **znanej nazwie pola**, a nie na dowolnym nagłówku, i po
# nazwie puszczamy `[^\n]*` — wzorem `bunmyaku-ios/Tools/asc-metadata.py:152`,
# jedynej kopii w rodzinie, która to już naprawiła.
BLOK = re.compile(r"```\n(.*?)\n```", re.S)


def bloki(sciezka: Path) -> dict:
    """Bloki ``` przypisane do nagłówków `## Nazwa`, po nazwach kanonicznych."""
    tekst = sciezka.read_text(encoding="utf-8")
    out = {}
    for naglowek, pole in ALIASY.items():
        wzorzec = re.compile(r"^## " + re.escape(naglowek) + r"(?![\wąćęłńóśźż])[^\n]*\n(.*?)(?=^## |\Z)",
                             re.S | re.M | re.I)
        dopasowanie = wzorzec.search(tekst)
        if not dopasowanie:
            continue
        fenced = BLOK.search(dopasowanie.group(1))
        if fenced:
            out[pole] = fenced.group(1).strip()
    return out


def z_markdown(repo: Path, jezyk: str) -> dict:
    plik = repo / "docs" / "app-store" / f"APP_STORE_METADATA_{jezyk.upper()}.md"
    if not plik.exists():
        raise SystemExit(f"brak pliku metadanych: {plik}")
    dane = bloki(plik)
    brakuje = [p for p in WYMAGANE if p not in dane]
    if brakuje:
        raise SystemExit(f"{plik}: brak pól {', '.join(brakuje)}")
    dane["_zrodlo"] = str(plik)
    return dane


def teksty(repo: Path, wpis: dict, jezyk: str) -> dict:
    """Teksty sklepowe jednej aplikacji, niezależnie od tego, gdzie je trzyma.

    Dziewięć sióstr trzyma je w `APP_STORE_METADATA_{PL,EN}.md`, Kaname
    w `version-texts.json` per wersja. To rozgałęzienie **stoi tutaj jeden raz**,
    a nie w każdym narzędziu, które chce znać nazwę aplikacji — bo drugie takie
    rozgałęzienie rozjechałoby się z pierwszym w dniu, w którym któraś siostra
    zmieni źródło, i **żadna bramka by tego nie zobaczyła**: oba wyglądałyby na
    działające, tylko mówiłyby co innego.
    """
    if wpis["zrodlo"] == "kaname":
        return z_json(repo, jezyk, wpis["wersja"])
    return z_markdown(repo, jezyk)


def wersje_kaname(repo: Path) -> list:
    """Numery wersji z `version-texts.json`, od najnowszej."""
    dane = json.loads((repo / "docs" / "app-store" / "version-texts.json").read_text(encoding="utf-8"))
    numery = [k for k in dane if re.fullmatch(r"\d+\.\d+\.\d+", k)]
    return sorted(numery, key=lambda v: [int(x) for x in v.split(".")], reverse=True)


def z_json(repo: Path, jezyk: str, wersja: str) -> dict:
    """Teksty Kaname dla podanej wersji.

    **Pole `name` jest tylko przy najnowszych wersjach** — nazwa zmieniła się
    dopiero 08.09.2026 (dwukropek zamiast pauzy) i wcześniejsze wpisy jej nie
    niosą. Szukamy więc w dół po wersjach, zamiast wpisywać nazwę w manifest:
    manifest ma trzymać fakty o aplikacji, nie kopie tekstu.
    """
    plik = repo / "docs" / "app-store" / "version-texts.json"
    dane = json.loads(plik.read_text(encoding="utf-8"))
    if wersja not in dane:
        raise SystemExit(f"{plik}: brak wersji {wersja}")
    lokalizacja = {"pl": "pl", "en": "en-US"}[jezyk]

    def pole(nazwa, od_wersji=None):
        blok = dane[od_wersji or wersja].get(nazwa) or {}
        return (blok.get(lokalizacja) or "").strip()

    nazwa = pole("name")
    if not nazwa:
        for kandydat in wersje_kaname(repo):
            nazwa = pole("name", kandydat)
            if nazwa:
                break
    out = {
        "nazwa": nazwa,
        "podtytul": pole("subtitle"),
        "promo": pole("promotionalText"),
        "opis": pole("description"),
        "tagi": pole("keywords"),
        "_zrodlo": f"{plik} (wersja {wersja})",
    }
    brakuje = [p for p in WYMAGANE if not out[p]]
    if brakuje:
        raise SystemExit(f"{plik} {wersja} {lokalizacja}: brak pól {', '.join(brakuje)}")
    return out


def pierwsze_zdanie(opis: str) -> str:
    """Pierwsze zdanie opisu — zdanie, które w App Store widać bez rozwijania.

    Kropka dziesiętna i skrót nie kończą zdania; kropka po spacji i wielkiej
    literze kończy. Świadomie prosto: opisy rodziny zaczynają się jednym zdaniem
    twierdzącym, a nie wyliczeniem.
    """
    akapit = opis.strip().split("\n\n", 1)[0].strip()
    cieta = re.split(r"(?<=[.!?])\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ0-9「『])", akapit, maxsplit=1)
    return cieta[0].strip()


def zdania(opis: str) -> list:
    """Zdania pierwszego akapitu opisu, po kolei."""
    akapit = opis.strip().split("\n\n", 1)[0].strip()
    return [z.strip() for z in
            re.split(r"(?<=[.!?])\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ0-9「『])", akapit) if z.strip()]


def sekcje(opis: str) -> list:
    """Opis rozbity na sekcje: `(nagłówek, [akapity])`.

    Opisy rodziny mają stały kształt wypracowany przy dziesięciu kartach: akapit
    pisany wersalikami otwiera sekcję, reszta jest jej treścią. Pierwsza sekcja
    nie ma nagłówka — to zdania otwierające, przed pierwszym wersalikiem.
    """
    out, naglowek, biezaca = [], None, []
    for akapit in akapity(opis):
        litery = [z for z in akapit if z.isalpha()]
        czy_naglowek = (litery and all(z.isupper() for z in litery)
                        and len(akapit) < 80 and "\n" not in akapit)
        if czy_naglowek:
            out.append((naglowek, biezaca))
            naglowek, biezaca = akapit, []
        else:
            biezaca.append(akapit)
    out.append((naglowek, biezaca))
    return [(n, a) for n, a in out if a]


def akapity(opis: str) -> list:
    return [a.strip() for a in opis.strip().split("\n\n") if a.strip()]
