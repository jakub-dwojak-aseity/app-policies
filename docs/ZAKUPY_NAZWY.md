# Zakupy w ASC — przemianowanie na wzorzec SEO (poz. 82, etap 2)

**Ten plik jest składem do wpisania, nie stanem.** Stan zakupów czyta się z API
(`v1/apps/<id>/inAppPurchasesV2` i `v2/inAppPurchases/<id>/inAppPurchaseLocalizations`),
nie stąd — §21.N. Tabela niżej była propozycją i **czekała na rozstrzygnięcie dziewięciu
nazw**, które nie mieściły się w trzydziestu znakach. **Rozstrzygnięte 13.09.2026 jedną
regułą** (niżej), więc tabela jest dziś składem do wpisania, nie materiałem do dyskusji.

**Zmierzone 15.09.2026:** produktów jest **38, nie 42**, wszystkie mają komplet nazw
i opisów w `pl` i `en-US` — to nie jest luka do wypełnienia, tylko przemianowanie.
Źródłem prawdy jest `Config/<App>.storekit`, nie ASC; zmiana idzie **do obu miejsc**.

## Reguła, którą to rozstrzygnięto

**Nazwa produktu nie powtarza słowa „japoński".** Kupujący widzi ją w koszyku
**pod nazwą aplikacji**, a ta nazwa już mówi, o jaki język chodzi: `Joshi: Partykuły
japońskie` nad `Partykuły japońskie: poziomy 3–5` to to samo słowo dwa razy w jednym
oknie, kupione za jedenaście znaków z trzydziestu.

Po zdjęciu tego słowa **wszystkie dziewięć nazw mieści się z zapasem** — najdłuższa ma
27 znaków. Jedna reguła zamiast dziewięciu decyzji redakcyjnych i **żadne słowo się nie
gubi**: to samo, którego szuka kupujący, stoi wiersz wyżej i jest polem indeksowanym
samo z siebie.

| dziedzina | było | jest |
|---|---|---|
| Bunmyaku | `japoński w zdaniu` / `Japanese in context` | `w zdaniu` / `in context` |
| Katsuyokei | `Odmiana czasownika` / `Verb conjugation` | `Odmiana` / `Conjugation` |
| Joshi | `Partykuły japońskie` / `Japanese particles` | `Partykuły` / `Particles` |
| Kazoekata | `Liczniki japońskie` / `Japanese counters` | `Liczniki` / `Counters` |
| Shindan | `Poziom japońskiego: pełny arkusz` | `Pełny arkusz` / `Full sheet` |

Kaname zostaje bez zmian — `gramatyka JLPT` nie powtarzała nazwy aplikacji i mieściła
się od początku.

## Co obalił pomiar

