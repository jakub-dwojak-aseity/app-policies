# Zakupy w ASC — przemianowanie na wzorzec SEO (poz. 82, etap 2)

**Ten plik jest materiałem do decyzji, nie stanem.** Stan zakupów czyta się z API
(`v1/apps/<id>/inAppPurchasesV2` i `v2/inAppPurchases/<id>/inAppPurchaseLocalizations`),
nie stąd — §21.N. Tabela niżej jest propozycją z 15.09.2026 i **czeka na rozstrzygnięcie
dziewięciu nazw**, które nie mieszczą się w trzydziestu znakach.

**Zmierzone 15.09.2026:** produktów jest **38, nie 42**, wszystkie mają komplet nazw
i opisów w `pl` i `en-US` — to nie jest luka do wypełnienia, tylko przemianowanie.
Źródłem prawdy jest `Config/<App>.storekit`, nie ASC; zmiana idzie **do obu miejsc**.

## Co obalił pomiar

Wzorzec z planu — `<dziedzina>: <zakres>` — **mieści się w 30 znakach tylko w 6 z 38 nazw**.
Dwadzieścia produktów kombinowanych Kaname i Bunmyaku nie unosi naraz poziomów i dziedziny.
Wariant niżej odwraca kolejność (poziomy z przodu, bez słowa „Poziomy”) i skraca dwie
dziedziny — zostaje **9 nazw za długich**, wszystkie do rozstrzygnięcia redakcyjnego.

## Propozycja

| apka | dziś (pl) | proponowane (pl) | dł | proponowane (en) | dł |
|---|---|---|---:|---|---:|
| kaname | Poziom N1 — pełny dostęp | `N1: gramatyka JLPT` | 18 | `N1: JLPT grammar` | 16 |
| kaname | Poziom N2 — pełny dostęp | `N2: gramatyka JLPT` | 18 | `N2: JLPT grammar` | 16 |
| kaname | Poziom N3 — pełny dostęp | `N3: gramatyka JLPT` | 18 | `N3: JLPT grammar` | 16 |
| kaname | Poziom N4 — pełny dostęp | `N4: gramatyka JLPT` | 18 | `N4: JLPT grammar` | 16 |
| kaname | N2 i N1 — pełny dostęp | `N2 i N1: gramatyka JLPT` | 23 | `N2 and N1: JLPT grammar` | 23 |
| kaname | N3 i N1 — pełny dostęp | `N3 i N1: gramatyka JLPT` | 23 | `N3 and N1: JLPT grammar` | 23 |
| kaname | N3 i N2 — pełny dostęp | `N3 i N2: gramatyka JLPT` | 23 | `N3 and N2: JLPT grammar` | 23 |
| kaname | N3, N2 i N1 — pełny dostęp | `N3, N2 i N1: gramatyka JLPT` | 27 | `N3, N2 and N1: JLPT grammar` | 27 |
| kaname | N4 i N1 — pełny dostęp | `N4 i N1: gramatyka JLPT` | 23 | `N4 and N1: JLPT grammar` | 23 |
| kaname | N4 i N2 — pełny dostęp | `N4 i N2: gramatyka JLPT` | 23 | `N4 and N2: JLPT grammar` | 23 |
| kaname | N4, N2 i N1 — pełny dostęp | `N4, N2 i N1: gramatyka JLPT` | 27 | `N4, N2 and N1: JLPT grammar` | 27 |
| kaname | N4 i N3 — pełny dostęp | `N4 i N3: gramatyka JLPT` | 23 | `N4 and N3: JLPT grammar` | 23 |
| kaname | N4, N3 i N1 — pełny dostęp | `N4, N3 i N1: gramatyka JLPT` | 27 | `N4, N3 and N1: JLPT grammar` | 27 |
| kaname | N4, N3 i N2 — pełny dostęp | `N4, N3 i N2: gramatyka JLPT` | 27 | `N4, N3 and N2: JLPT grammar` | 27 |
| kaname | Premium — pełny dostęp | `Gramatyka JLPT: wszystko` | 24 | `JLPT grammar: everything` | 24 |
| bunmyaku | Bunmyaku N1 | `N1: japoński w zdaniu` | 21 | `N1: Japanese in context` | 23 |
| bunmyaku | Bunmyaku N2 | `N2: japoński w zdaniu` | 21 | `N2: Japanese in context` | 23 |
| bunmyaku | Bunmyaku N3 | `N3: japoński w zdaniu` | 21 | `N3: Japanese in context` | 23 |
| bunmyaku | Bunmyaku N4 | `N4: japoński w zdaniu` | 21 | `N4: Japanese in context` | 23 |
| bunmyaku | Bunmyaku N2 i N1 | `N2 i N1: japoński w zdaniu` | 26 | `N2 and N1: Japanese in context` | 30 |
| bunmyaku | Bunmyaku N3 i N1 | `N3 i N1: japoński w zdaniu` | 26 | `N3 and N1: Japanese in context` | 30 |
| bunmyaku | Bunmyaku N3 i N2 | `N3 i N2: japoński w zdaniu` | 26 | `N3 and N2: Japanese in context` | 30 |
| bunmyaku | Bunmyaku N3, N2 i N1 | `N3, N2 i N1: japoński w zdaniu` | 30 ⚠ | `N3, N2 and N1: Japanese in context` | 34 |
| bunmyaku | Bunmyaku N4 i N1 | `N4 i N1: japoński w zdaniu` | 26 | `N4 and N1: Japanese in context` | 30 |
| bunmyaku | Bunmyaku N4 i N2 | `N4 i N2: japoński w zdaniu` | 26 | `N4 and N2: Japanese in context` | 30 |
| bunmyaku | Bunmyaku N4, N2 i N1 | `N4, N2 i N1: japoński w zdaniu` | 30 ⚠ | `N4, N2 and N1: Japanese in context` | 34 |
| bunmyaku | Bunmyaku N4 i N3 | `N4 i N3: japoński w zdaniu` | 26 | `N4 and N3: Japanese in context` | 30 |
| bunmyaku | Bunmyaku N4, N3 i N1 | `N4, N3 i N1: japoński w zdaniu` | 30 ⚠ | `N4, N3 and N1: Japanese in context` | 34 |
| bunmyaku | Bunmyaku N4, N3 i N2 | `N4, N3 i N2: japoński w zdaniu` | 30 ⚠ | `N4, N3 and N2: Japanese in context` | 34 |
| bunmyaku | Bunmyaku Premium | `Japoński w zdaniu: wszystko` | 27 ⚠ | `Japanese in context: everything` | 31 |
| katsuyokei | Katsuyokei Premium | `Odmiana czasownika: poziomy 3–5` | 31 ⚠ | `Verb conjugation: levels 3–5` | 28 |
| joshi | Joshi Premium | `Partykuły japońskie: poziomy 3–5` | 32 ⚠ | `Japanese particles: levels 3–5` | 30 |
| kazoekata | Kazoekata Premium | `Liczniki japońskie: poziomy 3–5` | 31 ⚠ | `Japanese counters: levels 3–5` | 29 |
| kuzushi | Kuzushi Premium | `Mowa potoczna: poziomy 3–5` | 26 | `Casual Japanese: levels 3–5` | 27 |
| keigo | Keigo Premium | `Japoński formalny: poziomy 3–5` | 30 | `Formal Japanese: levels 3–5` | 27 |
| onomatope | Onomatope Premium | `Onomatopeje: poziomy 3–5` | 24 | `Japanese mimetics: levels 3–5` | 29 |
| kifuku | Kifuku Premium | `Akcent japoński: poziomy 3–5` | 28 | `Pitch accent: levels 3–5` | 24 |
| shindan | Shindan Premium | `Poziom japońskiego: pełny arkusz` | 32 ⚠ | `Japanese level test: full test` | 30 |

