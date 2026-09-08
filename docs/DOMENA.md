# Domena `jd-japanese.pl` — co jest dziś, co trzeba przestawić i czym to grozi

Napisane w nocy 08/09.09.2026 razem ze stronami produktowymi. **Nic tu nie zostało
wykonane** — przestawienie domeny wymaga panelu OVH, do którego ma dostęp tylko Jakub.
Ten dokument ma sprawić, że decyzja zajmie kwadrans, a nie wieczór.

## Stan zmierzony 08.09.2026, ok. 23:55

| co | wynik |
|---|---|
| `jd-japanese.pl` A | `213.186.33.5` (parking OVH), TTL 3600 |
| `www.jd-japanese.pl` A | `213.186.33.5` |
| `http://jd-japanese.pl/` | **302** → `http://www.jd-japanese.pl/` |
| `http://www.jd-japanese.pl/` | 200, strona „Site en construction" |
| nagłówek na tej stronie | `<meta name="robots" content="none,noindex,nofollow">` |
| `https://jd-japanese.pl/` | **nie odpowiada w ogóle** (brak certyfikatu) |
| serwery nazw | `ns111.ovh.net`, `dns111.ovh.net` |
| `api.` i `admin.` | `34.58.188.69` — maszyna GCP `japanese-grammar` |
| `jakub-dwojak-aseity.github.io/app-policies/` | **200**, wraz z nowymi stronami |

**To jest cała stawka tej nocnej pracy.** Strony produktowe są zrobione i działają pod
adresem `github.io`, ale domena, którą ktoś mógłby podać dalej, **aktywnie odpycha roboty**
własnym `noindex,nofollow` — a strona, której nie ma w indeksie, nie trafi do żadnej
odpowiedzi modelu ani do żadnego wyniku wyszukiwania.

## Dwie drogi. Rekomendacja: apeks

### Droga A — apeks `jd-japanese.pl` na GitHub Pages *(rekomendowana)*

Cała domena staje się stroną rodziny. To jest ten adres, który da się komuś podać.

W panelu OVH, w **strefie DNS** domeny `jd-japanese.pl`:

1. **usunąć** rekord `A` apeksu wskazujący `213.186.33.5`;
2. **dodać cztery rekordy `A`** na apeksie (pole „subdomena" puste):

   ```
   185.199.108.153
   185.199.109.153
   185.199.110.153
   185.199.111.153
   ```

3. *(opcjonalnie, ale warto)* **cztery `AAAA`**, żeby domena działała po IPv6:

   ```
   2606:50c0:8000::153
   2606:50c0:8001::153
   2606:50c0:8002::153
   2606:50c0:8003::153
   ```

4. `www` **jako `CNAME`** na `jakub-dwojak-aseity.github.io.` (z kropką na końcu),
   zamiast dzisiejszego `A` na parking;
5. **`api.` i `admin.` zostawić bez zmian.** To osobne subdomeny i wskazują maszynę
   z produkcyjnym AI dziesięciu aplikacji — ta zmiana ich nie dotyka.

Potem w GitHubie: **Settings → Pages → Custom domain** → `jd-japanese.pl` → Save,
i po kilkunastu minutach, gdy certyfikat się wystawi, zaznaczyć **Enforce HTTPS**.
GitHub zapisze wtedy w repozytorium plik `CNAME` w katalogu głównym — jego treść leży
gotowa w `Tools/CNAME.przygotowany`. **Nie został wrzucony do katalogu głównego
celowo:** ten plik *jest* przełącznikiem, a nie przygotowaniem do przełączenia.

### Droga B — subdomena, np. `apps.jd-japanese.pl`

Jeden rekord `CNAME` (`apps` → `jakub-dwojak-aseity.github.io.`), zero dotykania apeksu
i parkingu, cofnięcie jednym kliknięciem. Kosztuje to tyle, że adres jest gorszy do
podania i słabszy w wyszukiwarce niż domena główna. **Sensowna, jeśli apeks ma kiedyś
służyć do czegoś innego.**

## Czym to grozi i co sprawdzić po przełączeniu

**Adresy dokumentów prawnych z App Store Connect nie przestaną działać, ale zmienią
zachowanie.** Po ustawieniu domeny własnej GitHub przekierowuje
`jakub-dwojak-aseity.github.io/app-policies/…` na nowy adres. Przekierowanie to nie
to samo co działający adres, a w ASC stoi dziś **dwadzieścia** takich odsyłaczy
(polityka i wsparcie ×10 aplikacji ×2 języki). **To jest pierwsza rzecz do zmierzenia
po przełączeniu**, jednym poleceniem:

```
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" \
  https://jakub-dwojak-aseity.github.io/app-policies/kaname/1.2/privacy.html
```

Oczekiwane: `301` i adres w nowej domenie. Gdyby wyszło `404`, adresy w ASC trzeba
przepisać **przy najbliższym wydaniu każdej aplikacji** — nie da się tego zrobić dla
aplikacji stojącej w kolejce inaczej niż razem z nią.

**Ścieżka bazowa się zmienia i strony trzeba wygenerować ponownie.** Dziś repozytorium
jest *project page* i stoi pod `/app-policies/`; z domeną własną staje się korzeniem.
Wszystkie adresy kanoniczne, `hreflang` i mapa witryny są absolutne, więc po przełączeniu:

1. w `Tools/apps.json` zmienić `bazaAdresu` na `https://jd-japanese.pl`;
2. `python3 Tools/generuj-strony.py` — przeliczy 28 plików, w tym `sitemap.xml`,
   `robots.txt` i sekcję adresów w README;
3. zgłosić `https://jd-japanese.pl/sitemap.xml` w Google Search Console.

**Parking OVH trzeba wyłączyć, a nie tylko ominąć.** Jeśli do domeny jest przypięty
hosting OVH, sama zmiana rekordów `A` w strefie DNS bywa nadpisywana przez panel
hostingu. W razie oporu: odpiąć hosting od domeny, dopiero potem ustawiać rekordy.

## Czego ta zmiana **nie** załatwia

Klucz App Store Connect oddaje **403 na `analyticsReportRequests`**, więc nie widać,
na jakie frazy ludzie trafiają do aplikacji. Raport *App Store Search terms* otwiera
się wyłącznie w przeglądarce i tylko Jakub może go zobaczyć. **Cała optymalizacja
stron i metadanych jest zakładem opartym na rozumowaniu, a nie pomiarem skutku** —
i pozostanie nim, dopóki ktoś nie otworzy tego raportu.
