#!/usr/bin/env python3
"""Generator stron produktowych rodziny — mapa rodziny i dziesięć podstron.

    python3 Tools/generuj-strony.py                # zapisuje strony
    python3 Tools/generuj-strony.py --sprawdz      # nic nie zapisuje, tylko bramki
    python3 Tools/generuj-strony.py --powtarzalnie # generuje dwa razy i porównuje bajt w bajt
    python3 Tools/generuj-strony.py --sprawdz-sklep  # porównuje manifest z App Store (sieć)

**Dlaczego generator, a nie jedenaście plików.** Jedyna istniejąca strona produktowa
(`kuzushi/index.html`, pisana ręcznie) mówiła „sixth of six" przy dziesięciu
aplikacjach i nie linkowała do App Store. README tego repozytorium opisywał siedem
aplikacji przy dzisiejszych dziesięciu. Tekst pisany ręcznie starzeje się dokładnie
tak — a tekst wyliczony z metadanych sklepowych starzeje się razem ze sklepem.

**Treść pochodzi wyłącznie z `docs/app-store/` aplikacji.** Opisy w App Store są
przejrzane i zatwierdzone; strona, która mówi coś innego, jest nową obietnicą,
której nikt nie sprawdził. Generator nie pisze zdań o aplikacjach — przepisuje je.
Jedyny tekst własny to nawigacja (nagłówki sekcji, etykiety linków), zebrany
w `NAPISY` i policzalny w jednym miejscu.

**Czego generator świadomie nie robi:**

- **nie pokazuje słów kluczowych.** Są polem sklepowym, a na stronie byłyby listą
  słów bez zdania — czyli dokładnie tym, za co wyszukiwarki karzą;
- **nie podaje cen zakupów liczbą.** Cena zależy od sklepu krajowego, więc jedna
  liczba na stronie jest fałszywa dla większości czytelników. Model płatności stoi
  w opisie każdej aplikacji, przepisany razem z resztą;
- **nie dotyka dokumentów prawnych.** Do nich tylko linkuje — i sprawdza, że plik
  istnieje.
"""

import argparse
import base64
import hashlib
import html
import json
import os
import re
import subprocess
import unicodedata
import sys
import urllib.parse
import urllib.request
from pathlib import Path

KORZEN = Path(__file__).resolve().parent.parent
NARZEDZIA = KORZEN / "Tools"
sys.path.insert(0, str(NARZEDZIA))
import glowy_dokumentow  # noqa: E402
import metadane  # noqa: E402

#: Korzeń drzew rodziny. **Na Macu rozwija się dokładnie w to, co stało tu wpisane
#: na sztywno** (`/Users/jakub/aseity`), więc zmiana jest bezobjawowa po tamtej stronie.
#:
#: Powód: od 16.09.2026 papiery rodziny są edytowane z dwóch maszyn (§5
#: `jp-grammar/docs/ANDROID_KIERUNEK.md`), a absolut macowy czyni ten generator
#: **nieuruchamialnym** na drugiej — zatrzymywał się na pierwszej aplikacji
#: komunikatem „brak drzewa \\Users\\jakub\\aseity\\...". To samo rozwiązanie stoi
#: już w `japanese-tools/lib/rodzina.py`, które liczy korzeń jako `Path.home()/"aseity"`.
ZRODLA = Path(os.environ.get("ASEITY_ROOT") or Path.home() / "aseity")
JEZYKI = ("pl", "en")

#: Adres, pod który idzie kanał zwrotny z „Co dalej" ([poz. 295]).
#:
#: `support@` istnieje od 09.09.2026 w catch-allu na własnej domenie i jest **ogólny,
#: nieprzypisany do żadnej aplikacji** ([poz. 84]) — w odróżnieniu od `kaname@`, `joshi@`
#: i reszty, które odbierają zgłoszenia z konkretnej apki. [poz. 295] zostawia otwarte,
#: czy zamiast niego założyć własny `pomysly@`: liczyłby się trywialnie, ale mnożyłby
#: skrzynki. Decyzja Jakuba, zmiana jednej stałej.
ADRES_ZWROTNY = "support@jd-japanese.pl"

#: Temat maila per oś pytania. **Osobny dla każdej**, żeby filtr w skrzynce liczył bez
#: czytania treści — to jest jedyny licznik, jaki ta witryna ma mieć ([poz. 295]:
#: „kanał TAK, publiczny licznik NIE").
TEMATY_MAILA = {
    "pl": {"android": "Co dalej: Android",
           "jezyki": "Co dalej: języki",
           "szostka": "Co dalej: zapowiedziane",
           "otwarte": "Co dalej: czego brakuje"},
    "en": {"android": "What is next: Android",
           "jezyki": "What is next: languages",
           "szostka": "What is next: announced apps",
           "otwarte": "What is next: what is missing"},
}

from napisy import NAPISY  # noqa: E402

STYL = """\
:root { color-scheme: light dark; --tlo:#fff; --tekst:#1c1c1e; --cichy:#6b6b70;
        --linia:#e3e3e6; --akcent:#a34f5a; --karta:#faf9f9; }
@media (prefers-color-scheme: dark) {
  :root { --tlo:#131315; --tekst:#ececef; --cichy:#9a9aa0; --linia:#2c2c30;
          --akcent:#e08a94; --karta:#1b1b1e; }
}
* { box-sizing: border-box; }
body { max-width: 46rem; margin: 0 auto; padding: 2.5rem 1.25rem 4rem;
       font: 1rem/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       color: var(--tekst); background: var(--tlo); }
h1 { font-size: 1.8rem; line-height: 1.25; margin: 0 0 .35rem; }
h2 { font-size: 1.15rem; margin: 2.5rem 0 .75rem; }
h3 { font-size: 1rem; margin: 1.75rem 0 .4rem; letter-spacing: .01em; }
p { margin: .75rem 0; }
a { color: var(--akcent); }
.podtytul { color: var(--cichy); margin: 0 0 1rem; font-size: 1.05rem; }
.lead { border-left: 3px solid var(--akcent); padding: .1rem 0 .1rem 1rem;
        margin: 1.5rem 0; color: var(--tekst); }
.gora { display: flex; justify-content: space-between; gap: 1rem; font-size: .9rem;
        margin-bottom: 2rem; color: var(--cichy); }
.gora a { text-decoration: none; }
.do-tresci { position: absolute; left: -9999px; }
.do-tresci:focus { position: static; display: inline-block; margin-bottom: 1rem; }
:focus-visible { outline: 2px solid var(--akcent); outline-offset: 2px; border-radius: 4px; }
footer { overflow-wrap: anywhere; }
.gora .znak { display: inline-block; margin-right: .6rem; vertical-align: -.35rem; }
.gora .znak img { width: 22px; height: 22px; border-radius: 6px; display: block; }
.szyld { display: flex; gap: 1rem; align-items: center; margin-bottom: .5rem; }
.szyld img { width: 72px; height: 72px; border-radius: 16px; flex: none; }
.jp { color: var(--cichy); font-weight: 400; font-size: .75em; margin-left: .4em; }
.karty { display: grid; gap: .5rem; padding: 0; list-style: none; }
.karta { display: flex; gap: .9rem; align-items: flex-start; padding: .85rem;
         border: 1px solid var(--linia); border-radius: 12px; background: var(--karta); }
.karta img { width: 52px; height: 52px; border-radius: 12px; flex: none; }
.karta { position: relative; }
.karta .nazwa { font-weight: 600; }
/* Cała karta jest celem dotknięcia, ale linkiem pozostaje sama nazwa: warstwa
   rozciągnięta na kafelek daje duży cel, a czytnik ekranu dalej słyszy „Kaname:
   Gramatyka japońska", a nie cały akapit o problemie.
   **Tylko tam, gdzie nazwa jest linkiem.** Karta aplikacji zapowiedzianej ma nazwę
   w `<span>`, a selektor `.karta .nazwa` łapał i ją — więc kafelek bez dokąd pójścia
   dostawał niewidzialny cel dotknięcia na całej powierzchni, identyczny z tym
   w dziesięciu kartach nad nim. Zmierzone okiem 13.09.2026 na telefonie: ten sam
   kształt, ten sam rozmiar celu, jedna reaguje, druga nie. §15 konwencji mówi o tym
   wprost: co wygląda na dotykalne, musi być dotykalne. */
a.nazwa::after { content: ""; position: absolute; inset: 0; border-radius: 12px; }
.karta .co { display: block; color: var(--cichy); font-size: .9em; margin-top: .1rem; }
.karta p { margin: .35rem 0 0; color: var(--cichy); font-size: .93rem; }
.znacznik { display: inline-block; font-size: .75rem; padding: .1rem .45rem;
            border: 1px solid var(--linia); border-radius: 6px; color: var(--cichy);
            margin-left: .4rem; vertical-align: .1em; }
/* Ikonki platform. Kolor z `currentColor` przez `--cichy`, więc tryb ciemny działa
   bez osobnej reguły — i to jest jedyny powód, dla którego znak jest rysowany, a nie
   wstawiony plikiem: `<img>` koloru nie dziedziczy i w ciemnym znika.
   Rozmiar w `em`, żeby znak skalował się razem z tytułem karty, a nie obok niego.
   Znak leży POD niewidzialną warstwą linku karty (`a.nazwa::after`) i nie dostaje
   ani `position`, ani własnego odsyłacza — inaczej rozciąłby cel dotknięcia na dwa. */
.platformy { display: inline-flex; gap: .3em; margin-left: .4rem;
             vertical-align: .02em; color: var(--cichy); }
.platforma { display: inline-flex; }
.platformy svg { width: .85em; height: .85em; display: block; }
/* Tekst wyłącznie dla czytnika ekranu — ten sam idiom, co skip-link wyżej, bez
   reguły `:focus`, bo ten element nie jest ogniskowalny. */
.czytnik { position: absolute; left: -9999px; }
.sklep { display: block; margin: .35rem 0 1.25rem; font-weight: 600; }
.nota { font-size: .8rem; margin-top: 2rem; }
.przycisk { display: inline-block; background: var(--akcent); color: var(--tlo);
            padding: .55rem 1.1rem; border-radius: 10px; text-decoration: none; }
.spis-sekcji ul { list-style: none; padding: 0; margin: 0 0 1.75rem;
                  display: flex; flex-wrap: wrap; gap: .35rem .9rem; font-size: .92rem; }
.spis-sekcji li { margin: 0; }
details { border-bottom: 1px solid var(--linia); padding: .55rem 0; }
details summary { cursor: pointer; font-weight: 600; list-style: none; padding-right: 1.5rem;
                  position: relative; }
details summary::-webkit-details-marker { display: none; }
details summary::after { content: "+"; position: absolute; right: .25rem; color: var(--cichy);
                         font-weight: 400; }
details[open] summary::after { content: "–"; }
details p { margin: .6rem 0 .3rem; }
.zrzuty { display: flex; gap: 1rem; overflow-x: auto; margin: 1rem 0 2rem;
          padding-bottom: .5rem; scroll-snap-type: x mandatory; }
.zrzuty figure { margin: 0; flex: 0 0 210px; scroll-snap-align: start; }
.zrzuty img { width: 210px; height: auto; border-radius: 14px;
              border: 1px solid var(--linia); display: block; }
.zrzuty figcaption { font-size: .85rem; color: var(--cichy); margin-top: .45rem;
                     line-height: 1.4; }
ul.zwykla { padding-left: 1.15rem; }
ul.zwykla li { margin: .3rem 0; }
/* Strony tematyczne. Pięć reguł i ani jednej więcej: hasło ma wyglądać jak
   sekcja opisu sklepowego, a nie jak inny gatunek strony. Rubin dostaje własny
   rozmiar, bo domyślny w Safari bywa większy niż linia tekstu wokół. */
.haslo + .haslo { border-top: 1px solid var(--linia); padding-top: .5rem; }
.haslo h2 { margin-top: 1.75rem; }
.przyklady { padding-left: 0; list-style: none; margin: .4rem 0 1.25rem; }
.przyklady li { margin: .6rem 0; }
.przyklady .pelna { color: var(--cichy); }
.przyklady .tlum { display: block; color: var(--cichy); font-size: .93rem; }
ruby rt { font-size: .55em; color: var(--cichy); }
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--linia);
         font-size: .88rem; color: var(--cichy); }
footer a { color: var(--akcent); }
code { font-size: .9em; }
"""


# ---------------------------------------------------------------- dane

def wczytaj_manifest():
    return json.loads((NARZEDZIA / "apps.json").read_text(encoding="utf-8"))


def data_zrodla(repo: Path, plik: Path, ref: str = "HEAD") -> str:
    """Data ostatniej zmiany pliku metadanych **na nazwanym stanie**.

    `lastmod` w mapie witryny ma mówić, kiedy zmieniła się TREŚĆ, a nie kiedy
    ktoś uruchomił generator. Data z zegara psułaby jedno i drugie: nie niosłaby
    informacji i odbierała wynikowi powtarzalność bit w bit.

    **Domyślne `HEAD` było wadą i kosztowało cofniętą datę na żywo.** 16.09.2026
    ta sama komenda dała 12.09 na Macu (gałąź wydaniowa) i 09.09 na maszynie
    windowsowej (`main`) — czyli dane strukturalne ogłosiły, że strona jest
    starsza, niż była dzień wcześniej. Stan podaje wołający, ze znacznika
    `sklep/<wersja>`.
    """
    wynik = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%cs", ref,
                            "--", str(plik)], capture_output=True, text=True)
    return (wynik.stdout or "").strip() or "2026-09-08"


def stan_sklepowy(repo: Path, wpis: dict) -> str:
    """Znacznik `sklep/<wersja>` — jedyne źródło treści karty produktu.

    **Witryna mówi to, co kupujący naprawdę zobaczy w App Store**, czyli wersję
    `READY_FOR_SALE` — nie tę, która czeka w recenzji, i nie tę, nad którą ktoś
    właśnie pracuje. Rozstrzygnięcie Jakuba 16.09.2026, po dniu, w którym
    przeliczenie z drugiej maszyny cofnęło treść na żywo: generator czytał
    „cokolwiek jest wymeldowane", więc to samo polecenie dawało inny wynik
    na Macu i na Windowsie, a oba wyglądały poprawnie.

    **Brak znacznika jest awarią, nie cichym powrotem do dysku.** Milczący odwrót
    przywróciłby dokładnie tę wadę — tylko rzadziej i trudniej do złapania.
    Znacznik zakłada droga wydania, w chwili gdy wersja wchodzi do sklepu.
    """
    wersja = wpis.get("wersja")
    if not wersja:
        raise SystemExit(f"{wpis['slug']}: manifest nie podaje wersji sklepowej "
                         f"(pole `wersja` w Tools/apps.json)")
    ref = f"sklep/{wersja}"
    if subprocess.run(["git", "-C", str(repo), "rev-parse", "-q", "--verify",
                       f"refs/tags/{ref}"], capture_output=True).returncode != 0:
        raise SystemExit(
            f"{wpis['slug']}: brak znacznika {ref} w {repo.name}.\n"
            f"  Strona produktowa bierze treść ze stanu wersji stojącej w sklepie.\n"
            f"  Znacznik zakłada się na commicie podbicia numeru:\n"
            f"    git -C {repo} tag -a {ref} <commit> -m 'Wersja {wersja} w sklepie'\n"
            f"  Numer w manifeście sprawdzisz: python3 Tools/generuj-strony.py --sprawdz-sklep")
    return ref


def zbierz(manifest):
    """Metadane wszystkich aplikacji w obu językach, ze stanu wersji ze sklepu."""
    apki = []
    for wpis in sorted(manifest["aplikacje"], key=lambda a: a["kolejnosc"]):
        repo = ZRODLA / wpis["repo"]
        if not repo.exists():
            raise SystemExit(f"{wpis['slug']}: brak drzewa {repo}")
        ref = stan_sklepowy(repo, wpis)
        teksty = {}
        for jezyk in JEZYKI:
            teksty[jezyk] = metadane.teksty(repo, wpis, jezyk, ref)
            plik = (Path("docs/app-store/version-texts.json") if wpis["zrodlo"] == "kaname"
                    else Path(f"docs/app-store/APP_STORE_METADATA_{jezyk.upper()}.md"))
        repo_zrzutow = ZRODLA / wpis.get("repoZrzuty", wpis["repo"])
        ref_zrzutow = ref if repo_zrzutow == repo else stan_sklepowy(repo_zrzutow, wpis)
        podpisy = {j: podpisy_kadrow(repo_zrzutow, j, ref_zrzutow) for j in JEZYKI}
        apki.append({**wpis, "teksty": teksty, "repoSciezka": repo, "podpisy": podpisy,
                     "stanSklepowy": ref, "data": data_zrodla(repo, plik, ref)})
    return apki


def zbierz_zapowiedziane(manifest):
    """Aplikacje, których jeszcze nie ma — nazwa i podtytuł, i nic więcej.

    **Trzeci stan, nie odmiana `wSklepie: false`.** Tamta flaga znaczy „złożona,
    czeka na recenzję Apple": buduje pełną stronę produktową i wymaga kompletu
    metadanych oraz dokumentów prawnych. Aplikacja bez produktu nie ma czym tego
    wypełnić — a wymyślenie opisu byłoby wymyśleniem treści.

    Zapowiedziana dostaje **wyłącznie kartę** w sekcji „Co dojdzie do rodziny" na
    mapie rodziny. Brak sekcji w manifeście nie jest błędem: rodzina bez planów
    po prostu nie ma czego zapowiadać.
    """
    wpisy = manifest.get("zapowiedziane") or []
    out = []
    for wpis in sorted(wpisy, key=lambda a: a["kolejnosc"]):
        repo = ZRODLA / wpis["repo"]
        if not repo.exists():
            raise SystemExit(f"{wpis['slug']}: brak drzewa {repo}")
        teksty = {j: metadane.zapowiedz(repo, j) for j in JEZYKI}
        out.append({**wpis, "teksty": teksty, "repoSciezka": repo})
    return out


# ---------------------------------------------------------------- HTML

def e(tekst: str) -> str:
    return html.escape(tekst, quote=False)


def wzgledny(z_glebokosci: int, cel: str) -> str:
    """Odsyłacz wewnętrzny — w tej samej postaci, co `canonical` i mapa witryny.

    **Postać katalogowa, nie `…/index.html`**, i to jest naprawa z pomiaru
    16.09.2026: **1013 odsyłaczy wewnętrznych kończyło się na `index.html`,
    zero miało postać katalogową** — a `canonical`, `hreflang` i `sitemap.xml`
    mówiły wyłącznie katalogiem. Obie postacie oddają 200 (GitHub Pages nie
    przekierowuje), więc nic nie ginęło z indeksu, ale całe przechodzenie robota
    wewnątrz witryny biegło po adresach, które strona sama nazywa niekanonicznymi.

    `publiczny()` stało tu obok od początku, z tym samym uzasadnieniem — tylko
    używane było na zewnątrz, a nie w odsyłaczach.

    Pusty wynik znaczy „ta sama strona, korzeń": `index.html` z głębokości zero.
    Musi zostać `./`, bo `href=""` przeglądarka czyta jako adres bieżący RAZEM
    z zapytaniem i kotwicą — czyli coś innego niż korzeń witryny.
    """
    return (("../" * z_glebokosci) + publiczny(cel)) or "./"


def akapit_html(akapit: str) -> str:
    """Jeden akapit opisu sklepowego → HTML.

    Opisy rodziny mają stały kształt, wypracowany przy dziesięciu kartach:
    akapit pisany wersalikami jest nagłówkiem sekcji, akapit złożony z linii
    zaczynających się od „•" albo „1." jest listą, reszta jest prozą. Nic tu nie
    jest przepisywane — zmienia się wyłącznie znacznik.
    """
    linie = [l.strip() for l in akapit.split("\n") if l.strip()]
    litery = [z for z in akapit if z.isalpha()]
    if len(linie) == 1 and litery and all(z.isupper() for z in litery) and len(akapit) < 80:
        return f"<h3>{e(akapit)}</h3>"
    if len(linie) > 1 and all(re.match(r"^([•–-]|\d+\.)\s", l) for l in linie):
        pozycje = "".join(f"<li>{e(re.sub(r'^([•–-]|\d+\.)\s+', '', l))}</li>" for l in linie)
        znacznik = "ol" if re.match(r"^\d+\.", linie[0]) else "ul"
        klasa = "" if znacznik == "ol" else ' class="zwykla"'
        return f"<{znacznik}{klasa}>{pozycje}</{znacznik}>"
    return "<p>" + "<br>".join(e(l) for l in linie) + "</p>"


def kotwica(tekst: str, zajete: set) -> str:
    """Adres kotwicy z nagłówka sekcji — bez znaków, które trzeba by kodować.

    Nagłówki są po polsku i po angielsku, więc ogonki idą przez rozkład Unicode
    do liter podstawowych. Adres z `%C4%85` w środku działa, ale nie da się go
    komuś podyktować ani wkleić do rozmowy bez tłumaczenia się z niego.
    """
    # `ł` i `Ł` **nie są literą z ogonkiem** — to osobne znaki i rozkład Unicode ich
    # nie rusza. Bez tej podmiany „WYŁAWIANIE ZDAŃ" dawało kotwicę `wy-awianie-zdan`.
    tekst = tekst.lower().replace("ł", "l")
    goly = unicodedata.normalize("NFKD", tekst)
    slug = re.sub(r"[^a-z0-9]+", "-", "".join(z for z in goly if not unicodedata.combining(z)))
    slug = slug.strip("-") or "sekcja"
    kandydat, licznik = slug, 2
    while kandydat in zajete:
        kandydat, licznik = f"{slug}-{licznik}", licznik + 1
    zajete.add(kandydat)
    return kandydat


def opis_html(opis: str) -> tuple:
    """Opis sklepowy jako HTML **i lista jego nagłówków**.

    Nagłówki dostają kotwice z dwóch powodów naraz: żeby dało się zbudować nad
    opisem spis treści (2200–4100 znaków jednym ciągiem to osiem do dziesięciu
    przewinięć na telefonie, bez żadnego punktu zaczepienia) i żeby dało się
    podesłać komuś adres prosto do sekcji, a nie do całej strony.
    """
    zajete, naglowki, kawalki = set(), [], []
    for akapit in metadane.akapity(opis):
        znacznik = akapit_html(akapit)
        if znacznik.startswith("<h3>"):
            tekst = znacznik[len("<h3>"):-len("</h3>")]
            adres = kotwica(akapit, zajete)
            naglowki.append((adres, tekst))
            znacznik = f'<h3 id="{adres}">{tekst}</h3>'
        kawalki.append(znacznik)
    return "\n".join(kawalki), naglowki


def meta_opis(teksty: dict) -> str:
    """Treść `<meta name="description">` — podtytuł plus pierwsze zdanie opisu.

    Oba pola są przejrzane i oba mówią o aplikacji zdaniem, a nie listą słów.
    Limit 155 znaków jest po to, żeby wyszukiwarka nie ucinała w połowie myśli.
    """
    zdania = metadane.zdania(teksty["opis"])
    # Samo pierwsze zdanie bywa za krótkie na zajawkę w wynikach: „Shindan nie uczy."
    # to prawda i zdanie ze sklepu, ale jako cała zajawka odstrasza. Dobieramy
    # kolejne zdania tego samego akapitu, dopóki mieszczą się w limicie.
    tresc = teksty["podtytul"].rstrip(".") + "."
    for zdanie in zdania:
        kandydat = f"{tresc} {zdanie}"
        if len(kandydat) > 155:
            break
        tresc = kandydat
    if tresc.rstrip(".") == teksty["podtytul"].rstrip("."):
        pierwsze = zdania[0] if zdania else ""
        return pierwsze[:152].rstrip(" ,;–-") + "…" if len(pierwsze) > 155 else \
            (f"{tresc} {pierwsze}"[:152].rstrip(" ,;–-") + "…")
    return tresc


def publiczny(adres: str) -> str:
    """Adres w postaci, w jakiej ma stać w linku kanonicznym i w mapie witryny.

    GitHub Pages oddaje tę samą stronę pod `…/apps/kaname/` i `…/apps/kaname/index.html`.
    Dwa adresy na jedną stronę to dokładnie ta sytuacja, dla której wymyślono link
    kanoniczny — więc wszędzie na zewnątrz mówimy katalogiem, a nie plikiem.
    """
    return adres[:-len("index.html")] if adres.endswith("index.html") else adres


def strona(*, jezyk, tytul, opis, kanoniczny, alternatywny, tresc, glebokosc,
           manifest, jsonld=None, dodatkowa_glowa="", nawigacja="", stopka_html=""):
    n = NAPISY[jezyk]
    baza = manifest["bazaAdresu"]
    kanoniczny, alternatywny = publiczny(kanoniczny), publiczny(alternatywny)
    inny = "en" if jezyk == "pl" else "pl"
    czesci = [
        "<!doctype html>",
        f'<html lang="{n["html_lang"]}">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{e(tytul)}</title>",
        f'<meta name="description" content="{html.escape(opis, quote=True)}">',
        f'<link rel="canonical" href="{baza}/{kanoniczny}">',
        f'<link rel="alternate" hreflang="{jezyk}" href="{baza}/{kanoniczny}">',
        f'<link rel="alternate" hreflang="{inny}" href="{baza}/{alternatywny}">',
        f'<link rel="alternate" hreflang="x-default" href="{baza}/{alternatywny if jezyk == "pl" else kanoniczny}">',
        f'<meta property="og:title" content="{html.escape(tytul, quote=True)}">',
        f'<meta property="og:description" content="{html.escape(opis, quote=True)}">',
        f'<meta property="og:url" content="{baza}/{kanoniczny}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{html.escape(n["tytul_mapy"], quote=True)}">',
        f'<meta property="og:locale" content="{"pl_PL" if jezyk == "pl" else "en_US"}">',
        f'<meta property="og:locale:alternate" content="{"en_US" if jezyk == "pl" else "pl_PL"}">',
        '<meta name="theme-color" content="#a34f5a">',
        # Ikona witryny. Google pokazuje ją obok wyniku na telefonie i **wymaga
        # co najmniej 48 px**; kafelek 180 px obsługuje iOS i podwójną gęstość.
        #
        # **Adresem bezwzględnym, nie względnym, i to jest naprawa z pomiaru.**
        # Zgłoszenie Jakuba 09.09.2026: ikona widoczna na mapie rodziny, na
        # podstronie aplikacji nie. Znacznik był na obu, ale mapa leży w korzeniu
        # (`assets/…`), a podstrona dwa katalogi niżej (`../../assets/…`) — i to
        # jedyne, czym się różniły. Adres bezwzględny zdejmuje głębokość z równania
        # i zgadza się z tym, co dostają dokumenty prawne.
        f'<link rel="icon" type="image/png" sizes="48x48" '
        f'href="{baza}/assets/znak-48.png">',
        f'<link rel="apple-touch-icon" href="{baza}/assets/znak-180.png">',
        dodatkowa_glowa,
        f"<style>\n{STYL}</style>",
    ]
    if jsonld:
        czesci.append('<script type="application/ld+json">\n'
                      + json.dumps(jsonld, ensure_ascii=False, indent=2) + "\n</script>")
    # Jeden `<main>` na stronę: czytnik ekranu daje wtedy skok do treści z pominięciem
    # nawigacji. Pasek języka i powrotu stoi **poza** nim, bo jest nawigacją, a stopka
    # poza nim, bo jest stopką — gdyby siedziały w środku, „przejdź do treści"
    # prowadziłoby do linków, czyli dokładnie tam, skąd czytnik miał uciec.
    # Że ta linia naprawdę wstawia landmark, sprawdza bramka 9 — na wytworze.
    # Skip-link. Położenie `<main>` było w tym pliku uzasadniane właśnie tym
    # mechanizmem — „przejdź do treści" ma omijać nawigację — a samego linku
    # nie było na żadnej stronie. Widoczny dopiero po dojściu do niego klawiszem.
    do_tresci = f'<a class="do-tresci" href="#tresc">{e(n["do_tresci"])}</a>'
    # Nota licencyjna znaku Androida — **tylko na stronach, na których ten znak
    # naprawdę stanął**. CC BY 3.0 adnotacji wymaga, a nota nad stroną bez znaku
    # jest szumem prawnym: mówi o rzeczy, której czytelnik tam nie widzi.
    #
    # Liczona z WYTWORU (`tresc`), nie z zamiaru — bo o tym, czy znak padł,
    # rozstrzyga `sklepy()` per aplikacja, a nie ustawienie strony. Dziś ta linia
    # nie zapala się nigdzie: żadna apka nie stoi na Play. Zapali się w dniu portu,
    # sama, bez pamiętania o niej.
    nota = ""
    if ZNAKI_PLATFORM == "logo" and 'data-platforma="android"' in tresc:
        nota = f'<p class="podtytul nota">{e(n["android_cc_by"])}</p>'
    czesci += ["</head>", "<body>", do_tresci, nawigacja,
               f'<main id="tresc">{tresc}</main>', nota, stopka_html,
               "</body>", "</html>", ""]
    return "\n".join(cz for cz in czesci if cz)


