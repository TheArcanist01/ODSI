# Dowody - Laboratorium 8 (RSA i podpis cyfrowy)

Python 3.10.12, `cryptography` 50.0.2. Wszystkie pliki czytane binarnie.
Nie zapisano haseł, kluczy prywatnych ani słowa kontrolnego.

## Zadanie 1 - RSA na małych liczbach

Polecenie: `python zad1.py`

```
Modular exponentiation tests:
  4^13 mod 497 = 445 (expected 445)
  65^17 mod 3233 = 2790 (expected 2790)
  2790^2753 mod 3233 = 65 (expected 65)
  12345^0 mod 497 = 1 (expected 1)
  0^0 mod 2 = 1 (expected 1)

n = 1466056398307 (41 bits), e = 65537, blocks: 30
p = 1048601, q = 1398107
p * q == n? True
Factorization time: 0.096 s

phi(n) = 1466053951600
d = 1396416556673
(e * d) mod phi = 1

Decrypted text: 'Klucz RSA o długości 41 bitów rozkładasz na czynniki w ułamku sekundy. Bezpieczne RSA ma co najmniej 2048 bitów.  '
```

Testy potęgowania (asercje w `main()` w `zad1.py`):

| Wejście | Oczekiwane | Wynik |
| --- | --- | --- |
| `4^13 mod 497` | 445 | 445 |
| `12345^0 mod 497`, `0^0 mod 2` | 1 | 1 |
| `65^17 mod 3233` | 2790 | 2790 |
| `2790^2753 mod 3233` | 65 | 65 |
| 
- Faktoryzacja: dzielenie próbne 2, potem nieparzyste do `isqrt(n)` ≈ 1 210 808; p = 1 048 601 znalezione po ~524 tys. dzieleniach.
- Bloki: każdy odszyfrowany blok → dokładnie 4 B big-endian, sklejenie 120 B, dopiero potem UTF-8 (znaki `ł`, `ó` przechodzą przez granice bloków). Ostatni blok dopełniony dwiema spacjami.

## Zadanie 2 - Podpisy RSA-PSS

Polecenie: `python zad2.py`. Parametry: `PSS(mgf=MGF1(SHA256()), salt_length=32)`, `SHA256()`. Funkcja `verify` zwraca `True`/`False` (wyjątki `InvalidSignature` i `ValueError` przechwytywane).

```
Documents:
  faktura.txt: ERROR
  protokol.txt: OK
  regulamin.txt: ERROR
  umowa.txt: OK

Own key: RSA 3072 bits, signature: 384 B
podpis.txt: b'Laboratorium 8: TheArcanist01'
  Verification before change: OK
podpis_zmieniony.txt: b'Maboratorium 8: TheArcanist01'
  Verification after change: ERROR
```

Kontrola, że `ERROR` nie wynika z formatu: dokumenty mają końce wierszy LF; `faktura.txt` i
`regulamin.txt` nie weryfikują się ani z bajtami oryginalnymi, ani po konwersji LF↔CRLF, ani
z `salt_length=PSS.AUTO`, ani z podpisem innego dokumentu - treść lub podpis zostały zmienione.

- `podpis.txt` (29 B, bez znaku nowego wiersza): `Laboratorium 8: TheArcanist01`,
  SHA-256 `3fa7f68e43768398687d9fcc51203e3ef9817a1cfcbdfeb2e480b16a4aa6ad88`.
- `moj_klucz_publiczny.pem`: RSA 3072 b, SHA-256(SPKI DER) `d482d75847b84a6bffc7196adca895a6...`.
- Zmiana bajtu: bajt 0 XOR 0x01 (`L` → `M`), plik `podpis_zmieniony.txt`.
- Weryfikacja niezależna (OpenSSL 3.0.2, wynik `Verified OK`): `openssl dgst -sha256 -sigopt rsa_padding_mode:pss -sigopt rsa_pss_saltlen:32 -sigopt rsa_mgf1_md:sha256 -verify moj_klucz_publiczny.pem -signature podpis.txt.sig podpis.txt`

## Zadanie 3 - Szyfrowanie hybrydowe

Polecenie: `LAB8_HASLO=... python zad3.py` (wiersz ze słowem kontrolnym pominięty w logu).

```
paczka.bin: 452 B, L = 256
Decrypted text:
Gratulacje, paczka odszyfrowana poprawnie.
Klucz AES tej wiadomości był losowy i zabezpieczony tylko algorytmem RSA-OAEP.

odpowiedz.bin: 437 B, L = 384

Modified files:
  changed ciphertext byte: REJECTED (invalid GCM tag)
  changed tag byte: REJECTED (invalid GCM tag)
  truncated (no tag): REJECTED (invalid GCM tag)
  truncated < L + 30 B: REJECTED (file truncated: 278 B < 286 B)
  wrong L in header: REJECTED (L = 255 differs from RSA modulus length 256 B)
  1 B file: REJECTED (file too short for header (1 B))
```

Rozkład `paczka.bin` (452 B): 2 B L=256 | 256 B klucz RSA-OAEP | 12 B nonce | 166 B kryptogram + 16 B tag.

Rozkład `odpowiedz.bin` (437 B): 2 B L=384 | 384 B klucz RSA-OAEP (klucz prowadzącego 3072 b) |
12 B nonce | 23 B kryptogram + 16 B tag. Treść: `<słowo kontrolne>\nTheArcanist01` (UTF-8).
Klucz AES: `AESGCM.generate_key(256)`, nonce: `os.urandom(12)` (CSPRNG systemu).
SHA-256 `odpowiedz.bin`: `5caff780c715728c0219e05fe822e1b6d0f3d6ff1d3d7ceb172f44497cc7b338`.

Kontrola własnej funkcji szyfrującej: szyfrowanie kluczem publicznym z pakietu i odszyfrowanie
`klucz_prywatny.pem` daje identyczny tekst (round-trip OK).

Krok 3: `paczka_zmieniona.bin` - bajt na pozycji 2+L+12 = 270 (pierwszy bajt kryptogramu) XOR 0x01.
`AESGCM.decrypt` zgłasza `InvalidTag` (w programie: `ValueError("invalid GCM tag")`) i nie zwraca żadnego tekstu jawnego.

## Część dodatkowa

Polecenie: `python dodatkowe.py`

```
Modular inverse:
  17 mod 3120: own = 2753, library = 2753, equal? True
  65537 mod 1466053951600: own = 1396416556673, library = 1396416556673, equal? True
  3 mod 10: own = 7, library = 7, equal? True
  6 mod 9: own = None, library = None, equal? True
  2 mod 4: own = None, library = None, equal? True

OAEP limit from formula: 190 B
  190 B: OK (256 B ciphertext)
  191 B: REJECTED (Encryption failed)

Textbook RSA: 1280454190433 / 1280454190433, equal? True
RSA-OAEP: 8e7543935f35de80... / 06aed1d47ad509e9..., equal? False
```

Podręcznikowe RSA jest deterministyczne (ta sama wiadomość → ten sam kryptogram, można
zgadywać i porównywać tekst jawny); OAEP dokleja losowe ziarno, więc kryptogramy się różnią.
