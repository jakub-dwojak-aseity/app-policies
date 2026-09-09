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
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

KORZEN = Path(__file__).resolve().parent.parent
NARZEDZIA = KORZEN / "Tools"
sys.path.insert(0, str(NARZEDZIA))
import glowy_dokumentow  # noqa: E402
import metadane  # noqa: E402

ZRODLA = Path("/Users/jakub/aseity")
JEZYKI = ("pl", "en")

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
   Gramatyka japońska", a nie cały akapit o problemie. */
.karta .nazwa::after { content: ""; position: absolute; inset: 0; border-radius: 12px; }
.karta .co { display: block; color: var(--cichy); font-size: .9em; margin-top: .1rem; }
.karta p { margin: .35rem 0 0; color: var(--cichy); font-size: .93rem; }
.znacznik { display: inline-block; font-size: .75rem; padding: .1rem .45rem;
            border: 1px solid var(--linia); border-radius: 6px; color: var(--cichy);
            margin-left: .4rem; vertical-align: .1em; }
.sklep { display: inline-block; margin: .35rem 0 1.25rem; font-weight: 600; }
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
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--linia);
         font-size: .88rem; color: var(--cichy); }
footer a { color: var(--akcent); }
code { font-size: .9em; }
"""


# ---------------------------------------------------------------- dane

def wczytaj_manifest():
    return json.loads((NARZEDZIA / "apps.json").read_text(encoding="utf-8"))


def data_zrodla(repo: Path, plik: Path) -> str:
    """Data ostatniej zmiany pliku metadanych, z gita.

    `lastmod` w mapie witryny ma mówić, kiedy zmieniła się TREŚĆ, a nie kiedy
    ktoś uruchomił generator. Data z zegara psułaby jedno i drugie: nie niosłaby
    informacji i odbierała wynikowi powtarzalność bit w bit.
    """
    wynik = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%cs", "--", str(plik)],
                           capture_output=True, text=True)
    return (wynik.stdout or "").strip() or "2026-09-08"


def zbierz(manifest):
    """Metadane wszystkich aplikacji w obu językach, plus daty z gita."""
    apki = []
    for wpis in sorted(manifest["aplikacje"], key=lambda a: a["kolejnosc"]):
        repo = ZRODLA / wpis["repo"]
        if not repo.exists():
            raise SystemExit(f"{wpis['slug']}: brak drzewa {repo}")
        teksty = {}
        for jezyk in JEZYKI:
            teksty[jezyk] = metadane.teksty(repo, wpis, jezyk)
            plik = (Path("docs/app-store/version-texts.json") if wpis["zrodlo"] == "kaname"
                    else Path(f"docs/app-store/APP_STORE_METADATA_{jezyk.upper()}.md"))
        podpisy = {j: podpisy_kadrow(ZRODLA / wpis.get("repoZrzuty", wpis["repo"]), j)
                   for j in JEZYKI}
        apki.append({**wpis, "teksty": teksty, "repoSciezka": repo, "podpisy": podpisy,
                     "data": data_zrodla(repo, plik)})
    return apki


# ---------------------------------------------------------------- HTML

def e(tekst: str) -> str:
    return html.escape(tekst, quote=False)


def wzgledny(z_glebokosci: int, cel: str) -> str:
    return ("../" * z_glebokosci) + cel


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


def opis_html(opis: str) -> str:
    return "\n".join(akapit_html(a) for a in metadane.akapity(opis))


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
    czesci += ["</head>", "<body>", nawigacja, f"<main>{tresc}</main>", stopka_html,
               "</body>", "</html>", ""]
    return "\n".join(cz for cz in czesci if cz)


def gora(jezyk, glebokosc, alternatywny, manifest, mapa=True):
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
    powrot = f'<a href="{dom}">← {e(n["wroc"])}</a>' if mapa else ""
    prawo = (f'<a href="{manifest["bazaAdresu"]}/{publiczny(alternatywny)}">'
             f'{e(n["inny_jezyk"])}</a>')
    return (f'<nav class="gora"><span>{znak_html}{powrot}</span>'
            f'<span>{prawo}</span></nav>')


def stopka(jezyk, glebokosc, manifest, kontakt=None):
    n = NAPISY[jezyk]
    spis = "dokumenty.html" if jezyk == "pl" else "en/documents.html"
    linki = [f'<a href="{wzgledny(glebokosc, spis)}">{e(n["spis_link"])}</a>']
    if kontakt:
        linki.append(f'<a href="mailto:{kontakt}">{e(kontakt)}</a>')
    return f"<footer>{e(manifest['autor'])} · " + " · ".join(linki) + "</footer>"


# ---------------------------------------------------------------- strony

def sciezki(slug, jezyk):
    if jezyk == "pl":
        return f"apps/{slug}/index.html", 2
    return f"en/apps/{slug}/index.html", 3


def link_sklepu(appId):
    return f"https://apps.apple.com/app/id{appId}"


def mapa_rodziny(apki, jezyk, manifest):
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
        znacznik = "" if a["wSklepie"] else f'<span class="znacznik">{e(n["wkrotce"])}</span>'
        karty.append(
            f'<li class="karta"><img src="{ikona}" alt="" width="52" height="52" loading="lazy">'
            f'<div><a class="nazwa" href="{cel}">{e(t["nazwa"])}</a>'
            f'<span class="jp" lang="ja">{e(a["japonska"])}</span>{znacznik}'
            f'<span class="co">{e(t["podtytul"])}</span>'
            f"<p>{e(t['promo'])}</p></div></li>")

    tresc = (
        f"<h1>{e(n['tytul_mapy'])}</h1>"
        + f'<p class="podtytul">{e(n["opis_mapy"])}</p>'
        + f"<h2>{e(n['naglowek_tabeli'])}</h2>"
        + '<ul class="karty">' + "".join(karty) + "</ul>")

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
    return kanoniczny, strona(jezyk=jezyk, tytul=n["tytul_mapy"], opis=n["opis_mapy"],
                              kanoniczny=kanoniczny, alternatywny=alternatywny,
                              tresc=tresc, glebokosc=glebokosc, manifest=manifest,
                              jsonld=jsonld,
                              nawigacja=gora(jezyk, glebokosc, alternatywny, manifest, mapa=False),
                              stopka_html=stopka(jezyk, glebokosc, manifest))


def podstrona(a, jezyk, manifest, apki, *, kanoniczny=None, sciezka=None, glebokosc=None):
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
        sklep = (f'<p class="sklep"><a href="{link_sklepu(a["appId"])}">{e(n["w_sklepie"])} →</a>'
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

    tresc = (
        f'<div class="szyld"><img src="{ikona}" alt="" width="72" height="72">'
        + f'<div><h1>{e(t["nazwa"])}<span class="jp" lang="ja">{e(a["japonska"])}</span></h1>'
        + f'<p class="podtytul">{e(t["podtytul"])}</p></div></div>'
        + sklep
        + f'<p class="lead">{e(t["promo"])}</p>'
        + galeria(a, jezyk, glebokosc)
        + f"<h2>{e(n['opis_naglowek'])}</h2>"
        + opis_html(t["opis"])
        + f'<p class="podtytul">{e(n["opis_stopka"])}</p>'
        + faq_html(pary, jezyk)
        + f"<h2>{e(n['dokumenty'])}</h2><ul class=\"zwykla\">{dokumenty}</ul>"
        + f"<h2>{e(n['rodzina'])}</h2><ul class=\"zwykla\">{rodzenstwo}</ul>")

    jsonld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": t["nazwa"],
        "alternateName": a["japonska"],
        "applicationCategory": "EducationalApplication",
        "operatingSystem": "iOS",
        "url": f"{manifest['bazaAdresu']}/{publiczny(kanoniczny)}",
        "description": metadane.pierwsze_zdanie(t["opis"]),
        "inLanguage": ["pl", "en"],
        "author": {"@type": "Person", "name": manifest["autor"]},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "PLN"},
    }
    if a["wSklepie"]:
        jsonld["sameAs"] = link_sklepu(a["appId"])
        jsonld["installUrl"] = link_sklepu(a["appId"])

    tytul = f'{t["nazwa"]} – {t["podtytul"]}'
    obrazek = f'{manifest["bazaAdresu"]}/assets/karty/{a["slug"]}-{jezyk}.png'

    # `image` opisuje aplikację, więc musi stać na węźle `SoftwareApplication`.
    # Przypisanie po owinięciu w `@graph` sadzało je w korzeniu, obok `@context`,
    # gdzie nie opisuje niczego — zmierzone 09.09.2026 na wygenerowanym HTML-u.
    jsonld["image"] = obrazek

    if pary:
        jsonld = {"@context": "https://schema.org",
                  "@graph": [{k: v for k, v in jsonld.items() if k != "@context"},
                             faq_jsonld(pary)]}
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


def galeria(a, jezyk, glebokosc):
    """Kadry sklepowe na stronie — te same, które widać w App Store.

    Podstrona była do 09.09.2026 ścianą tekstu: opis ze sklepu i nic więcej.
    Kadry są już zrobione, przejrzane i wgrane do App Store, więc **jedyne, co
    tu przybywa, to znacznik `<img>`** — nie nowa treść.

    Pusta, gdy zrzutów nie zaimportowano: aplikacja bez galerii ma wyglądać jak
    strona bez galerii, a nie jak strona z dziurą.
    """
    pliki = zrzuty_apki(a["slug"], jezyk)
    if not pliki:
        return ""
    n = NAPISY[jezyk]
    podpisy = a["podpisy"][jezyk]
    kadry = []
    for plik in pliki:
        naglowek, podtytul = podpisy.get(Path(plik).stem,
                                         (f'{a["teksty"][jezyk]["nazwa"]} – {n["zrzut"]}', ""))
        opis = f"{naglowek} {podtytul}".strip()
        sciezka = wzgledny(glebokosc, f"assets/zrzuty/{a['slug']}/{jezyk}/{plik}")
        podpis = f"<strong>{e(naglowek)}</strong>"
        if podtytul:
            podpis += f"<br>{e(podtytul)}"
        kadry.append(f'<figure><img src="{sciezka}" alt="{html.escape(opis, quote=True)}"'
                     f' width="420" height="912" loading="lazy">'
                     f"<figcaption>{podpis}</figcaption></figure>")
    return f"<h2>{e(n['naglowek_zrzutow'])}</h2>" + \
        f'<div class="zrzuty">{"".join(kadry)}</div>'


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
                              stopka_html=stopka(jezyk, glebokosc, manifest))


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
    return {a["adresHistoryczny"] for a in apki if a.get("adresHistoryczny")} | {"404.html"}


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


def llms_txt(apki, manifest):
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
    wiersze += ["", "## Pozostałe strony", "",
                f"- [Mapa rodziny: tabela problem → aplikacja]({baza}/)",
                f"- [Family map, English]({baza}/en/)",
                f"- [Dokumenty prawne wszystkich aplikacji]({baza}/dokumenty.html)",
                f"- [Legal documents, English]({baza}/en/documents.html)", ""]
    return "\n".join(wiersze)


def strona_404(apki, manifest):
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
    tresc = ("<h1>Nie ma takiej strony</h1>"
             '<p class="podtytul">Adres mógł się zmienić — dokumenty prawne dostały numer '
             "wersji w adresie, a cała witryna przeniosła się na tę domenę. Poniżej "
             "wszystko, co tu jest.</p>"
             f'<h2>{e(n["naglowek_kart"])}</h2><ul class="zwykla">{pozycje}</ul>'
             f'<h2>{e(n["dokumenty"])}</h2><ul class="zwykla">'
             f'<li><a href="{baza}/dokumenty.html">{e(n["spis_tytul"])}</a></li>'
             f'<li><a href="{baza}/">{e(n["tytul_mapy"])}</a></li></ul>')
    return strona(jezyk="pl", tytul="Nie ma takiej strony",
                  opis="Adres nie istnieje. Spis wszystkich aplikacji i dokumentów rodziny.",
                  kanoniczny="404.html", alternatywny="en/index.html",
                  tresc=tresc, glebokosc=0, manifest=manifest,
                  nawigacja=f'<nav class="gora"><span></span>'
                            f'<span><a href="{baza}/en/">English</a></span></nav>',
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

ZRZUTOW_NA_STRONE = 3
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


def podpisy_kadrow(repo: Path, jezyk: str) -> dict:
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
    plik = repo / "docs" / "app-store" / "screenshots.json"
    if not plik.exists():
        return {}
    lokalizacja = {"pl": "pl", "en": "en-US"}[jezyk]
    podpisy = {}
    for kadr in json.loads(plik.read_text(encoding="utf-8")).get("shots", []):
        tresc = (kadr.get("copy") or {}).get(lokalizacja) or {}
        naglowek = (tresc.get("headline") or "").strip()
        podtytul = (tresc.get("subtitle") or "").strip()
        if naglowek:
            podpisy[kadr["id"]] = (naglowek, podtytul)
    return podpisy


def zrzuty_apki(slug: str, jezyk: str) -> list:
    """Zrzuty już zaimportowane do repozytorium stron, po kolei."""
    katalog = KORZEN / "assets" / "zrzuty" / slug / jezyk
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
    nowe, zrobione, brakujace = dict(stare), [], []
    for a in apki:
        repo = ZRODLA / a.get("repoZrzuty", a["repo"])
        for jezyk, katalog_jezyka in KATALOGI_JEZYKA.items():
            zrodlo = repo / "docs" / "app-store" / "screenshots" / katalog_jezyka
            if not zrodlo.exists():
                brakujace.append(f"{a['slug']} {jezyk}")
                continue
            kadry = sorted(zrodlo.glob("*.png"))[:ZRZUTOW_NA_STRONE]
            cel_katalog = katalog / a["slug"] / jezyk
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
    return zrobione, brakujace


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
    """
    bez_linii = "\n".join(
        w for w in tresc.split("\n")
        if 'rel="canonical"' not in w and 'name="robots"' not in w
        and 'rel="icon"' not in w and 'rel="apple-touch-icon"' not in w
        and 'name="description"' not in w and 'property="og:' not in w
        and 'name="twitter:card"' not in w)
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