def gora(jezyk, glebokosc, alternatywny, manifest, mapa=True, powrot=None):
    """Pasek: znak witryny i powrót po lewej, przełącznik języka po prawej.

    Znak jest linkiem do mapy rodziny na podstronach, a na samej mapie zwykłym
    obrazkiem — link prowadzący do strony, na której się stoi, jest dla czytnika
    ekranu szumem. Opis alternatywny to nazwa witryny, czyli tekst, który i tak
    już stoi w `NAPISY`; znak nie dokłada ani jednego nowego zdania.
    """
    n = NAPISY[jezyk]
    dom = wzgledny(glebokosc, "index.html" if jezyk == "pl" else "en/index.html")
    # Na podstronie znak stoi tuż obok linku tekstowego prowadzącego w to samo
    # miejsce, więc jego opis alternatywny jest **pusty**: czytnik ekranu przeczytałby
    # inaczej dwa razy pod rząd ten sam cel. Na mapie sąsiada nie ma i opisem jest
    # nazwa witryny — tekst, który i tak stoi w `NAPISY`.
    def obrazek(opis):
        return (f'<img src="{wzgledny(glebokosc, "assets/znak-48.png")}" '
                f'alt="{opis}" width="22" height="22">')

    znak_html = (f'<a class="znak" href="{dom}" aria-hidden="true" tabindex="-1">{obrazek("")}</a>'
                 if mapa else f'<span class="znak">{obrazek(e(n["tytul_mapy"]))}</span>')
    # **Powrót prowadzi do rodzica, a nie zawsze do mapy aplikacji.** Strona
    # o licznikach leży pod rozdrożem `/nauka/`, a strona grupy N5 jeszcze piętro
    # niżej — wyprowadzanie ich obu na mapę dziesiątki kazałoby czytelnikowi
    # wracać przez korzeń za każdym razem, a przy trzech poziomach to jest
    # nawigacja, która gubi, zamiast prowadzić.
    if powrot:
        cel_powrotu, etykieta_powrotu = powrot
        powrot = f'<a href="{cel_powrotu}">← {e(etykieta_powrotu)}</a>'
    else:
        powrot = f'<a href="{dom}">← {e(n["wroc"])}</a>' if mapa else ""
    prawo = (f'<a href="{manifest["bazaAdresu"]}/{publiczny(alternatywny)}">'
             f'{e(n["inny_jezyk"])}</a>')
    return (f'<nav class="gora" aria-label="{e(n["nawigacja"])}">'
            f'<span>{znak_html}{powrot}</span>'
            f'<span>{prawo}</span></nav>')


def stopka(jezyk, glebokosc, manifest, kontakt=None, spis_dokumentow=False,
           nauka=True, co_dalej=True):
    """Stopka. `spis_dokumentow=True` na stronie spisu — żeby nie linkowała sama
    do siebie, tak jak `gora()` nie linkuje do mapy, stojąc na mapie.

    `nauka=False` z tego samego powodu na rozdrożu stron tematycznych. Wyjście
    na to rozdroże stoi w stopce **każdej** strony z rozmysłu: strona bez
    wejścia jest stroną, której nie ma, a 09.09.2026 sześćdziesiąt dziewięć
    dokumentów prawnych stało dokładnie w takim stanie.

    `co_dalej=False` na samej stronie „Co dalej", z tego samego powodu co dwa wyżej.
    Poza nią link stoi wszędzie i to jest **jedyne** wejście na tę stronę ([poz. 295]):
    mapa rodziny mówi o dziesięciu rzeczach, które są, i nie zaczyna mówić o czymś,
    czego nie ma, tuż obok nich.
    """
    n = NAPISY[jezyk]
    spis = "dokumenty.html" if jezyk == "pl" else "en/documents.html"
    autor = "o-autorze/index.html" if jezyk == "pl" else "en/about/index.html"
    dalej = "co-dalej/index.html" if jezyk == "pl" else "en/whats-next/index.html"
    linki = ([] if spis_dokumentow
             else [f'<a href="{wzgledny(glebokosc, spis)}">{e(n["spis_link"])}</a>'])
    if nauka:
        linki.insert(0, f'<a href="{wzgledny(glebokosc, ROZDROZE[jezyk])}">'
                        f'{e(n["nauka_link"])}</a>')
    if co_dalej:
        linki.insert(0, f'<a href="{wzgledny(glebokosc, dalej)}">{e(n["dalej_link"])}</a>')
    linki.insert(0, f'<a href="{wzgledny(glebokosc, autor)}">{e(n["autor_link"])}</a>')
    if kontakt:
        linki.append(f'<a href="mailto:{kontakt}">{e(kontakt)}</a>')
    czlony = [e(manifest["autor"])] + linki
    return f"<footer>{' · '.join(czlony)}</footer>"


# ---------------------------------------------------------------- strony

def sciezki(slug, jezyk):
    if jezyk == "pl":
        return f"apps/{slug}/index.html", 2
    return f"en/apps/{slug}/index.html", 3


#: Kolejność platform na stronie. **Stała, nie z manifestu** — kolejność przycisków ma
#: być ta sama na każdej podstronie, a wynik generatora powtarzalny bit w bit.
PLATFORMY = ("ios", "android")

#: Klucz w `NAPISY` z nazwą sklepu danej platformy.
NAZWA_SKLEPU = {"ios": "w_sklepie", "android": "w_sklepie_google"}

#: Nazwa systemu w danych strukturalnych `SoftwareApplication`.
SYSTEM = {"ios": "iOS", "android": "Android"}

#: Klucz w `NAPISY` z nazwą urządzenia nad galerią kadrów.
URZADZENIE = {"ios": "urzadzenie_ios", "android": "urzadzenie_android"}

#: Adres w sklepie, per platforma. Apple identyfikuje aplikację **liczbą**, Google
#: **identyfikatorem pakietu** — to nie jest ten sam rodzaj wartości i dlatego nie stoją
#: w jednym polu.
ADRES_SKLEPU = {
    "ios": lambda i: f"https://apps.apple.com/app/id{i}",
    "android": lambda i: f"https://play.google.com/store/apps/details?id={i}",
}

#: Klucz w `NAPISY` z nazwą systemu dla czytnika ekranu przy ikonce platformy.
PLATFORMA_NAZWA = {"ios": "platforma_ios", "android": "platforma_android"}

#: **Którym znakiem oznaczamy platformę.** Rozstrzygnięcie Jakuba 16.09.2026: logo
#: systemów. Stała istnieje, bo ten wybór ma cenę, którą trzeba dało się cofnąć bez
#: przerabiania układu — wszystkie warianty oddają ten sam `<span class="platformy">`
#: o tym samym pudełku, różni się wyłącznie zawartość `<svg>`.
#:
#: **Cena wariantu „logo", nazwana, a nie obejdzona:** znak Apple nie jest udostępniony
#: jako znacznik zgodności (Apple przewiduje do tego plakietkę „Download on the App
#: Store"), a jego wytyczne zabraniają przebarwiania — podczas gdy cała ta konstrukcja
#: stoi na `currentColor`, czyli na przebarwianiu, bo inaczej znak znika w trybie
#: ciemnym. Robot Androida jest na CC BY 3.0 i adnotacji wymaga; tę generator dokłada
#: sam, na stronach, na których robot faktycznie stanął.
#:
#: `"glif"` to ta sama informacja bez cudzych znaków: własny rysunek urządzenia.
ZNAKI_PLATFORM = "logo"          # "logo" | "glif"

#: Znaki platform. Rysowane w kodzie, nie plikiem w `assets/`, i to jest decyzja
#: z trzech pomiarów: `<img src=".svg">` **nie dziedziczy `currentColor`**, więc w trybie
#: ciemnym znak znika i trzeba by dwóch plików plus `<picture>`; plik wchodzi pod bramkę
#: odsyłaczy i pod maszynerię skrótów, bo `rsvg-convert` nie daje powtarzalnego bajtu;
#: a dziesięć osadzeń po ~200 bajtów jest tańsze niż dziesięć żądań HTTP na stronie,
#: która nie ma dziś ANI JEDNEGO zewnętrznego zasobu.
#:
#: Bez `width`/`height` w znaczniku — rozmiar idzie z CSS w `em`, żeby znak skalował się
#: razem z tytułem karty.
GLIFY = {
    "logo": {
        "ios": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" '
               'focusable="false"><path d="M16.3 12.8c0-2.2 1.8-3.3 1.9-3.3-1-1.5-2.7-1.7-3.3-1.7'
               '-1.4-.1-2.7.8-3.4.8-.7 0-1.8-.8-3-.8-1.5 0-2.9.9-3.7 2.3-1.6 2.7-.4 6.8 1.1 9'
               '.8 1.1 2.1 1.6 2.3 2.6 2.3s1.3-.6 2.6-.6 1.6.6 2.7.6 1.8-1 2.5-2c.8-1.2 1.1-2.3'
               ' 1.1-2.4 0 0-2.1-.8-2.1-3.2zM14.1 6.3c.6-.7 1-1.7.9-2.7-.8 0-1.9.6-2.5 1.3-.5.6'
               '-1 1.6-.9 2.6.9.1 1.8-.5 2.5-1.2z"/></svg>',
        "android": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" '
                   'focusable="false"><path d="M17.5 9.3c-.5 0-.9.4-.9.9v4.4c0 .5.4.9.9.9s.9-.4'
                   '.9-.9V10.2c0-.5-.4-.9-.9-.9zM6.5 9.3c-.5 0-.9.4-.9.9v4.4c0 .5.4.9.9.9s.9-.4'
                   '.9-.9V10.2c0-.5-.4-.9-.9-.9zM7.4 15.6c0 .5.4.9.9.9h.7v2.2c0 .5.4.9.9.9s.9-.4'
                   '.9-.9v-2.2h1.4v2.2c0 .5.4.9.9.9s.9-.4.9-.9v-2.2h.7c.5 0 .9-.4.9-.9V9.7H7.4v5.9z'
                   'M14.6 6.3l.8-1.3c.1-.1 0-.3-.1-.3-.1-.1-.3 0-.3.1l-.8 1.3c-.7-.3-1.4-.4-2.2-.4'
                   's-1.5.1-2.2.4l-.8-1.3c-.1-.1-.2-.2-.3-.1-.1.1-.2.2-.1.3l.8 1.3C7.9 7 6.9 8.3 6.8 9.8'
                   'h10.4c-.1-1.5-1.1-2.8-2.6-3.5zM9.7 8.4c-.2 0-.4-.2-.4-.4s.2-.4.4-.4.4.2.4.4-.2.4-.4.4z'
                   'm4.6 0c-.2 0-.4-.2-.4-.4s.2-.4.4-.4.4.2.4.4-.2.4-.4.4z"/></svg>',
    },
    "glif": {
        "ios": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
               'aria-hidden="true" focusable="false"><rect x="6.5" y="2.5" width="11" height="19" '
               'rx="3"/><path d="M10 5.2h4"/></svg>',
        "android": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
                   'aria-hidden="true" focusable="false"><rect x="6.5" y="2.5" width="11" '
                   'height="19" rx="1.5"/><path d="M10 18.6h4"/></svg>',
    },
}


def znaczki_platform(a, jezyk):
    """Ikonki platform, na których aplikacja STOI — jeden `<span>` na kartę.

    **Jeden wrapper z dwoma glifami, nie dwa wrappery**, żeby bramka mogła liczyć
    jedno i drugie osobno i złapać różnicę.

    Źródłem prawdy jest `sklepy()` — ta funkcja nie dokłada własnej wiedzy o sklepach
    i nie czyta manifestu. Dzięki temu w dniu portu wystarczy blok `sklepy` w jednym
    wpisie: karta dostaje drugi znak sama, bramka sama przelicza oczekiwanie.

    **Nazwa systemu dla czytnika ekranu stoi obok znaku**, tekstem poza ekranem —
    tym samym idiomem, co skip-link (`.do-tresci`). Ikona bez tekstu jest dla czytnika
    niewidzialna, a `aria-label` na `<svg>` bywa przez czytniki pomijany; tekst jest.
    """
    gdzie = [p for p in PLATFORMY if w_sklepie(a, p)]
    if not gdzie:
        return ""
    znaki = "".join(
        f'<span class="platforma" data-platforma="{p}">{GLIFY[ZNAKI_PLATFORM][p]}'
        f'<span class="czytnik">{e(NAPISY[jezyk][PLATFORMA_NAZWA[p]])}</span></span>'
        for p in gdzie)
    return f'<span class="platformy">{znaki}</span>'


def platformy_na_stronie(apki):
    """Ile znaków której platformy ma paść na mapie — oczekiwanie dla bramki 23."""
    return {p: sum(1 for a in apki if w_sklepie(a, p)) for p in PLATFORMY}


def link_sklepu(a, platforma="ios"):
    return ADRES_SKLEPU[platforma](sklepy(a)[platforma]["id"])


def sklepy(a):
    """Sklepy, w których aplikacja stoi albo ma stanąć — **jedyne miejsce, które o tym wie**.

    Dziś manifest opisuje jeden sklep dwoma polami: `appId` (liczba ASC) i `wSklepie`
    (bool). [poz. 307] mówi, czemu to nie wystarcza: **bool nie opisuje trzech stanów**
    („nie ma", „złożona, czeka na recenzję", „stoi"), a jedno `appId` nie ma miejsca na
    `applicationId` z Play.

    **Pola nie zmieniają kształtu i to jest decyzja, nie odkładanie.** Czyta je
    `japanese-tools/lib/rodzina.py` (obie), `jp-grammar/Tools/stan-rodziny.py` (`appId`)
    i `asc-marketing-url.py` (`appId`) — narzędzia, których z maszyny windowsowej nie da
    się uruchomić, więc zmiana kształtu byłaby zmianą niesprawdzoną w trzech miejscach naraz.

    Zamiast tego: **widok iOS wyprowadza się z dzisiejszych pól**, a blok `sklepy` pojawia
    się w manifeście dopiero wtedy, gdy aplikacja faktycznie wchodzi do drugiego sklepu.
    Dzięki temu dziś nie ma ani jednej wartości zapisanej dwa razy — a w dniu, w którym
    jakaś aplikacja stanie na Play, dwie prawdy o iOS zaczną istnieć obok siebie i **wtedy
    dopiero** bramka zaczyna pilnować ich zgody.

        "sklepy": {
          "ios":     {"id": "6802813564", "stan": "w-sklepie"},
          "android": {"id": "pl.jdjapanese.katsuyokei", "stan": "zlozona"}
        }

    Stany: `brak` · `zlozona` (czeka na recenzję) · `w-sklepie`.
    """
    jawne = a.get("sklepy")
    if jawne:
        return {p: jawne[p] for p in PLATFORMY if p in jawne}
    return {"ios": {"id": a["appId"],
                    "stan": "w-sklepie" if a.get("wSklepie") else "zlozona"}}


def w_sklepie(a, platforma=None):
    """Czy aplikacja stoi w sklepie — w tym konkretnym albo w którymkolwiek."""
    s = sklepy(a)
    if platforma:
        return s.get(platforma, {}).get("stan") == "w-sklepie"
    return any(w.get("stan") == "w-sklepie" for w in s.values())


def przyciski_sklepow(a, n):
    """Przyciski sklepów, po jednym na platformę, w stałej kolejności `PLATFORMY`.

    **Przy jednym sklepie wynik jest znak w znak taki jak przed [poz. 307]** — i to jest
    bramka tej zmiany, nie jej efekt uboczny: dziesięć dzisiejszych stron nie ma prawa
    drgnąć, bo model nauczył się drugiej platformy.
    """
    return "".join(
        f'<a class="przycisk" href="{link_sklepu(a, p)}">{e(n[NAZWA_SKLEPU[p]])} →</a>'
        for p in PLATFORMY if w_sklepie(a, p))


def mapa_rodziny(apki, jezyk, manifest, zywe=(), zapowiedziane=()):
    n = NAPISY[jezyk]
    kanoniczny = "index.html" if jezyk == "pl" else "en/index.html"
    alternatywny = "en/index.html" if jezyk == "pl" else "index.html"
    glebokosc = 0 if jezyk == "pl" else 1

    # **Jedna sekcja, nie dwie.** Do 09.09.2026 ta strona pokazywała tę samą dziesiątkę
    # dwa razy: najpierw tabelę „problem → aplikacja" (dziesięć akapitów prozy, klikalna
    # tylko nazwa), a pod nią karty z ikonami. Na telefonie było to około dwudziestu
    # przewinięć przez to samo. Karta niesie teraz oba wkłady: ikonę, po której apkę
    # się rozpoznaje, i zdanie o problemie, po którym się ją wybiera.
    karty = []
    for a in apki:
        t = a["teksty"][jezyk]
        cel = wzgledny(glebokosc, sciezki(a["slug"], jezyk)[0])
        ikona = wzgledny(glebokosc, f"assets/ikony/{a['slug']}.webp")
        # Znacznik na karcie niesie DWIE różne rzeczy i kolejność jest tu istotna.
        #
        # „Wkrótce w App Store" mówi o stanie w sklepie i **wygrywa**, bo aplikacji, której
        # jeszcze nie ma, nie opisuje się listą platform.
        #
        # **ODWRÓCONE 16.09.2026 rozstrzygnięciem Jakuba — i to jest zapis powodu, żeby
        # nie żył wyłącznie w git logu.** Do tego dnia znacznik platformy pojawiał się
        # dopiero przy drugim sklepie ([poz. 307]), z uzasadnieniem: „przy jednym byłby
        # szumem, dziś wszystkie dziesięć kart niosłoby ten sam napis, a po porcie
        # dziewięć mówiłoby »nie u ciebie«".
        #
        # Tamten argument był policzony dla NAPISU w ramce („App Store · Google Play",
        # ~90 px na każdej z dziesięciu kart) i na napis się trzyma. Na ikonę nie:
        # znak ~14 px czyta się jak atrybut, nie jak zdanie. Druga połowa argumentu —
        # „dziewięć powie »nie u ciebie«" — jest po porcie **prawdą, którą czytelnik
        # chce znać PRZED kliknięciem**, a nie wadą; zgłoszenie Jakuba brzmiało
        # dokładnie „nie widzę niczego takiego".
        #
        # Napis o dwóch sklepach zniknął razem z tym: dwa komunikaty o tej samej rzeczy
        # obok siebie byłyby wadą, a ikona mówi to samo w jednej linii tytułu.
        if not a["wSklepie"]:
            znacznik = f'<span class="znacznik">{e(n["wkrotce"])}</span>'
        else:
            znacznik = znaczki_platform(a, jezyk)
        karty.append(
            f'<li class="karta"><img src="{ikona}" alt="" width="52" height="52" loading="lazy">'
            f'<div><a class="nazwa" href="{cel}">{e(t["nazwa"])}</a>'
            f'<span class="jp" lang="ja">{e(a["japonska"])}</span>{znacznik}'
            f'<span class="co">{e(t["podtytul"])}</span>'
            f"<p>{e(t['promo'])}</p></div></li>")

    # Wyjście na strony tematyczne — z mapy, nie tylko ze stopki. To jedyna strona
    # witryny, na którą ktoś trafia sam, więc linki stąd są jedynym, co prowadzi
    # dalej niż do kart aplikacji. Zwykła lista, nie karty: karty na tej stronie
    # znaczą „aplikacja", a to nie są aplikacje.
    # **Co dojdzie do rodziny — osobna sekcja pod dziesiątką, nie karty wmieszane w nią.**
    # Do 13.09.2026 stał tu akapit „czego rodzina jeszcze nie uczy", wymieniający cztery
    # dziedziny bez nazw; teraz te aplikacje mają nazwę, znak i kolor, więc mają czym stanąć.
    #
    # Osobno, bo poz. 112 backlogu notuje ryzyko wprost: sześć „wkrótce" wmieszanych między
    # dziesięć gotowych czyta się jak rodzina niedokończona, a nie rosnąca. Dziesiątka
    # zostaje nietknięta u góry, a to, czego nie ma, stoi poniżej i jest nazwane tym, czym
    # jest. **Plakietka mówi „w przygotowaniu", nie „wkrótce w App Store"** — ta druga
    # znaczy w tej witrynie „złożona, czeka na recenzję" i byłaby obietnicą terminu.
    dojdzie_html = ""
    if zapowiedziane:
        karty_z = []
        for z in zapowiedziane:
            t = z["teksty"][jezyk]
            ikona = wzgledny(glebokosc, f"assets/ikony/{z['slug']}.webp")
            karty_z.append(
                f'<li class="karta"><img src="{ikona}" alt="" width="52" height="52" loading="lazy">'
                f'<div><span class="nazwa">{e(t["nazwa"])}</span>'
                f'<span class="jp" lang="ja">{e(z["japonska"])}</span>'
                f'<span class="znacznik">{e(n["w_przygotowaniu"])}</span>'
                f'<span class="co">{e(t["podtytul"])}</span></div></li>')
        dojdzie_html = (f"<h2>{e(n['dojdzie_naglowek'])}</h2>"
                        f'<p>{e(n["dojdzie_opis"])}</p>'
                        f'<ul class="karty">{"".join(karty_z)}</ul>')

    # **Sekcje tematu stoją tutaj, a nie tylko na stronie tematu** — i to jest
    # naprawa z pomiaru 16.09.2026, nie ozdoba. Search Console zgłosił wtedy
    # 44 strony poza indeksem i były to **co do sztuki** wszystkie strony grup,
    # czyli wszystko, co leżało dwa kliknięcia od korzenia. Kontrpróba trzyma wiek
    # na stałe: strony tematów i strony grup powstały tego samego dnia, 13.09,
    # w tych samych commitach — 18 stron na głębokości 1 weszło do indeksu,
    # 44 na głębokości 2 nie weszły.
    #
    # Trzy inne tłumaczenia obalono pomiarem, żeby nikt tu nie wracał: objętość
    # treści (mediana 5988 znaków wobec 5849), podobieństwo sióstr (3–8% przy tle
    # 1,4%, a najwyższe miały strony ZAINDEKSOWANE) i liczba wejść — ta wyglądała
    # na miarę, dopóki nie zawęziło się porównania do samych stron z głębokości 2,
    # gdzie rozkłady są identyczne.
    #
    # Rozdroże ani spis treści tego nie załatwią: **same leżą na głębokości 1**,
    # więc to, co linkują, ląduje na 2. Odsyłacz musi wyjść z korzenia i innego
    # miejsca nie ma. `<details>` zamiast gołej listy, bo 62 pozycje rozbiłyby
    # mapę rodziny na czytanie, a robot czyta treść zwiniętą tak samo jak otwartą.
    nauka_html = ""
    if zywe:
        pozycje = []
        for temat, _, eksport in zywe:
            cel = wzgledny(glebokosc, sciezki_tematu(temat, jezyk)[0])
            tytul_t = e(n["temat_%s_tytul" % temat["klucz"]])
            opis_t = e(n["temat_%s_opis" % temat["klucz"]])
            grupy = grupy_zywe(temat, eksport)
            sekcje = ""
            if grupy:
                wiersze_g = "".join(
                    f'<li><a href="{wzgledny(glebokosc, sciezki_tematu(temat, jezyk, g)[0])}">'
                    f'{e(nazwa_grupy(eksport, g, jezyk))}</a></li>'
                    for g in grupy)
                sekcje = (f'<details><summary>{e(n["nauka_sekcje"])} ({len(grupy)})</summary>'
                          f'<ul class="zwykla">{wiersze_g}</ul></details>')
            pozycje.append(f'<li><a href="{cel}">{tytul_t}</a> – {opis_t}{sekcje}</li>')
        nauka_html = (f"<h2>{e(n['nauka_link'])}</h2>"
                      f'<ul class="zwykla">{"".join(pozycje)}</ul>')

    tresc = (
        f"<h1>{e(n['tytul_mapy'])}</h1>"
        + f'<p class="podtytul">{e(n["opis_mapy"])}</p>'
        + f"<h2>{e(n['naglowek_wyboru'])}</h2>"
        + '<ul class="karty">' + "".join(karty) + "</ul>"
        + nauka_html
        + dojdzie_html)

    # Pytanie, które model dostaje o rodzinę aplikacji, brzmi „którą wybrać" — i tabela
    # wyżej jest na nie odpowiedzią, tylko zapisaną znacznikami tabeli. Tu ta sama treść
    # stoi jako pytanie i odpowiedź, czyli w kształcie, który modele cytują. Odpowiedź
    # skleja się z nazw i podtytułów, więc dalej nie ma tu ani jednego nowego zdania.
    wybor = "; ".join(f'{a["teksty"][jezyk]["nazwa"]} – {a["teksty"][jezyk]["podtytul"]}'
                      for a in apki)
    faq = {"@type": "FAQPage", "mainEntity": [{
        "@type": "Question",
        "name": n["pytanie_wyboru"],
        "acceptedAnswer": {"@type": "Answer", "text": n["odpowiedz_wyboru"] + " " + wybor},
    }]}

    jsonld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": n["tytul_mapy"],
        "description": n["opis_mapy"],
        "numberOfItems": len(apki),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "url": f"{manifest['bazaAdresu']}/{publiczny(sciezki(a['slug'], jezyk)[0])}",
             "name": a["teksty"][jezyk]["nazwa"]}
            for i, a in enumerate(apki)],
    }
    # `WebSite` mówi wyszukiwarce, jak nazywa się witryna jako całość — bez niego
    # nazwa w wynikach bierze się ze zgadywania z tytułu i domeny. Nazwa i opis są
    # te same, co w `tytul_mapy` i `opis_mapy`, więc tekstu własnego nie przybywa.
    witryna = {"@type": "WebSite",
               "name": n["tytul_mapy"],
               "description": n["opis_mapy"],
               "url": f"{manifest['bazaAdresu']}/{publiczny(kanoniczny)}",
               "inLanguage": jezyk,
               "author": {"@type": "Person", "name": manifest["autor"]}}
    jsonld = {"@context": "https://schema.org",
              "@graph": [witryna,
                         {k: v for k, v in jsonld.items() if k != "@context"}, faq]}
    obrazek = f'{manifest["bazaAdresu"]}/assets/karty/rodzina-{jezyk}.png'
    witryna["image"] = obrazek
    return kanoniczny, strona(jezyk=jezyk, tytul=n["tytul_mapy"], opis=n["opis_mapy"],
                              kanoniczny=kanoniczny, alternatywny=alternatywny,
                              tresc=tresc, glebokosc=glebokosc, manifest=manifest,
                              jsonld=jsonld,
                              dodatkowa_glowa=(f'<meta property="og:image" content="{obrazek}">'
                                               '<meta property="og:image:width" content="1200">'
                                               '<meta property="og:image:height" content="630">'
                                               '<meta name="twitter:card" content="summary_large_image">'),
                              nawigacja=gora(jezyk, glebokosc, alternatywny, manifest, mapa=False),
                              stopka_html=stopka(jezyk, glebokosc, manifest))


