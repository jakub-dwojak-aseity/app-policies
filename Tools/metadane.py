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
import subprocess
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


def czytaj(repo: Path, wzgledna: str, ref: str | None = None) -> str:
    """Treść pliku z NAZWANEGO STANU, a nie z tego, co akurat jest wymeldowane.

    Bez `ref` czyta drzewo robocze — i to jest zachowanie, które 16.09.2026 cofnęło
    treść sklepową na żywo: na Macu wymeldowana jest gałąź wydaniowa, na maszynie
    windowsowej `main`, więc to samo polecenie brało inne źródło i nikt tego nie
    widział, bo wynik wyglądał poprawnie w obu przypadkach.

    Z `ref` (znacznik `sklep/<wersja>`) źródło przestaje zależeć od maszyny.
    Brak stanu jest AWARIĄ, nie cichym powrotem do dysku: milczący odwrót
    przywróciłby dokładnie tę wadę, tylko rzadziej i trudniej do złapania.
    """
    if ref is None:
        sciezka = repo / wzgledna
        if not sciezka.exists():
            raise SystemExit(f"brak pliku metadanych: {sciezka}")
        return sciezka.read_text(encoding="utf-8")
    wynik = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{wzgledna}"],
                           capture_output=True, text=True)
    if wynik.returncode != 0:
        raise SystemExit("%s: nie ma %s na stanie %s — %s"
                         % (repo.name, wzgledna, ref, (wynik.stderr or "").strip()))
    return wynik.stdout


def bloki_z_tekstu(tekst: str) -> dict:
    """Bloki ``` przypisane do nagłówków `## Nazwa`, po nazwach kanonicznych."""
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


def bloki(sciezka: Path) -> dict:
    """Zgodność wsteczna: te same bloki, czytane wprost z dysku."""
    return bloki_z_tekstu(sciezka.read_text(encoding="utf-8"))


def z_markdown(repo: Path, jezyk: str, ref: str | None = None) -> dict:
    wzgledna = f"docs/app-store/APP_STORE_METADATA_{jezyk.upper()}.md"
    plik = repo / wzgledna
    dane = bloki_z_tekstu(czytaj(repo, wzgledna, ref))
    brakuje = [p for p in WYMAGANE if p not in dane]
    if brakuje:
        raise SystemExit(f"{plik}: brak pól {', '.join(brakuje)}")
    dane["_zrodlo"] = str(plik) + (f" ({ref})" if ref else "")
    return dane


ZAPOWIEDZ = ("nazwa", "podtytul")


def zapowiedz(repo: Path, jezyk: str) -> dict:
    """Nazwa i podtytuł aplikacji, której jeszcze nie ma — z tego samego pliku.

    **Osobna funkcja, a nie flaga w `teksty()`, i to jest decyzja.** Aplikacja
    zapowiedziana nie ma promo, opisu ani tagów, bo nie ma produktu, który dałoby
    się opisać — a `WYMAGANE` przerywa przebieg przy ich braku i **ma przerywać**:
    strona produktowa bez opisu byłaby pustą obietnicą. Poluzowanie tamtej stałej
    zdjęłoby tę bramkę **wszystkim dziesięciu** aplikacjom naraz, żeby obsłużyć
    sześć, które produktowych stron w ogóle nie dostają.

    Plik jest ten sam co u sióstr, więc gdy aplikacja wejdzie w budowę, dorastają
    w nim kolejne sekcje i wpis przenosi się z `zapowiedziane` do `aplikacje`
    w manifeście — bez przepisywania czegokolwiek.
    """
    plik = repo / "docs" / "app-store" / f"APP_STORE_METADATA_{jezyk.upper()}.md"
    if not plik.exists():
        raise SystemExit(f"brak pliku metadanych: {plik}")
    dane = bloki(plik)
    brakuje = [p for p in ZAPOWIEDZ if not dane.get(p)]
    if brakuje:
        raise SystemExit(f"{plik}: brak pól {', '.join(brakuje)} — "
                         f"zapowiedź potrzebuje nazwy i podtytułu")
    return {p: dane[p] for p in ZAPOWIEDZ} | {"_zrodlo": str(plik)}


