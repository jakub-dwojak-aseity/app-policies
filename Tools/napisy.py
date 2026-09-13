#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cały tekst własny witryny — jedna tablica, jeden plik.

Reguła brzmi: **treść stron pochodzi z tego, co przeszło przegląd, i nie jest
pisana od nowa.** Miarą, czy reguła trzyma, jest długość tej tablicy: wszystko,
co nie przyszło z metadanych sklepowych ani z dokumentu prawnego, musi tu stać
i dać się policzyć wzrokiem.

**Dlaczego osobny plik, a nie stała w generatorze.** Od 09.09.2026 w te same
napisy sięga drugie narzędzie — `glowy_dokumentow.py`, które dopisuje stopkę
nawigacyjną do dokumentów prawnych. Przepisanie do niego dwóch etykiet byłoby
najkrótszą drogą do tego, żeby tekst własny zaczął żyć w dwóch miejscach
i cicho się rozjechał, a tablica przestała być miarą czegokolwiek.
"""

# Cały tekst własny generatora. Trzymany w jednym miejscu z rozmysłem: przy stronach
# najłatwiej zsunąć się w pisanie zdań o aplikacjach obok ich opisów, a wtedy strona
# zaczyna obiecywać rzeczy, których nikt nie przejrzał. Jak długa jest ta tablica,
# tak dużo tekstu na stronach nie pochodzi ze sklepu.
NAPISY = {
    "pl": {
        "html_lang": "pl",
        # **Bez liczby aplikacji w tytule.** Do 13.09.2026 stało tu „w dziesięciu
        # aplikacjach" — liczba prawdziwa w dniu pisania i fałszywa od dnia, w którym
        # rodzina urosła. Tytuł strony głównej jest najdroższym napisem witryny
        # (wchodzi w `<title>`, w okruszek i w `WebSite.name`), więc ma mówić, CZYM
        # ta rodzina jest, a nie ile jej jest.
        "tytul_mapy": "Japoński w osobnych aplikacjach",
        # **Bez spójnika zamykającego listę.** Do 13.09.2026 kończyło się to zdanie
        # słowami „i onomatopeje" — i to „i" było całą wadą: spójnik zamykający
        # deklaruje komplet, więc lista musi być pełna. Nie była. Wyliczenie miało
        # dziewięć dziedzin przy dziesięciu aplikacjach: **wypadł Shindan**, a z nim
        # fraza „test poziomu", po której trafia tu ktoś, kto nie wie, od czego zacząć.
        # Ten sam błąd komentarz nad `tytul_mapy` naprawił już raz, o dwie linijki
        # wyżej — liczba prawdziwa w dniu pisania i fałszywa nazajutrz.
        # Lista bez klamry niesie frazy i nie obiecuje kompletu, więc jedenasta
        # aplikacja jej nie unieważni. To pole idzie w `meta description`,
        # `og:description` i na ekran — najdroższy napis tej witryny.
        "opis_mapy": "Aplikacje do nauki japońskiego, każda o jednej rzeczy: "
                     "gramatyka, kanji, odmiana, partykuły, keigo, akcent. "
                     "Jest też test poziomu, od którego można zacząć.",
        "naglowek_wyboru": "Którą aplikację wybrać",
        "naglowek_kart": "Wszystkie aplikacje",
        "w_sklepie": "App Store",
        "wkrotce": "Wkrótce w App Store",
        "wkrotce_opis": "Aplikacja czeka na recenzję Apple. Strona opisuje wersję złożoną do sklepu.",
        "przed_premiera": "przed premierą",
        "darmowa": "Aplikacja darmowa, z zakupem w środku",
        "wiecej": "Czytaj dalej",
        "naglowek_zrzutow": "Jak to wygląda",
        "naglowek_faq": "Częste pytania",
        "pytanie_wyboru": "Którą z tych aplikacji do nauki japońskiego wybrać?",
        "odpowiedz_wyboru": "Każda uczy jednej rzeczy i mierzy ją osobno:",
        "zrzut": "zrzut ekranu",
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
        "autor_link": "O autorze",
        "autor_tytul": "O autorze",
        "autor_opis": "Kto pisze te aplikacje i dlaczego jest ich tyle, a nie jedna.",
        "autor_kim": "Nazywam się Jakub Dwojak i piszę te aplikacje sam – kod, treść "
                     "i wszystko, co widać na ekranie.",
        "autor_naglowek_dlaczego": "Dlaczego osobne aplikacje, a nie jedna",
        "autor_dlaczego_1": "Bo to, czego uczą, to osobne umiejętności, "
                            "a nie zakładki jednego programu. Gramatyka, odmiana, "
                            "partykuły, liczniki, czytanie w kontekście, mowa potoczna, keigo, "
                            "akcent i onomatopeje ćwiczą się inaczej, mierzą się inaczej "
                            "i przydają się w innym momencie nauki.",
        "autor_dlaczego_2": "Aplikacja, która robi to wszystko naraz, zaczyna się od ekranu "
                            "z wyborem i każdą z tych rzeczy robi trochę gorzej. Osobne "
                            "aplikacje kosztują tyle kompletów wydań i dokumentów, ile "
                            "jest aplikacji – ale ten koszt płacę ja, nie Ty.",
        "autor_naglowek_jak": "Jak są zrobione",
        "autor_jak": "Wszystkie działają bez konta, bez reklam i bez śledzenia, a nauka "
                     "i powtórki nie potrzebują internetu. Nie jest to obietnica na tej "
                     "stronie – stoi to w polityce prywatności każdej z nich.",
        "autor_naglowek_kontakt": "Kontakt",
        "autor_kontakt": "Najszybciej mailem. Każda aplikacja ma własny adres – znajdziesz "
                         "go na jej stronie i w jej dokumentach.",
        "do_tresci": "Przejdź do treści",
        "nawigacja": "Witryna",

        # --- strony tematyczne ---------------------------------------------
        # Tytuł i jedno zdanie na temat, i nic ponadto: glosy, wyjaśnienia
        # i zdania przykładowe przychodzą z eksportów aplikacji, przejrzane
        # i z odciskiem. Jeżeli ten blok zacznie rosnąć poza tytuł i zdanie,
        # to znaczy, że strona tematyczna zaczęła mówić od siebie.
        # --- aplikacje zapowiedziane (poz. 112) ----------------------------
        # Do 13.09.2026 stał tu akapit „Czego rodzina jeszcze nie uczy" — cztery
        # dziedziny wymienione samym japońskim terminem, bez nazw i bez ikon, bo
        # aplikacje nie miały jeszcze tożsamości. Teraz ją mają, więc ta sama rzecz
        # jest kartami. **Sześć, nie cztery:** tamten akapit gubił pismo od zera
        # i kanji, a mówił 会話 tam, gdzie dziś stoi 発話.
        "dojdzie_naglowek": "Co dojdzie do rodziny",
        "dojdzie_opis": "Seria domyka się na szesnastu aplikacjach. Sześć poniżej ma już "
                        "nazwę, znak i zakres, ale nie ma jeszcze kodu – i dlatego nie mają "
                        "dat. Kiedy powstaną, staną wyżej, wśród tamtych.",
        "w_przygotowaniu": "W przygotowaniu",
        "nauka_tytul": "Nauka japońskiego – partykuły, liczniki, formy, keigo",
        "nauka_opis": "Materiał wyjęty z darmowej części aplikacji rodziny: partykuły, "
                      "liczniki, formy czasownika, mowa potoczna i keigo.",
        "nauka_link": "Nauka japońskiego",
        "nauka_spis": "Na tej stronie",
        "nauka_przyklady": "Przykłady",
        "nauka_skad": "Skąd ten materiał",
        "nauka_powiazane": "Zobacz też",
        # Zdania mostów między tematami. Każde mówi, **czym jest strona po drugiej
        # stronie linku** – bo to jest cała robota tego bloku: powiedzieć wprost,
        # która z dwóch stron o partykułach jest tą pełną.
        "powiazane_partykuly": "pełny przewodnik po sześciu partykułach i ich rolach",
        "powiazane_formy": "wszystkie czternaście form czasownika w jednym miejscu",
        "powiazane_n5_n5.g1.particles": "te same partykuły w kursie N5, po kolei "
                                        "z resztą gramatyki poziomu",
        "powiazane_n5_n5.g3.verb-forms": "formy czasownika jako punkt kursu N5",
        "powiazane_potoczny_voicing": "udźwięcznienia w mowie potocznej – ten sam "
                                      "znak 濁点 w skrótach, nie w onomatopejach",
        "powiazane_onomatopeje_l2": "pary onomatopei – 濁点 zmieniający nie skrót, "
                                    "tylko stan rzeczy",
        "nauka_skad_opis": "Wszystko powyżej pochodzi z darmowej części aplikacji {apka} "
                           "i przeszło jej przegląd treści.",
        "temat_partykuly_tytul": "Partykuły japońskie: は, が, を, に, で, へ",
        "temat_partykuly_opis": "Partykuły, które niosą zwykłe japońskie zdanie, i role, "
                                "w jakich stoją – z przykładami i tłumaczeniem.",
        "temat_n5_tytul": "Gramatyka japońska N5 – wszystkie punkty z poziomu",
        "temat_n5_opis": "Siedem grup gramatyki N5, od szkieletu zdania po ton wypowiedzi "
                         "– każdy punkt ze znaczeniem, budową i przykładami.",
        "temat_n5_sufiks": "gramatyka japońska N5",
        "temat_potoczny_sufiks": "japoński potoczny",
        "nauka_opis_grupy": "{grupa} – {sufiks}. Znaczenie, wyjaśnienie "
                             "i zdania przykładowe z tłumaczeniem.",
        "nauka_podtytul_grupy": "Znaczenie, wyjaśnienie i zdania przykładowe "
                                "z tłumaczeniem.",
        # Rodzaje skrótu w mowie potocznej. Katalog niesie je jako klucze
        # techniczne (`contraction`, `fusion`), bez brzmień dla czytelnika.
        "temat_keigo_sufiks": "keigo",
        "temat_onomatopeje_tytul": "Onomatopeje japońskie – dźwięki z mangi i anime",
        "temat_onomatopeje_opis": "Słowa, które naśladują dźwięk i stan – co znaczą "
                                  "i co robi z nimi 濁点.",
        "temat_onomatopeje_sufiks": "onomatopeje japońskie",
        # Sześć sekcji onomatopei. Cztery pierwsze dzielą ciało wg doznania,
        # dwie ostatnie dzielą pary wg tego, czy słowo umie być też dźwiękiem.
        "grupa_onomatope_l1.bol": "Ból",
        "grupa_onomatope_l1.drzenie": "Drżenie, dreszcze i zawroty",
        "grupa_onomatope_l1.zmeczenie": "Zmęczenie i sen",
        "grupa_onomatope_l1": "Ciało i samopoczucie",
        "grupa_onomatope_l1.bol_opis": "Jak po japońsku powiedzieć, że boli: "
                                       "ずきずき, きりきり, がんがん i cztery inne "
                                       "słowa na ból, każde o innym bólu.",
        "grupa_onomatope_l1.drzenie_opis": "Osiem słów o trzęsieniu się i kręceniu "
                                           "w głowie: ぶるぶる, ぞくぞく, くらくら "
                                           "– z czego bierze się drżenie w każdym.",
        "grupa_onomatope_l1.zmeczenie_opis": "へとへと, くたくた, うとうと – sześć "
                                             "japońskich słów o zmęczeniu i zasypianiu, "
                                             "ze zdaniami przykładowymi.",
        "grupa_onomatope_l1_opis": "Ciepło, głód, mdłości i swędzenie – japońskie "
                                   "słowa o tym, co czuje ciało, z przykładami "
                                   "i tłumaczeniem.",
        "grupa_onomatope_l2": "Pary dźwięczne: き–し",
        "grupa_onomatope_l2.b": "Pary dźwięczne: た–ほ",
        "grupa_onomatope_l2.dzwiek": "Pary dźwiękonaśladowcze: wiersz か",
        "grupa_onomatope_l2.dzwiek.b": "Pary dźwiękonaśladowcze: こ–と",
        "grupa_onomatope_l2_opis": "さらさら i ざらざら, きらきら i ぎらぎら – pięć par od き do し, w których 濁点 zmienia stan rzeczy, nie dźwięk.",
        "grupa_onomatope_l2.b_opis": "とろとろ i どろどろ, はらはら i ばらばら – cztery pary od た do ほ, gdzie znak dźwięczności robi rzecz gęstszą i cięższą.",
        "grupa_onomatope_l2.dzwiek_opis": "からから, かちかち, かりかり – pary z wiersza か, które są jednocześnie odgłosem i stanem; 濁点 pogrubia sam dźwięk.",
        "grupa_onomatope_l2.dzwiek.b_opis": "ころころ i ごろごろ, とんとん i どんどん – pary od こ do と, w których słychać, co puka, toczy się albo szeleści.",
        "grupa_contraction_opis": "〜ている → 〜てる, 〜なければ → 〜なきゃ – piętnaście skrótów, które powstają przez wypadnięcie głoski ze środka formy.",
        "grupa_fusion_opis": "では → じゃ, という → って, のです → んです – dziewięć miejsc, w których dwie sylaby zlewają się w jedną.",
        "grupa_voicing_opis": "〜でいる → 〜でる i dwa inne skróty po dźwięcznym 〜で – ten sam mechanizm co przy 〜ている, tylko po 濁点.",
        "grupa_layered_opis": "なければならない → なきゃ – cztery powinności ścinane dwa razy, aż z całego zdania zostaje jedno słowo.",
        "grupa_omission_opis": "ないといけない → ないと – trzy formy, w których druga połowa zdania po prostu nie pada, a znaczenie zostaje.",
        "grupa_relation_opis": "Pierwszy dzień w pracy, kelner, wykładowca, telefon w firmie – czternaście sytuacji i forma, której każda z nich wymaga.",
        "grupa_lexeme_opis": "いらっしゃる, 召し上がる, 伺う – dwadzieścia słów czczących i skromnych, każde z czasownikiem zwykłym obok i zdaniem, w którym stoi.",
        "grupa_n5.g1.particles_opis": "は, が, を, に, で, と, も, の, か – piętnaście ról partykuł, z których składa się zwykłe japońskie zdanie.",
        "grupa_n5.g2.time-place_opis": "に, から〜まで, ごろ, ぐらい, へ, あります i います – dziewięć punktów o tym, kiedy, gdzie i czy coś w ogóle jest.",
        "grupa_n5.g3.verb-forms_opis": "〜ます, 〜て, 〜ています, 〜ない, 〜た – jedenaście form czasownika N5, z różnicą między czynnością w toku a jej skutkiem.",
        "grupa_n5.g4.requests_opis": "〜てください, 〜てもいいです, 〜てはいけません – siedem sposobów na prośbę, pozwolenie i zakaz, od najgrzeczniejszego.",
        "grupa_n5.g5.adjectives_opis": "い形容詞 i な形容詞, 〜くないです, 〜より, いちばん – siedem punktów o odmianie przymiotnika i o porównywaniu.",
        "grupa_n5.g6.wishes_opis": "〜たい, 〜がほしい, 〜ませんか, 〜ましょう – sześć form, którymi mówi się, czego się chce i do czego się zaprasza.",
        "grupa_n5.g7.tone_opis": "から, あまり〜ない, ぜんぜん〜ない, ね, よ – pięć punktów o powodzie, natężeniu i o tym, co partykuła końcowa robi z tonem.",
        "grupa_relation": "Sytuacje",
        "grupa_lexeme": "Słowa czczące i skromne",
        "grupa_contraction": "Ściągnięcia",
        "grupa_fusion": "Zlania",
        "grupa_voicing": "Udźwięcznienia",
        "grupa_layered": "Skróty złożone",
        "grupa_omission": "Opuszczenia",
        "nauka_budowa": "Jak się to buduje",
        # Nazwy klas odmiany — etykiety terminologiczne, nie zdania o japońskim.
        # Brzmienia polskie przepisane z `RULE_GROUP_NAMES` w narzędziu przeglądu
        # Katsuyokei, żeby strona i aplikacja nazywały to samo tak samo.
        "klasa_godan": "czasownik godan",
        "klasa_ichidan": "czasownik ichidan",
        "klasa_suru": "czasownik złożony z する",
        "klasa_kuru": "来る",
        "klasa_iadj": "przymiotnik na い",
        "klasa_naadj": "przymiotnik na な",
        "klasa_shared": "wszystkie klasy naraz",
        "klasa_exception": "pojedyncze hasło nieregularne",
        "nauka_wstecz": "Poprzednia sekcja",
        "nauka_dalej": "Następna sekcja",
        "temat_pary_tytul": "Mylące pary w japońskim: は czy が, もう czy まだ",
        "temat_pary_opis": "Pary, które wyglądają wymiennie i nie są – przy każdym zdaniu "
                           "sytuacja i powód, dla którego druga forma nie pasuje.",
        "temat_liczniki_tytul": "Liczniki japońskie – jak liczyć ludzi, rzeczy i zwierzęta",
        "temat_liczniki_opis": "Czym liczy się ludzi, cienkie przedmioty, książki i zwierzęta "
                               "– z czytaniem, notą o wyjątkach i zdaniami przykładowymi.",
        "temat_formy_tytul": "Formy czasownika japońskiego: ます, て, た, ない",
        "temat_formy_opis": "Formy z pierwszych dwóch etapów odmiany – co każda robi "
                            "i kiedy się jej używa.",
        "temat_potoczny_tytul": "Japoński potoczny – skróty z anime i rozmowy",
        "temat_potoczny_opis": "Skróty, które słychać na co dzień, każdy obok pełnej formy, "
                               "z której powstał.",
        "temat_keigo_tytul": "Keigo – japońska grzeczność w praktyce",
        "temat_keigo_opis": "Sytuacje z pracy oraz formy czczące i skromne – co powiedzieć "
                            "i dlaczego akurat to.",
    },
    "en": {
        "html_lang": "en",
        "tytul_mapy": "Japanese in separate apps",
        # Patrz komentarz przy polskim `opis_mapy`: lista bez spójnika zamykającego.
        "opis_mapy": "Apps for learning Japanese, each about one thing: "
                     "grammar, kanji, conjugation, particles, keigo, pitch. "
                     "There is a level test to start from as well.",
        "naglowek_wyboru": "Which app do you need",
        "naglowek_kart": "All apps",
        "w_sklepie": "App Store",
        "wkrotce": "Coming to the App Store",
        "wkrotce_opis": "Waiting for Apple review. This page describes the version submitted.",
        "przed_premiera": "not yet released",
        "darmowa": "Free app with an in-app purchase",
        "wiecej": "Read on",
        "naglowek_zrzutow": "What it looks like",
        "naglowek_faq": "Common questions",
        "pytanie_wyboru": "Which of these Japanese learning apps should I use?",
        "odpowiedz_wyboru": "Each one teaches a single thing and measures it separately:",
        "zrzut": "screenshot",
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
        "autor_link": "About",
        "autor_tytul": "About the author",
        "autor_opis": "Who writes these apps, and why there are several rather than one.",
        "autor_kim": "I am Jakub Dwojak and I write these apps myself – the code, the content "
                     "and everything you see on screen.",
        "autor_naglowek_dlaczego": "Why separate apps rather than one",
        "autor_dlaczego_1": "Because what they teach is separate skills, not tabs of "
                            "one program. Grammar, conjugation, particles, counters, reading "
                            "in context, casual speech, keigo, pitch accent and mimetics are "
                            "drilled differently, measured differently, and each becomes "
                            "useful at a different point.",
        "autor_dlaczego_2": "An app that does all of it at once opens on a menu and does each "
                            "of those things slightly worse. Separate apps cost one set of "
                            "releases and documents per app – but that cost is mine, "
                            "not yours.",
        "autor_naglowek_jak": "How they are built",
        "autor_jak": "All of them work without an account, without ads and without tracking, "
                     "and studying works offline. That is not a promise made on this page – "
                     "it is written in each app's privacy policy.",
        "autor_naglowek_kontakt": "Contact",
        "autor_kontakt": "Email is fastest. Each app has its own address – you will find it "
                         "on its page and in its documents.",
        # --- strony tematyczne ---------------------------------------------
        # --- dziedziny jeszcze bez aplikacji (poz. 112) --------------------
        "dojdzie_naglowek": "What is coming to the family",
        "dojdzie_opis": "The series closes at sixteen apps. The six below already have "
                        "a name, a character and a scope, but no code yet – which is why "
                        "they carry no dates. When they exist, they will stand above, "
                        "among the others.",
        "w_przygotowaniu": "In the works",
        "nauka_tytul": "Learning Japanese – particles, counters, forms, keigo",
        "nauka_opis": "Material taken from the free part of the family's apps: particles, "
                      "counters, verb forms, casual speech and keigo.",
        "nauka_link": "Learning Japanese",
        "nauka_spis": "On this page",
        "nauka_przyklady": "Examples",
        "nauka_skad": "Where this comes from",
        "nauka_powiazane": "See also",
        "powiazane_partykuly": "the full guide to six particles and the roles they take",
        "powiazane_formy": "all fourteen verb forms in one place",
        "powiazane_n5_n5.g1.particles": "the same particles inside the N5 course, "
                                        "in order with the rest of the level",
        "powiazane_n5_n5.g3.verb-forms": "verb forms as a point of the N5 course",
        "powiazane_potoczny_voicing": "voicing in casual speech – the same 濁点, "
                                      "in contractions rather than in mimetics",
        "powiazane_onomatopeje_l2": "mimetic pairs – 濁点 changing not a contraction "
                                    "but the state of things",
        "nauka_skad_opis": "Everything above comes from the free part of the {apka} app "
                           "and has passed its content review.",
        "temat_partykuly_tytul": "Japanese particles: は, が, を, に, で, へ",
        "temat_partykuly_opis": "The particles that carry an ordinary Japanese sentence, "
                                "and the roles they stand in – with examples and translations.",
        "temat_n5_tytul": "Japanese N5 grammar – every point on the level",
        "temat_n5_opis": "Seven groups of N5 grammar, from the sentence skeleton to tone "
                         "– each point with its meaning, formation and examples.",
        "temat_n5_sufiks": "Japanese N5 grammar",
        "temat_potoczny_sufiks": "casual Japanese",
        "nauka_opis_grupy": "{grupa} – {sufiks}. Meaning, explanation and example "
                             "sentences with translations.",
        "nauka_podtytul_grupy": "Meaning, explanation and example sentences "
                                "with translations.",
        "temat_keigo_sufiks": "keigo",
        "temat_onomatopeje_tytul": "Japanese mimetics – the sounds in manga and anime",
        "temat_onomatopeje_opis": "Words that imitate sound and state – what they mean "
                                  "and what 濁点 does to them.",
        "temat_onomatopeje_sufiks": "Japanese mimetics",
        "grupa_onomatope_l1.bol": "Pain",
        "grupa_onomatope_l1.drzenie": "Shivering, trembling and dizziness",
        "grupa_onomatope_l1.zmeczenie": "Tiredness and sleep",
        "grupa_onomatope_l1": "Body and feeling",
        "grupa_onomatope_l1.bol_opis": "How to say it hurts in Japanese: ずきずき, "
                                       "きりきり, がんがん and four more words for "
                                       "pain, each for a different kind of it.",
        "grupa_onomatope_l1.drzenie_opis": "Eight words for shaking and for the room "
                                           "spinning: ぶるぶる, ぞくぞく, くらくら – "
                                           "and what makes each one tremble.",
        "grupa_onomatope_l1.zmeczenie_opis": "へとへと, くたくた, うとうと – six "
                                             "Japanese words for being worn out and "
                                             "for dozing off, with example sentences.",
        "grupa_onomatope_l1_opis": "Warmth, hunger, nausea and itching – Japanese "
                                   "words for what the body feels, with examples "
                                   "and translations.",
        "grupa_onomatope_l2": "Voicing pairs: き–し",
        "grupa_onomatope_l2.b": "Voicing pairs: た–ほ",
        "grupa_onomatope_l2.dzwiek": "Sound pairs: the か row",
        "grupa_onomatope_l2.dzwiek.b": "Sound pairs: こ–と",
        "grupa_onomatope_l2_opis": "さらさら and ざらざら, きらきら and ぎらぎら – five pairs from き to し where 濁点 changes the state of things, not the sound.",
        "grupa_onomatope_l2.b_opis": "とろとろ and どろどろ, はらはら and ばらばら – four pairs from た to ほ, where the voicing mark makes things thicker and heavier.",
        "grupa_onomatope_l2.dzwiek_opis": "からから, かちかち, かりかり – pairs from the か row that are a noise and a state at once; 濁点 thickens the sound itself.",
        "grupa_onomatope_l2.dzwiek.b_opis": "ころころ and ごろごろ, とんとん and どんどん – pairs from こ to と where you hear what knocks, rolls or rustles.",
        "grupa_contraction_opis": "〜ている → 〜てる, 〜なければ → 〜なきゃ – fifteen contractions made by dropping a sound from the middle of a form.",
        "grupa_fusion_opis": "では → じゃ, という → って, のです → んです – nine places where two syllables melt into one.",
        "grupa_voicing_opis": "〜でいる → 〜でる and two more contractions after a voiced 〜で – the same mechanism as 〜ている, only past the 濁点.",
        "grupa_layered_opis": "なければならない → なきゃ – four obligations cut twice over, until a whole clause is one word.",
        "grupa_omission_opis": "ないといけない → ないと – three forms where the second half of the sentence is simply never said, and the meaning stays.",
        "grupa_relation_opis": "First day at work, a waiter, a professor, the office phone – fourteen situations and the form each of them asks for.",
        "grupa_lexeme_opis": "いらっしゃる, 召し上がる, 伺う – twenty honorific and humble words, each beside its plain verb and inside a sentence.",
        "grupa_n5.g1.particles_opis": "は, が, を, に, で, と, も, の, か – fifteen particle roles that an ordinary Japanese sentence is built from.",
        "grupa_n5.g2.time-place_opis": "に, から〜まで, ごろ, ぐらい, へ, あります and います – nine points about when, where, and whether something is there at all.",
        "grupa_n5.g3.verb-forms_opis": "〜ます, 〜て, 〜ています, 〜ない, 〜た – eleven N5 verb forms, with the difference between an action in progress and its result.",
        "grupa_n5.g4.requests_opis": "〜てください, 〜てもいいです, 〜てはいけません – seven ways to ask, to permit and to forbid, from the most polite down.",
        "grupa_n5.g5.adjectives_opis": "い and な adjectives, 〜くないです, 〜より, いちばん – seven points on adjective inflection and on comparing things.",
        "grupa_n5.g6.wishes_opis": "〜たい, 〜がほしい, 〜ませんか, 〜ましょう – six forms for saying what you want and for inviting someone along.",
        "grupa_n5.g7.tone_opis": "から, あまり〜ない, ぜんぜん〜ない, ね, よ – five points on reason, degree, and what a final particle does to the tone.",
        "grupa_relation": "Situations",
        "grupa_lexeme": "Honorific and humble words",
        "grupa_contraction": "Contractions",
        "grupa_fusion": "Fusions",
        "grupa_voicing": "Voicing",
        "grupa_layered": "Layered contractions",
        "grupa_omission": "Omissions",
        "nauka_budowa": "How it is formed",
        "klasa_godan": "godan verb",
        "klasa_ichidan": "ichidan verb",
        "klasa_suru": "する compound verb",
        "klasa_kuru": "来る",
        "klasa_iadj": "い-adjective",
        "klasa_naadj": "な-adjective",
        "klasa_shared": "every class alike",
        "klasa_exception": "a single irregular word",
        "nauka_wstecz": "Previous section",
        "nauka_dalej": "Next section",
        "temat_pary_tytul": "Confusing pairs in Japanese: は or が, もう or まだ",
        "temat_pary_opis": "Pairs that look interchangeable and are not – each sentence "
                           "comes with the situation and the reason the other form fails.",
        "temat_liczniki_tytul": "Japanese counters – how to count people, things and animals",
        "temat_liczniki_opis": "What you use to count people, thin objects, books and animals "
                               "– with readings, notes on the exceptions and example sentences.",
        "temat_formy_tytul": "Japanese verb forms: masu, te, ta, nai",
        "temat_formy_opis": "The forms from the first two stages of conjugation – what each "
                            "one does and when it is used.",
        "temat_potoczny_tytul": "Casual Japanese – the contractions in anime and conversation",
        "temat_potoczny_opis": "The contractions you hear every day, each next to the full "
                               "form it came from.",
        "temat_keigo_tytul": "Keigo – Japanese politeness in practice",
        "temat_keigo_opis": "Situations from working life and the honorific and humble forms "
                            "– what to say and why that one.",
        "do_tresci": "Skip to content",
        "nawigacja": "Site",
    },
}