def podstrona(a, jezyk, manifest, apki, *, kanoniczny=None, sciezka=None,
              glebokosc=None, temat=None):
    n = NAPISY[jezyk]
    wlasny, wlasna_glebokosc = sciezki(a["slug"], jezyk)
    sciezka = sciezka or wlasny
    glebokosc = wlasna_glebokosc if glebokosc is None else glebokosc
    kanoniczny = kanoniczny or wlasny
    alternatywny = sciezki(a["slug"], "en" if jezyk == "pl" else "pl")[0]
    t = a["teksty"][jezyk]
    pary = pytania_apki(a, jezyk)
    katalog = a["dokumenty"][jezyk]
    ikona = wzgledny(glebokosc, f"assets/ikony/{a['slug']}.webp")

    if a["wSklepie"]:
        # Ikonka platformy stoi MIĘDZY przyciskiem a ceną, bo w tej kolejności pada
        # pytanie: gdzie to kupić, na czym to działa, ile kosztuje. Na stronę produktową
        # trafia się wprost z wyszukiwarki, z pominięciem mapy rodziny — a do 16.09.2026
        # nie padało tu ani razu słowo „iOS", „iPhone" ani „Android" (zmierzone: zero
        # trafień w wytworze). Jedynym sygnałem był napis na przycisku.
        sklep = (f'<p class="sklep">{przyciski_sklepow(a, n)}'
                 f'{znaczki_platform(a, jezyk)}'
                 f'<span class="znacznik">{e(n["darmowa"])}</span></p>')
    else:
        sklep = (f'<p class="sklep"><span class="znacznik">{e(n["wkrotce"])}</span></p>'
                 f'<p class="podtytul">{e(n["wkrotce_opis"])}</p>')

    dokumenty = "".join(
        f'<li><a href="{wzgledny(glebokosc, katalog)}/{plik}">{e(n[klucz])}</a></li>'
        for plik, klucz in (("privacy.html", "polityka"), ("terms.html", "warunki"),
                            ("support.html", "wsparcie")))

    rodzenstwo = "".join(
        f'<li><a href="{wzgledny(glebokosc, sciezki(inna["slug"], jezyk)[0])}">'
        f'{e(inna["teksty"][jezyk]["nazwa"])}</a> — {e(inna["teksty"][jezyk]["podtytul"])}</li>'
        for inna in apki if inna["slug"] != a["slug"])

    # Wyjście na stronę tematyczną tej aplikacji — tylko wtedy, gdy taka strona
    # istnieje. Stoi obok opisu, a nie wyłącznie w stopce, bo czytelnik podstrony
    # jest dokładnie tym, kto chce przeczytać o samym materiale.
    nauka_html = ""
    if temat:
        cel_tematu = wzgledny(glebokosc, sciezki_tematu(temat, jezyk)[0])
        nauka_html = (f"<h2>{e(n['nauka_link'])}</h2><ul class=\"zwykla\">"
                      f'<li><a href="{cel_tematu}">'
                      f'{e(n["temat_%s_tytul" % temat["klucz"]])}</a> – '
                      f'{e(n["temat_%s_opis" % temat["klucz"]])}</li></ul>')

    opis, naglowki = opis_html(t["opis"])
    # Spis sekcji tylko wtedy, gdy jest co spisywać: przy trzech nagłówkach byłby
    # dłuższy niż droga, którą skraca. Próg wzięty z pomiaru — opisy rodziny mają
    # od czterech do trzynastu sekcji.
    spis_sekcji = ""
    if len(naglowki) >= 4:
        pozycje = "".join(f'<li><a href="#{adres}">{tekst}</a></li>'
                          for adres, tekst in naglowki)
        spis_sekcji = (f'<nav class="spis-sekcji" aria-label="{e(n["opis_naglowek"])}">'
                       f"<ul>{pozycje}</ul></nav>")

    tresc = (
        f'<div class="szyld"><img src="{ikona}" alt="" width="72" height="72">'
        + f'<div><h1>{e(t["nazwa"])}<span class="jp" lang="ja">{e(a["japonska"])}</span></h1>'
        + f'<p class="podtytul">{e(t["podtytul"])}</p></div></div>'
        + sklep
        + f'<p class="lead">{e(t["promo"])}</p>'
        + galerie(a, jezyk, glebokosc)
        + f"<h2>{e(n['opis_naglowek'])}</h2>"
        + spis_sekcji
        + opis
        + f'<p class="podtytul">{e(n["opis_stopka"])}</p>'
        # Powtórzone wyjście do sklepu. Opis ma 2200–4100 znaków, więc czytelnik,
        # który doszedł tu do końca, miał dotąd jedyny przycisk App Store dziesięć
        # przewinięć wyżej — i musiał po niego wrócić na samą górę.
        + sklep
        + faq_html(pary, jezyk)
        + nauka_html
        + f"<h2>{e(n['dokumenty'])}</h2><ul class=\"zwykla\">{dokumenty}</ul>"
        + f"<h2>{e(n['rodzina'])}</h2><ul class=\"zwykla\">{rodzenstwo}</ul>")

    jsonld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": t["nazwa"],
        "alternateName": a["japonska"],
        "applicationCategory": "EducationalApplication",
        # Z listy sklepów, nie z literału. Przy jednym sklepie wychodzi "iOS",
        # czyli dokładnie to, co stało tu wpisane ([poz. 307]).
        "operatingSystem": ", ".join(SYSTEM[p] for p in PLATFORMY
                                     if w_sklepie(a, p)),
        "url": f"{manifest['bazaAdresu']}/{publiczny(kanoniczny)}",
        "description": metadane.pierwsze_zdanie(t["opis"]),
        "inLanguage": ["pl", "en"],
        "author": {"@type": "Person", "name": manifest["autor"]},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "PLN"},
    }
    if a["wSklepie"]:
        adresy = [link_sklepu(a, p) for p in PLATFORMY if w_sklepie(a, p)]
        # Tablica nawet przy jednym adresie? Nie: schema.org przyjmuje oba
        # kształty, a skalar przy jednym sklepie zostawia dzisiejszy wytwór
        # nietknięty. Tablica pojawia się dopiero, gdy jest co wyliczać.
        jsonld["sameAs"] = adresy[0] if len(adresy) == 1 else adresy
        jsonld["installUrl"] = jsonld["sameAs"]

    # Kadry sklepowe w danych strukturalnych. Leżą na dysku od 09.09.2026, a nie
    # deklarowaliśmy ani jednego — to najmocniejsze z pól, których tu brakowało.
    kadry = zrzuty_apki(a["slug"], jezyk)
    if kadry:
        jsonld["screenshot"] = [
            f"{manifest['bazaAdresu']}/assets/zrzuty/{a['slug']}/{jezyk}/{plik}"
            for plik in kadry]
    # Data ostatniej zmiany metadanych — ta sama, którą niesie mapa witryny.
    # `datePublished` świadomie pominięte: daty premiery w repozytorium nie ma,
    # a zmyślona data w danych strukturalnych jest gorsza niż jej brak.
    if a.get("data"):
        jsonld["dateModified"] = a["data"]

    tytul = f'{t["nazwa"]} – {t["podtytul"]}'
    obrazek = f'{manifest["bazaAdresu"]}/assets/karty/{a["slug"]}-{jezyk}.png'

    # `image` opisuje aplikację, więc musi stać na węźle `SoftwareApplication`.
    # Przypisanie po owinięciu w `@graph` sadzało je w korzeniu, obok `@context`,
    # gdzie nie opisuje niczego — zmierzone 09.09.2026 na wygenerowanym HTML-u.
    jsonld["image"] = obrazek

    # Okruszek: `Rodzina → Aplikacja`. Google pokazuje go w wynikach zamiast adresu,
    # a wizualnym odpowiednikiem jest „← Wszystkie aplikacje" w pasku — drugiego
    # okruszka na stronie nie stawiamy, bo mówiłby dokładnie to samo.
    baza = manifest["bazaAdresu"]
    dom = f"{baza}/" if jezyk == "pl" else f"{baza}/en/"
    okruszek = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": n["tytul_mapy"], "item": dom},
        {"@type": "ListItem", "position": 2, "name": t["nazwa"],
         "item": f"{baza}/{publiczny(kanoniczny)}"}]}
    wezly = [{k: v for k, v in jsonld.items() if k != "@context"}, okruszek]
    if pary:
        wezly.append(faq_jsonld(pary))
    jsonld = {"@context": "https://schema.org", "@graph": wezly}
    return sciezka, strona(jezyk=jezyk, tytul=tytul, opis=meta_opis(t),
                           kanoniczny=kanoniczny, alternatywny=alternatywny,
                           tresc=tresc, glebokosc=glebokosc, manifest=manifest,
                           jsonld=jsonld,
                           nawigacja=gora(jezyk, glebokosc, alternatywny, manifest),
                           stopka_html=stopka(jezyk, glebokosc, manifest, a["kontakt"]),
                           dodatkowa_glowa=(f'<meta property="og:image" content="{obrazek}">'
                                            '<meta property="og:image:width" content="1200">'
                                            '<meta property="og:image:height" content="630">'
                                            '<meta name="twitter:card" content="summary_large_image">'))


def galerie(a, jezyk, glebokosc):
    """Galeria na platformę — i **nagłówek tylko wtedy, gdy platform jest więcej niż jedna**.

    To jest cała odpowiedź na „wersje będą się różnić, więc i kadry będą inne".
    Przy jednej platformie wynik jest znak w znak dzisiejszy: żadnego `<h3>`, żadnej
    zmiany w dziesięciu stojących stronach. Przy dwóch czytelnik widzi, na co patrzy,
    zamiast zgadywać, czy zrzut z iPhone'a opisuje jego telefon.
    """
    maja = [p for p in PLATFORMY if zrzuty_apki(a["slug"], jezyk, p)]
    if not maja:
        return ""
    if len(maja) == 1:
        return galeria(a, jezyk, glebokosc, maja[0])
    n = NAPISY[jezyk]
    return "".join(f"<h3>{e(n[URZADZENIE[p]])}</h3>" + galeria(a, jezyk, glebokosc, p)
                   for p in maja)


def galeria(a, jezyk, glebokosc, platforma="ios"):
    """Kadry sklepowe na stronie — te same, które widać w App Store.

    Podstrona była do 09.09.2026 ścianą tekstu: opis ze sklepu i nic więcej.
    Kadry są już zrobione, przejrzane i wgrane do App Store, więc **jedyne, co
    tu przybywa, to znacznik `<img>`** — nie nowa treść.

    Pusta, gdy zrzutów nie zaimportowano: aplikacja bez galerii ma wyglądać jak
    strona bez galerii, a nie jak strona z dziurą.
    """
    pliki = zrzuty_apki(a["slug"], jezyk, platforma)
    if not pliki:
        return ""
    n = NAPISY[jezyk]
    podpisy = a["podpisy"][jezyk]
    kadry = []
    for plik in pliki:
        naglowek, podtytul = podpisy.get(Path(plik).stem,
                                         (f'{a["teksty"][jezyk]["nazwa"]} – {n["zrzut"]}', ""))
        pod = jezyk if platforma == "ios" else f"{platforma}/{jezyk}"
        sciezka = wzgledny(glebokosc, f"assets/zrzuty/{a['slug']}/{pod}/{plik}")
        podpis = f"<strong>{e(naglowek)}</strong>"
        if podtytul:
            podpis += f"<br>{e(podtytul)}"
        # `alt` jest **pusty**, bo podpis pod kadrem niesie dokładnie ten sam tekst
        # i stoi obok, widoczny. Do 09.09.2026 były to dwie kopie tego samego zdania
        # i czytnik ekranu czytał każdy kadr dwa razy.
        #
        # Kadr jest **linkiem do pełnego pliku**: na stronie ma 210 px, więc tekstu
        # na zrzucie telefonu nie da się przeczytać, a powiększenia nie było żadnego.
        kadry.append(f'<figure><a href="{sciezka}">'
                     f'<img src="{sciezka}" alt="" width="420" height="912" loading="lazy">'
                     f"</a><figcaption>{podpis}</figcaption></figure>")
    # `tabindex` na karuzeli: bez niego pas z kadrami przewija się wyłącznie
    # myszą i gestem, a klawiaturą nie da się go ruszyć wcale.
    return (f"<h2>{e(n['naglowek_zrzutow'])}</h2>"
            f'<div class="zrzuty" tabindex="0" role="group" '
            f'aria-label="{e(n["naglowek_zrzutow"])}">{"".join(kadry)}</div>')


def spis_dokumentow(apki, jezyk, manifest):
    n = NAPISY[jezyk]
    kanoniczny = "dokumenty.html" if jezyk == "pl" else "en/documents.html"
    alternatywny = "en/documents.html" if jezyk == "pl" else "dokumenty.html"
    glebokosc = 0 if jezyk == "pl" else 1
    sekcje = []
    for a in apki:
        t = a["teksty"][jezyk]
        pozycje = []
        for plik, klucz in (("privacy.html", "polityka"), ("terms.html", "warunki"),
                            ("support.html", "wsparcie")):
            pary = " · ".join(
                f'<a href="{wzgledny(glebokosc, a["dokumenty"][j])}/{plik}">'
                f'{e(NAPISY[j][klucz])}</a>' for j in JEZYKI)
            pozycje.append(f"<li>{pary}</li>")
        sekcje.append(f'<h2>{e(t["nazwa"])}<span class="jp" lang="ja">{e(a["japonska"])}</span></h2>'
                      f'<ul class="zwykla">{"".join(pozycje)}</ul>')

    # Aplikacje spoza rodziny japońskiej mają w tym repozytorium tylko dokumenty
    # i tylko w jednym języku. Stoją w spisie, bo dziś stoją w `index.html`, a spis,
    # który gubi aplikację, jest gorszy od spisu pisanego ręcznie.
    for inna in manifest.get("pozostale", []):
        pozycje = []
        for jezyk_dok, katalog in inna["dokumenty"].items():
            for plik, klucz in (("privacy.html", "polityka"), ("terms.html", "warunki"),
                                ("support.html", "wsparcie")):
                pozycje.append(f'<li><a href="{wzgledny(glebokosc, katalog)}/{plik}">'
                               f'{e(NAPISY[jezyk_dok][klucz])}</a></li>')
        sekcje.append(f'<h2>{e(inna["nazwa"][jezyk])}</h2>'
                      f'<ul class="zwykla">{"".join(pozycje)}</ul>')

    tresc = (f"<h1>{e(n['spis_tytul'])}</h1>"
             + f'<p class="podtytul">{e(n["spis_opis"])}</p>'
             + "".join(sekcje))
    return kanoniczny, strona(jezyk=jezyk, tytul=n["spis_tytul"], opis=n["spis_opis"],
                              kanoniczny=kanoniczny, alternatywny=alternatywny,
                              tresc=tresc, glebokosc=glebokosc, manifest=manifest,
                              nawigacja=gora(jezyk, glebokosc, alternatywny, manifest),
                              stopka_html=stopka(jezyk, glebokosc, manifest,
                                                 spis_dokumentow=True))


ZNACZNIK_OD = "<!-- ADRESY: sekcja poniżej jest generowana przez Tools/generuj-strony.py, nie edytować ręcznie -->"
ZNACZNIK_DO = "<!-- /ADRESY -->"


def readme(apki, manifest, poprzedni):
    """Sekcja „Adresy" w README — wyliczona, a nie przepisana.

    README tego repozytorium opisywał **siedem aplikacji przy dzisiejszych
    dziesięciu**: nie dlatego, że ktoś się pomylił, tylko dlatego, że lista
    aplikacji w prozie starzeje się przy każdym wydaniu, a nikt jej nie pilnuje.
    Lista wyliczona z manifestu starzeje się razem z manifestem.
    """
    baza = manifest["bazaAdresu"]
    wiersze = ["", "## Adresy", "",
               "| Aplikacja | Strona produktowa | Dokumenty |", "|---|---|---|"]
    for a in apki:
        strony = (f'[pl]({baza}/{publiczny(sciezki(a["slug"], "pl")[0])}) · '
                  f'[en]({baza}/{publiczny(sciezki(a["slug"], "en")[0])})')
        dokumenty = " · ".join(f'[{j}]({baza}/{a["dokumenty"][j]}/privacy.html)' for j in JEZYKI)
        stan = "" if a["wSklepie"] else " *(przed wydaniem)*"
        wiersze.append(f'| {a["teksty"]["pl"]["nazwa"]} {a["japonska"]}{stan} '
                       f"| {strony} | {dokumenty} |")
    for inna in manifest.get("pozostale", []):
        dokumenty = " · ".join(f'[{j}]({baza}/{k}/privacy.html)'
                               for j, k in inna["dokumenty"].items())
        wiersze.append(f'| {inna["nazwa"]["pl"]} | – | {dokumenty} |')
    wiersze += ["",
                f"Mapa rodziny: [pl]({baza}/) · [en]({baza}/en/). "
                f"Spis dokumentów: [pl]({baza}/dokumenty.html) · "
                f"[en]({baza}/en/documents.html).", ""]

    przed, _, reszta = poprzedni.partition(ZNACZNIK_OD)
    _, _, po = reszta.partition(ZNACZNIK_DO)
    return przed + ZNACZNIK_OD + "\n".join(wiersze) + ZNACZNIK_DO + po


# Roboty, które zbierają teksty dla modeli językowych. Wymienione z nazwy, a nie
# zostawione pod `User-agent: *`, bo **`Google-Extended` i `Applebot-Extended` nie są
# robotami indeksującymi** — to osobne tokeny zgody na użycie treści przez model.
# Ogólne `Allow: /` nie mówi o nich nic; wpis z nazwą mówi wprost.
ROBOTY_AI = ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
             "PerplexityBot", "Google-Extended", "Applebot-Extended", "CCBot",
             "Bingbot", "Amazonbot", "meta-externalagent")


# ---------------------------------------------------------------- strony tematyczne

# Pięć tematów, po jednym na aplikację, która ma eksport przejrzanej treści.
#
# **Adres jest tym, co ktoś wpisuje w wyszukiwarkę**, a nie nazwą aplikacji:
# nikt nie szuka „Kazoekaty", szuka „jaki licznik do butelek". Slug polski
# i angielski są różne z tego samego powodu i nie muszą być swoimi tłumaczeniami.
#
# Kolejność jest kolejnością nauki, nie alfabetem: partykuły niosą zdanie,
# formy je odmieniają, liczniki wchodzą wszędzie, a mowa potoczna i keigo są
# dwoma końcami tej samej skali rejestru.
TEMATY = (
    # `powiazane` — **wyjście na stronę o tej samej rzeczy widzianej z innej
    # strony**. Wypisane z ręki, tak jak adresy, i z tego samego powodu: para
    # „partykuły" i „szkielet zdania N5" to dwie strony pełne は・が・を, a bez
    # powiedzianej hierarchii wyszukiwarka sama zgaduje, która jest tą właściwą
    # na „japanese particles". Zmierzone 13.09: wszystkie 32 strony sekcji miały
    # zero linków do innego tematu.
    {"apka": "joshi", "klucz": "partykuly",
     "sciezka": {"pl": "nauka/partykuly-japonskie", "en": "en/learn/japanese-particles"},
     "powiazane": ({"klucz": "n5", "grupa": "n5.g1.particles"},)},
    # `tylko: ""` — z eksportu Kaname na tę stronę idą wyłącznie hasła bez sekcji,
    # czyli pary kontrastowe. Punkty N5 z tego samego pliku mają sekcje i trafiają
    # na strony grup niżej.
    {"apka": "kaname", "klucz": "pary", "tylko": "",
     "sciezka": {"pl": "nauka/mylace-pary", "en": "en/learn/confusing-pairs"}},
    {"apka": "katsuyokei", "klucz": "formy",
     "sciezka": {"pl": "nauka/formy-czasownika", "en": "en/learn/verb-forms"},
     "powiazane": ({"klucz": "n5", "grupa": "n5.g3.verb-forms"},)},
    {"apka": "kazoekata", "klucz": "liczniki",
     "sciezka": {"pl": "nauka/liczniki-japonskie", "en": "en/learn/japanese-counters"}},
    {"apka": "kuzushi", "klucz": "potoczny",
     "sciezka": {"pl": "nauka/mowa-potoczna", "en": "en/learn/casual-japanese"},
     "grupy": (
         {"grupa": "contraction",
          "sciezka": {"pl": "sciagniecia", "en": "contractions"}},
         {"grupa": "fusion", "sciezka": {"pl": "zlania", "en": "fusions"}},
         {"grupa": "voicing",
          "sciezka": {"pl": "udzwiecznienia", "en": "voicing"},
          "powiazane": ({"klucz": "onomatopeje", "grupa": "l2"},)},
         {"grupa": "layered", "sciezka": {"pl": "zlozone", "en": "layered"}},
         {"grupa": "omission",
          "sciezka": {"pl": "opuszczenia", "en": "omissions"}},
     )},
    # Sekcja `relation` (sytuacje) ZESZŁA 19.09.2026 z [poz. 376]: przebudowa
    # drabiny [poz. 372] przeniosła wszystkie 27 scenek na poziom piąty, czyli
    # płatny, a na stronę idzie wyłącznie materiał darmowy. W jej miejsce weszły
    # wzorce, które ta sama tura uczyniła darmowymi. Oba stare adresy nie znikają
    # — stoją dalej jako przekierowania, patrz `PRZEKIEROWANIA`.
    #
    # Kolejność kart jest kolejnością nauki: najpierw dwadzieścia słów do
    # zapamiętania (poziom 1), potem ramy, które nakłada się na dowolne słowo.
    {"apka": "keigo", "klucz": "keigo",
     "sciezka": {"pl": "nauka/keigo", "en": "en/learn/keigo"},
     "grupy": (
         {"grupa": "lexeme", "sciezka": {"pl": "slowa", "en": "words"}},
         {"grupa": "pattern", "sciezka": {"pl": "wzorce", "en": "patterns"}},
     )},
    # Sześć sekcji, nie dwie — i **oba stare adresy zostają**. Podział zapadł
    # 13.09, bo `pary-dzwieczne` i `cialo-i-samopoczucie` były najcięższymi
    # plikami witryny (86 i 60 KB przy 33 KB największej pozostałej). Oś wybiera
    # siostra w `review-content.py`, tutaj stoją tylko adresy; kubełki `l1` i `l2`
    # zachowały dawny klucz właśnie po to, żeby te dwa adresy nie zginęły —
    # poszły do Search Console 13.09.
    {"apka": "onomatope", "klucz": "onomatopeje",
     "sciezka": {"pl": "nauka/onomatopeje", "en": "en/learn/japanese-mimetics"},
     "grupy": (
         {"grupa": "l1.bol", "sciezka": {"pl": "bol", "en": "pain"}},
         {"grupa": "l1.drzenie", "sciezka": {"pl": "drzenie", "en": "shivering"}},
         {"grupa": "l1.zmeczenie", "sciezka": {"pl": "zmeczenie", "en": "tiredness"}},
         {"grupa": "l1",
          "sciezka": {"pl": "cialo-i-samopoczucie", "en": "body-and-feeling"}},
         # Obie sekcje par pocięte 13.09 na pół w kolejności gojūon — decyzja
         # Jakuba, bo znaczeniowej osi trzeciej katalog nie unosi. **Pierwsze
         # połówki zachowują dawne adresy**, drugie dostają zakres kana w slugu,
         # żeby adres mówił, gdzie się jest, a nie „część druga".
         {"grupa": "l2", "sciezka": {"pl": "pary-dzwieczne", "en": "voicing-pairs"},
          "powiazane": ({"klucz": "potoczny", "grupa": "voicing"},)},
         {"grupa": "l2.b",
          "sciezka": {"pl": "pary-dzwieczne-ta-ho", "en": "voicing-pairs-ta-ho"},
          "powiazane": ({"klucz": "potoczny", "grupa": "voicing"},)},
         {"grupa": "l2.dzwiek",
          "sciezka": {"pl": "pary-dzwiekowe", "en": "sound-pairs"},
          "powiazane": ({"klucz": "potoczny", "grupa": "voicing"},)},
         {"grupa": "l2.dzwiek.b",
          "sciezka": {"pl": "pary-dzwiekowe-ko-to", "en": "sound-pairs-ko-to"},
          "powiazane": ({"klucz": "potoczny", "grupa": "voicing"},)},
     )},
    # Temat z `grupy` nie jest stroną, tylko **rozdrożem drugiego poziomu**:
    # pod jego adresem stoją karty grup, a treść mieszka piętro niżej. Podział
    # wzięty z katalogu (`base_n5.json` ma siedem grup), nie wymyślony tutaj —
    # ale **adresy są wypisane z ręki i to jest decyzja**: slug wyliczony
    # z tytułu grupy zmieniałby się razem z tytułem, a adres jest obietnicą.
    {"apka": "kaname", "klucz": "n5",
     "sciezka": {"pl": "nauka/gramatyka-n5", "en": "en/learn/japanese-n5-grammar"},
     "grupy": (
         {"grupa": "n5.g1.particles",
          "sciezka": {"pl": "szkielet-zdania", "en": "sentence-skeleton"},
          "powiazane": ({"klucz": "partykuly"},)},
         {"grupa": "n5.g2.time-place",
          "sciezka": {"pl": "czas-i-miejsce", "en": "time-and-place"}},
         {"grupa": "n5.g3.verb-forms",
          "sciezka": {"pl": "formy-czasownika", "en": "verb-forms"},
          "powiazane": ({"klucz": "formy"},)},
         {"grupa": "n5.g4.requests",
          "sciezka": {"pl": "prosby-i-zakazy", "en": "requests-and-prohibitions"}},
         {"grupa": "n5.g5.adjectives",
          "sciezka": {"pl": "przymiotniki", "en": "adjectives"}},
         {"grupa": "n5.g6.wishes",
          "sciezka": {"pl": "checi-i-zaproszenia", "en": "wishes-and-invitations"}},
         {"grupa": "n5.g7.tone",
          "sciezka": {"pl": "powod-i-ton", "en": "reason-and-tone"}},
     )},
)

# Adresy ZDJĘTE, które mają dalej odpowiadać. Wypisane z ręki, tak jak adresy
# tematów, i z tego samego powodu: adres jest obietnicą, a te dwa stoją
# w `sitemap.xml` i w Search Console od 13.09.2026.
#
# **GitHub Pages nie umie 301** i to jest cały powód, dla którego ten mechanizm
# wygląda tak, a nie inaczej. Repertuar jest dwuelementowy: `canonical` na cudzy
# adres albo `noindex`. Bierzemy `canonical` plus odświeżenie META, bo `noindex`
# kazałby wyszukiwarce **zapomnieć** stronę, a nam zależy na czymś odwrotnym —
# żeby to, co ten adres uzbierał, przeszło na adres docelowy. Obu tych kształtów
# bramka indeksowania nie zaczepia (`indeks-witryny.py`, `spr_mapa_vs_linki`),
# więc wpisu w `Tools/indeks-wyjatki.json` dopisywać **nie wolno**: `spr_wyjatki`
# zgłosiłby go jako powód, który do niczego nie pasuje.
PRZEKIEROWANIA = (
    {"z": {"pl": "nauka/keigo/sytuacje", "en": "en/learn/keigo/situations"},
     "do": "keigo",
     "powod": "[poz. 376] — wszystkie 27 sytuacji przeszło przy [poz. 372] "
              "na poziom piąty, czyli płatny, a na stronę idzie tylko materiał darmowy"},
)

EKSPORT_SCHEMA = 1
EKSPORT_PLIK = Path("docs") / "www" / "eksport.json"

ROZDROZE = {"pl": "nauka/index.html", "en": "en/learn/index.html"}


def sciezki_tematu(temat, jezyk, grupa=None):
    """Adres tematu, a przy `grupa` — adres strony grupy pod nim."""
    czlony = [temat["sciezka"][jezyk]]
    if grupa:
        czlony.append(grupa["sciezka"][jezyk])
    sciezka = "/".join(czlony) + "/index.html"
    return sciezka, sciezka.count("/")


def jednostki_tematu(eksport, temat=None, grupa=None):
    """Hasła należące do tej strony. **Wybór jest jawny, nie domyślany.**

    Pole `grupa` w eksporcie znaczy „do jakiej sekcji katalogu należy to hasło"
    i **nie znaczy** „na jaką stronę ma iść". Joshi wpisuje tam partykułę (は, が),
    choć strona jest jedna; Kaname wpisuje grupę N5, a pary kontrastowe zostawia
    puste. Reguła „strona płaska bierze to, co grupy nie ma" wyglądała więc na
    ogólną i **wycięła stronę o partykułach z budowy** — złapane przy pierwszym
    przebiegu po zmianie, bo mapa witryny zgłosiła brakujący klucz.

    Stąd trzy przypadki, wszystkie deklarowane w `TEMATY`:

    * `grupa` podana — hasła tej grupy (strona grupy pod rozdrożem);
    * temat z `tylko` — hasła dokładnie tej sekcji (Kaname: pary, czyli `""`);
    * ani jedno, ani drugie — **wszystkie** hasła eksportu.
    """
    if grupa:
        return [j for j in eksport["jednostki"] if j.get("grupa") == grupa["grupa"]]
    if temat is not None and "tylko" in temat:
        return [j for j in eksport["jednostki"]
                if (j.get("grupa") or "") == temat["tylko"]]
    return list(eksport["jednostki"])


