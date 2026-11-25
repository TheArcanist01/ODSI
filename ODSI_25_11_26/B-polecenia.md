# Laboratorium 8 - RSA i podpis cyfrowy

**3 zadania po 1 pkt. 90 minut (2 × 45).** Plan: 10 minut wprowadzenia, 20 + 20 + 25 minut na zadania, 15 minut na raport i oddanie. Napisz cały kod samodzielnie w **dowolnym języku**. W zadaniu 1 samodzielnie implementujesz faktoryzację i szybkie potęgowanie; odwrotność modulo możesz policzyć biblioteką. W zadaniach 2 i 3 użyj biblioteki kryptograficznej do RSA-PSS, RSA-OAEP, AES-GCM i losowania bajtów; nie implementuj tych algorytmów od podstaw. Wystarczy prosty program bez menu.

Dozwolone: ISOD, dokumentacja, własne notatki i własny wcześniej napisany kod. Podczas zajęć wyłącz czaty i podpowiedzi LLM. Przy odbiorze wyjaśniasz działanie programu.

Pliki z katalogu `pliki-dla-studentow` czytaj **binarnie** i nie zmieniaj końców wierszy: podpisy dotyczą dokładnych bajtów. Wszystkie liczby zapisane w bajtach mają kolejność big-endian.

## Pomoc i zapis wyników

Pomoc podczas zajęć: `pliki-dla-studentow/PRZEWODNIK.md`. Raport ma jedną stronę: zwięzłe wyniki i wnioski. Długie polecenia, ładunki i logi możesz zapisać w `dowody.md` w repozytorium, wskazując sekcje w raporcie. Skracaj tokeny; nie zapisuj haseł ani kluczy prywatnych. Część dodatkowa nie jest wymagana na pełne 3 pkt.

## Zadanie 1 - RSA na małych liczbach (20 min, 1 pkt)

Plik `male_rsa.txt` zawiera klucz publiczny `n`, `e` oraz kryptogram `c`: liczby oddzielone przecinkami. Tekst jawny w UTF-8 podzielono na bloki po 4 B, a ostatni blok uzupełniono spacjami. Blok to liczba big-endian m, a `c = m^e mod n`.

1. Napisz własne szybkie potęgowanie modularne metodą kwadratów i mnożeń. Sprawdź m.in. `4^13 mod 497 = 445` i `a^0 mod n = 1` dla n > 1. Do odwrotności modulo możesz użyć biblioteki (np. Python `pow(e, -1, phi)`, Java `BigInteger.modInverse`).
2. Rozłóż `n` na czynniki pierwsze `p · q` przez dzielenie próbne. Zmierz czas.
3. Oblicz φ(n) i klucz prywatny `d` jako odwrotność e modulo φ(n); sprawdź `(e*d) mod φ(n) = 1`. Odszyfruj wszystkie bloki własnym potęgowaniem, zamień każdy na 4 bajty i zdekoduj tekst UTF-8.

**W raporcie:** p, q, d, czas faktoryzacji, odszyfrowany tekst oraz jedno zdanie: dlaczego ta sama metoda nie złamie klucza o długości 2048 bitów.

## Zadanie 2 - Podpisy RSA-PSS (20 min, 1 pkt)

Każdy plik `dokumenty/*.txt` ma podpis w pliku o tej samej nazwie z dodanym `.sig` (surowe 384 B). Parametry: **RSA-PSS, SHA-256, MGF1 z SHA-256, sól 32 B**. Klucz publiczny podpisującego: `klucz_podpisu.pem` (PEM, SubjectPublicKeyInfo).

1. Dla każdego z czterech dokumentów zweryfikuj podpis kluczem z `klucz_podpisu.pem` i wypisz `OK` albo `BŁĄD`. Nieudana weryfikacja nie może przerwać programu.
2. Wygeneruj własną parę kluczy RSA 3072 bity. Utwórz plik `podpis.txt` o treści `Laboratorium 8: ` i Twój login GitHub. Podpisz go tymi samymi parametrami. W repozytorium umieść `podpis.txt`, `podpis.txt.sig` i klucz publiczny `moj_klucz_publiczny.pem`. Klucza prywatnego nie publikuj.
3. Zmień jeden bajt w kopii `podpis.txt` i sprawdź, że weryfikacja kopii się nie udaje.

**W raporcie:** status czterech dokumentów, wynik weryfikacji własnego podpisu przed zmianą i po niej oraz jedno zdanie: czego nie potwierdza poprawny podpis, jeśli klucz publiczny pochodzi z niezaufanego źródła.

