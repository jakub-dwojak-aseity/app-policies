# AGENTS.md — app-policies (witryna `jd-japanese.pl`)

Witryna rodziny i **dokumenty prawne dziesiątki**: strony produktowe generowane z metadanych sklepowych
plus polityki, warunki i wsparcie, na które wskazuje ASC. GitHub Pages z `main`, katalog `/`.
**Drzewo ŻYWE i PUBLICZNE** — kluczy ani sekretów tu nie ma i nie wkładamy.

## Mapa rodziny jest gdzie indziej

**`/Users/jakub/aseity/jp-grammar/AGENTS.md`** — mapa dziesiątki: które drzewo żywe, gdzie papiery,
co robi które narzędzie, siedem reguł twardych. **Przeczytaj ją, zanim cokolwiek tu ruszysz.**

| czego szukasz | gdzie |
|---|---|
| **stan witryny/SEO** | **`docs/TERAZ.md`** (tu — tor witryny jedzie osobno od wydań) |
| od czego zacząć dziś | `/Users/jakub/aseity/jp-grammar/docs/TERAZ.md` |
| co zostało do zrobienia | `/Users/jakub/aseity/jp-grammar/docs/BACKLOG_UI_RODZINA.md` (poz. 82, 84, 112, 113) |
| co ma być takie samo w dziesiątce | `/Users/jakub/aseity/jp-grammar/docs/FAMILY_CONVENTIONS.md` |
| pomiary SEO/AEO i kolejka toru | `/Users/jakub/aseity/jp-grammar/docs/PLAN_SEO_AEO.md` §11–§12 |

**Papiery rodziny pisze się w hubie, nie tutaj.** Dokumentów z datą w nazwie nie zakładamy
(§23) — bramka je odbija. Co przestało obowiązywać, idzie do `docs/archiwum/`.

## Miny tego repo

1. **Strony są GENEROWANE** (`Tools/generuj-strony.py`) — poprawkę wnosi się w metadanych apki albo
   w tablicy `NAPISY`, **nigdy w wyniku**. `Tools/apps.json` ma wskazywać `jp-grammar-1.2.5` i `bunmyaku-n2`.
2. **`READY_FOR_SALE` w ASC nie znaczy, że strona sklepowa żyje.** `wSklepie` jest **zmierzone**
   `itunes.apple.com/lookup`, a jedna witryna potrafi chwilę oddać zero — `--sprawdz-sklep` pyta pięciu.
3. **`Tools/asc-marketing-url.py` przerywa na pierwszym `409`** od apki w sklepie (okno zapisu to tylko
   `WAITING_FOR_REVIEW`, §21.AB) — przy mieszanej rodzinie iść `--apka <slug>`, apka po apce.
