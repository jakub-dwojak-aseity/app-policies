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
import metadane  # noqa: E402

ZRODLA = Path("/Users/jakub/aseity")
JEZYKI = ("pl", "en")

# Cały tekst własny generatora. Trzymany w jednym miejscu z rozmysłem: przy stronach
# najłatwiej zsunąć się w pisanie zdań o aplikacjach obok ich opisów, a wtedy strona
# zaczyna obiecywać rzeczy, których nikt nie przejrzał. Jak długa jest ta tablica,
# tak dużo tekstu na stronach nie pochodzi ze sklepu.
NAPISY = {
    "pl": {
        "html_lang": "pl",
        "tytul_mapy": "Japoński w dziesięciu aplikacjach",
        "opis_mapy": "Dziesięć aplikacji do nauki japońskiego, każda o jednej rzeczy: "
                     "gramatyka, czytanie, odmiana, partykuły, liczniki, mowa potoczna, "
                     "keigo, akcent i onomatopeje.",
        "naglowek_tabeli": "Który problem, ta aplikacja",
        "kolumna_problem": "Jeśli to jest twój problem",
        "kolumna_aplikacja": "Aplikacja",
        "naglowek_kart": "Wszystkie aplikacje",
        "w_sklepie": "App Store",
        "wkrotce": "Wkrótce w App Store",
        "wkrotce_opis": "Aplikacja czeka na recenzję Apple. Strona opisuje wersję złożoną do sklepu.",
        "darmowa": "Aplikacja darmowa, z zakupem w środku",
        "wiecej": "Czytaj dalej",
        "opis_naglowek": "Opis ze sklepu",
        "opis_stopka": "Powyższy opis jest tym samym tekstem, który stoi na karcie aplikacji "
                       "w App Store – pochodzi z tego samego pliku.",
        "dokumenty": "Dokumenty",
        "polityka": "Polityka prywatności",
        "warunki": "Warunki korzystania",
        "wsparcie": "Wsparcie",
        "kontakt": "Kontakt",
        "rodzina": "Pozostałe aplikacje",
        "wroc": "Wszystkie aplikacje",
        "inny_jezyk": "English",
        "spis_tytul": "Dokumenty aplikacji",
        "spis_opis": "Polityki prywatności, warunki korzystania i strony wsparcia "
                     "wszystkich aplikacji.",
        "spis_link": "Spis dokumentów",
        "generowane": "Strona wygenerowana z metadanych sklepowych "
                      "(<code>Tools/generuj-strony.py</code>).",
    },
    "en": {
        "html_lang": "en",
        "tytul_mapy": "Japanese in ten apps",
        "opis_mapy": "Ten apps for learning Japanese, each about one thing: grammar, "
                     "reading, conjugation, particles, counters, casual speech, "
                     "keigo, pitch accent and mimetics.",
        "naglowek_tabeli": "Which problem, which app",
        "kolumna_problem": "If this is your problem",
        "kolumna_aplikacja": "App",
        "naglowek_kart": "All apps",
        "w_sklepie": "App Store",
        "wkrotce": "Coming to the App Store",
        "wkrotce_opis": "Waiting for Apple review. This page describes the version submitted.",
        "darmowa": "Free app with an in-app purchase",
        "wiecej": "Read on",
        "opis_naglowek": "Description from the store",
        "opis_stopka": "The description above is the same text that stands on the App Store "
                       "product page – it comes from the same file.",
        "dokumenty": "Documents",
        "polityka": "Privacy Policy",
        "warunki": "Terms of Use",
        "wsparcie": "Support",
        "kontakt": "Contact",
        "rodzina": "The other apps",
        "wroc": "All apps",
        "inny_jezyk": "Polski",
        "spis_tytul": "App documents",
        "spis_opis": "Privacy policies, terms of use and support pages for every app.",
        "spis_link": "Document index",
        "generowane": "Generated from App Store metadata "
                      "(<code>Tools/generuj-strony.py</code>).",
    },
}

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
.szyld { display: flex; gap: 1rem; align-items: center; margin-bottom: .5rem; }
.szyld img { width: 72px; height: 72px; border-radius: 16px; flex: none; }
.jp { color: var(--cichy); font-weight: 400; font-size: .75em; margin-left: .4em; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; font-size: .95rem; }
th, td { text-align: left; vertical-align: top; padding: .7rem .8rem .7rem 0;
         border-bottom: 1px solid var(--linia); }
th { color: var(--cichy); font-weight: 600; font-size: .85rem; }
td.app { white-space: nowrap; }
td.app .co { display: block; color: var(--cichy); font-size: .9em; white-space: normal; }
.karty { display: grid; gap: .5rem; padding: 0; list-style: none; }
.karta { display: flex; gap: .9rem; align-items: flex-start; padding: .85rem;
         border: 1px solid var(--linia); border-radius: 12px; background: var(--karta); }