def bramki(apki, pliki, manifest):
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
    powstana |= {f"assets/zrzuty/{a['slug']}/{j}/{p}"
                 for a in apki for j in JEZYKI for p in zrzuty_apki(a["slug"], j)}
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
        # Wyjście na witrynę. Dokument prawny bez niego jest ślepym zaułkiem dla
        # człowieka, który przyszedł tu z App Store — a to jest ruch od kogoś,
        # kto już kupił jedną aplikację i nie widzi pozostałych dziewięciu.
        if wzgledna in ctx["apka"] and f"{baza}/" not in tresc.split("<footer")[-1]:
            bledy.append(f"{wzgledna}: stopka bez wyjścia na witrynę "
                         f"(uruchom Tools/glowy_dokumentow.py)")

    return bledy, uwagi


SKLEPY = ("pl", "us", "gb", "de", "jp")


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
        for kraj in SKLEPY:
            adres = f"https://itunes.apple.com/lookup?id={a['appId']}&country={kraj}"
            try:
                with urllib.request.urlopen(adres, timeout=20) as odpowiedz:
                    odczyt = json.loads(odpowiedz.read().decode())
            except (urllib.error.URLError, json.JSONDecodeError):
                continue
            if odczyt["resultCount"] > 0:
                dane = odczyt
                break
        zywa = dane["resultCount"] > 0
        if zywa != a["wSklepie"]:
            rozjazdy.append(f"{a['slug']}: manifest mówi wSklepie={a['wSklepie']}, "
                            f"App Store mówi {zywa}")
        if zywa:
            nazwa = dane["results"][0]["trackName"]
            if nazwa != a["teksty"]["en"]["nazwa"] and nazwa != a["teksty"]["pl"]["nazwa"]:
                rozjazdy.append(f"{a['slug']}: w sklepie „{nazwa}”, w repo "
                                f"„{a['teksty']['pl']['nazwa']}” / „{a['teksty']['en']['nazwa']}”")
    return rozjazdy


