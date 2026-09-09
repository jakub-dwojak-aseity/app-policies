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
- **brak ikony witryny** — dokumenty prawne nie idą przez generator, więc `<link rel="icon">`
  nie dostają skądinąd i ich karta w przeglądarce stoi pusta;
- **dokument w manifeście, którego nie ma na dysku** — błąd, bo to znaczy, że strona
  linkuje w pustkę.

Kod wyjścia: 0, gdy wszystko przeszło; 1, gdy któryś plik został odrzucony albo
(w `--sprawdz`) gdy którykolwiek dokument nie ma jeszcze kompletnej głowy.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metadane  # noqa: E402
from napisy import NAPISY  # noqa: E402

KORZEN = Path(__file__).resolve().parent.parent
ZRODLA = Path("/Users/jakub/aseity")
PLIKI_DOKUMENTU = ("privacy.html", "terms.html", "support.html")
CANONICAL = '<link rel="canonical" href="{adres}">'
NOINDEX = '<meta name="robots" content="noindex, follow">'
# Ikona witryny — adresem bezwzględnym, nie względnym. Dokumenty leżą na czterech
# różnych głębokościach (`kuzushi/`, `kaname/1.2/`, `kaname/1.2/en/`, …), a wyliczanie
# `../..` dla każdej z nich to trzy okazje do pomyłki w plikach, których nikt nie
# generuje. `canonical` obok i tak jest bezwzględny.
IKONY = ('<link rel="icon" type="image/png" sizes="48x48" href="{baza}/assets/znak-48.png">',
         '<link rel="apple-touch-icon" href="{baza}/assets/znak-180.png">')
OPIS = '<meta name="description" content="{tresc}">'
OG = ('<meta property="og:title" content="{tytul}">',
      '<meta property="og:description" content="{tresc}">',
      '<meta property="og:url" content="{adres}">',
      '<meta property="og:type" content="article">',
      '<meta property="og:image" content="{obrazek}">',
      '<meta name="twitter:card" content="summary_large_image">')
# Wyjście z dokumentu prawnego na witrynę. Etykietami są **nazwa aplikacji ze sklepu**
# i nazwa witryny z `napisy.py` — obie już istnieją, więc ta stopka nie dokłada ani
# jednego własnego zdania.
WYJSCIE = ('<br><a href="{apka}">{nazwa}</a> · <a href="{mapa}">{witryna}</a>')


def manifest() -> dict:
    return json.loads((KORZEN / "Tools" / "apps.json").read_text(encoding="utf-8"))


def biezace(m: dict) -> set[str]:
    """Ścieżki dokumentów, na które wskazuje dziś którakolwiek aplikacja."""
    wynik = set()
    for a in list(m["aplikacje"]) + list(m.get("pozostale", [])):
        for katalog in a["dokumenty"].values():
            wynik |= {f"{katalog}/{plik}" for plik in PLIKI_DOKUMENTU}
    return wynik


def kontekst(m: dict) -> dict:
    """Dla każdego dokumentu: do której aplikacji należy i w jakim jest języku.

    Dokumenty **bieżące** rozpoznaje manifest — on wprost mówi, który katalog jest
    czyj i w jakim języku. Dokumenty **przestarzałe** (nieuwersjonowane kopie Kaname
    i Bunmyaku) w manifeście nie stoją, więc aplikację bierzemy z pierwszego członu
    ścieżki, a język z `<html lang>` **samego pliku** — bo to jedyne miejsce, które
    o nim nie kłamie. Zgadywanie języka ze ścieżki wywróciłoby się na Kuzushim, gdzie
    angielski leży w korzeniu, a polski w podkatalogu `pl/`.

    Aplikacje spoza rodziny (`pozostale`, dziś SpoolCalc) **nie dostają wyjścia na
    witrynę** i to jest celowe: kalkulator pojemności szpuli nie ma czego szukać
    w mapie aplikacji do japońskiego.
    """
    rodzina = {a["slug"] for a in m["aplikacje"]}
    nazwy, wynik = {}, {}
    for a in m["aplikacje"]:
        repo = ZRODLA / a["repo"]
        nazwy[a["slug"]] = {j: metadane.teksty(repo, a, j)["nazwa"] for j in ("pl", "en")}
        for jezyk, katalog in a["dokumenty"].items():
            for plik in PLIKI_DOKUMENTU:
                wynik[f"{katalog}/{plik}"] = (a["slug"], jezyk)

    for wzgledna in dokumenty_na_dysku():
        if wzgledna in wynik:
            continue
        slug = wzgledna.split("/")[0]
        if slug not in rodzina:
            continue
        tresc = (KORZEN / wzgledna).read_text(encoding="utf-8")
        dopasowanie = re.search(r'<html lang="([a-z-]+)"', tresc)
        jezyk = "en" if dopasowanie and dopasowanie.group(1).startswith("en") else "pl"
        wynik[wzgledna] = (slug, jezyk)

    return {"apka": wynik, "nazwy": nazwy}


