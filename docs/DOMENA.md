# `jd-japanese.pl` — krok po kroku

Stan zmierzony **09.09.2026**. Nic z tego nie zostało wykonane: apeks wymaga panelu OVH.
Każdy krok ma pod spodem polecenie, którym sprawdzasz, czy zadziałał — **nie przechodź
dalej, dopóki nie odpowie tak, jak napisane.**

## Zanim zaczniesz: jedna decyzja

**Cztery aplikacje stoją teraz w recenzji** (Shindan, Keigo, Kifuku, Onomatope), a recenzent
Apple otwiera adres polityki prywatności. Te adresy wskazują `github.io` i po ustawieniu
domeny własnej GitHub zacznie je **przekierowywać** na `jd-japanese.pl`. Między ustawieniem
domeny a wystawieniem certyfikatu jest okno — zwykle kilkanaście minut — w którym
przekierowanie prowadzi pod adres bez działającego HTTPS.

- **Zero ryzyka:** zrób kroki 1–5 (same rekordy DNS, apeks i tak stoi na parkingu),
  a krok 6 zostaw do czasu, aż ta czwórka wyjdzie z recenzji.
- **Teraz:** zrób wszystko, ale krok 6 wykonaj wtedy, gdy masz dwadzieścia minut, żeby
  dopilnować kroku 7. Prawdopodobieństwo, że recenzent trafi akurat w to okno, jest małe —
  ale kosztem jest odrzucona recenzja, nie ostrzeżenie.

To jest Twoja decyzja i dlatego nie została podjęta za Ciebie.

---

## Krok 1 — otwórz strefę DNS

OVH Manager → **Web Cloud** → **Domeny** → `jd-japanese.pl` → zakładka **Strefa DNS**.

Zobaczysz tam m.in. rekord `A` bez subdomeny (apeks) wskazujący `213.186.33.5` oraz `www`
też na `213.186.33.5`. `api` i `admin` wskazują `34.58.188.69` — **tych dwóch nie ruszaj**,
to maszyna z produkcyjnym AI dziesięciu aplikacji.

## Krok 2 — usuń rekord `A` apeksu

Skasuj rekord `A` z pustą subdomeną, ten na `213.186.33.5`.

> **Jeśli panel nie pozwala go zmienić**, to znaczy, że do domeny przypięty jest hosting
> OVH i to on nadpisuje strefę. Wtedy najpierw: **Web Cloud → Hosting → odepnij domenę**
> (albo w ustawieniach domeny zdejmij powiązanie z hostingiem), i dopiero wróć tutaj.
> Sama zmiana rekordów przy przypiętym hostingu potrafi się cofnąć.

## Krok 3 — dodaj cztery rekordy `A` na apeksie

**Pole „subdomena" zostaw PUSTE.** Puste znaczy „sama domena", czyli apeks. `@` to notacja
z plików strefy (BIND) i z paneli w stylu Cloudflare — OVH pyta o subdomenę i chce tam
pustki. Gdyby formularz pustego nie przyjął, `@` znaczy to samo. Po dodaniu rekord jest
na liście opisany jako `jd-japanese.pl.` z kropką na końcu, a nie jako `@`.

Typ `A`, po jednym rekordzie na adres:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

To są cztery adresy GitHub Pages. Cztery, a nie jeden — jeśli któryś padnie, domena dalej
działa.

## Krok 4 — przestaw `www` na `CNAME`

Najpierw **usuń** istniejący rekord `A` dla `www` (ten na `213.186.33.5`), potem dodaj:

```
subdomena: www     typ: CNAME     cel: jakub-dwojak-aseity.github.io.
```

**Kropka na końcu jest istotna** — bez niej OVH dokleja nazwę domeny i cel wychodzi
`jakub-dwojak-aseity.github.io.jd-japanese.pl`.

## Krok 5 — *(opcjonalnie)* cztery `AAAA`, żeby działało po IPv6

Subdomena znów **pusta**, typ `AAAA`:

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

### Sprawdzenie kroków 2–5

Stary rekord ma TTL 3600, więc na propagację daj do godziny.

```
dig +short A jd-japanese.pl
dig +short CNAME www.jd-japanese.pl
dig +short A api.jd-japanese.pl
```

Ma wyjść: cztery adresy `185.199.10*.153`, `jakub-dwojak-aseity.github.io.`
oraz **niezmienione** `34.58.188.69`. Dopóki widzisz `213.186.33.5`, nie idź dalej.

---

## Krok 6 — powiedz GitHubowi, że to jego domena

`github.com/jakub-dwojak-aseity/app-policies` → **Settings** → **Pages** →
**Custom domain** → wpisz `jd-japanese.pl` → **Save**.

