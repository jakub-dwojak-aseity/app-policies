#!/usr/bin/env python3
"""Wpisuje Marketing URL dziesięciu aplikacji — po jednym adresie na język.

    python3 Tools/asc-marketing-url.py              # pokazuje, co by zrobił
    python3 Tools/asc-marketing-url.py --zapisz     # wpisuje do App Store Connect

Pole *Marketing URL* siedzi w `appStoreVersionLocalizations` i jest **per lokalizacja**,
więc polska karta może wskazywać polską stronę, a angielska angielską. Do 09.09.2026
wypełnione było **jedno pole z dwudziestu**: Kuzushi miało w obu lokalizacjach ten sam
angielski adres, bo była to jedyna strona produktowa, jaka istniała.

**Adresy pochodzą z tego samego manifestu co strony** (`Tools/apps.json`), a nie są
wpisane tutaj. To jest cały powód, dla którego to jest narzędzie, a nie dwadzieścia
kliknięć: po przestawieniu domeny (`docs/DOMENA.md`) zmienia się `bazaAdresu`, wszystkie
dwadzieścia adresów staje się nieaktualnych naraz i trzeba je wpisać po raz drugi.

**Wersję wybiera się STANEM, nie pozycją na liście.** `data[0]` bywa wersją, która jeszcze
nie wyszła, albo taką, która już zeszła — ta sama pomyłka wyszła w rodzinie w trzech
narzędziach. Bierzemy wersję w recenzji albo przygotowywaną, a gdy takiej nie ma —
najnowszą wydaną.

**Ścieżki bez wiodącego ukośnika — i to nie jest kosmetyka.** `asc.py` skleja adres jako
`ROOT + "v1/" + path`, kiedy `path` **nie** zaczyna się od `v1/`. Ścieżka `/v1/…` daje więc
`…/v1//v1/…`, a bramka Apple **część takich adresów obsługuje, a części nie**: kolekcje pod
aplikacją (`/v1/apps/{id}/appStoreVersions`) wracają poprawnymi danymi, a pojedynczy zasób
(`/v1/appStoreVersionLocalizations/{id}`) wraca `404 NOT_FOUND` z komunikatem o typie
zasobu, który brzmi jak błąd w treści żądania. **Odczyty przechodziły, zapis nie** — czyli
najgorszy możliwy układ, bo skrypt czyta poprawnie i nie zapisuje nic. Zmierzone
09.09.2026 na tym narzędziu, gdy pierwszy `PATCH` „przeszedł", a wartość została stara.

**Zmierzone 09.09.2026, zanim cokolwiek zostało wpisane:**

- sonda tożsamościowa (`PATCH` tą samą wartością) na wersji `READY_FOR_SALE` przechodzi
  kodem **200**, a stan wersji i wartość pola zostają bez zmian;
- pole jest widoczne publicznie jako `sellerUrl` w `itunes.apple.com/lookup` — i to jest
  jedyny sposób, żeby zmierzyć **skutek**, a nie samo powodzenie wywołania. Karta
  w sklepie aktualizuje się z opóźnieniem, więc brak zmiany zaraz po zapisie nie jest
  jeszcze dowodem, że zapis nie zadziałał.
"""

import argparse
import json
import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parent.parent

# `asc.py` mieszka w prywatnych repozytoriach aplikacji — to repozytorium jest publiczne
# i **nie ma go u siebie z rozmysłu**. Klucza ani identyfikatora wydawcy nie ma w żadnym
# z nich (klucz: `~/.appstoreconnect/private_keys/`, wydawca: `ASC_ISSUER_ID`).
KLIENT = KORZEN.parent / "kifuku" / "Tools"


def klient():
    if not (KLIENT / "asc.py").exists():
        raise SystemExit(f"brak klienta App Store Connect: {KLIENT / 'asc.py'}\n"
                         "To narzędzie pożycza `asc.py` z repozytorium aplikacji — "
                         "publiczne repozytorium stron nie trzyma własnej kopii.")
    sys.path.insert(0, str(KLIENT))
    import asc
    return asc