## Dziewięć do rozstrzygnięcia

Każda przekracza 30 znaków w jednym z języków. Skrócenie musi wybrać, co wypada:

- **bunmyaku** — `N3, N2 i N1: japoński w zdaniu` (30) / `N3, N2 and N1: Japanese in context` (34)
- **bunmyaku** — `N4, N2 i N1: japoński w zdaniu` (30) / `N4, N2 and N1: Japanese in context` (34)
- **bunmyaku** — `N4, N3 i N1: japoński w zdaniu` (30) / `N4, N3 and N1: Japanese in context` (34)
- **bunmyaku** — `N4, N3 i N2: japoński w zdaniu` (30) / `N4, N3 and N2: Japanese in context` (34)
- **bunmyaku** — `Japoński w zdaniu: wszystko` (27) / `Japanese in context: everything` (31)
- **katsuyokei** — `Odmiana czasownika: poziomy 3–5` (31) / `Verb conjugation: levels 3–5` (28)
- **joshi** — `Partykuły japońskie: poziomy 3–5` (32) / `Japanese particles: levels 3–5` (30)
- **kazoekata** — `Liczniki japońskie: poziomy 3–5` (31) / `Japanese counters: levels 3–5` (29)
- **shindan** — `Poziom japońskiego: pełny arkusz` (32) / `Japanese level test: full test` (30)

## Miny z planu SEO, nietknięte

1. `localize()` w większości kopii `asc-iap.py` **zakłada brakujące lokalizacje i pomija
   istniejące**; zmianę wpisuje wyłącznie `--relocalize`, który jest **tylko w `shindan-ios`
   i `kazoekata-ios`**.
2. **Sześć aplikacji stoi dziś w recenzji Apple** — przemianowanie zakupu w trakcie recenzji
   to ruch, którego skutku nikt w rodzinie nie zmierzył.
3. Produkt raz założony w ASC **nie kasuje się nigdy**: każdy przebieg na sucho, z `APP_ID`
   sprawdzonym przed wywołaniem (§21.L).
