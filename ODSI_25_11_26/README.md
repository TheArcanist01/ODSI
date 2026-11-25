## Wymagane biblioteki

- `cryptography` (testowane na 50.0.2): `pip install cryptography`
- Python ≥ 3.8 (`math.isqrt`, `pow(e, -1, phi)`)

Środowisko wirtualne (Windows PowerShell): uruchom `.\utworz_venv.ps1` - tworzy `.venv`
w tym katalogu i instaluje pakiety z `requirements.txt`. Jeśli uruchamianie skryptów jest zablokowane:
`powershell -ExecutionPolicy Bypass -File .\utworz_venv.ps1`. Ręcznie:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

`zad1.py` korzysta wyłącznie z biblioteki standardowej: własne potęgowanie modularne
(`mod_pow`) i faktoryzacja przez dzielenie próbne (`factorize`).

## Wywołanie plików

Wywołanie po kolei plików zadań (w katalogu `ODSI_25_11_26`, pliki pakietu w `pliki-dla-studentow/`):

```
python zad1.py
python zad2.py
LAB8_HASLO=... python zad3.py
python dodatkowe.py
```

W Windows PowerShell: `$env:LAB8_HASLO="..."; python zad3.py`. Hasło do `klucz_prywatny.pem`
podaje polecenie laboratorium; nie jest zapisane w kodzie.

## Pliki wynikowe

- `podpis.txt`, `podpis.txt.sig`, `moj_klucz_publiczny.pem` - zadanie 2 (RSA-PSS, SHA-256, MGF1-SHA-256, sól 32 B, RSA 3072 b)
- `odpowiedz.bin` - zadanie 3, format: `[2 B L big-endian][L B klucz AES-256 zaszyfrowany RSA-OAEP-SHA-256][12 B nonce][kryptogram AES-GCM || tag 16 B]`, bez AAD
- `podpis_zmieniony.txt`, `paczka_zmieniona.bin` - kopie z jednym zmienionym bajtem

Klucze prywatne (`moj_klucz_prywatny.pem`, `pliki-dla-studentow/klucz_prywatny.pem`) są w `.gitignore`.
`zad2.py` przy istniejącym `moj_klucz_prywatny.pem` używa tej samej pary; podpis PSS jest losowy,
więc `podpis.txt.sig` zmienia się przy każdym uruchomieniu, a `zad3.py` za każdym razem tworzy nowy `odpowiedz.bin`.

Pełne wyniki: `dowody.md`.
