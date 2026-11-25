# Przewodnik do laboratorium 8

## Co masz umieć po zajęciach

Odzyskać mały klucz przez faktoryzację, wyjaśnić rolę zaufanego klucza publicznego przy podpisie i odtworzyć format szyfrowania hybrydowego z kontrolą integralności.

## Kontrola na początku zajęć

Wczytaj zaszyfrowany PKCS#8 zgodnie z A. Sprawdź API PSS, OAEP i GCM swojej biblioteki. Przygotuj funkcje binarnego odczytu/zapisu oraz zamiany liczby na ustaloną liczbę bajtów. W Java/C#/C++ użyj typu dużych liczb: iloczyny pośrednie w potęgowaniu mogą przekroczyć 64 bity, mimo że n ma 41 bitów.

## Wskazówki do RSA

- Potęgowanie: ustaw wynik na 1, zredukuj podstawę modulo n. Dopóki wykładnik jest dodatni: przy nieparzystym wykładniku pomnóż wynik przez podstawę modulo n; podnieś podstawę do kwadratu modulo n; podziel wykładnik całkowicie przez 2.
- Faktoryzacja: zacznij od 2, potem testuj nieparzyste dzielniki; wystarczy dojść do pierwiastka n. Drugi czynnik otrzymasz przez dzielenie całkowite. Sprawdź p*q = n.
- Po obliczeniu odwrotności sprawdź `(e*d) mod phi = 1`. Własny rozszerzony Euklides jest dodatkowy.
- Każdy odszyfrowany blok zamień na dokładnie 4 B, także z początkowymi zerami. Najpierw połącz bajty, dopiero potem dekoduj UTF-8: znak może przebiegać przez granicę bloków.

## Wskazówki do bibliotek

- W PSS ustaw osobno SHA-256, MGF1-SHA256 i sól 32 B. Nie włączaj trybu „prehashed”, jeśli przekazujesz cały dokument. Weryfikacja może zwracać bool lub rzucać wyjątek; sprawdź dokumentację.
- Nie poprawiaj plików wejściowych edytorem. Nawet zmiana LF na CRLF zmienia podpisywane bajty.
- Paczka: offset zaszyfrowanego klucza = 2; nonce = 2+L; kryptogram z tagiem = 2+L+12. GCM nie wymaga PKCS#7. Jedne biblioteki zwracają tag osobno, inne doklejają go do kryptogramu.
- Przy uszkodzonym tagu nie zwracaj tekstu jawnego. Do szyfrowania odpowiedzi służy klucz publiczny prowadzącego, do odszyfrowania paczki klucz prywatny z pakietu.

## Punkty kontrolne

- Zadanie 1: test potęgowania przechodzi, e*d daje 1 modulo phi, cały tekst poprawnie dekoduje się jako UTF-8.
- Zadanie 2: program obsługuje wszystkie dokumenty mimo błędnego podpisu; własny podpis działa i przestaje działać po zmianie bajtu.
- Zadanie 3: odrzucasz zmieniony kryptogram, a odpowiedź ma udokumentowaną strukturę. Nie porównuj losowych podpisów lub kryptogramów z oczekiwanymi bajtami.

## Krótki raport i dowody

Na bieżąco zapisuj: wejście, oczekiwany wynik, wynik przed, wynik po i jednozdaniowy wniosek. Na pierwszej stronie podaj dane autora, repozytorium i commit, następnie trzy zwięzłe sekcje zadań. Pełne logi, ładunki i polecenia mogą być w `dowody.md` w repozytorium. Nie kopiuj tokenów ani kluczy prywatnych. Oddajesz jeden plik raportu do końca zajęć; części dodatkowe nie wpływają na pełną punktację.

Nie czekaj do końca z diagnozą problemu. Po 5 minutach bez postępu wróć do punktu kontrolnego i pokaż prowadzącemu ostatni działający krok, wejście oraz komunikat błędu.