Wzorzec z planu — `<dziedzina>: <zakres>` — **mieścił się w 30 znakach tylko w 6 z 38 nazw**.
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
| bunmyaku | Bunmyaku N1 | `N1: w zdaniu` | 12 | `N1: in context` | 14 |
| bunmyaku | Bunmyaku N2 | `N2: w zdaniu` | 12 | `N2: in context` | 14 |
| bunmyaku | Bunmyaku N3 | `N3: w zdaniu` | 12 | `N3: in context` | 14 |
| bunmyaku | Bunmyaku N4 | `N4: w zdaniu` | 12 | `N4: in context` | 14 |
| bunmyaku | Bunmyaku N2 i N1 | `N2 i N1: w zdaniu` | 17 | `N2 and N1: in context` | 21 |
| bunmyaku | Bunmyaku N3 i N1 | `N3 i N1: w zdaniu` | 17 | `N3 and N1: in context` | 21 |
| bunmyaku | Bunmyaku N3 i N2 | `N3 i N2: w zdaniu` | 17 | `N3 and N2: in context` | 21 |
| bunmyaku | Bunmyaku N3, N2 i N1 | `N3, N2 i N1: w zdaniu` | 21 | `N3, N2 and N1: in context` | 25 |
| bunmyaku | Bunmyaku N4 i N1 | `N4 i N1: w zdaniu` | 17 | `N4 and N1: in context` | 21 |
| bunmyaku | Bunmyaku N4 i N2 | `N4 i N2: w zdaniu` | 17 | `N4 and N2: in context` | 21 |
| bunmyaku | Bunmyaku N4, N2 i N1 | `N4, N2 i N1: w zdaniu` | 21 | `N4, N2 and N1: in context` | 25 |
| bunmyaku | Bunmyaku N4 i N3 | `N4 i N3: w zdaniu` | 17 | `N4 and N3: in context` | 21 |
| bunmyaku | Bunmyaku N4, N3 i N1 | `N4, N3 i N1: w zdaniu` | 21 | `N4, N3 and N1: in context` | 25 |
| bunmyaku | Bunmyaku N4, N3 i N2 | `N4, N3 i N2: w zdaniu` | 21 | `N4, N3 and N2: in context` | 25 |
| bunmyaku | Bunmyaku Premium | `W zdaniu: wszystko` | 18 | `In context: everything` | 22 |
| katsuyokei | Katsuyokei Premium | `Odmiana: poziomy 3–5` | 20 | `Conjugation: levels 3–5` | 23 |
| joshi | Joshi Premium | `Partykuły: poziomy 3–5` | 22 | `Particles: levels 3–5` | 21 |
| kazoekata | Kazoekata Premium | `Liczniki: poziomy 3–5` | 21 | `Counters: levels 3–5` | 20 |
| kuzushi | Kuzushi Premium | `Mowa potoczna: poziomy 3–5` | 26 | `Casual Japanese: levels 3–5` | 27 |
| keigo | Keigo Premium | `Japoński formalny: poziomy 3–5` | 30 | `Formal Japanese: levels 3–5` | 27 |
| onomatope | Onomatope Premium | `Onomatopeje: poziomy 3–5` | 24 | `Japanese mimetics: levels 3–5` | 29 |
| kifuku | Kifuku Premium | `Akcent japoński: poziomy 3–5` | 28 | `Pitch accent: levels 3–5` | 24 |
| shindan | Shindan Premium | `Pełny arkusz` | 12 | `Full sheet` | 10 |

## Dziewięć, które stały tu jako nierozstrzygnięte

**Zamknięte 13.09.2026** regułą wyżej. Zostawione jako zapis, bo pokazuje, ile kosztowało
jedno powtórzone słowo: dziewięć nazw wisiało na nim przez tydzień.

| apka | przed regułą | dł | po regule | dł |
|---|---|---:|---|---:|
| bunmyaku | `N3, N2 i N1: japoński w zdaniu` | 30 | `N3, N2 i N1: w zdaniu` | 21 |
| bunmyaku | `N4, N2 i N1: japoński w zdaniu` | 30 | `N4, N2 i N1: w zdaniu` | 21 |
| bunmyaku | `N4, N3 i N1: japoński w zdaniu` | 30 | `N4, N3 i N1: w zdaniu` | 21 |
| bunmyaku | `N4, N3 i N2: japoński w zdaniu` | 30 | `N4, N3 i N2: w zdaniu` | 21 |
| bunmyaku | `Japoński w zdaniu: wszystko` | 27 | `W zdaniu: wszystko` | 18 |
| katsuyokei | `Odmiana czasownika: poziomy 3–5` | 31 | `Odmiana: poziomy 3–5` | 20 |
| joshi | `Partykuły japońskie: poziomy 3–5` | 32 | `Partykuły: poziomy 3–5` | 22 |
| kazoekata | `Liczniki japońskie: poziomy 3–5` | 31 | `Liczniki: poziomy 3–5` | 21 |
| shindan | `Poziom japońskiego: pełny arkusz` | 32 | `Pełny arkusz` | 12 |

Miara po regule: **38 z 38 nazw w limicie, zero przekroczeń** w obu językach.

## Miny z planu SEO, nietknięte

1. `localize()` w większości kopii `asc-iap.py` **zakłada brakujące lokalizacje i pomija
   istniejące**; zmianę wpisuje wyłącznie `--relocalize`, który jest **tylko w `shindan-ios`
   i `kazoekata-ios`**.
2. **Sześć aplikacji stoi dziś w recenzji Apple** — przemianowanie zakupu w trakcie recenzji
   to ruch, którego skutku nikt w rodzinie nie zmierzył.
3. Produkt raz założony w ASC **nie kasuje się nigdy**: każdy przebieg na sucho, z `APP_ID`
   sprawdzonym przed wywołaniem (§21.L).