## Zadanie 3 - Szyfrowanie hybrydowe (25 min, 1 pkt)

Format pliku, wszystkie pola po kolei, bez separatorów:

- 2 B: długość L zaszyfrowanego klucza (big-endian);
- L B: losowy klucz AES-256 (32 B) zaszyfrowany **RSA-OAEP z SHA-256 i MGF1 z SHA-256**, bez etykiety;
- 12 B: nonce;
- pozostałe bajty: kryptogram **AES-256-GCM** z tagiem 16 B dołączonym na końcu, bez danych dodatkowych (AAD).

1. Przed odszyfrowaniem sprawdź format: co najmniej 2 B nagłówka, L równe długości modułu RSA w bajtach i co najmniej L + 30 B całego pliku (2 + L + 12 + 16). Odrzuć plik ucięty albo z błędnym tagiem; nie udostępniaj tekstu przed weryfikacją tagu. Wczytaj `klucz_prywatny.pem` (PKCS#8 zaszyfrowany hasłem `Lab8-cwiczenie`). Odszyfruj `paczka.bin` i wypisz tekst. Tekst zawiera słowo kontrolne.
2. Utwórz `odpowiedz.bin` w tym samym formacie dla klucza publicznego prowadzącego z pliku `klucz_prowadzacego.pem`. Treść w UTF-8: słowo kontrolne w pierwszym wierszu i Twój login GitHub w drugim. Klucz AES i nonce wylosuj bezpiecznym generatorem. Umieść `odpowiedz.bin` w repozytorium.
3. Zmień jeden bajt kryptogramu w kopii `paczka.bin` i sprawdź, że odszyfrowanie zostaje odrzucone.

**W raporcie:** wartość L dla `paczka.bin` i dla `odpowiedz.bin`, pierwszy wiersz odszyfrowanego tekstu, wynik kroku 3 oraz jedno zdanie: dlaczego plik szyfrujemy AES, a RSA tylko klucz. Nie przepisuj słowa kontrolnego; prowadzący odczyta je z `odpowiedz.bin`.

## Dodatkowo - dla chętnych, poza zakresem 90 minut

Te ćwiczenia nie są wymagane do uzyskania pełnych 3 pkt ani do raportu.

- Zaimplementuj rozszerzony algorytm Euklidesa i odwrotność modulo. Porównaj wyniki z biblioteką, także gdy odwrotność nie istnieje.
- Ustal doświadczalnie limit długości wiadomości RSA-OAEP z SHA-256 dla klucza 2048 bitów: zaszyfruj 190 B i 191 B. Porównaj z wzorem k − 2·hLen − 2.
- Zaszyfruj dwa razy ten sam blok podręcznikowym RSA z zadania 1 i dwa razy tę samą wiadomość RSA-OAEP. Porównaj kryptogramy i wyjaśnij różnicę.

## Oddanie - jeden plik raportu do końca zajęć

Oddaj **jeden plik w formacie tekstowym**, np. **TXT, MD lub PDF z tekstem**. **Nazwa pliku jest dowolna. Raport należy oddać do końca zajęć** w miejscu wskazanym przez prowadzącego. Raport do jednej strony zawiera imię i nazwisko, numer indeksu, wybrany język, link do repozytorium GitHub, identyfikator commitu oraz wyniki i krótkie odpowiedzi z trzech zadań. Uzupełniaj go podczas pracy; oddaj również ukończone części.

W repozytorium umieść cały samodzielnie napisany kod, README z wymaganymi bibliotekami i komendą uruchomienia, `podpis.txt`, `podpis.txt.sig`, `moj_klucz_publiczny.pem` oraz `odpowiedz.bin`. **Nie umieszczaj w repozytorium żadnego klucza prywatnego**, także tego z pakietu. Repozytorium musi być dostępne dla prowadzącego. Nie oddawaj ZIP-a, osobnych załączników z kodem ani samych zrzutów ekranu.

## Punktacja

Za każde zadanie: **0,50 pkt** za działający, samodzielnie napisany kod w repozytorium, **0,25 pkt** za wymagane wyniki w raporcie i **0,25 pkt** za poprawne wyjaśnienie. W zadaniach 2 i 3 część za kod obejmuje poprawny podpis i poprawny plik `odpowiedz.bin`. Łącznie **3 pkt**. Wybór języka nie wpływa na ocenę.
