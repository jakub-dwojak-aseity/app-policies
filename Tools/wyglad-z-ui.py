#!/usr/bin/env python3
"""Przenosi wygląd rodziny z `japanese-ui` do witryny: kolory apek, neutralne i Kinako.

    python3 Tools/wyglad-z-ui.py            # próba: mówi, czy kopia jest świeża
    python3 Tools/wyglad-z-ui.py --wykonaj  # zapisuje Tools/wyglad.json

**Witryna czyta nazwany stan, nie cudze drzewo.** Źródłem jest `HEAD` w
`~/aseity/japanese-ui` (`git show HEAD:…`), a nie pliki na dysku: drzewo pakietu
bywa w połowie roboty i niezacommitowany kolor wszedłby na stronę publiczną bez
przeglądu. Kopia trzyma skróty obu plików źródłowych, więc bramka w
`generuj-strony.py` widzi, że pakiet poszedł dalej, i **ostrzega** (nie blokuje,
bo nowy kolor w pakiecie nie psuje stojącej witryny, tylko ją postarza).

Z `tokens.json` bierze się `color.apps.<slug>.{band,accentText}` i `color.neutral`;
z `kinako.json` — siatki czterech emocji i paletę (jasną i ciemną). Nic poza tym:
witryna nie potrzebuje animacji ani scenek.

Kody: 0 — kopia świeża albo zapisana; 1 — w próbie: kopia nieaktualna; 2 — nie
sprawdziłem (brak repo albo pliku).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parent.parent
CEL = KORZEN / "Tools" / "wyglad.json"
UI = Path(os.environ.get("ASEITY_ROOT") or Path.home() / "aseity") / "japanese-ui"
ZRODLA = {"tokens": "tokens/tokens.json",
          "kinako": "Sources/JapaneseUI/Resources/kinako.json"}


def z_head(sciezka: str) -> str | None:
    wynik = subprocess.run(["git", "-C", str(UI), "show", f"HEAD:{sciezka}"],
                           capture_output=True, text=True)
    return wynik.stdout if wynik.returncode == 0 else None


def skrot(tekst: str) -> str:
    return hashlib.sha256(tekst.encode("utf-8")).hexdigest()[:16]


def zloz() -> dict | None:
    surowe = {k: z_head(v) for k, v in ZRODLA.items()}
    if any(v is None for v in surowe.values()):
        return None
    tokeny = json.loads(surowe["tokens"])["color"]
    kinako = json.loads(surowe["kinako"])["kinako"]
    apki = {slug: {"band": w["band"], "accentText": w["accentText"]}
            for slug, w in sorted(tokeny["apps"].items()) if isinstance(w, dict) and "band" in w}
    neutralne = {k: {"light": w["light"], "dark": w["dark"]}
                 for k, w in tokeny["neutral"].items() if isinstance(w, dict)}
    return {
        "_": "Wygenerowane przez Tools/wyglad-z-ui.py z japanese-ui (HEAD) — nie edytować ręcznie.",
        "zrodla": {k: {"plik": ZRODLA[k], "skrot": skrot(v)} for k, v in surowe.items()},
        "apki": apki,
        "neutralne": neutralne,
        "kinako": {"rozmiar": kinako["rozmiar"], "paleta": kinako["paleta"],
                   "paleta_ciemna": kinako["paleta_ciemna"], "emocje": kinako["emocje"]},
    }


def swiezosc() -> str | None:
    """Pusty napis — kopia świeża; tekst — co się rozjechało; None — nie sprawdziłem."""
    if not CEL.exists():
        return "brak Tools/wyglad.json"
    stare = json.loads(CEL.read_text(encoding="utf-8"))["zrodla"]
    rozjazd = []
    for k, sciezka in ZRODLA.items():
        tekst = z_head(sciezka)
        if tekst is None:
            return None
        if stare.get(k, {}).get("skrot") != skrot(tekst):
            rozjazd.append(sciezka)
    return ", ".join(rozjazd)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--wykonaj", action="store_true", help="zapisuje Tools/wyglad.json")
    args = parser.parse_args()
    if not args.wykonaj:
        stan = swiezosc()
        if stan is None:
            print(f"nie sprawdziłem: brak {UI} albo plików w HEAD")
            return 2
        print("wygląd: kopia świeża" if not stan else f"wygląd: nieaktualny ({stan}) — puść z --wykonaj")
        return 1 if stan else 0
    dane = zloz()
    if dane is None:
        print(f"nie sprawdziłem: brak {UI} albo plików w HEAD")
        return 2
    CEL.write_text(json.dumps(dane, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"zapisane: {CEL.relative_to(KORZEN)} ({len(dane['apki'])} apek, "
          f"{len(dane['kinako']['emocje'])} emocje Kinako)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