def opis_dokumentu(tresc: str) -> str:
    """Zajawka dokumentu — jego **własne pierwsze zdanie**, nie zdanie napisane od nowa.

    Bierze pierwszy akapit po `<h1>`, pomijając wiersz `class="updated"` z wersją
    i datą: on jest metryczką, a nie treścią, i jako zajawka w wynikach wyszukiwania
    nie mówi nic. Limit 155 znaków — tyle, ile pokazuje wyszukiwarka — a cięcie idzie
    po granicy zdania, potem po granicy słowa, żeby nie urwać w połowie myśli.
    """
    # **Akapit spod sekcji bierzemy razem z jej nagłówkiem.** Polityka Kuzushiego
    # nie ma wstępu i zaczyna się od „Nie ma go." — zdania prawdziwego i całkiem
    # niezrozumiałego bez „Twoje konto" nad nim. Samo przycięcie do wstępu gubiło
    # z kolei dobre zdania z warunków, które otwierają się nagłówkiem od razu
    # („Joshi is an educational app for practicing Japanese particles."). Nagłówek
    # jako przedrostek rozwiązuje oba przypadki i **nie dokłada ani jednego słowa
    # spoza dokumentu**.
    po_naglowku = tresc.split("</h1>", 1)[-1]
    wstep = po_naglowku.split("<h2", 1)[0]
    if (zajawka := _zajawka(wstep)):
        return zajawka

    sekcja = re.search(r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|\Z)", po_naglowku, re.S)
    if sekcja:
        naglowek = " ".join(re.sub(r"<[^>]+>", "", sekcja.group(1)).split())
        tresc_sekcji = _zajawka(sekcja.group(2), limit=155 - len(naglowek) - 2)
        if tresc_sekcji:
            return f"{naglowek}: {tresc_sekcji}"

    ramka = re.search(r'<div class="note">.*?</div>', po_naglowku, re.S)
    return _zajawka(ramka.group(0)) if ramka else ""


def _zajawka(obszar: str, limit: int = 155) -> str:
    """Pierwszy sensowny akapit obszaru, przycięty do limitu znaków."""
    for dopasowanie in re.finditer(r"<p[^>]*>.*?</p>", obszar, re.S):
        # Klasy szukamy w **całym znaczniku**, nie w jego zawartości: `class="updated"`
        # stoi w otwarciu `<p>`, więc sprawdzanie samego wnętrza nie łapie nigdy
        # i metryczka „wersja 1.0 · ostatnia aktualizacja…" wchodzi jako zajawka.
        # Złapane na wytworze 09.09.2026, nie na zamiarze.
        akapit = dopasowanie.group(0)
        if 'class="updated"' in akapit:
            continue
        goly = re.sub(r"<[^>]+>", "", akapit)
        goly = html.unescape(" ".join(goly.split()))
        if not goly:
            continue
        if len(goly) <= limit:
            return goly
        zdania = re.split(r"(?<=[.!?])\s+", goly)
        zebrane = ""
        for zdanie in zdania:
            if len(f"{zebrane} {zdanie}".strip()) > limit:
                break
            zebrane = f"{zebrane} {zdanie}".strip()
        if zebrane:
            return zebrane
        return goly[:limit - 3].rsplit(" ", 1)[0].rstrip(" ,;–-") + "…"
    return ""


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