def nazwa_grupy(eksport, grupa, jezyk):
    """Nazwa sekcji: **z katalogu, jeśli ją ma; z `NAPISY`, jeśli nie ma**.

    Grupy N5 niosą tytuł w katalogu i są przejrzane razem z punktami, więc nazwa
    przyjeżdża w eksporcie. Rodzaje skrótu w Kuzushim to klucze techniczne
    (`contraction`, `fusion`) bez brzmienia dla czytelnika — tam nazwa jest
    tekstem własnym witryny i stoi tam, gdzie stoi cały taki tekst.
    """
    for wpis in eksport.get("grupy", ()):
        if wpis["slug"] == grupa["grupa"] and (wpis.get("nazwa") or {}).get(jezyk):
            return wpis["nazwa"][jezyk]
    # Klucz z nazwą aplikacji ma pierwszeństwo: `l1` w Onomatope znaczy co innego
    # niż `l1` gdziekolwiek indziej, a klucz ogólny podpisałby obie sekcje tak samo
    # i zrobiłby to po cichu.
    n = NAPISY[jezyk]
    return (n.get("grupa_%s_%s" % (eksport.get("apka", ""), grupa["grupa"]))
            or n.get("grupa_%s" % grupa["grupa"], grupa["grupa"]))


def opis_grupy(eksport, temat, grupa, jezyk, nazwa_g, sufiks):
    """Opis sekcji do głowy strony: **własny, jeśli ktoś go napisał**.

    Domyślnie każda sekcja dostaje ten sam ogon („Znaczenie, wyjaśnienie i zdania
    przykładowe z tłumaczeniem"), co przy dwudziestu sekcjach w dwóch językach
    daje czterdzieści stron z jednym opisem — a opis jest tym, co wyszukiwarka
    pokazuje pod tytułem. Klucz jest **opcjonalny z rozmysłu**: zdania pisze się
    po jednym, a nie hurtem, więc brak klucza nie może wstrzymywać przeliczenia.
    Które sekcje jeszcze stoją na ogonie, wypisuje bramka 19.
    """
    n = NAPISY[jezyk]
    # Ten sam odwrót co w `nazwa_grupy`: klucz z nazwą aplikacji ma pierwszeństwo,
    # bo `l2` w Onomatope znaczy co innego niż `l2` gdziekolwiek indziej; klucz ogólny
    # wystarcza tam, gdzie nazwa grupy jest sama w sobie jednoznaczna (`contraction`,
    # `relation`, `n5.g1.particles`). Brak tego odwrotu kosztował czternaście sekcji,
    # które **miały napisane opisy i dalej stały na wspólnym ogonie** — bramka 19
    # świeciła na nie, choć tekst istniał.
    wlasny = (n.get("grupa_%s_%s_opis" % (eksport.get("apka", ""), grupa["grupa"]))
              or n.get("grupa_%s_opis" % grupa["grupa"]))
    if wlasny:
        return wlasny
    return n["nauka_opis_grupy"].format(grupa=nazwa_g, sufiks=sufiks)


def grupy_zywe(temat, eksport):
    """Grupy tematu, które mają czym stanąć — w kolejności z `TEMATY`."""
    return [g for g in temat.get("grupy", ())
            if jednostki_tematu(eksport, temat, g)]


def wczytaj_eksporty(apki):
    """Eksporty przejrzanej treści z repozytoriów aplikacji — slug → zawartość.

    **Witryna nie liczy odcisków i nie umie ich policzyć.** Odcisk powstaje
    z jednostki złożonej z bazy i nakładki, a narzędzia przeglądu ośmiu sióstr
    to osiem różnych programów o różnym kształcie jednostki. Czytnik odtwarzający
    tutaj ich sposób hashowania rozjechałby się przy pierwszej zmianie u siostry
    i zrobił to **cicho**: strona nie zniknęłaby, tylko przestała odpadać przy
    rozjeździe, czyli bramka zamieniłaby się w ozdobę.

    Dlatego każda siostra ma u siebie `review-content.py --eksport-www`, który
    wypuszcza wyłącznie jednostki darmowe, zielone we wszystkich soczewkach
    i z aktualnym odciskiem. Tu czyta się gotowy plik i sprawdza jego kształt.

    Brak pliku **nie jest błędem**: aplikacja, która eksportu jeszcze nie ma,
    po prostu nie dostaje strony tematycznej. Bramka 12 to nazywa.
    """
    eksporty = {}
    for a in apki:
        plik = a["repoSciezka"] / EKSPORT_PLIK
        if not plik.is_file():
            continue
        eksporty[a["slug"]] = json.loads(plik.read_text(encoding="utf-8"))
    return eksporty


def tematy_zywe(apki, eksporty):
    """Tematy, które mają czym stanąć: (temat, aplikacja, eksport)."""
    po_slugu = {a["slug"]: a for a in apki}
    zywe = []
    for temat in TEMATY:
        eksport = eksporty.get(temat["apka"])
        apka = po_slugu.get(temat["apka"])
        if not eksport or not apka:
            continue
        if temat.get("grupy"):
            if not grupy_zywe(temat, eksport):
                continue
        elif not jednostki_tematu(eksport, temat):
            continue
        zywe.append((temat, apka, eksport))
    return zywe


# Notacja czytań rodziny: `見[み]る`. Podstawą jest **ciąg znaków chińskich tuż
# przed nawiasem** — 家族[かぞく] daje 家族, a お名前[なまえ] zostawia お poza
# rubinem, bo お kanji nie jest. Znak 々 (powtórzenie) wchodzi do podstawy.
CZYTANIE = re.compile(r"([一-鿿々]+)\[([^\]]+)\]")


def ruby_html(tekst: str) -> str:
    """Notacja czytań → `<ruby>`. Bez notacji zwraca tekst bez zmian.

    Escape idzie **przed** podmianą, nie po: inaczej znaczniki, które ta funkcja
    dokłada, same zostałyby zescape'owane. Nawiasy kwadratowe nie są dla HTML-a
    znakami szczególnymi, więc kolejność jest bezpieczna.
    """
    return CZYTANIE.sub(r"<ruby>\1<rt>\2</rt></ruby>", e(tekst))


def haslo_html(jednostka, jezyk, n, zajete, powtorzone=frozenset()):
    """Jedno hasło strony tematycznej. Zwraca `(kotwica, etykieta, html)`.

    Kotwica bierze się z **identyfikatora jednostki**, nie z nagłówka: nagłówki
    są po japońsku, a `kotwica()` sprowadza tekst do liter łacińskich i z 本
    zrobiłaby „sekcja", z 冊 „sekcja-2" i tak dalej. Identyfikatory katalogów są
    ASCII i mówią, co to jest (`c.hon`, `p.teiru.teru`, `l2.lex.ossharu`).
    """
    termin = jednostka.get("termin") or ""
    nazwa = jednostka["nazwa"][jezyk]
    kot = kotwica(jednostka["id"], zajete)

    # **Nagłówek zawsze w jednym kształcie: termin, czytanie, nazwa w jednej
    # linii** — rozstrzygnięcie Jakuba z 13.09, wzorem strony o partykułach.
    #
    # Pierwsza wersja miała dwa kształty: sam znak, a nazwa pod nim w osobnym
    # podpisie, i tylko przy terminie powtórzonym nazwa wchodziła do nagłówka.
    # Powód tamtego wyjątku był realny (が niesie pięć ról, więc pięć sekcji
    # miało identyczny nagłówek i spis „は が が が が を に に に に に で で へ",
    # po którym nie da się nawigować) — ale lekarstwo rozjeżdżało wygląd między
    # stronami. Jeden kształt załatwia oba: nazwa stoi w nagłówku zawsze, więc
    # żaden nagłówek nie powtarza sąsiada, a spis czyta się tak samo wszędzie.
    #
    # Czytanie tylko wtedy, gdy mówi coś ponad sam termin: licznik つ ma czytanie
    # „つ" i plakietka powtarzałaby to, co stoi tuż obok.
    czytanie = jednostka.get("czytanie")
    czlony = []
    if termin:
        czlony.append(f'<span lang="ja">{ruby_html(termin)}</span>')
        if czytanie and czytanie != termin:
            czlony.append(f'<span class="znacznik" lang="ja">{e(czytanie)}</span>')
    if nazwa:
        # `ruby_html`, nie `e` — bo spis tuż niżej renderuje tę samą etykietę
        # przez `ruby_html(etykieta)`, więc nagłówek eskejpujący ją na płasko
        # pokazywał notację zamiast czytania. Wyszło 19.09.2026 przy wzorcach
        # Keigo: `お茶[ちゃ]` stało w `<h2>` z nawiasami, a w spisie nad nim
        # poprawnie. Zasięg zmierzony na wytworze: **dwa nagłówki na całej
        # witrynie** — dotąd żadna `nazwa` nie niosła czytań, bo tytuły sytuacji
        # i glosy leksemów są prozą. Bez notacji `ruby_html` zwraca to samo,
        # co `e`, więc pozostałe 88 stron nie drgnie.
        czlony.append(("· " if termin else "") + ruby_html(nazwa))
    naglowek = " ".join(czlony)
    etykieta = " · ".join(c for c in (termin, nazwa) if c)

    czesci = [f'<h2 id="{kot}">{naglowek}</h2>']

    if jednostka["glosa"][jezyk]:
        czesci.append(f'<p class="lead">{ruby_html(jednostka["glosa"][jezyk])}</p>')

    for akapit in jednostka["wyjasnienie"][jezyk].split("\n\n"):
        if akapit.strip():
            czesci.append(f"<p>{ruby_html(akapit.strip())}</p>")

    # Budowa formy — po jednej regule na klasę odmiany. Etykieta klasy stoi nad
    # regułą tą samą szarą linią co sytuacja nad zdaniem: reguła „Odpada る,
    # dochodzi końcówka grzecznościowa" bez niej nie mówi, czego dotyczy.
    if jednostka.get("reguly"):
        czesci.append(f'<p class="podtytul">{e(n["nauka_budowa"])}</p>')
        wiersze_r = []
        for regula in jednostka["reguly"]:
            etykieta_k = n.get("klasa_%s" % regula["klasa"], regula["klasa"])
            wiersze_r.append(
                f'<li><span class="tlum">{e(etykieta_k)}</span>'
                f'{ruby_html(regula["tekst"][jezyk])}</li>')
        czesci.append(f'<ul class="przyklady">{"".join(wiersze_r)}</ul>')

    if jednostka["przyklady"]:
        czesci.append(f'<p class="podtytul">{e(n["nauka_przyklady"])}</p>')
        wiersze = []
        for p in jednostka["przyklady"]:
            wiersz = ""
            # Sytuacja **nad** zdaniem, nie pod: u Kaname zdanie kontrastowe bez niej
            # nie ma czego rozstrzygać — „あまり czy ぜんぜん" zależy od tego, ile się
            # naprawdę rozumie. Kolejność na ekranie jest kolejnością czytania.
            if (p.get("kontekst") or {}).get(jezyk):
                wiersz += f'<span class="tlum">{e(p["kontekst"][jezyk])}</span>'
            # Pełna forma przed skrótem — tylko Kuzushi ją niesie, bo tylko tam
            # nauka polega na złożeniu jednego z drugim. Strzałkę wyjaśnia zdanie
            # wprowadzające strony, więc nie dokładamy do niej etykiety.
            if p.get("jpPelne"):
                wiersz += (f'<span class="pelna" lang="ja">{ruby_html(p["jpPelne"])}'
                           f"</span> → ")
            wiersz += f'<span lang="ja">{ruby_html(p["jp"])}</span>'
            # Tłumaczenie zdania. Osobne pole od `uwaga` z rozmysłu: czytelnik bierze
            # polską linijkę pod japońskim zdaniem za tłumaczenie, więc wpisanie tam
            # uzasadnienia byłoby drobnym kłamstwem na każdej pozycji.
            if p.get(jezyk):
                wiersz += f'<span class="tlum">{e(p[jezyk])}</span>'
            if (p.get("uwaga") or {}).get(jezyk):
                wiersz += f'<span class="tlum">{e(p["uwaga"][jezyk])}</span>'
            wiersze.append(f"<li>{wiersz}</li>")
        czesci.append(f'<ul class="przyklady">{"".join(wiersze)}</ul>')

    return kot, etykieta, '<section class="haslo">%s</section>' % "".join(czesci)


def strona_tematu(temat, a, eksport, jezyk, manifest, apki, zywe=(), grupa=None):
    """Strona tematyczna: hasła z eksportu plus wyjście do aplikacji, z której są.

    Układ jest **układem strony produktowej**, celowo co do kolejności: szyld
    z ikoną, zdanie wprowadzające, spis sekcji z kotwicami, treść, wyjście do
    sklepu, stopka. Czytelnik, który przyszedł z podstrony aplikacji, ma nie
    poznać, że to inny typ strony.

    `grupa` robi z tego **stronę grupy** pod rozdrożem tematu: tytuł bierze się
    wtedy z katalogu (nazwa grupy), a nie z `NAPISY`, i dochodzi przejście do
    grupy poprzedniej i następnej — bo kolejność grup jest kolejnością nauki.
    """
    n = NAPISY[jezyk]
    inny = "en" if jezyk == "pl" else "pl"
    sciezka, glebokosc = sciezki_tematu(temat, jezyk, grupa)
    alternatywny = sciezki_tematu(temat, inny, grupa)[0]
    t = a["teksty"][jezyk]
    if grupa:
        nazwa_g = nazwa_grupy(eksport, grupa, jezyk)
        sufiks = n.get("temat_%s_sufiks" % temat["klucz"],
                       n["temat_%s_tytul" % temat["klucz"]])
        tytul = "%s – %s" % (nazwa_g, sufiks)
        opis = opis_grupy(eksport, temat, grupa, jezyk, nazwa_g, sufiks)
        # **Podtytuł na stronie mówi co innego niż `<title>` — dopóki opis jest
        # wspólnym ogonem.** Ogon powtarza nazwę sekcji, a pod nagłówkiem, który tę
        # nazwę właśnie niesie, czytało się to jak zacięcie płyty. Sekcja z własnym
        # opisem tej wady nie ma: własne zdanie mówi, o czym ta sekcja jest, więc
        # stoi i w głowie, i pod nagłówkiem — jedno zdanie zamiast dwóch do pisania.
        wlasny = (n.get("grupa_%s_%s_opis" % (eksport.get("apka", ""), grupa["grupa"]))
                  or n.get("grupa_%s_opis" % grupa["grupa"]))
        podtytul = wlasny or n["nauka_podtytul_grupy"]
    else:
        tytul = n["temat_%s_tytul" % temat["klucz"]]
        opis = n["temat_%s_opis" % temat["klucz"]]
        podtytul = opis
    ikona = wzgledny(glebokosc, f"assets/ikony/{a['slug']}.webp")

    # Które terminy powtarzają się na tej stronie — liczone przed składaniem haseł,
    # bo o kształcie nagłówka decyduje to, co stoi obok niego, a nie samo hasło.
    moje = jednostki_tematu(eksport, temat, grupa)
    liczba = {}
    for jednostka in moje:
        t_j = jednostka.get("termin") or ""
        if t_j:
            liczba[t_j] = liczba.get(t_j, 0) + 1
    powtorzone = frozenset(t_j for t_j, ile in liczba.items() if ile > 1)

    zajete, spis, hasla, etykiety = set(), [], [], []
    for jednostka in moje:
        kot, etykieta, html_hasla = haslo_html(jednostka, jezyk, n, zajete, powtorzone)
        spis.append(f'<li><a href="#{kot}">{ruby_html(etykieta)}</a></li>')
        etykiety.append(etykieta)
        hasla.append(html_hasla)

    # **Spis sekcji zawsze pionowy, jeden odnośnik pod drugim** — rozstrzygnięcie
    # Jakuba z 13.09, wzorem strony o partykułach. Pierwsza wersja przełączała
    # kształt długością etykiet: krótkie hasła (本, 〜ている) szły w wiersz, długie
    # w kolumnę. Wyglądało to na oszczędność miejsca, a dawało dwie różne
    # nawigacje na jednej witrynie i kazało czytelnikowi uczyć się ich osobno —
    # przy dwudziestu dwóch licznikach wiersz i tak zawija się w akapit, tylko
    # bez możliwości wodzenia okiem w dół.
    spis_sekcji = (f'<nav aria-label="{e(n["nauka_spis"])}">'
                   f'<ul class="zwykla">{"".join(spis)}</ul></nav>')

    if a["wSklepie"]:
        sklep = (f'<p class="sklep">{przyciski_sklepow(a, n)}'
                 f'<span class="znacznik">{e(n["darmowa"])}</span></p>')
    else:
        sklep = f'<p class="sklep"><span class="znacznik">{e(n["wkrotce"])}</span></p>'

    # Wyjście do aplikacji, z której ten materiał pochodzi. Ta sama karta, co na
    # mapie rodziny — bo to jest ta sama rzecz, a druga jej postać byłaby drugim
    # językiem wizualnym na tej samej witrynie.
    cel_apki = wzgledny(glebokosc, sciezki(a["slug"], jezyk)[0])
    karta = (f'<ul class="karty"><li class="karta">'
             f'<img src="{ikona}" alt="" width="52" height="52">'
             f'<div><a class="nazwa" href="{cel_apki}">{e(t["nazwa"])}</a>'
             f'<span class="co">{e(t["podtytul"])}</span></div></li></ul>')

    # Wyjście na pozostałe tematy. Czytelnik, który przyszedł tu po liczniki, jest
    # najbardziej prawdopodobnym czytelnikiem strony o partykułach — a bez tych
    # linków jedyną drogą dalej jest stopka. Ta sama lista co na mapie rodziny.
    # **Poprzednia i następna grupa.** Kolejność grup w katalogu jest kolejnością
    # nauki, więc czytelnik, który skończył „szkielet zdania", ma jedno kliknięcie
    # do „czasu i miejsca" — a nie drogę przez rozdroże. Na stronie płaskiej tego
    # nie ma, bo tematy nie stoją wobec siebie w żadnej kolejności.
    sasiedzi_html = ""
    if grupa:
        wszystkie = grupy_zywe(temat, eksport)
        gdzie = wszystkie.index(grupa)
        kroki = []
        if gdzie > 0:
            poprz = wszystkie[gdzie - 1]
            kroki.append(
                f'<li><a href="{wzgledny(glebokosc, sciezki_tematu(temat, jezyk, poprz)[0])}">'
                f'← {e(n["nauka_wstecz"])}: {e(nazwa_grupy(eksport, poprz, jezyk))}</a></li>')
        if gdzie + 1 < len(wszystkie):
            nast = wszystkie[gdzie + 1]
            kroki.append(
                f'<li><a href="{wzgledny(glebokosc, sciezki_tematu(temat, jezyk, nast)[0])}">'
                f'{e(n["nauka_dalej"])}: {e(nazwa_grupy(eksport, nast, jezyk))} →</a></li>')
        kroki.append(
            f'<li><a href="{wzgledny(glebokosc, sciezki_tematu(temat, jezyk)[0])}">'
            f'{e(n["temat_%s_tytul" % temat["klucz"]])}</a></li>')
        sasiedzi_html = (f'<h2>{e(n["nauka_link"])}</h2>'
                         f'<ul class="zwykla">{"".join(kroki)}</ul>')

    # **Wyjście na stronę o tej samej rzeczy, widzianej z innej strony.** Nie to
    # samo co sąsiedzi: sąsiad jest krokiem w tym samym temacie, a to jest most
    # między tematami. Powiązania są **zadeklarowane w `TEMATY`, nie domyślane** —
    # podobieństwo treści wyliczone tutaj byłoby zgadywaniem, a chodzi o zdanie,
    # które mówi czytelnikowi (i wyszukiwarce), która z dwóch stron o partykułach
    # jest tą pełną. Cel nieżywy pomija się w ciszy na stronie i głośno w bramce 18:
    # eksport siostry może zniknąć w środku jej własnej roboty i nie jest to powód,
    # żeby witryna przestała się przeliczać.
    powiazane_html = ""
    cele = (grupa or temat).get("powiazane", ())
    if cele:
        pozycje_p = []
        for cel in cele:
            wpis = next((z for z in zywe if z[0]["klucz"] == cel["klucz"]), None)
            if wpis is None:
                continue
            inny_t, _, inny_e = wpis
            inna_g = None
            if cel.get("grupa"):
                inna_g = next((g for g in grupy_zywe(inny_t, inny_e)
                               if g["grupa"] == cel["grupa"]), None)
                if inna_g is None:
                    continue
            sufiks_i = n.get("temat_%s_sufiks" % inny_t["klucz"],
                             n["temat_%s_tytul" % inny_t["klucz"]])
            if inna_g:
                napis = "%s – %s" % (nazwa_grupy(inny_e, inna_g, jezyk), sufiks_i)
                powod = n.get("powiazane_%s_%s" % (cel["klucz"], cel["grupa"]), "")
            else:
                napis = n["temat_%s_tytul" % inny_t["klucz"]]
                powod = n.get("powiazane_%s" % cel["klucz"], "")
            cel_p = wzgledny(glebokosc, sciezki_tematu(inny_t, jezyk, inna_g)[0])
            pozycje_p.append(f'<li><a href="{cel_p}">{e(napis)}</a>'
                             + (f" – {e(powod)}" if powod else "") + "</li>")
        if pozycje_p:
            powiazane_html = (f'<h2>{e(n["nauka_powiazane"])}</h2>'
                              f'<ul class="zwykla">{"".join(pozycje_p)}</ul>')

    pozostale = [] if grupa else [t for t in zywe if t[0]["klucz"] != temat["klucz"]]
    pozostale_html = ""
    if pozostale:
        pozycje_t = []
        for inny, _, _ in pozostale:
            cel_t = wzgledny(glebokosc, sciezki_tematu(inny, jezyk)[0])
            pozycje_t.append(
                f'<li><a href="{cel_t}">'
                f'{e(n["temat_%s_tytul" % inny["klucz"]])}</a> – '
                f'{e(n["temat_%s_opis" % inny["klucz"]])}</li>')
        pozostale_html = (f'<h2>{e(n["nauka_link"])}</h2>'
                          f'<ul class="zwykla">{"".join(pozycje_t)}</ul>')

    tresc = (
        f'<div class="szyld"><img src="{ikona}" alt="" width="72" height="72">'
        f'<div><h1>{e(tytul)}</h1>'
        f'<p class="podtytul">{e(podtytul)}</p></div></div>'
        + spis_sekcji
        + "".join(hasla)
        + f"<h2>{e(n['nauka_skad'])}</h2>"
        # Sama nazwa własna, bez podtytułu ze sklepu: „z darmowej części aplikacji
        # Kazoekata: Liczniki japońskie i przeszło jej przegląd" rozpada się na
        # dwukropku. Nazwa przed dwukropkiem jest tą, której aplikacja używa o sobie.
        + f'<p>{e(n["nauka_skad_opis"].format(apka=t["nazwa"].split(":")[0].strip()))}</p>'
        + karta
        + sklep
        + powiazane_html
        + sasiedzi_html
        + pozostale_html)

    baza = manifest["bazaAdresu"]
    dom = "index.html" if jezyk == "pl" else "en/index.html"
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            # `DefinedTermSet`, a nie `Article`. To nie jest artykuł, tylko zestaw
            # haseł wyjętych z katalogu aplikacji — typ ma mówić prawdę o treści,
            # bo dokładnie po to stoi w danych strukturalnych.
            {
                "@type": "DefinedTermSet",
                "name": tytul,
                "description": opis,
                "url": f"{manifest['bazaAdresu']}/{publiczny(sciezka)}",
                "inLanguage": jezyk,
                "hasDefinedTerm": [
                    {
                        "@type": "DefinedTerm",
                        "name": j.get("termin") or j["nazwa"][jezyk],
                        "description": (j["glosa"][jezyk]
                                        or j["wyjasnienie"][jezyk].split("\n\n")[0]),
                    }
                    for j in moje
                ],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": n["tytul_mapy"],
                     "item": f"{baza}/{publiczny(dom)}"},
                    {"@type": "ListItem", "position": 2, "name": n["nauka_link"],
                     "item": f"{baza}/{publiczny(ROZDROZE[jezyk])}"},
                    *([{"@type": "ListItem", "position": 3,
                        "name": n["temat_%s_tytul" % temat["klucz"]],
                        "item": f"{baza}/{publiczny(sciezki_tematu(temat, jezyk)[0])}"}]
                      if grupa else []),
                    {"@type": "ListItem", "position": 4 if grupa else 3,
                     "name": tytul,
                     "item": f"{baza}/{publiczny(sciezka)}"},
                ],
            },
        ],
    }

    karta_og = f"assets/karty/{a['slug']}-{jezyk}.png"
    dodatkowa = (f'<meta property="og:image" content="{baza}/{karta_og}">'
                 '<meta property="og:image:width" content="1200">'
                 '<meta property="og:image:height" content="630">'
                 '<meta name="twitter:card" content="summary_large_image">')

    return sciezka, strona(
        jezyk=jezyk, tytul=tytul, opis=opis, kanoniczny=sciezka,
        alternatywny=alternatywny, tresc=tresc, glebokosc=glebokosc,
        manifest=manifest, jsonld=jsonld, dodatkowa_glowa=dodatkowa,
        nawigacja=gora(jezyk, glebokosc, alternatywny, manifest,
                       powrot=(wzgledny(glebokosc, sciezki_tematu(temat, jezyk)[0]),
                               n.get("temat_%s_sufiks" % temat["klucz"],
                                     n["temat_%s_tytul" % temat["klucz"]])) if grupa
                       else (wzgledny(glebokosc, ROZDROZE[jezyk]), n["nauka_link"])),
        stopka_html=stopka(jezyk, glebokosc, manifest, kontakt=a["kontakt"]))


def rozdroze_tematu(temat, a, eksport, jezyk, manifest):
    """Rozdroże drugiego poziomu: karty grup jednego tematu.

    Istnieje, bo siedem grup N5 dołożonych wprost do `/nauka/` zrobiłoby z niego
    listę trzynastu pozycji, w której sześć tematów i siedem grup jednego tematu
    stoi obok siebie jako równe — a nie są równe. Rozdroże trzyma poziomy osobno:
    `/nauka/` mówi „o czym", a to piętro „w jakiej kolejności".
    """
    n = NAPISY[jezyk]
    inny = "en" if jezyk == "pl" else "pl"
    sciezka, glebokosc = sciezki_tematu(temat, jezyk)
    alternatywny = sciezki_tematu(temat, inny)[0]
    t = a["teksty"][jezyk]
    tytul = n["temat_%s_tytul" % temat["klucz"]]
    opis = n["temat_%s_opis" % temat["klucz"]]
    ikona = wzgledny(glebokosc, f"assets/ikony/{a['slug']}.webp")
    baza = manifest["bazaAdresu"]
    dom = "index.html" if jezyk == "pl" else "en/index.html"

    karty = []
    for grupa in grupy_zywe(temat, eksport):
        cel = wzgledny(glebokosc, sciezki_tematu(temat, jezyk, grupa)[0])
        nazwa = nazwa_grupy(eksport, grupa, jezyk)
        # Podpis karty to **terminy z grupy**, nie zdanie o niej: „は, が, を, に…"
        # mówi czytelnikowi więcej niż każda proza, którą moglibyśmy tu dopisać,
        # i nie jest ani jednym nowym słowem — stoi w katalogu.
        terminy = [j["termin"] for j in jednostki_tematu(eksport, temat, grupa)
                   if j.get("termin")]
        podpis = ", ".join(terminy[:8]) + ("…" if len(terminy) > 8 else "")
        karty.append(
            f'<li class="karta"><img src="{ikona}" alt="" width="52" height="52">'
            f'<div><a class="nazwa" href="{cel}">{e(nazwa)}</a>'
            f'<span class="co" lang="ja">{e(podpis)}</span></div></li>')

    tresc = (f'<div class="szyld"><img src="{ikona}" alt="" width="72" height="72">'
             f'<div><h1>{e(tytul)}</h1>'
             f'<p class="podtytul">{e(opis)}</p></div></div>'
             f'<ul class="karty">{"".join(karty)}</ul>'
             f"<h2>{e(n['nauka_skad'])}</h2>"
             f'<p>{e(n["nauka_skad_opis"].format(apka=t["nazwa"].split(":")[0].strip()))}</p>')

    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i,
                 "name": nazwa_grupy(eksport, grupa, jezyk),
                 "url": f"{baza}/{publiczny(sciezki_tematu(temat, jezyk, grupa)[0])}"}
                for i, grupa in enumerate(grupy_zywe(temat, eksport), start=1)]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": n["tytul_mapy"],
                 "item": f"{baza}/{publiczny(dom)}"},
                {"@type": "ListItem", "position": 2, "name": n["nauka_link"],
                 "item": f"{baza}/{publiczny(ROZDROZE[jezyk])}"},
                {"@type": "ListItem", "position": 3, "name": tytul,
                 "item": f"{baza}/{publiczny(sciezka)}"}]},
        ],
    }
    dodatkowa = (f'<meta property="og:image" content="{baza}/assets/karty/'
                 f'{a["slug"]}-{jezyk}.png">'
                 '<meta property="og:image:width" content="1200">'
                 '<meta property="og:image:height" content="630">'
                 '<meta name="twitter:card" content="summary_large_image">')

    return sciezka, strona(
        jezyk=jezyk, tytul=tytul, opis=opis, kanoniczny=sciezka,
        alternatywny=alternatywny, tresc=tresc, glebokosc=glebokosc,
        manifest=manifest, jsonld=jsonld, dodatkowa_glowa=dodatkowa,
        nawigacja=gora(jezyk, glebokosc, alternatywny, manifest,
                       powrot=(wzgledny(glebokosc, ROZDROZE[jezyk]), n["nauka_link"])),
        stopka_html=stopka(jezyk, glebokosc, manifest, kontakt=a["kontakt"]))