# ---------------------------------------------------------------- przebieg

def zbuduj(apki, manifest):
    pliki = {}
    daty = {}
    for jezyk in JEZYKI:
        adres, tresc = mapa_rodziny(apki, jezyk, manifest)
        pliki[adres] = tresc
        daty[adres] = max(a["data"] for a in apki)
        adres, tresc = spis_dokumentow(apki, jezyk, manifest)
        pliki[adres] = tresc
        daty[adres] = max(a["data"] for a in apki)
        for a in apki:
            adres, tresc = podstrona(a, jezyk, manifest, apki)
            pliki[adres] = tresc
            daty[adres] = a["data"]

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

    pliki["robots.txt"] = robots(manifest)
    pliki["llms.txt"] = llms_txt(apki, manifest)
    pliki["404.html"] = strona_404(apki, manifest)
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

    if args.sprawdz_sklep:
        rozjazdy = sprawdz_sklep(apki)
        for r in rozjazdy:
            print("  ⚠", r)
        print(f"App Store: {len(rozjazdy)} rozjazdów na {len(apki)} aplikacji")
        return 1 if rozjazdy else 0

    if args.zrzuty:
        zrobione, brakujace = importuj_zrzuty(apki, manifest, zapisuj=True)
        print(f"zrzuty: {len(zrobione)} przeskalowanych")
        for b in brakujace:
            print(f"  ⚠ brak kadrów: {b}")
        print("teraz puść generator bez flagi, żeby galerie weszły na strony")
        return 0

    pliki = zbuduj(apki, manifest)

    if args.powtarzalnie:
        drugie = zbuduj(zbierz(manifest), manifest)
        rozne = [a for a in pliki if pliki[a] != drugie.get(a)]
        print("powtarzalność:", "ten sam wynik bit w bit" if not rozne else f"ROZJAZD {rozne}")
        return 1 if rozne else 0

    bledy, uwagi = bramki(apki, pliki, manifest)
    for uwaga in uwagi:
        print("  ⚠", uwaga)
    if uwagi:
        print(f"rozjazd z kopiami źródłowymi: {len(uwagi)} — nazwane, nie blokujące")
    for blad in bledy:
        print("  ✗", blad)
    if bledy:
        print(f"bramki: {len(bledy)} błędów — nic nie zapisano")
        return 1

    zrobione_ikony = (ikony(apki, zapisuj=not args.sprawdz)
                      + karty_og(apki, zapisuj=not args.sprawdz)
                      + znak(zapisuj=not args.sprawdz))
    if args.sprawdz:
        print(f"bramki: zielone ({len(pliki)} plików, {len(apki)} aplikacji)")
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