def dopisz_do_stopki(tresc: str, wyjscie: str) -> str:
    """Dokłada wyjście na witrynę **wewnątrz istniejącej** stopki, na jej końcu.

    Stopki tych dokumentów mają kilkanaście różnych kształtów — kontakt, rodzeństwo
    w tym samym katalogu, wersja językowa, w różnych układach i kolejnościach.
    Przepisanie ich na jeden wzór znaczyłoby **skasowanie cudzej treści w pliku
    prawnym**, więc tego nie robimy: dopisujemy jedną linię przed `</footer>`
    i zostawiamy resztę bajt w bajt.

    Odmawia, gdy stopki nie ma albo jest więcej niż jedna — wtedy nie wiadomo,
    która jest ta właściwa, a zgadywanie w dokumencie prawnym jest gorsze niż brak.
    """
    ile = tresc.count("</footer>")
    if ile != 1:
        raise ValueError(f"znaczników </footer>: {ile}, oczekiwano jednego")
    return tresc.replace("</footer>", wyjscie + "</footer>", 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sprawdz", action="store_true",
                        help="nic nie zapisuje; kod 1, gdy czegoś brakuje")
    args = parser.parse_args()

    m = manifest()
    baza = m["bazaAdresu"].rstrip("/")
    aktualne = biezace(m)
    ctx = kontekst(m)
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
        ma_ikone = 'rel="icon"' in tresc
        ma_opis = 'name="description"' in tresc
        ma_og = 'property="og:' in tresc
        ma_wyjscie = f"{baza}/apps/" in tresc or f"{baza}/en/apps/" in tresc

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
        if not ma_ikone:
            potrzebne.extend(wzor.format(baza=baza) for wzor in IKONY)

        wpis = ctx["apka"].get(wzgledna)
        zajawka = opis_dokumentu(tresc) if not (ma_opis and ma_og) else ""
        if not ma_opis and zajawka:
            potrzebne.append(OPIS.format(tresc=html.escape(zajawka, quote=True)))
        if not ma_og and zajawka and wpis:
            slug, jezyk = wpis
            tytul = re.search(r"<title>(.*?)</title>", tresc, re.S)
            potrzebne.extend(wzor.format(
                tytul=html.escape(tytul.group(1).strip() if tytul else "", quote=True),
                tresc=html.escape(zajawka, quote=True),
                adres=adres,
                obrazek=f"{baza}/assets/karty/{slug}-{jezyk}.png") for wzor in OG)

        # Wyjście na witrynę. Do 09.09.2026 dokument prawny był ślepym zaułkiem:
        # zero nawigacji, zero linku do aplikacji, zero linku do mapy rodziny —
        # a wchodzi tam człowiek z App Store, czyli ktoś, kto już kupił jedną apkę
        # i nie ma jak zobaczyć pozostałych dziewięciu.
        wyjscie = ""
        if not ma_wyjscie and wpis:
            slug, jezyk = wpis
            przedrostek = "" if jezyk == "pl" else "en/"
            wyjscie = WYJSCIE.format(
                apka=f"{baza}/{przedrostek}apps/{slug}/",
                nazwa=html.escape(ctx["nazwy"][slug][jezyk]),
                mapa=f"{baza}/{przedrostek}",
                witryna=html.escape(NAPISY[jezyk]["tytul_mapy"]))

        if not potrzebne and not wyjscie:
            pominiete += 1
            continue

        if args.sprawdz:
            zmienione.append(wzgledna)
            continue
        try:
            nowa = wstaw(tresc, potrzebne) if potrzebne else tresc
            if wyjscie:
                nowa = dopisz_do_stopki(nowa, wyjscie)
        except ValueError as blad:
            bledy.append(f"{wzgledna}: {blad}")
            continue
        plik.write_text(nowa, encoding="utf-8")
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