def rozdroze_nauki(zywe, jezyk, manifest):
    """Rozdroże `/nauka/`: pięć kart, po jednej na temat.

    Istnieje po to, żeby strony tematyczne nie były sierotami. Lekcja z 09.09:
    69 dokumentów prawnych stało bez jednego wyjścia na witrynę, a wchodził tam
    kupujący z App Store. Strona bez wejścia jest stroną, której nie ma.
    """
    n = NAPISY[jezyk]
    sciezka = ROZDROZE[jezyk]
    alternatywny = ROZDROZE["en" if jezyk == "pl" else "pl"]
    glebokosc = sciezka.count("/")

    karty = []
    for temat, a, eksport in zywe:
        cel = wzgledny(glebokosc, sciezki_tematu(temat, jezyk)[0])
        ikona = wzgledny(glebokosc, f"assets/ikony/{a['slug']}.webp")
        tytul_tematu = e(n["temat_%s_tytul" % temat["klucz"]])
        opis_tematu = e(n["temat_%s_opis" % temat["klucz"]])
        karty.append(
            f'<li class="karta"><img src="{ikona}" alt="" width="52" height="52">'
            f'<div><a class="nazwa" href="{cel}">{tytul_tematu}</a>'
            f'<p>{opis_tematu}</p></div></li>')

    tresc = (f'<h1>{e(n["nauka_tytul"])}</h1>'
             f'<p class="podtytul">{e(n["nauka_opis"])}</p>'
             f'<ul class="karty">{"".join(karty)}</ul>')

    baza = manifest["bazaAdresu"]
    dom = "index.html" if jezyk == "pl" else "en/index.html"
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i,
                 "name": n["temat_%s_tytul" % temat["klucz"]],
                 "url": f"{baza}/{publiczny(sciezki_tematu(temat, jezyk)[0])}"}
                for i, (temat, _, _) in enumerate(zywe, start=1)]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": n["tytul_mapy"],
                 "item": f"{baza}/{publiczny(dom)}"},
                {"@type": "ListItem", "position": 2, "name": n["nauka_link"],
                 "item": f"{baza}/{publiczny(sciezka)}"}]},
        ],
    }

    # Karta podglądu: znak rodziny, nie żadnej z pięciu aplikacji. Rozdroże nie jest
    # o jednej z nich, a karta z cudzą ikoną obiecywałaby przy udostępnieniu co innego,
    # niż stoi pod adresem.
    karta_og = f"{baza}/assets/karty/rodzina-{jezyk}.png"
    dodatkowa = (f'<meta property="og:image" content="{karta_og}">'
                 '<meta property="og:image:width" content="1200">'
                 '<meta property="og:image:height" content="630">'
                 '<meta name="twitter:card" content="summary_large_image">')

    return sciezka, strona(
        jezyk=jezyk, tytul=n["nauka_tytul"], opis=n["nauka_opis"],
        kanoniczny=sciezka, alternatywny=alternatywny, tresc=tresc,
        glebokosc=glebokosc, manifest=manifest, jsonld=jsonld,
        dodatkowa_glowa=dodatkowa,
        nawigacja=gora(jezyk, glebokosc, alternatywny, manifest),
        stopka_html=stopka(jezyk, glebokosc, manifest, nauka=False))


def strona_przekierowania(wpis, jezyk, manifest):
    """Zdjęty adres, który dalej odpowiada i mówi, dokąd poszła treść.

    Trzy rzeczy naraz, bo każda łapie kogo innego: `canonical` mówi wyszukiwarce,
    który adres jest dziś tym właściwym, odświeżenie META przenosi przeglądarkę,
    a widoczne zdanie z odsyłaczem ratuje kogoś, komu odświeżenie nie zadziała
    (czytnik ekranu, robot, przeglądarka z wyłączonym przenoszeniem).

    **Zdania nie ma jak pominąć i to jest celowe.** Strona bez treści, która tylko
    przerzuca dalej, wygląda w oczach wyszukiwarki jak pusta — a ta ma przekazać
    dalej to, co adres uzbierał, nie zostać skasowana.
    """
    n = NAPISY[jezyk]
    temat = next(t for t in TEMATY if t["klucz"] == wpis["do"])
    cel, _ = sciezki_tematu(temat, jezyk)
    skad = wpis["z"][jezyk] + "/index.html"
    glebokosc = skad.count("/")
    inny = "en" if jezyk == "pl" else "pl"
    baza = manifest["bazaAdresu"]
    tytul_celu = n[f"temat_{temat['klucz']}_tytul"]

    tresc = (f'<h1>{e(n["przeniesione_tytul"])}</h1>'
             f'<p class="podtytul">{e(n["przeniesione_opis"])}</p>'
             f'<p><a href="{"../" * glebokosc}{publiczny(cel)}">{e(tytul_celu)}</a></p>')

    return skad, strona(
        jezyk=jezyk, tytul=n["przeniesione_tytul"],
        opis=n["przeniesione_opis"],
        # Kanonicznym jest CEL, nie ten adres — o to w tym całym pliku chodzi.
        kanoniczny=cel,
        alternatywny=wpis["z"][inny] + "/index.html",
        tresc=tresc, glebokosc=glebokosc, manifest=manifest,
        nawigacja=gora(jezyk, glebokosc, wpis["z"][inny] + "/index.html", manifest),
        stopka_html=stopka(jezyk, glebokosc, manifest),
        dodatkowa_glowa=f'<meta http-equiv="refresh" content="0; url={baza}/{publiczny(cel)}">')


def poza_mapa(apki):
    """Strony, które powstają, ale do mapy witryny nie należą.

    Dwa powody, oba inne. **Adres historyczny** (`kuzushi/index.html`) jest kopią
    podstrony pod starym adresem i ma w mapie stać jego wersja kanoniczna, nie obie.
    **`404.html`** ma ratować gościa, który trafił pod nieistniejący adres, a nie
    wchodzić do indeksu — dlatego niesie też `noindex`.

    Lista stoi w jednym miejscu, bo pierwsza wersja miała dwie i rozjechały się przy
    pierwszym dopisanym pliku: mapa pomijała `404.html`, a bramka pilnująca zgodności
    mapy ze stronami już nie.
    """
    return ({a["adresHistoryczny"] for a in apki if a.get("adresHistoryczny")}
            | {"404.html"}
            | {w["z"][j] + "/index.html" for w in PRZEKIEROWANIA for j in JEZYKI})


def robots(manifest):
    wiersze = ["# Roboty wyszukiwarek i modeli językowych są tu mile widziane.",
               "",
               "User-agent: *",
               "Allow: /",
               "",
               "# Zbieranie treści na potrzeby modeli językowych: zgoda wyrażona wprost.",
               "# Tokeny takie jak Google-Extended i Applebot-Extended nie sterują",
               "# indeksowaniem, tylko użyciem treści — i milczenie znaczy tam co innego",
               "# niż zgoda."]
    for bot in ROBOTY_AI:
        wiersze += ["", f"User-agent: {bot}", "Allow: /"]
    wiersze += ["", f"Sitemap: {manifest['bazaAdresu']}/sitemap.xml", ""]
    return "\n".join(wiersze)


def llms_txt(apki, manifest, zywe=(), zapowiedziane=()):
    """`llms.txt` — indeks strony w markdownie, pisany pod modele językowe.

    Model, który dostaje HTML, musi z niego wyłuskać treść; `llms.txt` podaje mu to
    samo bez parsowania. **Nie jest to inna treść, tylko ta sama krócej**: nazwa,
    podtytuł i tekst promocyjny każdej aplikacji, czyli dokładnie to, co stoi w mapie
    rodziny — a mapa rodziny jest tym fragmentem, który model cytuje w całości.

    Konwencja jest młoda i nikt nie zmierzył, ile daje. Kosztuje jeden plik
    wyliczany z manifestu, więc stoi tu na tej samej zasadzie co `sitemap.xml`:
    tanio i zgodnie z tym, jak te systemy szukają treści.
    """
    n = NAPISY["pl"]
    baza = manifest["bazaAdresu"]
    wiersze = [f"# {n['tytul_mapy']}", "",
               f"> {n['opis_mapy']}", "",
               "Autor: " + manifest["autor"] + ". Aplikacje na iPhone'a, po polsku "
               "i po angielsku. Każdy opis niżej jest tym samym tekstem, który stoi "
               "na karcie aplikacji w App Store.", "",
               "## Aplikacje", ""]
    for a in apki:
        t = a["teksty"]["pl"]
        stan = "" if a["wSklepie"] else f" ({NAPISY['pl']['przed_premiera']})"
        wiersze.append(f"- [{t['nazwa']}]({baza}/apps/{a['slug']}/){stan}: "
                       f"{t['podtytul']}. {t['promo']}")
    wiersze += ["", "## Wersja angielska", ""]
    for a in apki:
        t = a["teksty"]["en"]
        # Sekcja angielska do 09.09.2026 gubiła ten dopisek: cztery aplikacje czekające
        # na recenzję wyglądały po angielsku na dostępne w sklepie. Bramka 6 pilnuje
        # symetrii pytań między językami, tego nie pilnowało nic.
        stan = "" if a["wSklepie"] else f" ({NAPISY['en']['przed_premiera']})"
        wiersze.append(f"- [{t['nazwa']}]({baza}/en/apps/{a['slug']}/){stan}: "
                       f"{t['podtytul']}. {t['promo']}")
    # Strony tematyczne. Dla modelu językowego są tu najcenniejszą częścią indeksu:
    # to jedyne miejsce na witrynie, które mówi o **japońskim**, a nie o aplikacjach,
    # i jedyne, które odpowiada na pytanie zadane wprost („は czy が").
    if zywe:
        wiersze += ["", "## Nauka japońskiego", ""]
        for jezyk in JEZYKI:
            n_j = NAPISY[jezyk]
            for temat, a, eksport in zywe:
                tytul = n_j["temat_%s_tytul" % temat["klucz"]]
                opis_t = n_j["temat_%s_opis" % temat["klucz"]]
                adres = publiczny(sciezki_tematu(temat, jezyk)[0])
                wiersze.append(f"- [{tytul}]({baza}/{adres}): {opis_t}")

    # Sekcja bez adresów, bo zapowiedziane nie mają dokąd prowadzić — a jednak stoi
    # tu z nazwy. Model pytany „ile jest tych aplikacji" ma wiedzieć, że rodzina rośnie
    # do szesnastu, i nie ma skąd tego wyczytać z dziesięciu kart.
    if zapowiedziane:
        wiersze += ["", "## " + NAPISY["pl"]["dojdzie_naglowek"], "",
                    NAPISY["pl"]["dojdzie_opis"], ""]
        for z in zapowiedziane:
            t = z["teksty"]["pl"]
            wiersze.append(f"- {t['nazwa']} ({z['japonska']}): {t['podtytul']} — "
                           f"{NAPISY['pl']['w_przygotowaniu'].lower()}, bez daty")

    wiersze += ["", "## Pozostałe strony", "",
                f"- [Rozdroże stron tematycznych]({baza}/nauka/)",
                f"- [Learning Japanese, English]({baza}/en/learn/)",
                f"- [Mapa rodziny: tabela problem → aplikacja]({baza}/)",
                f"- [Family map, English]({baza}/en/)",
                f"- [Dokumenty prawne wszystkich aplikacji]({baza}/dokumenty.html)",
                f"- [Legal documents, English]({baza}/en/documents.html)",
                # Kanał zwrotny [poz. 295]. Wiersz mówi wprost „bez daty", bo czytnik
                # maszynowy dostaje tu samą nazwę strony i nie widzi jej treści —
                # a nazwa „Co dalej" bez tego ogona czyta się jak zapowiedź terminu.
                f"- [Co dalej: cztery pytania, bez daty]({baza}/co-dalej/)",
                f"- [What is next, English]({baza}/en/whats-next/)", ""]
    return "\n".join(wiersze)


def strona_autora(apki, jezyk, manifest):
    """Jedyna strona witryny pisana od siebie — i jedyny wyjątek od reguły `NAPISY`.

    **Wyjątek dotyczy autora, a nie aplikacji, i tak ma zostać.** O aplikacjach ta
    witryna nadal nie mówi ani jednego własnego zdania: obietnicy o produkcie nikt
    nie sprawdził, więc obowiązuje metadana ze sklepu. Zdanie o sobie Jakub
    potwierdza sam — i to jest cała różnica.

    Po co w ogóle: `SoftwareApplication` deklarował `author` typu `Person` bez
    żadnego adresu, a w stopce stało „Jakub Dwojak" bez linku. Przy treści
    edukacyjnej wyszukiwarka pyta, kto za nią stoi, i dotąd nie miała gdzie
    sprawdzić. Stąd też `sameAs` na profil, pod którym stoi to repozytorium.
    """
    n = NAPISY[jezyk]
    kanoniczny = "o-autorze/index.html" if jezyk == "pl" else "en/about/index.html"
    alternatywny = "en/about/index.html" if jezyk == "pl" else "o-autorze/index.html"
    glebokosc = 1 if jezyk == "pl" else 2
    baza = manifest["bazaAdresu"]

    apki_lista = "".join(
        f'<li><a href="{wzgledny(glebokosc, sciezki(a["slug"], jezyk)[0])}">'
        f'{e(a["teksty"][jezyk]["nazwa"])}</a></li>' for a in apki)

    tresc = (f"<h1>{e(n['autor_tytul'])}</h1>"
             + f'<p class="lead">{e(n["autor_kim"])}</p>'
             + f"<h2>{e(n['autor_naglowek_dlaczego'])}</h2>"
             + f"<p>{e(n['autor_dlaczego_1'])}</p><p>{e(n['autor_dlaczego_2'])}</p>"
             + f"<h2>{e(n['autor_naglowek_jak'])}</h2><p>{e(n['autor_jak'])}</p>"
             + f"<h2>{e(n['autor_naglowek_kontakt'])}</h2><p>{e(n['autor_kontakt'])}</p>"
             + f"<h2>{e(n['naglowek_kart'])}</h2>"
             + f'<ul class="zwykla">{apki_lista}</ul>')

    osoba = {"@context": "https://schema.org", "@type": "Person",
             "name": manifest["autor"],
             "url": f"{baza}/{publiczny(kanoniczny)}",
             "sameAs": [manifest["profil"]],
             "description": n["autor_opis"]}
    return kanoniczny, strona(jezyk=jezyk, tytul=n["autor_tytul"], opis=n["autor_opis"],
                              kanoniczny=kanoniczny, alternatywny=alternatywny,
                              tresc=tresc, glebokosc=glebokosc, manifest=manifest,
                              jsonld=osoba,
                              nawigacja=gora(jezyk, glebokosc, alternatywny, manifest),
                              stopka_html=stopka(jezyk, glebokosc, manifest))


def strona_co_dalej(jezyk, manifest):
    """Kanał zwrotny — [poz. 295]. Drugi i ostatni wyjątek od reguły `NAPISY`.

    **Ta strona mówi o tym, co Jakub postanowił, a nie o tym, co dostanie produkt** —
    i to jest dokładnie ta sama furtka, którą wchodzi strona o autorze. Obietnicy
    o aplikacji nie ma tu ani jednej: jest kierunek, jest brak daty i jest prośba
    o zdanie.

    Czego tu nie ma i mieć nie może, wszystko z [poz. 295]:

    - **licznika** — witryna nie ma czym zapisać (GitHub Pages), własny backend
      wymagałby CORS-u, którego brak w `japanese-be` **jest decyzją bezpieczeństwa**,
      a usługa trzecia wciągnęłaby obcy JS i podmiot przetwarzający na stronę bez
      własnej polityki prywatności;
    - **progu liczbowego** — „tysiąc i robię" jest warunkiem wewnętrznym; wypisany
      publicznie staje się obietnicą i stoi w poprzek sąsiedniej sekcji, która
      świadomie mówi „bez dat";
    - **słowa „wkrótce"** — na tej witrynie znaczy ono „złożona, czeka na recenzję
      Apple", więc użyte tutaj rozmyłoby jedyny stan, który dziś coś znaczy.

    Kanał to `mailto:` i nic więcej. **Każda oś ma własny temat**, żeby filtr
    w skrzynce liczył bez czytania treści.
    """
    n = NAPISY[jezyk]
    kanoniczny = "co-dalej/index.html" if jezyk == "pl" else "en/whats-next/index.html"
    alternatywny = "en/whats-next/index.html" if jezyk == "pl" else "co-dalej/index.html"
    glebokosc = 1 if jezyk == "pl" else 2

    adres_zwrotny = manifest["kontaktOgolny"]

    def blok(klucz, temat):
        adres = f"mailto:{adres_zwrotny}?subject={urllib.parse.quote(temat)}"
        return (f"<h2>{e(n[klucz + '_naglowek'])}</h2>"
                f"<p>{e(n[klucz])}</p>"
                f'<p><a href="{adres}">{e(n["dalej_napisz"])} →</a></p>')

    tresc = (f"<h1>{e(n['dalej_tytul'])}</h1>"
             + f'<p class="lead">{e(n["dalej_lead"])}</p>'
             + blok("dalej_android", TEMATY_MAILA[jezyk]["android"])
             + blok("dalej_jezyki", TEMATY_MAILA[jezyk]["jezyki"])
             + blok("dalej_szostka", TEMATY_MAILA[jezyk]["szostka"])
             + blok("dalej_otwarte", TEMATY_MAILA[jezyk]["otwarte"])
             + f'<p class="podtytul">{e(n["dalej_bez_licznika"])}</p>')

    # Głowa tej strony wypadła z wzorca, bo powstała jako KOPIA strony o autorze —
    # git widzi ją jako `C071`. Kopia wzięła układ i zgubiła dwie rzeczy, które
    # wzorzec ma; zmierzone 16.09.2026, dzień po postawieniu strony.
    #
    # `og:image`: wzorzec (`o-autorze`) go NIE ma i mimo to tutaj wchodzi — bo to
    # jedyna strona witryny pisana DO PODANIA DALEJ. Bez karty jest w każdym
    # komunikatorze szarym prostokątem, czyli traci dokładnie to, po co powstała.
    # Bierze kartę rodziny, a nie własną: mówi o całej rodzinie, nie o aplikacji.
    obrazek = f'{manifest["bazaAdresu"]}/assets/karty/rodzina-{jezyk}.png'
    # Tytuł z marką po myślniku. Frazy dokładać nie ma po co — nikt nie wpisuje
    # „co dalej" w wyszukiwarkę i ta strona nie ma tam czego szukać. Marka kosztuje
    # zero znaków uwagi i odróżnia zakładkę od dziesięciu innych „Co dalej".
    tytul = f'{n["dalej_tytul"]} — {n["tytul_mapy"]}'
    strona_ld = {"@context": "https://schema.org", "@type": "WebPage",
                 "name": n["dalej_tytul"],
                 "url": f'{manifest["bazaAdresu"]}/{publiczny(kanoniczny)}',
                 "description": n["dalej_opis"],
                 "inLanguage": "pl-PL" if jezyk == "pl" else "en-US",
                 "isPartOf": {"@type": "WebSite",
                              "name": n["tytul_mapy"],
                              "url": manifest["bazaAdresu"]},
                 "author": {"@type": "Person", "name": manifest["autor"],
                            "url": f'{manifest["bazaAdresu"]}/'
                                   f'{publiczny("o-autorze/index.html" if jezyk == "pl" else "en/about/index.html")}'}}
    return kanoniczny, strona(jezyk=jezyk, tytul=tytul, opis=n["dalej_opis"],
                              kanoniczny=kanoniczny, alternatywny=alternatywny,
                              tresc=tresc, glebokosc=glebokosc, manifest=manifest,
                              jsonld=strona_ld,
                              dodatkowa_glowa=(f'<meta property="og:image" content="{obrazek}">'
                                               '<meta property="og:image:width" content="1200">'
                                               '<meta property="og:image:height" content="630">'
                                               '<meta name="twitter:card" content="summary_large_image">'),
                              nawigacja=gora(jezyk, glebokosc, alternatywny, manifest),
                              stopka_html=stopka(jezyk, glebokosc, manifest,
                                                 co_dalej=False))


def strona_404(apki, manifest, zywe=()):
    """Strona 404 — po przenosinach domeny jest realnie potrzebna.

    W obiegu krąży dwadzieścia starych adresów z App Store Connect i nieznana liczba
    linków do plików, które przez lata zmieniały ścieżki (dokumenty dostały wersję
    w adresie, §6b). Domyślna strona GitHuba nie ma **ani jednego linku** do rodziny,
    więc każdy taki gość i każdy crawler kończy w ślepym zaułku.

    `noindex` jest tu celowo: strona ma ratować gościa, a nie wchodzić do indeksu.
    """
    n = NAPISY["pl"]
    baza = manifest["bazaAdresu"]
    pozycje = "".join(
        f'<li><a href="{baza}/apps/{a["slug"]}/">{e(a["teksty"]["pl"]["nazwa"])}</a> — '
        f'{e(a["teksty"]["pl"]["podtytul"])}</li>' for a in apki)
    # Ta strona obiecuje „poniżej wszystko, co tu jest" i obietnica ma zostać
    # prawdziwa: od 13.09.2026 witryna ma też strony tematyczne, więc pominięcie
    # ich zamieniłoby zdanie wyżej w nieprawdę.
    tematy_html = ""
    if zywe:
        pozycje_t = "".join(
            f'<li><a href="{baza}/{publiczny(sciezki_tematu(temat, "pl")[0])}">'
            f'{e(n["temat_%s_tytul" % temat["klucz"]])}</a></li>'
            for temat, _, _ in zywe)
        tematy_html = (f'<h2>{e(n["nauka_link"])}</h2>'
                       f'<ul class="zwykla">{pozycje_t}</ul>')

    tresc = ("<h1>Nie ma takiej strony</h1>"
             '<p class="podtytul">Adres mógł się zmienić — dokumenty prawne dostały numer '
             "wersji w adresie, a cała witryna przeniosła się na tę domenę. Poniżej "
             "wszystko, co tu jest.</p>"
             f'<h2>{e(n["naglowek_kart"])}</h2><ul class="zwykla">{pozycje}</ul>'
             f'{tematy_html}'
             f'<h2>{e(n["dokumenty"])}</h2><ul class="zwykla">'
             f'<li><a href="{baza}/dokumenty.html">{e(n["spis_tytul"])}</a></li>'
             f'<li><a href="{baza}/">{e(n["tytul_mapy"])}</a></li></ul>')
    return strona(jezyk="pl", tytul="Nie ma takiej strony",
                  opis="Adres nie istnieje. Spis wszystkich aplikacji i dokumentów rodziny.",
                  kanoniczny="404.html", alternatywny="en/index.html",
                  tresc=tresc, glebokosc=0, manifest=manifest,
                  # Do 09.09.2026 pasek na 404 miał pusty lewy `<span>`: jako
                  # jedyna strona witryny nie niosła znaku ani powrotu — czyli
                  # dokładnie tam, gdzie gość jest zgubiony, brakowało wyjścia.
                  nawigacja=gora("pl", 0, "en/index.html", manifest),
                  stopka_html=stopka("pl", 0, manifest),
                  dodatkowa_glowa='<meta name="robots" content="noindex">')


def sitemap(strony, manifest):
    wpisy = []
    for adres, data in strony:
        wpisy.append("  <url>\n"
                     f"    <loc>{manifest['bazaAdresu']}/{publiczny(adres)}</loc>\n"
                     f"    <lastmod>{data}</lastmod>\n"
                     "  </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(wpisy) + "\n</urlset>\n")


# ---------------------------------------------------------------- ikony

def ikony(apki, zapisuj):
    """Ikona 180×180 na aplikację, przeskalowana z zasobu 1024×1024.

    Skalowanie idzie przez `sips`, a wynik nie musi być bajt w bajt ten sam przy
    każdym wywołaniu — dlatego plik powstaje **tylko wtedy, gdy zmienił się skrót
    źródła**, zapisany obok w `zrodla.json`. Bez tego `--powtarzalnie` mierzyłby
    determinizm `sips`, a nie generatora.
    """
    katalog = KORZEN / "assets" / "ikony"
    rejestr = katalog / "zrodla.json"
    stare = json.loads(rejestr.read_text(encoding="utf-8")) if rejestr.exists() else {}
    nowe, zrobione = dict(stare), []
    for a in apki:
        zrodlo = a["repoSciezka"] / a["ikona"]
        if not zrodlo.exists():
            raise SystemExit(f"{a['slug']}: brak ikony {zrodlo}")
        skrot = hashlib.sha256(zrodlo.read_bytes()).hexdigest()[:16]
        cel = katalog / f"{a['slug']}.webp"
        nowe[a["slug"]] = skrot
        if cel.exists() and stare.get(a["slug"]) == skrot:
            continue
        if not zapisuj:
            zrobione.append(a["slug"])
            continue
        katalog.mkdir(parents=True, exist_ok=True)
        do_webp(zrodlo, cel, dluzszy_bok=180)
        zrobione.append(a["slug"])
    if zapisuj and nowe != stare:
        katalog.mkdir(parents=True, exist_ok=True)
        rejestr.write_text(json.dumps(nowe, ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
    return zrobione


# ---------------------------------------------------------------- pytania i odpowiedzi

# **Pytania piszemy my, odpowiedzi nigdy.** To jest cała granica tej sekcji i jedyny
# powód, dla którego wolno ją było dopisać obok reguły „treść pochodzi z metadanych".
# Modele odpowiadające na pytania cytują tekst zbudowany jako pytanie i odpowiedź —
# a my mamy odpowiedzi już napisane i przejrzane, tylko rozsypane po opisie sklepowym.
# Pytanie **wskazuje** sekcję opisu; jeśli aplikacja takiej sekcji nie ma, pytanie się
# nie pojawia. Nigdy nie powstaje odpowiedź, której nie ma w sklepie.
#
# Klucze to fragmenty NAGŁÓWKÓW sekcji, wielkimi literami, bo tak są pisane w opisach.
PYTANIA = (
    {
        "pl": "Czego uczy {nazwa}?",
        "en": "What does {nazwa} teach?",
        "otwarcie": True,                     # zdania przed pierwszym nagłówkiem
    },
    {
        "pl": "Ile kosztuje {nazwa}?",
        "en": "What does {nazwa} cost?",
        "klucze_pl": ("DARMOW", "ZA DARMO", "PREMIUM", "KUPIĆ", "PŁATNE", "ZAKUP"),
        "klucze_en": ("FREE", "PAID", "PREMIUM", "BUY", "COSTS", "PURCHASE"),
    },
    {
        "pl": "Czy działa bez internetu i bez konta?",
        "en": "Does it work without an account or a network?",
        "klucze_pl": ("BEZ KONTA", "BEZ SIECI", "PRYWAT"),
        "klucze_en": ("NO ACCOUNT", "NO NETWORK", "PRIVAC", "PRIVATE", "OFFLINE"),
    },
    {
        "pl": "W jakich językach działa?",
        "en": "What languages does it support?",
        "klucze_pl": ("POLSKI I ANGIELSKI",),
        "klucze_en": ("POLISH AND ENGLISH", "ENGLISH AND POLISH"),
    },
    {
        "pl": "Czego ta aplikacja nie robi?",
        "en": "What does this app not do?",
        "klucze_pl": ("CZEGO NIE", "NIE ZROBI", "BEZ ĆWICZEŃ", "CZEGO TU NIE MA"),
        "klucze_en": ("WHAT IT DOES NOT", "DOES NOT DO", "NO PRACTICE", "WHAT IS NOT HERE",
                      "WHAT IT WILL NOT"),
    },
)

# Odpowiedź to najwyżej tyle akapitów sekcji. Sekcje bywają długie, a odpowiedź
# w wynikach wyszukiwania i tak jest przycinana — lepiej przyciąć świadomie.
AKAPITOW_W_ODPOWIEDZI = 2


def pytania_apki(a, jezyk):
    """Pary pytanie–odpowiedź dla jednej aplikacji, wyłącznie z jej opisu."""
    sekcje = metadane.sekcje(a["teksty"][jezyk]["opis"])
    nazwa = a["teksty"][jezyk]["nazwa"].split(":")[0].split(" —")[0].strip()
    pary = []
    for wzorzec in PYTANIA:
        if wzorzec.get("otwarcie"):
            akapity = next((tresc for naglowek, tresc in sekcje if naglowek is None), [])
        else:
            klucze = wzorzec[f"klucze_{jezyk}"]
            akapity = []
            for naglowek, tresc in sekcje:
                if naglowek and any(k in naglowek for k in klucze):
                    akapity.extend(tresc)
        if not akapity:
            continue
        pary.append((wzorzec[jezyk].format(nazwa=nazwa), akapity[:AKAPITOW_W_ODPOWIEDZI]))
    return pary


def faq_html(pary, jezyk):
    if not pary:
        return ""
    pozycje = []
    for pytanie, akapity in pary:
        odpowiedz = "".join(akapit_html(a) for a in akapity)
        pozycje.append(f"<details><summary>{e(pytanie)}</summary>{odpowiedz}</details>")
    return f"<h2>{e(NAPISY[jezyk]['naglowek_faq'])}</h2>" + "".join(pozycje)


def faq_jsonld(pary):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": pytanie,
             "acceptedAnswer": {"@type": "Answer", "text": "\n\n".join(akapity)}}
            for pytanie, akapity in pary],
    }