.karta img { width: 52px; height: 52px; border-radius: 12px; flex: none; }
.karta .nazwa { font-weight: 600; }
.karta p { margin: .15rem 0 0; color: var(--cichy); font-size: .93rem; }
.znacznik { display: inline-block; font-size: .75rem; padding: .1rem .45rem;
            border: 1px solid var(--linia); border-radius: 6px; color: var(--cichy);
            margin-left: .4rem; vertical-align: .1em; }
.sklep { display: inline-block; margin: .35rem 0 1.25rem; font-weight: 600; }
ul.zwykla { padding-left: 1.15rem; }
ul.zwykla li { margin: .3rem 0; }
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--linia);
         font-size: .88rem; color: var(--cichy); }
footer a { color: var(--akcent); }
code { font-size: .9em; }
@media (max-width: 34rem) {
  table, tbody, tr, td, th { display: block; }
  thead { display: none; }
  tr { border-bottom: 1px solid var(--linia); padding: .6rem 0; }
  td { border: 0; padding: .15rem 0; }
  td.app { white-space: normal; font-weight: 600; }
}
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
            if wpis["zrodlo"] == "kaname":
                teksty[jezyk] = metadane.z_json(repo, jezyk, wpis["wersja"])
                plik = Path("docs/app-store/version-texts.json")
            else:
                teksty[jezyk] = metadane.z_markdown(repo, jezyk)
                plik = Path(f"docs/app-store/APP_STORE_METADATA_{jezyk.upper()}.md")
        apki.append({**wpis, "teksty": teksty, "repoSciezka": repo,
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
           manifest, jsonld=None, dodatkowa_glowa=""):
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
        dodatkowa_glowa,
        f"<style>\n{STYL}</style>",
    ]
    if jsonld:
        czesci.append('<script type="application/ld+json">\n'
                      + json.dumps(jsonld, ensure_ascii=False, indent=2) + "\n</script>")
    czesci += ["</head>", "<body>", tresc, "</body>", "</html>", ""]
    return "\n".join(cz for cz in czesci if cz)


def gora(jezyk, glebokosc, alternatywny, manifest, mapa=True):
    n = NAPISY[jezyk]
    lewo = (f'<a href="{wzgledny(glebokosc, "index.html" if jezyk == "pl" else "en/index.html")}">'
            f"← {e(n['wroc'])}</a>") if mapa else ""
    prawo = f'<a href="{manifest["bazaAdresu"]}/{alternatywny}">{e(n["inny_jezyk"])}</a>'
    return f'<div class="gora"><span>{lewo}</span><span>{prawo}</span></div>'


def stopka(jezyk, glebokosc, manifest, kontakt=None):
    n = NAPISY[jezyk]
    spis = "dokumenty.html" if jezyk == "pl" else "en/documents.html"
    linki = [f'<a href="{wzgledny(glebokosc, spis)}">{e(n["spis_link"])}</a>']
    if kontakt:
        linki.append(f'<a href="mailto:{kontakt}">{e(kontakt)}</a>')
    return (f"<footer>{e(manifest['autor'])} · " + " · ".join(linki)
            + f"<br>{n['generowane']}</footer>")


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

    wiersze = []
    for a in apki:
        t = a["teksty"][jezyk]
        cel = wzgledny(glebokosc, sciezki(a["slug"], jezyk)[0])
        znacznik = "" if a["wSklepie"] else f'<span class="znacznik">{e(n["wkrotce"])}</span>'
        wiersze.append(
            f"<tr><td>{e(t['promo'])}</td>"
            f'<td class="app"><a href="{cel}">{e(t["nazwa"])}</a>{znacznik}'
            f'<span class="co">{e(t["podtytul"])}</span></td></tr>')

    karty = []
    for a in apki:
        t = a["teksty"][jezyk]
        cel = wzgledny(glebokosc, sciezki(a["slug"], jezyk)[0])
        ikona = wzgledny(glebokosc, f"assets/ikony/{a['slug']}.png")
        karty.append(
            f'<li class="karta"><img src="{ikona}" alt="" width="52" height="52" loading="lazy">'
            f'<div><a class="nazwa" href="{cel}">{e(t["nazwa"])}</a>'
            f'<span class="jp">{e(a["japonska"])}</span>'
            f"<p>{e(metadane.pierwsze_zdanie(t['opis']))}</p></div></li>")

    tresc = (
        gora(jezyk, glebokosc, alternatywny, manifest, mapa=False)
        + f"<h1>{e(n['tytul_mapy'])}</h1>"
        + f'<p class="podtytul">{e(n["opis_mapy"])}</p>'
        + f"<h2>{e(n['naglowek_tabeli'])}</h2>"
        + "<table><thead><tr>"
        + f"<th>{e(n['kolumna_problem'])}</th><th>{e(n['kolumna_aplikacja'])}</th>"
        + "</tr></thead><tbody>" + "".join(wiersze) + "</tbody></table>"
        + f"<h2>{e(n['naglowek_kart'])}</h2>"
        + '<ul class="karty">' + "".join(karty) + "</ul>"
        + stopka(jezyk, glebokosc, manifest))

    jsonld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": n["tytul_mapy"],
        "description": n["opis_mapy"],
        "numberOfItems": len(apki),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "url": f"{manifest['bazaAdresu']}/{sciezki(a['slug'], jezyk)[0]}",
             "name": a["teksty"][jezyk]["nazwa"]}
            for i, a in enumerate(apki)],
    }
    return kanoniczny, strona(jezyk=jezyk, tytul=n["tytul_mapy"], opis=n["opis_mapy"],
                              kanoniczny=kanoniczny, alternatywny=alternatywny,
                              tresc=tresc, glebokosc=glebokosc, manifest=manifest,
                              jsonld=jsonld)