# Wersja, do której wolno pisać, w kolejności pierwszeństwa. Stan `READY_FOR_SALE` jest
# ostatni: gdy istnieje cokolwiek nowszego, metadane należą do tamtej wersji.
PIERWSZENSTWO = ("PREPARE_FOR_SUBMISSION", "DEVELOPER_REJECTED", "REJECTED",
                 "METADATA_REJECTED", "WAITING_FOR_REVIEW", "IN_REVIEW",
                 "PENDING_DEVELOPER_RELEASE", "READY_FOR_SALE")


def wersja_docelowa(asc, app_id):
    dane = asc.get(f"v1/apps/{app_id}/appStoreVersions?limit=10")["data"]
    for stan in PIERWSZENSTWO:
        pasujace = [w for w in dane if w["attributes"]["appStoreState"] == stan]
        if pasujace:
            return pasujace[0]
    raise SystemExit(f"{app_id}: żadna wersja nie jest w stanie, do którego wolno pisać")


def adresy(manifest, apka):
    baza = manifest["bazaAdresu"]
    return {"pl": f"{baza}/apps/{apka['slug']}/",
            "en-US": f"{baza}/en/apps/{apka['slug']}/"}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--zapisz", action="store_true",
                        help="bez tego narzędzie tylko pokazuje, co by zrobiło")
    parser.add_argument("--apka", help="ogranicz do jednej aplikacji (slug)")
    args = parser.parse_args()

    asc = klient()
    manifest = json.loads((KORZEN / "Tools" / "apps.json").read_text(encoding="utf-8"))
    apki = sorted(manifest["aplikacje"], key=lambda a: a["kolejnosc"])
    if args.apka:
        apki = [a for a in apki if a["slug"] == args.apka] or \
            sys.exit(f"nie ma aplikacji o slugu {args.apka}")

    zmian = bez_zmian = 0
    for apka in apki:
        wersja = wersja_docelowa(asc, apka["appId"])
        stan = wersja["attributes"]["appStoreState"]
        numer = wersja["attributes"]["versionString"]
        chciane = adresy(manifest, apka)
        lokalizacje = asc.get(
            f"v1/appStoreVersions/{wersja['id']}/appStoreVersionLocalizations")["data"]
        print(f"\n{apka['slug']}  {numer}  {stan}")
        for lokalizacja in sorted(lokalizacje, key=lambda l: l["attributes"]["locale"]):
            jezyk = lokalizacja["attributes"]["locale"]
            teraz = lokalizacja["attributes"].get("marketingUrl")
            cel = chciane.get(jezyk)
            if cel is None:
                print(f"  {jezyk:6} pomijam — manifest nie zna tej lokalizacji")
                continue
            if teraz == cel:
                print(f"  {jezyk:6} bez zmian")
                bez_zmian += 1
                continue
            print(f"  {jezyk:6} {teraz or '—'}\n         → {cel}")
            zmian += 1
            if args.zapisz:
                # `asc.patch` **nie rzuca wyjątkiem przy błędzie HTTP** — oddaje słownik
                # z kluczem `HTTPError`. Pierwsza wersja tego narzędzia tego nie sprawdzała
                # i meldowała zapis, którego nie było.
                odpowiedz = asc.patch(f"v1/appStoreVersionLocalizations/{lokalizacja['id']}",
                          "appStoreVersionLocalizations", lokalizacja["id"],
                          {"marketingUrl": cel})
                if odpowiedz.get("HTTPError"):
                    raise SystemExit(f"  {jezyk}: {odpowiedz['HTTPError']} "
                                     f"{odpowiedz.get('body', '')[:400]}")
                po = asc.get(f"v1/appStoreVersionLocalizations/{lokalizacja['id']}")
                zapisane = po["data"]["attributes"].get("marketingUrl")
                if zapisane != cel:
                    raise SystemExit(f"  {jezyk}: odczyt po zapisie oddał {zapisane!r}")
                stan_po = asc.get(f"v1/appStoreVersions/{wersja['id']}"
                                  )["data"]["attributes"]["appStoreState"]
                if stan_po != stan:
                    raise SystemExit(f"  {apka['slug']}: stan wersji {stan} → {stan_po} "
                                     "— przerywam, zanim ruszę kolejne aplikacje")
                print(f"         zapisane, stan wersji nadal {stan_po}")

    print(f"\n{zmian} pól do zmiany, {bez_zmian} już zgodnych"
          + ("" if args.zapisz else "  (przebieg na sucho — nic nie zapisano)"))


if __name__ == "__main__":
    main()