# ---------------------------------------------------------------- zrzuty

ZRZUTOW_NA_STRONE = 5
KATALOGI_JEZYKA = {"pl": "pl", "en": "en-US"}


def do_webp(zrodlo: Path, cel: Path, dluzszy_bok: int):
    """Skaluje `sips`-em i zapisuje jako WebP przez `cwebp`.

    **Format, nie wymiary, był tu całym kosztem.** Kadr sklepowy ma tło z gradientem
    i zrzut telefonu — jako PNG waży 168 kB przy 912 px dłuższego boku, jako WebP
    przy tej samej wielkości **16 kB**. Trzy kadry na stronie to było pół megabajta
    obrazków na stronę tekstową; teraz jest 48 kB. Ikona: 20 kB → 4 kB.

    Wymiary zostają: strona pokazuje kadr na 210 px, więc na ekranie o podwójnej
    gęstości potrzeba 420 px szerokości, czyli 912 px wysokości przy proporcji kadru
    sklepowego. Zmniejszanie poniżej tego dałoby rozmyty obrazek na telefonie —
    a to jest urządzenie, na którym te strony się ogląda.

    **Karty `og:image` zostają PNG-iem** i to jest świadome: czytniki podglądu
    w komunikatorach obsługują WebP nierówno, a karta ma się pokazać wszędzie.
    """
    posrednie = cel.with_suffix(".posrednie.png")
    subprocess.run(["sips", "-Z", str(dluzszy_bok), str(zrodlo), "--out", str(posrednie)],
                   check=True, capture_output=True)
    subprocess.run(["cwebp", "-q", "80", "-quiet", str(posrednie), "-o", str(cel)],
                   check=True, capture_output=True)
    posrednie.unlink()


def podpisy_kadrow(repo: Path, jezyk: str, ref: str | None = None) -> dict:
    """Podpisy kadrów z `docs/app-store/screenshots.json` — po identyfikatorze kadru.

    **To jest źródło, a nie kopia.** Ten sam plik składa kadry (`screenshots.sh`),
    rysuje na nich nagłówek (`make-store-frame.swift`) i jest pilnowany bramką
    treści (`check-store-frames.swift`) — czyli tekst, który widać na obrazku
    w App Store, bierze się dokładnie stąd.

    Pierwsza wersja tej funkcji czytała sekcję `Screenshot copy` z pliku markdown
    i na tej podstawie ogłosiłem, że **siedem aplikacji nie ma podpisów**. Nieprawda:
    sekcja w markdownie jest ręczną kopią i ma ją troje z dziesięciu, a `copy`
    w `screenshots.json` mają **wszystkie dziesięć, w obu językach, co do kadru**.
    Czytanie kopii zamiast źródła dało fałszywy brak — i fałszywą zaległość.

    Klucz to identyfikator kadru (`01-dzis`), a nie jego pozycja na liście:
    kolejność kadrów w sklepie już raz się przesunęła (Joshi, „kadry 2–6 to dawne
    1–5"), a identyfikator to przetrwał.
    """
    if ref is None:
        plik = repo / "docs" / "app-store" / "screenshots.json"
        if not plik.exists():
            return {}
        tresc = plik.read_text(encoding="utf-8")
    else:
        wynik = subprocess.run(["git", "-C", str(repo), "show",
                                "%s:docs/app-store/screenshots.json" % ref],
                               capture_output=True, text=True)
        if wynik.returncode != 0:
            return {}
        tresc = wynik.stdout
    lokalizacja = {"pl": "pl", "en": "en-US"}[jezyk]
    podpisy = {}
    for kadr in json.loads(tresc).get("shots", []):
        tresc = (kadr.get("copy") or {}).get(lokalizacja) or {}
        naglowek = (tresc.get("headline") or "").strip()
        podtytul = (tresc.get("subtitle") or "").strip()
        if naglowek:
            podpisy[kadr["id"]] = (naglowek, podtytul)
    return podpisy


def zrzuty_apki(slug: str, jezyk: str, platforma: str = "ios") -> list:
    """Zrzuty już zaimportowane do repozytorium stron, po kolei.

    **iOS zostaje pod dzisiejszą ścieżką bez poziomu platformy** i to jest decyzja, nie
    niedokończenie: przeniesienie stu kilkudziesięciu plików po to, żeby ścieżka wyglądała
    symetrycznie, zmieniłoby wytwór dziesięciu stron i zamazało jedyną bramkę tej zmiany
    — że wytwór nie drgnął. Android dostaje własny poziom od razu, bo tam nie ma czego
    przenosić.
    """
    katalog = (KORZEN / "assets" / "zrzuty" / slug / jezyk if platforma == "ios"
               else KORZEN / "assets" / "zrzuty" / slug / platforma / jezyk)
    if not katalog.exists():
        return []
    return sorted(p.name for p in katalog.glob("*.webp"))