GitHub sam dopisze do repozytorium plik `CNAME` w katalogu głównym (jego treść leży
w `Tools/CNAME.przygotowany`) i zacznie sprawdzać DNS. Poczekaj na komunikat
**„DNS check successful"**.

## Krok 7 — poczekaj na certyfikat i włącz HTTPS

Gdy pod polem pojawi się możliwość zaznaczenia **Enforce HTTPS**, zaznacz. Certyfikat
wystawia się zwykle kilkanaście minut, czasem dłużej.

### Sprawdzenie kroków 6–7 — trzy polecenia, wszystkie muszą przejść

```
curl -sI https://jd-japanese.pl/ | head -1
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" \
  https://jakub-dwojak-aseity.github.io/app-policies/kifuku/1.0/privacy.html
curl -s -o /dev/null -w "%{http_code}\n" https://jd-japanese.pl/kifuku/1.0/privacy.html
```

Oczekiwane: `HTTP/2 200`, potem `301` z adresem w nowej domenie, potem `200`.
**Drugie polecenie jest najważniejsze** — to jest ten adres, który recenzent Apple ma
wpisany w karcie aplikacji, dwadzieścia razy w dziesięciu aplikacjach.

---

## Krok 8 — przelicz strony na nową domenę

Repozytorium przestaje stać pod `/app-policies/` i staje się korzeniem domeny, więc
wszystkie adresy kanoniczne, `hreflang` i mapa witryny są od tej chwili nieaktualne.

```
cd ~/aseity/app-policies
git pull                                   # zaciąga plik CNAME dopisany przez GitHub
sed -i '' 's|"bazaAdresu": ".*"|"bazaAdresu": "https://jd-japanese.pl"|' Tools/apps.json
python3 Tools/generuj-strony.py --sprawdz  # bramki muszą być zielone
python3 Tools/generuj-strony.py
git add -A && git commit -m "Strony przeliczone na domenę jd-japanese.pl" && git push
```

## Krok 9 — wpisz nowe adresy stron do App Store Connect

Marketing URL w kartach aplikacji wskazuje dziś stary adres `github.io`. To samo narzędzie,
które je wpisało, wpisze nowe:

```
export ASC_ISSUER_ID=$(cat ~/.appstoreconnect/issuer_id)
python3 Tools/asc-marketing-url.py            # przebieg na sucho
python3 Tools/asc-marketing-url.py --zapisz
```

**Przyjmą to tylko aplikacje stojące w kolejce** — apka wydana odbija
`409 STATE_ERROR` i czeka na swoje najbliższe wydanie (§21.AB). Narzędzie samo pokazuje,
które to które, i przerywa, gdyby stan wersji drgnął po zapisie.

## Krok 10 — zgłoś mapę witryny

Google Search Console → dodaj własność `jd-japanese.pl` → **Sitemaps** →
`https://jd-japanese.pl/sitemap.xml`.

To jest też jedyne miejsce, w którym w ogóle zobaczysz, czy ta cała robota działa: klucz
App Store Connect oddaje **403 na `analyticsReportRequests`**, więc frazy z App Store są
poza zasięgiem skryptów. Raport *App Store Search terms* otwiera się wyłącznie
w przeglądarce i tylko Ty możesz go zobaczyć.

---

## Stan wyjściowy, zmierzony 09.09.2026

| co | wynik |
|---|---|
| `jd-japanese.pl` A | `213.186.33.5` (parking OVH), TTL 3600 |
| `www.jd-japanese.pl` A | `213.186.33.5` |
| `http://jd-japanese.pl/` | **302** → `http://www.jd-japanese.pl/` |
| `http://www.jd-japanese.pl/` | 200, „Site en construction", `robots: none,noindex,nofollow` |
| `https://jd-japanese.pl/` | **nie odpowiada w ogóle** |
| serwery nazw | `ns111.ovh.net`, `dns111.ovh.net` |
| `api.` i `admin.` | `34.58.188.69` — maszyna GCP `japanese-grammar`, **nie ruszać** |
| `jakub-dwojak-aseity.github.io/app-policies/` | 200, strony produktowe żywe |

**To jest cała stawka.** Strony są zrobione i działają, ale domena, którą można komuś
podać, dziś **aktywnie odpycha roboty** własnym `noindex,nofollow` — a strona, której nie
ma w indeksie, nie trafi do żadnej odpowiedzi modelu ani do żadnego wyniku wyszukiwania.

## Wariant zapasowy: subdomena zamiast apeksu

Jeden rekord `CNAME` (`apps` → `jakub-dwojak-aseity.github.io.`), zero dotykania apeksu
i parkingu, cofnięcie jednym kliknięciem. Kosztuje to tyle, że adres jest gorszy do podania
i słabszy w wyszukiwarce niż domena główna. Sensowne tylko wtedy, gdy apeks ma kiedyś
służyć do czegoś innego.