def teksty(repo: Path, wpis: dict, jezyk: str, ref: str | None = None) -> dict:
    """Teksty sklepowe jednej aplikacji, niezależnie od tego, gdzie je trzyma.

    Dziewięć sióstr trzyma je w `APP_STORE_METADATA_{PL,EN}.md`, Kaname
    w `version-texts.json` per wersja. To rozgałęzienie **stoi tutaj jeden raz**,
    a nie w każdym narzędziu, które chce znać nazwę aplikacji — bo drugie takie
    rozgałęzienie rozjechałoby się z pierwszym w dniu, w którym któraś siostra
    zmieni źródło, i **żadna bramka by tego nie zobaczyła**: oba wyglądałyby na
    działające, tylko mówiłyby co innego.
    """
    if wpis["zrodlo"] == "kaname":
        return z_json(repo, jezyk, wpis["wersja"], ref)
    return z_markdown(repo, jezyk, ref)


def wersje_kaname(repo: Path, ref: str | None = None) -> list:
    """Numery wersji z `version-texts.json`, od najnowszej."""
    dane = json.loads(czytaj(repo, "docs/app-store/version-texts.json", ref))
    numery = [k for k in dane if re.fullmatch(r"\d+\.\d+\.\d+", k)]
    return sorted(numery, key=lambda v: [int(x) for x in v.split(".")], reverse=True)


def z_json(repo: Path, jezyk: str, wersja: str, ref: str | None = None) -> dict:
    """Teksty Kaname dla podanej wersji.

    **Pole `name` jest tylko przy najnowszych wersjach** — nazwa zmieniła się
    dopiero 08.09.2026 (dwukropek zamiast pauzy) i wcześniejsze wpisy jej nie
    niosą. Szukamy więc w dół po wersjach, zamiast wpisywać nazwę w manifest:
    manifest ma trzymać fakty o aplikacji, nie kopie tekstu.
    """
    plik = repo / "docs" / "app-store" / "version-texts.json"
    dane = json.loads(czytaj(repo, "docs/app-store/version-texts.json", ref))
    if wersja not in dane:
        raise SystemExit(f"{plik}: brak wersji {wersja}")
    lokalizacja = {"pl": "pl", "en": "en-US"}[jezyk]

    def pole(nazwa, od_wersji=None):
        blok = dane[od_wersji or wersja].get(nazwa) or {}
        return (blok.get(lokalizacja) or "").strip()

    # **Wpis wersji niesie TYLKO to, co się w niej zmieniło** — i tak samo działa
    # App Store: tekst raz ustawiony stoi, dopóki ktoś go nie nadpisze. Wydanie
    # poprawkowe ma więc często sam `whatsNew`, a reszta pól jest pusta.
    #
    # Pierwsza wersja tej funkcji schodziła w dół tylko po `name` i wyglądała na
    # działającą, bo manifest wskazywał akurat wersję z kompletem pól (1.3.2).
    # Gdy 16.09.2026 wskazał wersję STOJĄCĄ W SKLEPIE (1.3.5, poprawkową),
    # generator padł na „brak pól podtytul, promo, opis, tagi". Wada była w
    # odczycie, nie w danych: pusto znaczy tu „bez zmian", a nie „nie ma".
    starsze = [k for k in wersje_kaname(repo, ref)
               if [int(x) for x in k.split(".")] < [int(x) for x in wersja.split(".")]]

    def pole_z_historia(nazwa):
        wartosc = pole(nazwa)
        for kandydat in starsze:
            if wartosc:
                break
            wartosc = pole(nazwa, kandydat)
        return wartosc

    out = {
        "nazwa": pole_z_historia("name"),
        "podtytul": pole_z_historia("subtitle"),
        "promo": pole_z_historia("promotionalText"),
        "opis": pole_z_historia("description"),
        "tagi": pole_z_historia("keywords"),
        "_zrodlo": f"{plik} (wersja {wersja}{', ' + ref if ref else ''})",
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
