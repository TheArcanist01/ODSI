# Laboratorium 4

*Szymon Opryński nr indeksu 325556*

- GitHub: https://github.com/TheArcanist01/ODSI/tree/main/ODSI_28_10_26

- Istotny commit: Lab04

- Wybrany język: Python

## Zadanie 1

Wynik wywołania kodu:

```
Checksums:
  dokumenty/budzet.csv: BŁĄD
  dokumenty/dane.bin: OK
  dokumenty/harmonogram.txt: BRAK
  dokumenty/kontakt.txt: OK
  dokumenty/regulamin.txt: OK

SHA-256('Ala ma kota.'): 9b9ae722342758f4bb6a5dd94470ddfab3c95cda15186231f53bb4666e657605
SHA-256('Ola ma kota.'): f7f49ccc3e7308f936f9cb71a792c3526663e9ddee89dc3e38fb83db4f308535
Different bits: 131 / 256

dane.bin whole == chunks of 4096 B? True
```

Statusy zgadzają się z wynikiem `sha256sum -c SHA256SUMS.txt`. Zmiana jednej litery zmieniła 131 z 256 bitów skrótu, czyli około połowę (efekt lawinowy). Suma kontrolna zapisana obok pliku nie chroni przed celową podmianą, ponieważ atakujący, który podmienia plik, może równie łatwo policzyć i podmienić jego sumę - zamiast niej trzeba użyć HMAC z tajnym kluczem albo podpisu cyfrowego.

## Zadanie 2

Wynik wywołania kodu:

```
Verification tests:
  weryfikuj(anna, Kasztan-2026): True
  weryfikuj(anna, kasztan-2026): False
  weryfikuj(piotr, Żółw na łące): True
  weryfikuj(kasia, Kasztan-2026): False

New accounts with the same password:
  Salt 1 == Salt 2: False
  Digest 1 == Digest 2: False
  weryfikuj(test1): True
  weryfikuj(test2): True

Logins with < 600000 iterations: marek, zofia
PBKDF2 1 iteration: 2.04 us, 26^6 passwords: 10.5 min
PBKDF2 600000 iterations: 0.107 s, 26^6 passwords: 381 days
```

Wszystkie cztery testy dały oczekiwany wynik; nieznany login kasia zwraca fałsz. Konta test1 i test2 mają to samo hasło, ale różne sole, a więc i różne skróty - oba konta weryfikują się poprawnie. Sól sprawia, że te same hasła dają różne skróty, więc atakujący nie może użyć gotowych tablic ani łamać wielu kont jednocześnie; liczba iteracji spowalnia każdą próbę odgadnięcia hasła, przez co atak siłowy staje się bardzo kosztowny.

## Zadanie 3

Wynik wywołania kodu:

```
Found pair: v_original = 7282, v_changed = 1761, h24 = aac6b9
h24 of unchanged original: 9a8fd6
Changed variants matching unchanged original: 0 / 8192

All colliding pairs: 3
Expected: 4.0
```

Znaleziona para to wariant 7282 oryginału i wariant 1761 zmienionego dokumentu o wspólnym h24 = aac6b9. Żaden z 8192 wariantów zmienionego dokumentu nie ma h24 równego niezmienionemu oryginałowi. Znalezienie dowolnej pary jest znacznie łatwiejsze, ponieważ każdy wariant zmienionego dokumentu porównujemy ze wszystkimi 8192 wariantami oryginału (około 67 mln par, czyli około 2^(n/2) prób - paradoks urodzinowy), a przy ustalonym skrócie każdy wariant ma tylko jedną szansę na 2^24 (około 2^n prób).
