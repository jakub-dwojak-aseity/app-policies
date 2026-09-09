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
        "tytul_mapy": "Japoński w dziesięciu aplikacjach",
        "opis_mapy": "Dziesięć aplikacji do nauki japońskiego, każda o jednej rzeczy: "
                     "gramatyka, czytanie, odmiana, partykuły, liczniki, mowa potoczna, "
                     "keigo, akcent i onomatopeje.",
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
        "autor_opis": "Kto pisze te aplikacje i dlaczego jest ich dziesięć, a nie jedna.",
        "autor_kim": "Nazywam się Jakub Dwojak i piszę te aplikacje sam – kod, treść "
                     "i wszystko, co widać na ekranie.",
        "autor_naglowek_dlaczego": "Dlaczego dziesięć aplikacji, a nie jedna",
        "autor_dlaczego_1": "Bo to, czego uczą, to dziesięć osobnych umiejętności, "
                            "a nie dziesięć zakładek jednego programu. Gramatyka, odmiana, "
                            "partykuły, liczniki, czytanie w kontekście, mowa potoczna, keigo, "
                            "akcent i onomatopeje ćwiczą się inaczej, mierzą się inaczej "
                            "i przydają się w innym momencie nauki.",
        "autor_dlaczego_2": "Aplikacja, która robi to wszystko naraz, zaczyna się od ekranu "
                            "z wyborem i każdą z tych rzeczy robi trochę gorzej. Osobne "
                            "aplikacje kosztują dziesięć razy więcej wydań i dziesięć "
                            "kompletów dokumentów – ale ten koszt płacę ja, nie Ty.",
        "autor_naglowek_jak": "Jak są zrobione",
        "autor_jak": "Wszystkie działają bez konta, bez reklam i bez śledzenia, a nauka "
                     "i powtórki nie potrzebują internetu. Nie jest to obietnica na tej "
                     "stronie – stoi to w polityce prywatności każdej z nich.",
        "autor_naglowek_kontakt": "Kontakt",
        "autor_kontakt": "Najszybciej mailem. Każda aplikacja ma własny adres – znajdziesz "
                         "go na jej stronie i w jej dokumentach.",
        "do_tresci": "Przejdź do treści",
        "nawigacja": "Witryna",
    },
    "en": {
        "html_lang": "en",
        "tytul_mapy": "Japanese in ten apps",
        "opis_mapy": "Ten apps for learning Japanese, each about one thing: grammar, "
                     "reading, conjugation, particles, counters, casual speech, "
                     "keigo, pitch accent and mimetics.",
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
        "autor_opis": "Who writes these apps, and why there are ten of them rather than one.",
        "autor_kim": "I am Jakub Dwojak and I write these apps myself – the code, the content "
                     "and everything you see on screen.",
        "autor_naglowek_dlaczego": "Why ten apps rather than one",
        "autor_dlaczego_1": "Because what they teach is ten separate skills, not ten tabs of "
                            "one program. Grammar, conjugation, particles, counters, reading "
                            "in context, casual speech, keigo, pitch accent and mimetics are "
                            "drilled differently, measured differently, and each becomes "
                            "useful at a different point.",
        "autor_dlaczego_2": "An app that does all of it at once opens on a menu and does each "
                            "of those things slightly worse. Separate apps cost ten times the "
                            "releases and ten sets of documents – but that cost is mine, "
                            "not yours.",
        "autor_naglowek_jak": "How they are built",
        "autor_jak": "All of them work without an account, without ads and without tracking, "
                     "and studying works offline. That is not a promise made on this page – "
                     "it is written in each app's privacy policy.",
        "autor_naglowek_kontakt": "Contact",
        "autor_kontakt": "Email is fastest. Each app has its own address – you will find it "
                         "on its page and in its documents.",
        "do_tresci": "Skip to content",
        "nawigacja": "Site",
    },
}