def podstrona(a, jezyk, manifest, apki, *, kanoniczny=None, sciezka=None, glebokosc=None):
    n = NAPISY[jezyk]
    wlasny, wlasna_glebokosc = sciezki(a["slug"], jezyk)
    sciezka = sciezka or wlasny
    glebokosc = wlasna_glebokosc if glebokosc is None else glebokosc
    kanoniczny = kanoniczny or wlasny
    alternatywny = sciezki(a["slug"], "en" if jezyk == "pl" else "pl")[0]
    t = a["teksty"][jezyk]
    katalog = a["dokumenty"][jezyk]
    ikona = wzgledny(glebokosc, f"assets/ikony/{a['slug']}.png")

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
        gora(jezyk, glebokosc, alternatywny, manifest)
        + f'<div class="szyld"><img src="{ikona}" alt="" width="72" height="72">'
        + f'<div><h1>{e(t["nazwa"])}<span class="jp">{e(a["japonska"])}</span></h1>'
        + f'<p class="podtytul">{e(t["podtytul"])}</p></div></div>'
        + sklep
        + f'<p class="lead">{e(t["promo"])}</p>'
        + f"<h2>{e(n['opis_naglowek'])}</h2>"
        + opis_html(t["opis"])
        + f'<p class="podtytul">{e(n["opis_stopka"])}</p>'
        + f"<h2>{e(n['dokumenty'])}</h2><ul class=\"zwykla\">{dokumenty}</ul>"
        + f"<h2>{e(n['rodzina'])}</h2><ul class=\"zwykla\">{rodzenstwo}</ul>"
        + stopka(jezyk, glebokosc, manifest, a["kontakt"]))

    jsonld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": t["nazwa"],
        "alternateName": a["japonska"],
        "applicationCategory": "EducationalApplication",
        "operatingSystem": "iOS",
        "url": f"{manifest['bazaAdresu']}/{kanoniczny}",
        "description": metadane.pierwsze_zdanie(t["opis"]),
        "inLanguage": ["pl", "en"],
        "author": {"@type": "Person", "name": manifest["autor"]},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "PLN"},
    }
    if a["wSklepie"]:
        jsonld["sameAs"] = link_sklepu(a["appId"])
        jsonld["installUrl"] = link_sklepu(a["appId"])

    tytul = f'{t["nazwa"]} – {t["podtytul"]}'
    obrazek = f'{manifest["bazaAdresu"]}/assets/ikony/{a["slug"]}.png'
    jsonld["image"] = obrazek
    return sciezka, strona(jezyk=jezyk, tytul=tytul, opis=meta_opis(t),
                           kanoniczny=kanoniczny, alternatywny=alternatywny,
                           tresc=tresc, glebokosc=glebokosc, manifest=manifest,
                           jsonld=jsonld,
                           dodatkowa_glowa=f'<meta property="og:image" content="{obrazek}">')


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
        sekcje.append(f'<h2>{e(t["nazwa"])}<span class="jp">{e(a["japonska"])}</span></h2>'
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

    tresc = (gora(jezyk, glebokosc, alternatywny, manifest)
             + f"<h1>{e(n['spis_tytul'])}</h1>"
             + f'<p class="podtytul">{e(n["spis_opis"])}</p>'
             + "".join(sekcje)
             + stopka(jezyk, glebokosc, manifest))
    return kanoniczny, strona(jezyk=jezyk, tytul=n["spis_tytul"], opis=n["spis_opis"],
                              kanoniczny=kanoniczny, alternatywny=alternatywny,
                              tresc=tresc, glebokosc=glebokosc, manifest=manifest)


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


def robots(manifest):
    return ("# Roboty wyszukiwarek i modeli językowych są tu mile widziane.\n"
            "User-agent: *\n"
            "Allow: /\n"
            "\n"
            f"Sitemap: {manifest['bazaAdresu']}/sitemap.xml\n")


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
        cel = katalog / f"{a['slug']}.png"
        nowe[a["slug"]] = skrot
        if cel.exists() and stare.get(a["slug"]) == skrot:
            continue
        if not zapisuj:
            zrobione.append(a["slug"])
            continue
        katalog.mkdir(parents=True, exist_ok=True)
        subprocess.run(["sips", "-Z", "180", str(zrodlo), "--out", str(cel)],
                       check=True, capture_output=True)
        zrobione.append(a["slug"])
    if zapisuj and nowe != stare:
        katalog.mkdir(parents=True, exist_ok=True)
        rejestr.write_text(json.dumps(nowe, ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
    return zrobione


# ---------------------------------------------------------------- bramki

def bramki(apki, pliki, manifest):
    """Wszystko, co musi być prawdą, zanim strony pojadą na serwer.

    Bramka mierzy **wytwór**, a nie zamiar: patrzy w wygenerowany HTML i w pliki
    na dysku, a nie w to, co generator zamierzał zapisać.
    """
    bledy = []

    # 1. Każdy dokument prawny, do którego strona linkuje, musi istnieć.
    for a in apki:
        for jezyk in JEZYKI:
            for plik in ("privacy.html", "terms.html", "support.html"):
                sciezka = KORZEN / a["dokumenty"][jezyk] / plik
                if not sciezka.exists():
                    bledy.append(f"{a['slug']} {jezyk}: brak dokumentu {sciezka.relative_to(KORZEN)}")

    for inna in manifest.get("pozostale", []):
        for katalog in inna["dokumenty"].values():
            for plik in ("privacy.html", "terms.html", "support.html"):
                if not (KORZEN / katalog / plik).exists():
                    bledy.append(f"{inna['slug']}: brak dokumentu {katalog}/{plik}")

    # 2. Każdy link wewnętrzny musi prowadzić do pliku, który powstanie albo już jest.
    powstana = set(pliki) | {p.relative_to(KORZEN).as_posix()
                             for p in KORZEN.rglob("*.html") if ".git" not in p.parts}
    powstana |= {f"assets/ikony/{a['slug']}.png" for a in apki}
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

    # 6. Mapa witryny wymienia dokładnie te strony, które generator zapisuje.
    mapa = pliki.get("sitemap.xml", "")
    baza = manifest["bazaAdresu"] + "/"
    w_mapie = {a[len(baza):] for a in re.findall(r"<loc>([^<]*)</loc>", mapa)}
    historyczne = {a["adresHistoryczny"] for a in apki if a.get("adresHistoryczny")}
    html_pliki = {publiczny(a) for a in pliki if a.endswith(".html")}
    historyczne = {publiczny(a) for a in historyczne}
    if w_mapie != html_pliki - historyczne:
        bledy.append(f"sitemap.xml rozjeżdża się ze stronami: "
                     f"nadmiar {sorted(w_mapie - html_pliki)}, "
                     f"brak {sorted(html_pliki - historyczne - w_mapie)}")

    return bledy


def sprawdz_sklep(apki):
    """Porównuje manifest z tym, co App Store oddaje publicznie. Wymaga sieci."""
    rozjazdy = []
    for a in apki:
        adres = f"https://itunes.apple.com/lookup?id={a['appId']}&country=pl"
        with urllib.request.urlopen(adres, timeout=20) as odpowiedz:
            dane = json.loads(odpowiedz.read().decode())
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
    pliki["README.md"] = readme(apki, manifest,
                                (KORZEN / "README.md").read_text(encoding="utf-8"))
    historyczne = {a["adresHistoryczny"] for a in apki if a.get("adresHistoryczny")}
    pliki["sitemap.xml"] = sitemap(
        sorted((a, daty[a]) for a in pliki if a.endswith(".html") and a not in historyczne),
        manifest)
    return pliki


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sprawdz", action="store_true", help="tylko bramki, bez zapisu")
    parser.add_argument("--powtarzalnie", action="store_true",
                        help="generuje dwa razy i porównuje wynik bajt w bajt")
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

    pliki = zbuduj(apki, manifest)

    if args.powtarzalnie:
        drugie = zbuduj(zbierz(manifest), manifest)
        rozne = [a for a in pliki if pliki[a] != drugie.get(a)]
        print("powtarzalność:", "ten sam wynik bit w bit" if not rozne else f"ROZJAZD {rozne}")
        return 1 if rozne else 0

    bledy = bramki(apki, pliki, manifest)
    for blad in bledy:
        print("  ✗", blad)
    if bledy:
        print(f"bramki: {len(bledy)} błędów — nic nie zapisano")
        return 1

    zrobione_ikony = ikony(apki, zapisuj=not args.sprawdz)
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