def importuj_zrzuty(apki, manifest, zapisuj):
    """Wciąga kadry sklepowe z repozytoriów aplikacji i skaluje je na stronę.

    **Osobne polecenie, nie część zwykłego przebiegu**, i to jest cała ostrożność
    tej funkcji: w większości repozytoriów `docs/app-store/screenshots/` jest
    **ignorowany przez gita** — kadry są artefaktem odtwarzanym z App Store Connect.
    Gdyby galeria powstawała z tego, co akurat leży w drzewie obok, przebieg na
    maszynie bez kadrów wyczyściłby ją po cichu. Strony rysują więc galerię z tego,
    co już zostało zaimportowane do `assets/zrzuty/`.
    """
    katalog = KORZEN / "assets" / "zrzuty"
    rejestr = katalog / "zrodla.json"
    stare = json.loads(rejestr.read_text(encoding="utf-8")) if rejestr.exists() else {}
    nowe, zrobione, brakujace, usuniete = dict(stare), [], [], []
    for a in apki:
        repo = ZRODLA / a.get("repoZrzuty", a["repo"])
        for jezyk, katalog_jezyka in KATALOGI_JEZYKA.items():
            zrodlo = repo / "docs" / "app-store" / "screenshots" / katalog_jezyka
            if not zrodlo.exists():
                brakujace.append(f"{a['slug']} {jezyk}")
                continue
            kadry = sorted(zrodlo.glob("*.png"))[:ZRZUTOW_NA_STRONE]
            cel_katalog = katalog / a["slug"] / jezyk
            # Sprzątanie po ZMIANIE NUMERACJI, a nie po zmianie pliku — i to jest
            # cała ta pętla. Kadry mają w nazwie pozycję (`03-dlaczego`), więc
            # dołożenie jednego przesuwa wszystkie następne; import dokładał wtedy
            # nowe nazwy i ZOSTAWIAŁ stare obok. Galeria brała je razem (`sorted`
            # po nazwie), a bramka podpisów czerwieniła się na plik, którego
            # w źródle już nie ma — i tym samym BLOKOWAŁA CAŁY GENERATOR, bo
            # `bledy` zatrzymują zapis. Zmierzone 16.09.2026 na Keigo: trzy pliki
            # z 09.09 przeżyły dołożenie kadru `03-dlaczego` ([poz. 279]).
            oczekiwane = {kadr.stem + ".webp" for kadr in kadry}
            for zbedny in sorted(cel_katalog.glob("*.webp")) if cel_katalog.exists() else []:
                if zbedny.name in oczekiwane:
                    continue
                usuniete.append(f"{a['slug']}/{jezyk}/{zbedny.stem}")
                nowe.pop(f"{a['slug']}/{jezyk}/{zbedny.stem}", None)
                if zapisuj:
                    zbedny.unlink()
            for kadr in kadry:
                klucz = f"{a['slug']}/{jezyk}/{kadr.stem}"
                skrot = hashlib.sha256(kadr.read_bytes()).hexdigest()[:16]
                cel = cel_katalog / f"{kadr.stem}.webp"
                nowe[klucz] = skrot
                if cel.exists() and stare.get(klucz) == skrot:
                    continue
                zrobione.append(klucz)
                if not zapisuj:
                    continue
                cel_katalog.mkdir(parents=True, exist_ok=True)
                do_webp(kadr, cel, dluzszy_bok=912)
    if zapisuj and nowe != stare:
        katalog.mkdir(parents=True, exist_ok=True)
        rejestr.write_text(json.dumps(nowe, ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
    return zrobione, brakujace, usuniete


# ---------------------------------------------------------------- karty do podglądu

KARTA_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#faf9f9"/>
  <rect x="0" y="0" width="1200" height="10" fill="#a34f5a"/>
  <clipPath id="rog"><rect x="90" y="175" width="280" height="280" rx="62" ry="62"/></clipPath>
  <image x="90" y="175" width="280" height="280" clip-path="url(#rog)"
         xlink:href="data:image/png;base64,{ikona}"/>
  <text x="440" y="285" font-family="Helvetica Neue, Helvetica, Arial, sans-serif"
        font-size="{stopien}" font-weight="600" fill="#1c1c1e">{nazwa}</text>
  <text x="440" y="345" font-family="Helvetica Neue, Helvetica, Arial, sans-serif"
        font-size="36" fill="#6b6b70">{podtytul}</text>
  <text x="440" y="430" font-family="Helvetica Neue, Helvetica, Arial, sans-serif"
        font-size="28" fill="#a34f5a">jd-japanese.pl</text>
</svg>
"""


ZNAK_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="180" height="180" viewBox="0 0 180 180">
  <rect width="180" height="180" rx="40" ry="40" fill="#a34f5a"/>
  <text x="90" y="122" font-family="Helvetica Neue, Helvetica, Arial, sans-serif"
        font-size="92" font-weight="600" fill="#ffffff" text-anchor="middle">jd</text>
</svg>
"""

ZNAK_ROZMIARY = (48, 180)


def znak(zapisuj):
    """Znak witryny: kafelek w pasku nawigacji i ikona karty przeglądarki.

    **Czego tu wcześniej nie było w ogóle: favicony.** Google pokazuje ikonę witryny
    obok wyniku na telefonie, a karta przeglądarki stała pusta. Nie jest to nowa
    tożsamość wizualna — litery `jd` i barwa `#a34f5a` stoją już na kartach `og:image`
    razem z napisem `jd-japanese.pl`, a zaokrąglony kwadrat powtarza kształt ikon
    aplikacji na stronie. Znak zbiera to, co już jest, w jedno miejsce.

    Dwa rozmiary: **48 px, bo tyle Google wymaga jako minimum** i lubi wielokrotności
    48, oraz 180 px na kafelek iOS i na pasek przy podwójnej gęstości.

    Jak przy kartach: plik powstaje **tylko przy zmianie skrótu wejścia**, bo
    `rsvg-convert` nie gwarantuje powtarzalnego bajtu, a `--powtarzalnie` mierzy
    determinizm generatora, nie konwertera.
    """
    katalog = KORZEN / "assets"
    rejestr = katalog / "znak.json"
    skrot = hashlib.sha256(ZNAK_SVG.encode()).hexdigest()[:16]
    stare = json.loads(rejestr.read_text(encoding="utf-8")) if rejestr.exists() else {}
    zrobione = []
    for bok in ZNAK_ROZMIARY:
        cel = katalog / f"znak-{bok}.png"
        klucz = f"znak-{bok}"
        if cel.exists() and stare.get(klucz) == skrot:
            continue
        zrobione.append(klucz)
        if not zapisuj:
            continue
        katalog.mkdir(parents=True, exist_ok=True)
        zrodlo = katalog / ".znak.svg"
        zrodlo.write_text(ZNAK_SVG, encoding="utf-8")
        subprocess.run(["rsvg-convert", "-w", str(bok), "-h", str(bok),
                        "-o", str(cel), str(zrodlo)], check=True, capture_output=True)
        zrodlo.unlink()
    # `/favicon.ico` w korzeniu — bo przeglądarka sięga po ten adres **sama**, nawet
    # gdy nie zrozumiała znacznika w głowie, i to jest jedyna droga do ikony, która
    # nie zależy od niczego w HTML-u. `sips` robi z PNG-a poprawny zasób ikony
    # Windows, co potwierdza `file`; `rsvg-convert` tego formatu nie umie.
    ico = KORZEN / "favicon.ico"
    if not ico.exists() or stare.get("favicon") != skrot:
        zrobione.append("favicon.ico")
        if zapisuj:
            subprocess.run(["sips", "-s", "format", "ico", str(katalog / "znak-48.png"),
                            "--out", str(ico)], check=True, capture_output=True)
    if zapisuj and zrobione:
        rejestr.write_text(json.dumps({**{f"znak-{b}": skrot for b in ZNAK_ROZMIARY},
                                       "favicon": skrot},
                                      ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    return zrobione


KARTA_RODZINY_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#faf9f9"/>
  <rect x="0" y="0" width="1200" height="10" fill="#a34f5a"/>
  <clipPath id="rog"><rect x="90" y="175" width="280" height="280" rx="62" ry="62"/></clipPath>
  <image x="90" y="175" width="280" height="280" clip-path="url(#rog)"
         xlink:href="data:image/png;base64,{znak}"/>
  <text x="440" y="290" font-family="Helvetica Neue, Helvetica, Arial, sans-serif"
        font-size="56" font-weight="600" fill="#1c1c1e">{tytul}</text>
  <text x="440" y="430" font-family="Helvetica Neue, Helvetica, Arial, sans-serif"
        font-size="28" fill="#a34f5a">jd-japanese.pl</text>
</svg>
"""


def karta_rodziny(zapisuj):
    """Karta podglądu mapy rodziny — jedyna strona, która jej nie miała.

    Udostępniony link do `jd-japanese.pl` dawał dotąd goły tekst, bo `og:image`
    stało wyłącznie na dwudziestu podstronach aplikacji. Karta powstaje tą samą
    drogą co tamte i z tych samych składników: znak witryny zamiast ikony
    aplikacji, nazwa mapy zamiast nazwy apki. Ani jednego nowego napisu.
    """
    katalog = KORZEN / "assets" / "karty"
    rejestr = katalog / "zrodla.json"
    stare = json.loads(rejestr.read_text(encoding="utf-8")) if rejestr.exists() else {}
    nowe, zrobione = dict(stare), []
    piksele = base64.b64encode((KORZEN / "assets" / "znak-180.png").read_bytes()).decode()
    for jezyk in JEZYKI:
        svg = KARTA_RODZINY_SVG.format(znak=piksele,
                                       tytul=html.escape(NAPISY[jezyk]["tytul_mapy"]))
        klucz = f"rodzina-{jezyk}"
        skrot = hashlib.sha256(svg.encode()).hexdigest()[:16]
        cel = katalog / f"{klucz}.png"
        nowe[klucz] = skrot
        if cel.exists() and stare.get(klucz) == skrot:
            continue
        zrobione.append(klucz)
        if not zapisuj:
            continue
        katalog.mkdir(parents=True, exist_ok=True)
        zrodlo = katalog / f".{klucz}.svg"
        zrodlo.write_text(svg, encoding="utf-8")
        subprocess.run(["rsvg-convert", "-w", "1200", "-h", "630",
                        "-o", str(cel), str(zrodlo)], check=True, capture_output=True)
        zrodlo.unlink()
    if zapisuj and nowe != stare:
        rejestr.write_text(json.dumps(nowe, ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
    return zrobione


def karty_og(apki, zapisuj):
    """Karty 1200×630 do podglądu w komunikatorach i w wynikach wyszukiwania.

    Do 09.09.2026 w `og:image` stała **ikona 180×180**. Serwisy społecznościowe mają
    dolny próg na obrazek karty (zwykle 200–300 px) i przy mniejszym albo pokazują
    mikro-miniaturę obok tekstu, albo nie pokazują nic — czyli link do strony
    produktowej wyglądał jak goły adres.

    Karta powstaje jako SVG i idzie przez `rsvg-convert`, bo `sips` nie umie tekstu,
    a rysowanie liter przez CoreGraphics wymagałoby własnego programu. Nazwa
    i podtytuł pochodzą — jak wszystko tutaj — z metadanych sklepowych.

    Jak przy ikonach: plik powstaje **tylko przy zmianie skrótu wejścia**, bo
    `rsvg-convert` nie gwarantuje powtarzalnego bajtu, a `--powtarzalnie` ma mierzyć
    determinizm generatora, nie konwertera.
    """
    katalog = KORZEN / "assets" / "karty"
    rejestr = katalog / "zrodla.json"
    stare = json.loads(rejestr.read_text(encoding="utf-8")) if rejestr.exists() else {}
    nowe, zrobione = dict(stare), []
    for a in apki:
        piksele = base64.b64encode((a["repoSciezka"] / a["ikona"]).read_bytes()).decode()
        for jezyk in JEZYKI:
            teksty = a["teksty"][jezyk]
            # Nazwa ma 13–29 znaków i przy 64 px najdłuższa wychodziła poza krawędź:
            # na tekst zostaje 700 px, a „Kifuku: Japanese Pitch Accent" potrzebuje
            # przy tym stopniu około 950. Stopień dobiera się długością, zamiast
            # łamać nazwę aplikacji na dwie linie.
            stopien = 64 if len(teksty["nazwa"]) <= 22 else 56 if len(teksty["nazwa"]) <= 26 else 48
            svg = KARTA_SVG.format(ikona=piksele, stopien=stopien,
                                   nazwa=html.escape(teksty["nazwa"]),
                                   podtytul=html.escape(teksty["podtytul"]))
            klucz = f"{a['slug']}-{jezyk}"
            skrot = hashlib.sha256(svg.encode()).hexdigest()[:16]
            cel = katalog / f"{klucz}.png"
            nowe[klucz] = skrot
            if cel.exists() and stare.get(klucz) == skrot:
                continue
            zrobione.append(klucz)
            if not zapisuj:
                continue
            katalog.mkdir(parents=True, exist_ok=True)
            zrodlo = KORZEN / "assets" / "karty" / f".{klucz}.svg"
            zrodlo.write_text(svg, encoding="utf-8")
            subprocess.run(["rsvg-convert", "-w", "1200", "-h", "630",
                            "-o", str(cel), str(zrodlo)], check=True, capture_output=True)
            zrodlo.unlink()
    if zapisuj and nowe != stare:
        katalog.mkdir(parents=True, exist_ok=True)
        rejestr.write_text(json.dumps(nowe, ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
    return zrobione


# ---------------------------------------------------------------- bramki

DOKUMENTY = ("privacy.html", "terms.html", "support.html")


def landmark(tresc):
    """Czy strona ma dokładnie jeden `<main>` i we właściwym miejscu.

    Audyt dostępności („One main landmark helps screen reader users navigate a web
    page") pyta o jeden landmark treści; czytnik ekranu daje wtedy skok do treści
    z pominięciem nawigacji i stopki.

    Liczy **oba** znaczniki osobno, bo samo `grep -c '<main'` przepuszcza landmark
    niezamknięty — a niezamknięty jest gorszy niż żaden: obejmuje wtedy także stopkę.
    Sprawdza też, że `<h1>` stoi w środku: nagłówek strony poza landmarkiem znaczy,
    że skok do treści mija tytuł, czyli robi dokładnie to, czemu miał zapobiec.
    """
    skargi = []
    otwarc, zamkniec = tresc.count("<main"), tresc.count("</main>")
    if (otwarc, zamkniec) != (1, 1):
        return [f"<main ×{otwarc}, </main> ×{zamkniec} zamiast po jednym"]
    otwarcie, zamkniecie = tresc.index("<main"), tresc.index("</main>")
    body = re.search(r"<body\b[^>]*>", tresc)
    stopka = re.search(r"<footer\b[^>]*>", tresc)
    if not body or otwarcie < body.end():
        skargi.append("<main> nie stoi za <body>")
    if stopka and zamkniecie > stopka.start():
        skargi.append("</main> nie stoi przed <footer>")
    if any(not otwarcie < h.start() < zamkniecie for h in re.finditer(r"<h1\b", tresc)):
        skargi.append("<h1> poza <main>")
    return skargi


def jezyk_pliku(sciezka: Path):
    """Język dokumentu wzięty z `<html lang>`, a nie z tego, w jakim leży katalogu.

    Katalogi bywają nazwane różnie w każdym repozytorium (`en/`, `1.0/en/`, a Kuzushi
    trzyma angielski w korzeniu i polski w `pl/`); atrybut `lang` jest w każdym pliku
    i mówi to samo. Wyciągnięcie języka z **treści** jest jedynym parowaniem, które
    przeżyje przeprowadzkę katalogu.
    """
    trafienie = re.search(r'<html lang="([a-z]{2})"',
                          sciezka.read_text(encoding="utf-8", errors="replace"))
    return trafienie.group(1) if trafienie else None


def bez_glowy_witryny(tresc: str) -> str:
    """Treść dokumentu bez linii, które dokłada sama witryna.

    Bramka 10 pyta, czy **tekst** dokumentu rozjechał się z kopią w repozytorium
    aplikacji. `canonical` i `robots` nie są tekstem dokumentu — są adresem, pod
    którym ta witryna go serwuje, i w repozytorium aplikacji nie mają czego szukać
    (ten sam plik stoi tam pod żadnym adresem).

    Bez tego przesiewu bramka po wstawieniu głów 09.09.2026 zgłosiła **60 rozjazdów
    zamiast 5** — czyli utopiła własny sygnał w zmianie, która treści nie dotknęła.
    **Powtórzyło się 13.09.2026 przy `hreflang`**, dokładnie tak samo: 5 → 60. Ta lista
    jest więc rejestrem, nie jednorazową łatką — każdy nowy znacznik, który witryna
    dokłada do cudzego pliku, trzeba tu dopisać, inaczej bramka przestaje mierzyć treść.
    """
    bez_linii = "\n".join(
        w for w in tresc.split("\n")
        if 'rel="canonical"' not in w and 'name="robots"' not in w
        and 'rel="icon"' not in w and 'rel="apple-touch-icon"' not in w
        and 'name="description"' not in w and 'property="og:' not in w
        and 'name="twitter:card"' not in w and 'rel="alternate"' not in w)
    # Wyjście na witrynę dopisujemy **wewnątrz** istniejącej stopki, więc przy stopce
    # jednolinijkowej siedzi w tej samej linii co `</footer>` i wycinanie po liniach
    # zabrałoby razem z nim koniec stopki. Stąd wzorzec, a nie filtr linii.
    return re.sub(r'<br><a href="https://[^"]*/apps/[^"]*">.*?</a> · '
                  r'<a href="https://[^"]*">.*?</a>', "", bez_linii)


def skrot_dokumentu(sciezka: Path) -> str:
    return hashlib.sha256(
        bez_glowy_witryny(sciezka.read_text(encoding="utf-8")).encode("utf-8")).hexdigest()


def kopie_zrodlowe(a):
    """Skróty i ścieżki dokumentów prawnych w repozytorium aplikacji.

    Zwraca (skróty → ścieżka, katalog). Pusty słownik przy braku drzewa — o czym
    bramka 10 mówi wprost, zamiast przemilczeć.
    """
    katalog = ZRODLA / a["repo"] / "docs" / "app-store"
    if not katalog.is_dir():
        return {}, katalog
    return ({skrot_dokumentu(p): p
             for p in sorted(katalog.rglob("*.html"))}, katalog)


def bramki(apki, pliki, manifest, zapowiedziane=()):
    """Wszystko, co musi być prawdą, zanim strony pojadą na serwer.

    Bramka mierzy **wytwór**, a nie zamiar: patrzy w wygenerowany HTML i w pliki
    na dysku, a nie w to, co generator zamierzał zapisać.

    Zwraca dwie listy: `bledy` **zatrzymują zapis**, `uwagi` są nazwane i wypisane,
    ale przepuszczają. Rozdział jest z pomiaru, nie z wygody: bramka 10 (rozjazd
    z kopiami w repozytoriach aplikacji) świeci na czerwono od dnia narodzin, bo
    kopie są w cudzych repozytoriach i naprawia je kto inny. Bramka blokująca,
    której nie da się dziś zazielenić, kończy tak, że ktoś ją wyłącza.
    """
    bledy, uwagi = [], []

    # 1. Każdy dokument prawny, do którego strona linkuje, musi istnieć,
    # 9. i mieć landmark `<main>` — dokumenty prawne pisze się ręcznie, więc
    #    znacznika nie pilnuje szablon. Doczepione do tej samej pętli, bo ona już
    #    wylicza dokładnie te ścieżki.
    for a in apki:
        for jezyk in JEZYKI:
            for plik in DOKUMENTY:
                sciezka = KORZEN / a["dokumenty"][jezyk] / plik
                if not sciezka.exists():
                    bledy.append(f"{a['slug']} {jezyk}: brak dokumentu {sciezka.relative_to(KORZEN)}")
                    continue
                for skarga in landmark(sciezka.read_text(encoding="utf-8")):
                    bledy.append(f"{a['slug']} {jezyk} {plik}: {skarga}")

    for inna in manifest.get("pozostale", []):
        for katalog in inna["dokumenty"].values():
            for plik in DOKUMENTY:
                sciezka = KORZEN / katalog / plik
                if not sciezka.exists():
                    bledy.append(f"{inna['slug']}: brak dokumentu {katalog}/{plik}")
                    continue
                for skarga in landmark(sciezka.read_text(encoding="utf-8")):
                    bledy.append(f"{inna['slug']} {katalog}/{plik}: {skarga}")

    # 2. Każdy link wewnętrzny musi prowadzić do pliku, który powstanie albo już jest.
    powstana = set(pliki) | {p.relative_to(KORZEN).as_posix()
                             for p in KORZEN.rglob("*.html") if ".git" not in p.parts}
    powstana |= {f"assets/ikony/{a['slug']}.webp" for a in apki}
    powstana |= {f"assets/karty/{a['slug']}-{j}.png" for a in apki for j in JEZYKI}
    powstana |= {f"assets/znak-{bok}.png" for bok in ZNAK_ROZMIARY}
    powstana |= {f"assets/karty/rodzina-{j}.png" for j in JEZYKI}
    # Kadry per platforma. iOS stoi bez poziomu platformy (patrz `zrzuty_apki`),
    # więc ścieżkę składa się tak samo jak tam — z jednego miejsca, nie z dwóch.
    powstana |= {f"assets/zrzuty/{a['slug']}/{j if pl == 'ios' else pl + '/' + j}/{p}"
                 for a in apki for j in JEZYKI for pl in PLATFORMY
                 for p in zrzuty_apki(a["slug"], j, pl)}
    for adres, tresc in pliki.items():
        if not adres.endswith(".html"):
            continue
        katalog = Path(adres).parent
        for link in re.findall(r'href="([^"#:]+)"', tresc):
            cel = (katalog / link).as_posix()
            cel = str(Path(cel).resolve().relative_to(Path(KORZEN).resolve())) \
                if Path(cel).is_absolute() else Path(cel)
            cel = Path(cel)
            czesci = []
            for czesc in cel.parts:
                if czesc == "..":
                    if czesci:
                        czesci.pop()
                elif czesc != ".":
                    czesci.append(czesc)
            docelowy = "/".join(czesci)
            # Odsyłacze mają od 16.09.2026 postać KATALOGOWĄ (`apps/kaname/`),
            # zgodną z `canonical` i mapą witryny — a ta bramka pyta o PLIK.
            # Rozwijamy więc katalog na jego `index.html`; pusty odsyłacz `./`
            # znaczy korzeń. Bez tego bramka czerwieniła się 1013 razy nad
            # stanem poprawnym, czyli dokładnie tyle, ile witryna ma odsyłaczy.
            if docelowy == "" or link.endswith("/"):
                docelowy = (docelowy + "/index.html").lstrip("/")
            if docelowy not in powstana:
                bledy.append(f"{adres}: link do nieistniejącego {docelowy}")

    # 3. Każda strona ma tytuł, opis, język i adres kanoniczny; opis mieści się w 160.
    for adres, tresc in pliki.items():
        if not adres.endswith(".html"):
            continue
        opis = re.search(r'<meta name="description" content="([^"]*)"', tresc)
        if not opis:
            bledy.append(f"{adres}: brak <meta name=description>")
        elif len(opis.group(1)) > 160:
            bledy.append(f"{adres}: opis ma {len(opis.group(1))} znaków (limit 160)")
        for czego, wzorzec in (("<title>", r"<title>[^<]+</title>"),
                               ("lang", r'<html lang="[a-z]{2}">'),
                               ("canonical", r'<link rel="canonical"')):
            if not re.search(wzorzec, tresc):
                bledy.append(f"{adres}: brak {czego}")

    # 4. Pauzy w tekście własnym generatora (§21.Z: półpauza, nie pauza).
    #    Tekstu ze sklepu bramka nie dotyczy — tam pauzy pilnują narzędzia ASC.
    for jezyk, napisy in NAPISY.items():
        for klucz, wartosc in napisy.items():
            if "—" in str(wartosc):
                bledy.append(f"NAPISY[{jezyk}][{klucz}]: pauza — zamiast półpauzy –")

    # 5. Nazwy i podtytuły nie mogą być puste ani się dublować między aplikacjami.
    for jezyk in JEZYKI:
        nazwy = {}
        for a in apki:
            nazwa = a["teksty"][jezyk]["nazwa"]
            if nazwa in nazwy:
                bledy.append(f"{jezyk}: nazwa „{nazwa}” w dwóch aplikacjach "
                             f"({nazwy[nazwa]}, {a['slug']})")
            nazwy[nazwa] = a["slug"]

    # 6. Pytania dobierają się nagłówkami sekcji opisu, a te są pisane ręcznie
    #    i osobno w każdym języku. Jeśli angielski nagłówek zmieni brzmienie, pytanie
    #    **cicho zniknie z jednej wersji językowej** — strona dalej się zbuduje, tylko
    #    będzie uboższa. Bramka porównuje liczby zamiast ufać, że nagłówki są zgodne.
    for a in apki:
        ile = {j: len(pytania_apki(a, j)) for j in JEZYKI}
        if ile["pl"] != ile["en"]:
            bledy.append(f"{a['slug']}: pytań pl={ile['pl']}, en={ile['en']} — "
                         "nagłówek sekcji w opisie rozjechał się między językami")

    # 7. Każdy kadr na stronie ma podpis w obu językach. Tekst alternatywny czyta
    #    czytnik ekranu i indeksuje wyszukiwarka, a zastępnik „zrzut ekranu" nie niesie
    #    nic — ma być widoczny jako błąd, a nie jako cichy domyślny wybór.
    for a in apki:
        for jezyk in JEZYKI:
            for plik in zrzuty_apki(a["slug"], jezyk):
                if Path(plik).stem not in a["podpisy"][jezyk]:
                    bledy.append(f"{a['slug']} {jezyk}: kadr {plik} bez podpisu "
                                 "w screenshots.json")

    # 8. Mapa witryny wymienia dokładnie te strony, które generator zapisuje.
    mapa = pliki.get("sitemap.xml", "")
    baza = manifest["bazaAdresu"] + "/"
    w_mapie = {a[len(baza):] for a in re.findall(r"<loc>([^<]*)</loc>", mapa)}
    html_pliki = {publiczny(a) for a in pliki if a.endswith(".html")}
    historyczne = {publiczny(a) for a in poza_mapa(apki)}
    if w_mapie != html_pliki - historyczne:
        bledy.append(f"sitemap.xml rozjeżdża się ze stronami: "
                     f"nadmiar {sorted(w_mapie - html_pliki)}, "
                     f"brak {sorted(html_pliki - historyczne - w_mapie)}")

    # 9 (lustro). Landmark na stronach generowanych. Dziś trzyma go **jedna linia
    #    szablonu i żaden test** — nowy szablon bez `<main>` przeszedłby bez słowa,
    #    a to jest dokładnie ta zmiana, której nikt nie zauważy przy przeglądzie.
    for adres, tresc in pliki.items():
        if adres.endswith(".html"):
            for skarga in landmark(tresc):
                bledy.append(f"{adres}: {skarga}")

    # 9 (dosprzątanie). Strony, których generator nie tworzy i których nie wymienia
    #    manifest — dziś sześć adresów nieuwersjonowanych (`kaname/privacy.html`,
    #    `bunmyaku/…`) żyjących równolegle z wersjonowanymi. Manifest ich nie zna, bo
    #    ASC wskazuje na wersjonowane; crawler i czytnik ekranu widzą je tak samo.
    #    Bez tego przebiegu zostałyby jedynymi stronami bez bramki.
    sprawdzone = set(pliki) | {(KORZEN / a["dokumenty"][j] / p).relative_to(KORZEN).as_posix()
                               for a in apki for j in JEZYKI for p in DOKUMENTY}
    sprawdzone |= {f"{k}/{p}" for inna in manifest.get("pozostale", [])
                   for k in inna["dokumenty"].values() for p in DOKUMENTY}
    for plik in sorted(KORZEN.rglob("*.html")):
        adres = plik.relative_to(KORZEN).as_posix()
        if ".git" in plik.parts or adres in sprawdzone:
            continue
        for skarga in landmark(plik.read_text(encoding="utf-8")):
            bledy.append(f"{adres}: {skarga}")

    # 10. Rozjazd z kopiami źródłowymi. Te same dokumenty prawne leżą w repozytoriach
    #     aplikacji (`<repo>/docs/app-store/**`) i to stamtąd trafiły tutaj. Dwie kopie
    #     jednego tekstu rozjeżdżają się zawsze — pytanie tylko, czy ktoś to zobaczy.
    #
    #     **Parowanie idzie po sumie kontrolnej treści, nie po mapie ścieżek.** Mapa
    #     ścieżek rozjeżdża się przy pierwszej przeprowadzce katalogu (Kaname ma dziś
    #     dwa drzewa robocze, Bunmyaku też) i wtedy bramka zaczyna kłamać o czymś
    #     zupełnie innym, niż mierzy. Dopiero gdy bliźniaka o tej samej treści nie ma,
    #     szukamy kopii po nazwie pliku i języku — po to wyłącznie, żeby **nazwać**
    #     rozjazd konkretnym plikiem zamiast napisać „coś się nie zgadza".
    for a in apki:
        skroty, katalog = kopie_zrodlowe(a)
        if not skroty:
            uwagi.append(f"{a['slug']}: brak kopii źródłowych obok — {katalog} "
                         f"{'jest puste' if katalog.is_dir() else 'nie istnieje'}")
            continue
        for jezyk in JEZYKI:
            for plik in DOKUMENTY:
                sciezka = KORZEN / a["dokumenty"][jezyk] / plik
                if not sciezka.exists():
                    continue
                if skrot_dokumentu(sciezka) in skroty:
                    continue
                kandydaci = [p for p in skroty.values()
                             if p.name == plik and jezyk_pliku(p) == jezyk]
                gdzie = ", ".join(str(p.relative_to(ZRODLA)) for p in kandydaci)
                uwagi.append(
                    f"{a['slug']} {jezyk} {plik}: kopia w repo {a['repo']} "
                    + (f"rozjechała się ({gdzie})" if kandydaci
                       else f"nie istnieje — {katalog.relative_to(ZRODLA)} nie ma "
                            f"pliku {plik} w języku {jezyk}"))

    # 11. Głowa dokumentu prawnego: `canonical` na własny adres, a przy dokumencie
    #     przestarzałym dodatkowo `noindex`. Zmierzone 09.09.2026: siedemdziesiąt
    #     dokumentów miało w `<head>` sam `<title>`, więc pierwszy obchód robota
    #     szedł w nie zamiast w dwadzieścia stron produktowych. Bramka 3 tego nie
    #     widziała, bo mierzy wyłącznie pliki, które generator wytwarza — a te są
    #     pisane ręcznie i generator ich nie dotyka.
    #
    #     Wstawia je `Tools/glowy_dokumentow.py`; tutaj tylko pomiar wytworu.
    aktualne = glowy_dokumentow.biezace(manifest)
    ctx = glowy_dokumentow.kontekst(manifest)
    baza = manifest["bazaAdresu"].rstrip("/")
    pary = glowy_dokumentow.pary_jezykowe(manifest, baza)
    for wzgledna in glowy_dokumentow.dokumenty_na_dysku():
        tresc = (KORZEN / wzgledna).read_text(encoding="utf-8")
        adres = f"{baza}/{wzgledna}"
        if f'rel="canonical" href="{adres}"' not in tresc:
            bledy.append(f"{wzgledna}: brak canonical na własny adres "
                         f"(uruchom Tools/glowy_dokumentow.py)")
        przestarzaly = wzgledna not in aktualne
        if przestarzaly and "noindex" not in tresc:
            bledy.append(f"{wzgledna}: dokument przestarzały bez noindex")
        if not przestarzaly and "noindex" in tresc:
            bledy.append(f"{wzgledna}: dokument bieżący ma noindex")
        if 'rel="icon"' not in tresc:
            bledy.append(f"{wzgledna}: brak ikony witryny "
                         f"(uruchom Tools/glowy_dokumentow.py)")
        if 'name="description"' not in tresc:
            bledy.append(f"{wzgledna}: brak opisu (uruchom Tools/glowy_dokumentow.py)")
        # Para językowa. Mierzymy **oba adresy osobno**, nie samą obecność słowa
        # `hreflang`: dokument, który wskazuje siebie jako obie wersje albo wskazuje
        # nie tego brata, przechodzi każdą bramkę pytającą „czy jest hreflang".
        # Kuzushi trzyma angielski w korzeniu, a polski w `pl/` — dokładnie tam
        # wzorzec „`/en/` znaczy angielski" robi parę na opak.
        para = pary.get(wzgledna)
        if para:
            for jezyk, adres_pary in para.items():
                if f'hreflang="{jezyk}" href="{adres_pary}"' not in tresc:
                    bledy.append(f"{wzgledna}: brak hreflang {jezyk} → {adres_pary} "
                                 f"(uruchom Tools/glowy_dokumentow.py)")
        elif "hreflang" in tresc:
            bledy.append(f"{wzgledna}: ma hreflang, a nie ma pary językowej w manifeście")
        # Wyjście na witrynę. Dokument prawny bez niego jest ślepym zaułkiem dla
        # człowieka, który przyszedł tu z App Store — a to jest ruch od kogoś,
        # kto już kupił jedną aplikację i nie widzi pozostałych dziewięciu.
        if wzgledna in ctx["apka"] and f"{baza}/" not in tresc.split("<footer")[-1]:
            bledy.append(f"{wzgledna}: stopka bez wyjścia na witrynę "
                         f"(uruchom Tools/glowy_dokumentow.py)")

    # 12. Eksport przejrzanej treści: schemat, komplet obu języków, poręczenie.
    #
    #     Witryna nie liczy odcisków — liczy je siostra, u siebie, bo tam mieszka
    #     ich definicja. Zostaje więc pomiar tego, czy plik, który dostała,
    #     w ogóle da się postawić na stronie: czy zna schemat, czy każde hasło ma
    #     nazwę w OBU językach, czy ma czym być wyjaśnione i czy niesie choć jeden
    #     odcisk. Hasło bez odcisku jest hasłem, za które nikt nie ręczy.
    #
    #     Brak eksportu **nie jest błędem** — to stan roboczy: eksport dopisuje
    #     agent biorący repozytorium swojej apki, tak samo jak przy wydaniach.
    #     Dlatego uwaga, nie błąd; ale wypisana z nazwy, bo cicha nieobecność
    #     strony tematycznej wygląda dokładnie jak jej brak w planie.
    eksporty = wczytaj_eksporty(apki)
    po_slugu = {a["slug"]: a for a in apki}
    for temat in TEMATY:
        eksport = eksporty.get(temat["apka"])
        if eksport is None:
            uwagi.append(f"{temat['apka']}: brak {EKSPORT_PLIK} — strona tematyczna "
                         f"nie powstaje (uruchom Tools/review-content.py --eksport-www)")
            continue
        if eksport.get("schemaVersion") != EKSPORT_SCHEMA:
            bledy.append(f"{temat['apka']}: eksport ma schemat "
                         f"{eksport.get('schemaVersion')}, witryna zna {EKSPORT_SCHEMA}")
            continue
        if not eksport.get("jednostki"):
            uwagi.append(f"{temat['apka']}: eksport jest pusty — strona tematyczna "
                         f"nie powstaje")
            continue
        for j in eksport["jednostki"]:
            gdzie = f"{temat['apka']}/{j.get('id', '?')}"
            if not j.get("odciski"):
                bledy.append(f"{gdzie}: hasło bez odcisku — nikt za nie nie ręczy")
            # Nagłówkiem hasła jest termin **albo** nazwa. Para kontrastowa Kaname
            # („あまり〜ない / ぜんぜん〜ない") krótkiej nazwy nie ma i mieć nie może:
            # nazwą pary jest samo zestawienie. Termin jest jeden dla obu języków,
            # więc wystarcza sam; nazwa musi być w obu, bo jest tekstem.
            if not j.get("termin") and not all(
                    (j.get("nazwa") or {}).get(jezyk) for jezyk in JEZYKI):
                bledy.append(f"{gdzie}: hasło bez nagłówka — ani terminu, "
                             f"ani nazwy w obu językach")
            for jezyk in JEZYKI:
                tresci = [(j.get("glosa") or {}).get(jezyk),
                          (j.get("wyjasnienie") or {}).get(jezyk)]
                if not any(t and t.strip() for t in tresci):
                    bledy.append(f"{gdzie}: nie ma czym wyjaśnić hasła "
                                 f"w języku {jezyk}")

    # 13. Czy eksport nie zwietrzał wobec katalogu, z którego powstał.
    #
    #     To jest bramka na klasę błędu zmierzoną 09.09.2026: **strona wyliczana
    #     psuje się w ŹRÓDLE, a nie w wytworze.** Metadane zmieniły się o 14:15,
    #     strony stały przeliczone o 10:35, dziesięć stron z dwudziestu czterech
    #     niosło stare tytuły przez pół dnia — i nie sygnalizowało tego nic, bo
    #     wszystkie bramki mierzyły wytwór i wytwór był poprawny.
    #
    #     Uwaga, nie błąd, z tego samego powodu co przy bramce 10: katalog leży
    #     w cudzym repozytorium, a agent tej apki może być w środku zmiany treści.
    #     Rozjazd ma być **widoczny i nazwany**, a nie blokować przeliczenie stron.
    for temat in TEMATY:
        eksport = eksporty.get(temat["apka"])
        a = po_slugu.get(temat["apka"])
        if not eksport or not a:
            continue
        zrodlo = eksport.get("zrodlo") or {}
        if not zrodlo.get("sciezka") or not zrodlo.get("commit"):
            uwagi.append(f"{temat['apka']}: eksport nie mówi, z jakiego commitu "
                         f"katalogu powstał — świeżości nie da się zmierzyć")
            continue
        wynik = subprocess.run(
            ["git", "-C", str(a["repoSciezka"]), "log", "-1", "--format=%H",
             "--", zrodlo["sciezka"]],
            capture_output=True, text=True)
        biezacy = (wynik.stdout or "").strip()
        if biezacy and biezacy != zrodlo["commit"]:
            uwagi.append(
                f"{temat['apka']}: eksport powstał z {zrodlo['commit'][:12]}, "
                f"a {zrodlo['sciezka']} stoi dziś na {biezacy[:12]} — przelicz "
                f"eksport (Tools/review-content.py --eksport-www)")

    # 14. Żadnej cudzej treści na stronie tematycznej.
    #
    #     Kifuku niesie `Vendor/tofugu` na CC BY-SA 4.0 i `Vendor/unidic` jako
    #     jedyna z dziesięciu. Użycie w aplikacji to co innego niż publikacja na
    #     stronie: share-alike przenosi warunki na to, co się z tego wyprowadzi.
    #     Dziś żaden temat z Kifuku nie korzysta i ta bramka jest bezczynna —
    #     stoi po to, żeby rozszerzenie listy tematów o repozytorium z `Vendor/`
    #     zatrzymało się tutaj, a nie na stronie, która już wyszła.
    for temat in TEMATY:
        a = po_slugu.get(temat["apka"])
        if a and (a["repoSciezka"] / "Vendor").exists():
            bledy.append(
                f"{temat['apka']}: repozytorium ma Vendor/ (cudza treść, możliwe "
                f"share-alike) — proweniencja wymaga sprawdzenia pozycja po pozycji, "
                f"zanim cokolwiek stąd trafi na stronę")

    # 15. Przeciek języka w eksporcie: polska nakładka wpisana w pole angielskie.
    #
    #     Bramka 12 widzi pole PUSTE, a nie pole wypełnione nie tym językiem — a to
    #     drugie jest właśnie tym, co robi katalog z niedokończoną nakładką: nakłada
    #     polski tekst jako zapasowy i **nie mówi ani słowa**. Rodzina ma tę bliznę
    #     opisaną: liczenie pokrycia po katalogu daje fałszywą zieleń.
    #
    #     Miarą są polskie znaki diakrytyczne, bo to jedyna cecha, która odróżnia
    #     oba języki maszynowo i nie da się jej pomylić z japońskim. Mierzone na
    #     eksporcie, nie na wytworze, żeby komunikat wskazywał hasło i repozytorium,
    #     a nie stronę, na której skutek widać dopiero okiem.
    POLSKIE = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")
    for temat in TEMATY:
        eksport = eksporty.get(temat["apka"])
        if not eksport or eksport.get("schemaVersion") != EKSPORT_SCHEMA:
            continue
        for j in eksport.get("jednostki", []):
            teksty = [(j.get("nazwa") or {}).get("en", ""),
                      (j.get("glosa") or {}).get("en", ""),
                      (j.get("wyjasnienie") or {}).get("en", "")]
            teksty += [p.get("en", "") for p in j.get("przyklady") or []]
            for tekst in teksty:
                if POLSKIE & set(tekst or ""):
                    bledy.append(
                        f"{temat['apka']}/{j.get('id', '?')}: polski tekst w polu "
                        f"angielskim — nakładka jest niedokończona, a nie pusta")
                    break

    # 16. Manifest wskazuje wersję STOJĄCĄ W SKLEPIE — nie najświeższą, jaką ma repo.
    #
    #     **Ta bramka została odwrócona 16.09.2026 i to jest rozstrzygnięcie, nie
    #     złagodzenie.** Do tego dnia pilnowała reguły „manifest ma wskazywać
    #     NAJŚWIEŻSZY blok" i czerwieniła się, gdy repo miało nowszy. Reguła jest
    #     dziś inna: witryna mówi to, co kupujący naprawdę zobaczy w App Store,
    #     czyli wersję `READY_FOR_SALE`. Nowszy blok w repo to **stan normalny**
    #     przez cały czas, gdy wydanie czeka w recenzji — czerwień nad nim byłaby
    #     czerwienią nad stanem poprawnym, a taka bramka uczy pomijania siebie.
    #
    #     Co ZOSTAJE błędem: numer, którego w pliku nie ma wcale, i numer, który
    #     nie jest `x.y.z`. Jedno i drugie znaczy, że strona nie ma z czego powstać.
    #
    #     Czego ta bramka **nie umie** i trzeba o tym wiedzieć: nie widzi sieci,
    #     więc nie powie, czy numer w manifeście naprawdę stoi w sklepie. Od tego
    #     jest `--sprawdz-sklep` i znacznik `sklep/<wersja>`, bez którego przebieg
    #     odmawia startu.
    #
    #     Liczą się wyłącznie bloki z polami INDEKSOWANYMI. Wersje niosące samo
    #     `whatsNew` nowszym blokiem nie są.
    POLA_SKLEPOWE = ("subtitle", "description", "keywords", "promotionalText")

    def _wersja_klucz(tekst):
        czlony = tekst.split(".")
        if len(czlony) != 3 or not all(c.isdigit() for c in czlony):
            return None
        return tuple(int(c) for c in czlony)

    for a in apki:
        if a.get("zrodlo") != "kaname" or not a.get("wersja"):
            continue
        plik = a["repoSciezka"] / "docs" / "app-store" / "version-texts.json"
        if not plik.is_file():
            continue
        dane = json.loads(plik.read_text(encoding="utf-8"))
        wskazana = _wersja_klucz(a["wersja"])
        if wskazana is None:
            bledy.append(f"{a['slug']}: `wersja` w apps.json nie jest numerem x.y.z")
            continue
        nowsze = sorted(
            k for k, blok in dane.items()
            if isinstance(blok, dict)
            and any(blok.get(pole) for pole in POLA_SKLEPOWE)
            and (_wersja_klucz(k) or (0, 0, 0)) > wskazana)
        if wskazana not in {_wersja_klucz(k) for k in dane if _wersja_klucz(k)}:
            bledy.append(
                f"{a['slug']}: apps.json wskazuje wersję {a['wersja']}, a {plik.name} "
                f"nie ma takiego bloku — strona nie ma z czego powstać")
        elif nowsze:
            uwagi.append(
                f"{a['slug']}: w repo czekają nowsze teksty ({', '.join(nowsze)}) niż wersja "
                f"sklepowa {a['wersja']} — i tak ma być, dopóki tamta wersja nie wejdzie do "
                f"sklepu. Wtedy odśwież `wersja` w apps.json i załóż znacznik sklep/<wersja>")

    # 17. Każdy klucz grupy z eksportu musi być zadeklarowany w `TEMATY`.
    #
    #     Bramka na cichą utratę treści. `jednostki_tematu()` wybiera hasła po
    #     **dokładnym** kluczu grupy, więc siostra, która przemianuje albo rozbije
    #     swoją grupę, wypycha jej hasła ze strony **bez jednego komunikatu**:
    #     strona nie znika, tylko chudnie, a wszystkie pozostałe bramki świecą
    #     zielono, bo wytwór jest poprawny. Zmierzone przy podziale Onomatope
    #     13.09: gdyby eksport oddał `l1.bol`, a ten plik o tym kluczu nie wiedział,
    #     siedem haseł zeszłoby z witryny po cichu.
    #
    #     Błąd, nie uwaga — w odróżnieniu od bramek 12 i 13 nie chodzi o cudze
    #     repozytorium w środku roboty, tylko o to, że wytwór **już** jest niepełny.
    #     Klucze zbiera się **per aplikacja, nie per temat**: Kaname stoi w `TEMATY`
    #     dwa razy (pary kontrastowe i kurs N5) i dzieli jeden eksport na dwa
    #     tematy, więc liczone per temat każdy z nich uznałby grupy drugiego za
    #     nieznane. Złapane własną bramką przy pierwszym przebiegu.
    braki = {}
    for temat in TEMATY:
        eksport = eksporty.get(temat["apka"])
        if not eksport or eksport.get("schemaVersion") != EKSPORT_SCHEMA:
            continue
        znane, wszystko = braki.setdefault(temat["apka"], (set(), False))
        if temat.get("grupy"):
            znane |= {g["grupa"] for g in temat["grupy"]}
        elif "tylko" in temat:
            znane.add(temat["tylko"])
        else:
            # Temat bez grup i bez `tylko` bierze **wszystkie** hasła eksportu,
            # więc żaden klucz nie może z niego wypaść.
            wszystko = True
        braki[temat["apka"]] = (znane, wszystko)
    for apka, (znane, wszystko) in braki.items():
        if wszystko:
            continue
        jednostki = eksporty[apka].get("jednostki", [])
        widziane = {(j.get("grupa") or "") for j in jednostki}
        for klucz in sorted(widziane - znane):
            ile = sum(1 for j in jednostki if (j.get("grupa") or "") == klucz)
            bledy.append(
                f"{apka}: eksport ma grupę {klucz!r} ({ile} haseł), "
                f"której TEMATY nie zna — te hasła nie stanęłyby na żadnej stronie")

    # 18. Powiązanie między tematami musi mieć dokąd prowadzić.
    #
    #     `powiazane` wypisuje się z ręki, więc literówka w kluczu nie ma jak
    #     wyjść inaczej: strona po prostu nie pokazuje mostu i wygląda dokładnie
    #     tak, jak wyglądała przedtem. Uwaga, nie błąd — cel przestaje być żywy
    #     także wtedy, gdy siostra chwilowo nie ma eksportu, a to stan roboczy.
    zywe_b = tematy_zywe(apki, eksporty)
    klucze_zywe = {t["klucz"]: (t, e_) for t, _, e_ in zywe_b}
    for temat in TEMATY:
        zrodla = [(temat["klucz"], temat)]
        zrodla += [("%s/%s" % (temat["klucz"], g["grupa"]), g)
                   for g in temat.get("grupy", ())]
        for skad, wpis in zrodla:
            for cel in wpis.get("powiazane", ()):
                para = klucze_zywe.get(cel["klucz"])
                if para is None:
                    uwagi.append(f"{skad}: powiązanie wskazuje temat "
                                 f"{cel['klucz']!r}, którego nie ma wśród żywych")
                    continue
                if cel.get("grupa") and not any(
                        g["grupa"] == cel["grupa"]
                        for g in grupy_zywe(para[0], para[1])):
                    uwagi.append(f"{skad}: powiązanie wskazuje grupę "
                                 f"{cel['grupa']!r} tematu {cel['klucz']!r}, "
                                 f"której nie ma wśród żywych")

    # 19. Które sekcje stoją jeszcze na wspólnym ogonie opisu.
    #
    #     Opis jest tym, co wyszukiwarka pokazuje pod tytułem, a domyślny ogon jest
    #     jeden dla wszystkich sekcji witryny. To nie jest wada wytworu, więc nie
    #     błąd — ale dług policzony, a nie pamiętany, bo pamiętany nie wraca.
    bez_opisu = []
    for temat in TEMATY:
        eksport = eksporty.get(temat["apka"])
        if not eksport or eksport.get("schemaVersion") != EKSPORT_SCHEMA:
            continue
        for g in temat.get("grupy", ()):
            if not jednostki_tematu(eksport, temat, g):
                continue
            klucze = ("grupa_%s_%s_opis" % (eksport.get("apka", ""), g["grupa"]),
                      "grupa_%s_opis" % g["grupa"])
            if not all(any(NAPISY[jezyk].get(k) for k in klucze) for jezyk in JEZYKI):
                bez_opisu.append("%s/%s" % (temat["klucz"], g["grupa"]))
    if bez_opisu:
        uwagi.append("sekcje bez własnego opisu w głowie (%d z %d): %s"
                     % (len(bez_opisu),
                        sum(len(grupy_zywe(t, e_)) for t, _, e_ in zywe_b),
                        ", ".join(bez_opisu)))

    # 20. Aplikacja zapowiedziana ma być kartą, a nie stroną.
    #
    #     Bramka na obie strony tej granicy. **W dół:** zapowiedziana nie może mieć
    #     strony produktowej ani wpisu w mapie witryny — sześć stron po jednym zdaniu
    #     to cienka treść, a nie obecność w wyszukiwarce, i dokładnie ten ruch odrzucono
    #     świadomie przy stronach long-tail. **W górę:** musi mieć nazwę i podtytuł
    #     w obu językach oraz ikonę, bo karta bez nich byłaby pustym miejscem.
    #
    #     Nazwa i podtytuł muszą być **unikalne wobec dziesiątki** z tego samego powodu
    #     co w bramce 5: dwie karty o tym samym napisie na jednej stronie są wadą, a nie
    #     dwiema aplikacjami.
    adresy_stron = set(pliki)
    for z in zapowiedziane:
        for jezyk in JEZYKI:
            strona_z = f"apps/{z['slug']}/index.html" if jezyk == "pl" \
                else f"en/apps/{z['slug']}/index.html"
            if strona_z in adresy_stron:
                bledy.append(f"{z['slug']}: zapowiedziana aplikacja ma stronę produktową "
                             f"{strona_z} — zapowiedź jest kartą, nie stroną")
            t = z["teksty"].get(jezyk) or {}
            for pole in ("nazwa", "podtytul"):
                if not (t.get(pole) or "").strip():
                    bledy.append(f"{z['slug']} {jezyk}: zapowiedź bez pola {pole}")
        zrodlo_ikony = z["repoSciezka"] / z["ikona"]
        if not zrodlo_ikony.exists():
            bledy.append(f"{z['slug']}: brak ikony {zrodlo_ikony}")

    wszystkie_napisy = {}
    for a_ in list(apki) + list(zapowiedziane):
        for jezyk in JEZYKI:
            t = a_["teksty"][jezyk]
            for pole in ("nazwa", "podtytul"):
                klucz = (jezyk, pole, (t.get(pole) or "").strip().lower())
                if not klucz[2]:
                    continue
                if klucz in wszystkie_napisy:
                    bledy.append(f"{a_['slug']} {jezyk}: {pole} „{t[pole]}” powtarza "
                                 f"{wszystkie_napisy[klucz]}")
                wszystkie_napisy[klucz] = a_["slug"]

    # 21. „Co dalej" pyta, a nie obiecuje — i mówi to w obu językach.
    #
    #     Bramka na trzy rzeczy naraz, bo każda z nich osobno wygląda niewinnie:
    #
    #     **Strona istnieje w obu językach i ma wejście.** Strona bez wejścia jest
    #     stroną, której nie ma — 09.09.2026 stało tak sześćdziesiąt dziewięć dokumentów
    #     prawnych naraz.
    #
    #     **Adres zwrotny zgadza się ze stałą.** Literówka w `mailto:` daje stronę, która
    #     wygląda poprawnie i **cicho gubi każdą odpowiedź** — a odpowiedzi są tu jedynym
    #     licznikiem, jaki ta witryna ma ([poz. 295]: „kanał TAK, publiczny licznik NIE").
    #
    #     **Treść nie niesie daty, progu ani słowa „wkrótce".** Próg „tysiąc i robię" jest
    #     warunkiem wewnętrznym z §6 `ANDROID_KIERUNEK.md`; wypisany publicznie staje się
    #     obietnicą. „Wkrótce" znaczy na tej witrynie „złożona, czeka na recenzję Apple",
    #     więc użyte tutaj rozmyłoby jedyny stan, który dziś coś znaczy.
    zakazane = re.compile(r"wkrótce|\bsoon\b|\b(19|20)\d\d\b|\b\d{3,}\b", re.IGNORECASE)
    for jezyk in JEZYKI:
        adres = "co-dalej/index.html" if jezyk == "pl" else "en/whats-next/index.html"
        tresc_strony = pliki.get(adres)
        if not tresc_strony:
            bledy.append(f"„Co dalej” {jezyk}: brak strony {adres}")
            continue
        klucze = ["dalej_tytul", "dalej_lead", "dalej_napisz", "dalej_bez_licznika"]
        for os_ in ("android", "jezyki", "szostka", "otwarte"):
            klucze += [f"dalej_{os_}", f"dalej_{os_}_naglowek"]
        for klucz in klucze:
            if not (NAPISY[jezyk].get(klucz) or "").strip():
                bledy.append(f"„Co dalej” {jezyk}: pusty napis {klucz}")
        # Adres bierze się z MANIFESTU, a `ADRES_ZWROTNY` jest drugą, niezależną prawdą.
        # Porównanie strony ze stałą, z której ta strona powstała, mierzyłoby własne
        # wejście i nie zapaliłoby się nigdy — zmierzone mutacją 16.09.2026.
        if manifest["kontaktOgolny"] != ADRES_ZWROTNY:
            bledy.append(f"adres zwrotny rozjechał się: manifest ma "
                         f"„{manifest['kontaktOgolny']}”, generator „{ADRES_ZWROTNY}”")
        for temat in TEMATY_MAILA[jezyk].values():
            oczekiwany = f"mailto:{ADRES_ZWROTNY}?subject={urllib.parse.quote(temat)}"
            if oczekiwany not in tresc_strony:
                bledy.append(f"„Co dalej” {jezyk}: brak odnośnika o temacie „{temat}”")
        # Mierzy się **treść**, a nie cały plik: `<style>` jest wpisany w stronę i niesie
        # dziesiątki liczb, więc sito puszczone na całości łapie CSS zamiast obietnicy.
        # Zmierzone przy pierwszym przebiegu tej bramki — zapaliła się na „131315”.
        srodek = re.search(r"<main\b[^>]*>(.*?)</main>", tresc_strony, re.S)
        widoczny = re.sub(r"<[^>]+>", " ", srodek.group(1) if srodek else "")
        trafienie = zakazane.search(widoczny)
        if trafienie:
            bledy.append(f"„Co dalej” {jezyk}: treść niesie „{trafienie.group(0)}” — "
                         f"ta strona nie podaje dat, progów ani terminów")
        # Wejście z każdej innej strony. Liczone na WYTWORZE, nie na wywołaniu `stopka()`:
        # parametr można ustawić i nie użyć, a link albo w HTML-u stoi, albo nie.
        cel = "co-dalej/" if jezyk == "pl" else "en/whats-next/"
        bez_wejscia = [a for a, t in pliki.items()
                       if a.endswith(".html") and a not in (adres, "404.html")
                       and f'<html lang="{NAPISY[jezyk]["html_lang"]}">' in t
                       and cel not in t]
        if bez_wejscia:
            bledy.append(f"„Co dalej” {jezyk}: {len(bez_wejscia)} stron bez wejścia "
                         f"w stopce, m.in. {bez_wejscia[0]}")

    # 22. Jawny blok `sklepy` nie rozjeżdża się z polami, które czyta reszta rodziny.
    #
    #     Dopóki aplikacja stoi w jednym sklepie, `sklepy` wyprowadza się z `appId`
    #     i `wSklepie` i **żadna wartość nie jest zapisana dwa razy** — bramka nie ma
    #     wtedy czego pilnować i słusznie milczy.
    #
    #     Blok jawny pojawia się dopiero przy drugim sklepie i **od tego momentu dwie
    #     prawdy o iOS istnieją obok siebie**. `appId` czyta jeszcze `stan-rodziny.py`
    #     i `asc-marketing-url.py`, a `wSklepie` — `japanese-tools/lib/rodzina.py`;
    #     rozjazd między manifestem a blokiem byłby wadą widoczną dopiero po stronie
    #     Apple, czyli najpóźniej jak się da.
    for a_ in apki:
        jawne = a_.get("sklepy")
        if not jawne or "ios" not in jawne:
            continue
        if jawne["ios"].get("id") != a_.get("appId"):
            bledy.append(f"{a_['slug']}: sklepy.ios.id „{jawne['ios'].get('id')}” "
                         f"rozjeżdża się z appId „{a_.get('appId')}”")
        if (jawne["ios"].get("stan") == "w-sklepie") != bool(a_.get("wSklepie")):
            bledy.append(f"{a_['slug']}: sklepy.ios.stan „{jawne['ios'].get('stan')}” "
                         f"rozjeżdża się z wSklepie={a_.get('wSklepie')}")
        for platforma, wpis in jawne.items():
            if platforma not in PLATFORMY:
                bledy.append(f"{a_['slug']}: nieznana platforma „{platforma}” w sklepy")
            elif wpis.get("stan") not in ("brak", "zlozona", "w-sklepie"):
                bledy.append(f"{a_['slug']} {platforma}: nieznany stan „{wpis.get('stan')}”")

    # 23. Ikonka platformy stoi dokładnie tam, gdzie ma, i tyle razy, ile ma.
    #
    #     Liczona na WYTWORZE i porównywana z `sklepy()` — jedynym miejscem, które wie
    #     o sklepach. Bramka, która liczyłaby manifest na własną rękę, byłaby drugą
    #     prawdą o tym samym i rozjechałaby się z pierwszą w dniu portu.
    #
    #     Niezmiennik strony produktowej jest **liczbowy, nie wpisany**: blok sklepu
    #     stoi na niej DWA razy (nad opisem i pod nim, bo opis ma 2200–4100 znaków),
    #     więc „ma być jedna ikonka" byłoby nieprawdą. Prawdą jest:
    #     `liczba opakowań × liczba platform == liczba przycisków sklepu`.
    #     Ten kształt przeżyje zarówno trzeci blok sklepu, jak i drugą platformę.
    oczekiwane = platformy_na_stronie(apki)
    mapy = {"index.html", "en/index.html"}
    for adres_, tresc in pliki.items():
        if not adres_.endswith(".html"):
            continue
        opakowan = tresc.count('class="platformy"')
        czytnikow = tresc.count('class="czytnik"')
        per_platforma = {p: tresc.count(f'data-platforma="{p}"') for p in PLATFORMY}
        if adres_ in mapy:
            for p, ile in oczekiwane.items():
                if per_platforma[p] != ile:
                    bledy.append(f"{adres_}: ikonek platformy „{p}” jest {per_platforma[p]}, "
                                 f"a aplikacji stojących w tym sklepie {ile}")
            if opakowan != sum(1 for a_ in apki if w_sklepie(a_)):
                bledy.append(f"{adres_}: opakowań ikonek {opakowan}, a aplikacji w sklepie "
                             f"{sum(1 for a_ in apki if w_sklepie(a_))} — po jednym na kartę")
        elif re.search(r'rel="canonical" href="[^"]*/(en/)?apps/[^"]+"', tresc):
            # Rozpoznanie po ADRESIE KANONICZNYM, nie po ścieżce i nie po kształcie.
            #
            # Po ścieżce — bo `kuzushi/index.html` to stara strona produktowa leżąca
            # w korzeniu; dopasowanie do `apps/` wzięłoby ją za wyciek.
            #
            # Po kształcie („ma przycisk sklepu") — bo **strona tematyczna ma dokładnie
            # ten sam kształt**: też niesie blok sklepu z przyciskiem. Pierwsza wersja
            # tej bramki rozpoznawała właśnie tak i kontrpróba B (ikonka wstawiona na
            # stronę tematyczną) przeszła przez nią NA ZIELONO. Złapane przebiegiem,
            # nie czytaniem — i to jest cały powód, dla którego kontrpróby idą przed
            # commitem, a nie po nim.
            # Porównanie WEWNĄTRZ każdego bloku sklepu, nie sumami na stronie.
            #
            # Suma przepuszczała stan „zero ikonek": warunek zaczynał się od
            # `if opakowan`, więc strona bez ani jednej ikonki przechodziła cicho —
            # złapane kontrpróbą E (ikonka tylko po polsku), nie czytaniem kodu.
            # Blok sklepu stoi na stronie produktowej dwa razy i **każdy** ma nieść
            # tyle znaków, ile ma przycisków.
            for blok in re.findall(r'<p class="sklep">.*?</p>', tresc, re.S):
                przyciskow = blok.count('class="przycisk"')
                znakow = sum(blok.count(f'data-platforma="{p}"') for p in PLATFORMY)
                if przyciskow != znakow:
                    bledy.append(f"{adres_}: blok sklepu ma {przyciskow} przycisków "
                                 f"i {znakow} ikonek platformy — po jednej na przycisk")
        elif opakowan:
            # Wyciek. Ikonka ma stać na mapie rodziny i na stronie produktowej —
            # nigdzie indziej. Strona tematyczna ma kartę apki świadomie uboższą,
            # a karta zapowiedzianej aplikacji nie ma platformy, bo nie ma aplikacji.
            bledy.append(f"{adres_}: ikonka platformy poza mapą rodziny i stroną "
                         f"produktową ({opakowan})")
        if czytnikow != sum(per_platforma.values()):
            bledy.append(f"{adres_}: ikonek platformy {sum(per_platforma.values())}, "
                         f"a nazw dla czytnika ekranu {czytnikow} — ikona bez tekstu "
                         f"jest dla czytnika niewidzialna")

    # Nota licencyjna robota Androida: wymagana przez CC BY 3.0 i tylko tam, gdzie
    # robot faktycznie stanął. Dziś żadna apka nie stoi na Play, więc ta bramka jest
    # bezczynna — stoi po to, żeby dzień portu nie wypuścił znaku bez adnotacji.
    if ZNAKI_PLATFORM == "logo":
        for adres_, tresc in pliki.items():
            if adres_.endswith(".html") and tresc.count('data-platforma="android"'):
                jezyk_ = "pl" if '<html lang="pl">' in tresc else "en"
                if NAPISY[jezyk_]["android_cc_by"][:40] not in tresc:
                    bledy.append(f"{adres_}: stoi znak Androida bez noty CC BY — "
                                 f"licencja znaku jej WYMAGA")

    return bledy, uwagi


SKLEPY = ("pl", "us", "gb", "de", "jp")


def _numer_wersji(tekst):
    """`1.2.0` → `(1, 2, 0)`. Porównanie napisami dałoby `1.10.0 < 1.2.0`."""
    czlony = []
    for czlon in str(tekst).split("."):
        try:
            czlony.append(int(czlon))
        except ValueError:
            czlony.append(0)
    return tuple(czlony)


def sprawdz_sklep(apki):
    """Porównuje manifest z tym, co App Store oddaje publicznie. Wymaga sieci.

    **Pyta pięć witryn sklepu, nie jedną, i to jest naprawa z pomiaru.** 09.09.2026
    Kifuku po wydaniu wracało z `pl` jako `resultCount: 0`, a z `us`, `gb`, `de`
    i `jp` jako `1.0.0` wydane o 10:05 UTC — przy czym `apps.apple.com/pl/app/id…`
    oddawało `200`. Czyli aplikacja **była** dostępna w Polsce, a spóźniał się indeks
    wyszukiwania jednej witryny. Pytanie o samo `pl` kazałoby wtedy trzymać na stronie
    „wkrótce w App Store" nad aplikacją, którą dało się kupić.

    Obecna w którejkolwiek witrynie znaczy obecna. Nazwę bierzemy z pierwszej, która
    odpowiedziała — jest ta sama we wszystkich, bo to jedno pole w App Store Connect.
    """
    rozjazdy = []
    for a in apki:
        dane = {"resultCount": 0}
        # **Wersje zbieramy ze WSZYSTKICH witryn, nie z pierwszej — [poz. 356].**
        # Pętla niżej przerywa na pierwszej odpowiadającej i to jest poprawne dla
        # pytania „czy aplikacja jest": obecna w którejkolwiek znaczy obecna.
        # Dla pytania „która wersja" ten sam skrót daje FAŁSZ, i to zmierzony:
        # 18.09.2026 Shindan oddawał `1.1.2` z `pl` i `1.2.0` z `us`, `gb`, `de`
        # i `jp` — indeks polskiej witryny spóźniał się o dobę. Porównanie z samym
        # `pl` zapaliłoby czerwień nad poprawnym manifestem albo zieleń nad złym,
        # zależnie od tego, w którą stronę akurat kłamie indeks.
        wersje = {}
        for kraj in SKLEPY:
            adres = f"https://itunes.apple.com/lookup?id={a['appId']}&country={kraj}"
            try:
                with urllib.request.urlopen(adres, timeout=20) as odpowiedz:
                    odczyt = json.loads(odpowiedz.read().decode())
            except (urllib.error.URLError, json.JSONDecodeError):
                continue
            if odczyt["resultCount"] > 0:
                if dane["resultCount"] == 0:
                    dane = odczyt
                wersja_sklepu = odczyt["results"][0].get("version")
                if wersja_sklepu:
                    wersje[kraj] = wersja_sklepu
        zywa = dane["resultCount"] > 0
        if zywa != a["wSklepie"]:
            rozjazdy.append(f"{a['slug']}: manifest mówi wSklepie={a['wSklepie']}, "
                            f"App Store mówi {zywa}")
        if zywa:
            nazwa = dane["results"][0]["trackName"]
            if nazwa != a["teksty"]["en"]["nazwa"] and nazwa != a["teksty"]["pl"]["nazwa"]:
                rozjazdy.append(f"{a['slug']}: w sklepie „{nazwa}”, w repo "
                                f"„{a['teksty']['pl']['nazwa']}” / „{a['teksty']['en']['nazwa']}”")
            # **Numer wersji — dołożone 18.09.2026, [poz. 356].**
            #
            # Do tego dnia ta bramka porównywała OBECNOŚĆ i NAZWĘ, i nic więcej.
            # Zdanie „App Store: 0 rozjazdów na 10 aplikacji" czytało się jak
            # „manifest zgadza się ze sklepem", a pole `wersja` — to, po którym
            # strona wybiera znacznik `sklep/<wersja>` i którego dotyczy cała
            # [poz. 324] — nie było porównywane z niczym. Zmierzone tego dnia:
            # Shindan stał w manifeście na 1.1.2 przy 1.2.0 w czterech witrynach,
            # a bramka świeciła zielono.
            #
            # **Czerwień zapala się tylko wtedy, gdy manifest jest STARSZY** od
            # najnowszej wersji widzianej w którejkolwiek witrynie. Kierunek jest
            # tu treścią: manifest starszy znaczy, że strona reklamuje wydanie,
            # którego już nie ma; manifest nowszy zdarza się w trakcie rozjazdu
            # indeksów i mija sam, więc jest uwagą, nie błędem.
            najnowsza = max(wersje.values(), key=_numer_wersji, default=None)
            if najnowsza and a.get("wersja"):
                moja, ich = _numer_wersji(a["wersja"]), _numer_wersji(najnowsza)
                gdzie = ", ".join(f"{k}={w}" for k, w in sorted(wersje.items()))
                if moja < ich:
                    rozjazdy.append(
                        f"{a['slug']}: manifest mówi wersja={a['wersja']}, a w sklepie "
                        f"stoi {najnowsza} — strona reklamuje wydanie, którego już nie ma "
                        f"({gdzie})")
                elif moja > ich:
                    print(f"  uwaga  {a['slug']}: manifest {a['wersja']} wyprzedza sklep "
                          f"({gdzie}) — jeśli wydanie właśnie wychodzi, mija samo")
    return rozjazdy


# ---------------------------------------------------------------- przebieg

def zbuduj(apki, manifest, zapowiedziane=()):
    pliki = {}
    daty = {}
    # Liczone raz i przed pętlą, bo potrzebuje tego i strona tematyczna, i podstrona
    # produktowa — ta druga po to, żeby wyjście na temat stało obok opisu aplikacji,
    # a nie tylko w stopce.
    zywe = tematy_zywe(apki, wczytaj_eksporty(apki))
    temat_apki = {temat["apka"]: temat for temat, _, _ in zywe}
    for jezyk in JEZYKI:
        adres, tresc = mapa_rodziny(apki, jezyk, manifest, zywe, zapowiedziane)
        pliki[adres] = tresc
        daty[adres] = max(a["data"] for a in apki)
        adres, tresc = spis_dokumentow(apki, jezyk, manifest)
        pliki[adres] = tresc
        daty[adres] = max(a["data"] for a in apki)
        adres, tresc = strona_autora(apki, jezyk, manifest)
        pliki[adres] = tresc
        daty[adres] = max(a["data"] for a in apki)
        adres, tresc = strona_co_dalej(jezyk, manifest)
        pliki[adres] = tresc
        daty[adres] = max(a["data"] for a in apki)
        for a in apki:
            adres, tresc = podstrona(a, jezyk, manifest, apki,
                                     temat=temat_apki.get(a["slug"]))
            pliki[adres] = tresc
            daty[adres] = a["data"]

    # Strony tematyczne. Powstają tylko dla aplikacji, które mają eksport przejrzanej
    # treści — reszta po prostu nie dostaje strony i **to nie jest błąd**, tylko stan
    # roboczy: eksport dopisuje agent biorący repozytorium swojej apki, tak jak przy
    # wydaniach. `daty` muszą dostać wpis razem z plikiem, bo mapa witryny czyta je
    # słownikiem i przy braku wywala `KeyError`, a nie ostrzeżenie.
    for jezyk in JEZYKI:
        for temat, a, eksport in zywe:
            data_eksportu = data_zrodla(a["repoSciezka"], EKSPORT_PLIK)
            if temat.get("grupy"):
                adres, tresc = rozdroze_tematu(temat, a, eksport, jezyk, manifest)
                pliki[adres] = tresc
                daty[adres] = data_eksportu
                for grupa in grupy_zywe(temat, eksport):
                    adres, tresc = strona_tematu(temat, a, eksport, jezyk, manifest,
                                                 apki, zywe, grupa)
                    pliki[adres] = tresc
                    daty[adres] = data_eksportu
                continue
            adres, tresc = strona_tematu(temat, a, eksport, jezyk, manifest,
                                         apki, zywe)
            pliki[adres] = tresc
            daty[adres] = data_eksportu
        if zywe:
            adres, tresc = rozdroze_nauki(zywe, jezyk, manifest)
            pliki[adres] = tresc
            daty[adres] = max(daty[sciezki_tematu(t, jezyk)[0]] for t, _, _ in zywe)

    # Adres historyczny: `kuzushi/index.html` jest wpisany w App Store Connect jako
    # Marketing URL i był jedyną stroną produktową w tym repozytorium. Zostaje żywy,
    # po angielsku (bo `primaryLocale` Kuzushi to `en-US`) i wskazuje kanonicznie na
    # nową podstronę — przekierowania GitHub Pages nie umie, a zmiana pola w ASC jest
    # decyzją do podjęcia przy najbliższym wydaniu, nie przy generowaniu stron.
    for a in apki:
        if not a.get("adresHistoryczny"):
            continue
        adres, tresc = podstrona(a, "en", manifest, apki,
                                 kanoniczny=sciezki(a["slug"], "en")[0],
                                 sciezka=a["adresHistoryczny"], glebokosc=1)
        pliki[adres] = tresc

    # Zdjęte adresy tematów — **po stronach tematycznych**, bo czytają ich adresy.
    for jezyk in JEZYKI:
        for wpis in PRZEKIEROWANIA:
            adres, tresc = strona_przekierowania(wpis, jezyk, manifest)
            pliki[adres] = tresc

    pliki["robots.txt"] = robots(manifest)
    pliki["llms.txt"] = llms_txt(apki, manifest, zywe, zapowiedziane)
    pliki["404.html"] = strona_404(apki, manifest, zywe)
    pliki["README.md"] = readme(apki, manifest,
                                (KORZEN / "README.md").read_text(encoding="utf-8"))
    pliki["sitemap.xml"] = sitemap(
        sorted((a, daty[a]) for a in pliki
               if a.endswith(".html") and a not in poza_mapa(apki)),
        manifest)
    return pliki


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sprawdz", action="store_true", help="tylko bramki, bez zapisu")
    parser.add_argument("--powtarzalnie", action="store_true",
                        help="generuje dwa razy i porównuje wynik bajt w bajt")
    parser.add_argument("--zrzuty", action="store_true",
                        help="wciąga kadry sklepowe z repozytoriów aplikacji do assets/zrzuty/")
    parser.add_argument("--sprawdz-sklep", action="store_true",
                        help="porównuje manifest z App Store (wymaga sieci)")
    args = parser.parse_args()

    manifest = wczytaj_manifest()
    apki = zbierz(manifest)
    zapowiedziane = zbierz_zapowiedziane(manifest)

    if args.sprawdz_sklep:
        rozjazdy = sprawdz_sklep(apki)
        for r in rozjazdy:
            print("  ⚠", r)
        print(f"App Store: {len(rozjazdy)} rozjazdów na {len(apki)} aplikacji")
        return 1 if rozjazdy else 0

    if args.zrzuty:
        # `--zrzuty --sprawdz` to przebieg próbny: kasowanie plików jest
        # nieodwracalne, a §21.T mówi, że takie narzędzie ma mieć tryb próbny.
        zrobione, brakujace, usuniete = importuj_zrzuty(apki, manifest,
                                                        zapisuj=not args.sprawdz)
        czasownik = "do przeskalowania" if args.sprawdz else "przeskalowanych"
        print(f"zrzuty: {len(zrobione)} {czasownik}")
        for u in usuniete:
            print(f"  − {'do usunięcia' if args.sprawdz else 'usunięty'} (nie ma go w źródle): {u}")
        for b in brakujace:
            print(f"  ⚠ brak kadrów: {b}")
        if args.sprawdz:
            print("to był przebieg próbny — nic nie zapisano ani nie skasowano")
        else:
            print("teraz puść generator bez flagi, żeby galerie weszły na strony")
        return 0

    pliki = zbuduj(apki, manifest, zapowiedziane)

    if args.powtarzalnie:
        drugie = zbuduj(zbierz(manifest), manifest, zbierz_zapowiedziane(manifest))
        rozne = [a for a in pliki if pliki[a] != drugie.get(a)]
        print("powtarzalność:", "ten sam wynik bit w bit" if not rozne else f"ROZJAZD {rozne}")
        return 1 if rozne else 0

    bledy, uwagi = bramki(apki, pliki, manifest, zapowiedziane)
    for uwaga in uwagi:
        print("  ⚠", uwaga)
    if uwagi:
        print(f"rozjazd z kopiami źródłowymi: {len(uwagi)} — nazwane, nie blokujące")
    for blad in bledy:
        print("  ✗", blad)
    if bledy:
        print(f"bramki: {len(bledy)} błędów — nic nie zapisano")
        return 1

    zrobione_ikony = (ikony(list(apki) + list(zapowiedziane), zapisuj=not args.sprawdz)
                      + karty_og(apki, zapisuj=not args.sprawdz)
                      + karta_rodziny(zapisuj=not args.sprawdz)
                      + znak(zapisuj=not args.sprawdz))
    if args.sprawdz:
        print(f"bramki: zielone ({len(pliki)} plików, {len(apki)} aplikacji"
              + (f" + {len(zapowiedziane)} zapowiedzianych)" if zapowiedziane else ")"))
        if zrobione_ikony:
            print(f"  ikony do przeskalowania: {', '.join(zrobione_ikony)}")
        return 0

    zmienione = 0
    for adres, tresc in sorted(pliki.items()):
        cel = KORZEN / adres
        cel.parent.mkdir(parents=True, exist_ok=True)
        if cel.exists() and cel.read_text(encoding="utf-8") == tresc:
            continue
        cel.write_text(tresc, encoding="utf-8")
        zmienione += 1
    print(f"zapisane: {zmienione} z {len(pliki)} plików"
          + (f", ikony: {', '.join(zrobione_ikony)}" if zrobione_ikony else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
