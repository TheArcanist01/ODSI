# Laboratorium 5 - dowody

Szymon Opryński, 325556. Pomiary wykonane skryptami `zad1.py`, `zad2.py`, `zad3.py` (katalog `pliki-dla-studentow`), które dla każdego etapu zapisują `konfiguracja/dostep.conf`, wykonują `docker compose exec web httpd -t` (wymagane `Syntax OK`), `docker compose restart web` i pełne żądania GET. Hasło ćwiczeniowe i baza `auth/uzytkownicy` nie są tu zapisane.

## Środowisko

```
docker compose up -d --build web
```

Obraz `httpd:2.4-alpine` z Python 3, serwer pod `http://127.0.0.1:8080`, użytkownik serwera `daemon` (`User daemon`, `Group daemon` w `httpd.conf`).

## Zadanie 1 - dostęp do katalogów

Reguły (etap 1 `dostep.conf`):

```
<Directory "/usr/local/apache2/htdocs/materialy">
    Options -Indexes
</Directory>

<Directory "/usr/local/apache2/htdocs/wewnetrzne">
    Require all denied
</Directory>
```

| Wejście (GET) | Oczekiwany wynik | Przed (pusty `dostep.conf`) | Po |
|---|---|---|---|
| `curl.exe -i http://127.0.0.1:8080/materialy/` | brak listy | 200, lista plików („Index of”) | 403 |
| `curl.exe -i http://127.0.0.1:8080/materialy/notatka.txt` | plik dostępny | 200 | 200 |
| `curl.exe -i http://127.0.0.1:8080/wewnetrzne/` | brak dostępu | 200, lista plików („Index of”) | 403 |
| `curl.exe -i http://127.0.0.1:8080/wewnetrzne/plan.txt` | brak dostępu | 200 | 403 |

Log (`docker compose logs --tail 30 web`):

```
web-1  | [Wed Nov 04 11:44:14.719065 2026] [authz_core:error] [pid 12:tid 58] [client 172.18.0.1:58218] AH01630: client denied by server configuration: /usr/local/apache2/htdocs/wewnetrzne/plan.txt
```

Wniosek: `-Indexes` usuwa tylko automatyczną listę, `Require all denied` blokuje każdy zasób katalogu; `AH01630` potwierdza odmowę przez regułę autoryzacji.

## Zadanie 2 - HTTP Basic

Utworzenie bazy (hasło podane interaktywnie, skrót bcrypt):

```
docker compose run --rm --no-deps narzedzia -cB /auth/uzytkownicy student
New password:
Re-type new password:
Adding password for user student
```

Reguła (etap 2 - dopisana do etapu 1):

```
<Directory "/usr/local/apache2/htdocs/panel">
    AuthType Basic
    AuthName "Laboratorium 5"
    AuthBasicProvider file
    AuthUserFile "/auth/uzytkownicy"
    Require valid-user
</Directory>
```

| Wejście (GET) | Oczekiwany wynik | Wynik |
|---|---|---|
| `curl.exe -i http://127.0.0.1:8080/panel/raport.txt` | 401 + `WWW-Authenticate` | 401, `WWW-Authenticate: Basic realm="Laboratorium 5"` |
| `curl.exe -i -u student:<błędne> http://127.0.0.1:8080/panel/raport.txt` | 401 | 401 |
| `curl.exe -i -u student http://127.0.0.1:8080/panel/raport.txt` | 200 | 200, `Raport cwiczeniowy: dostep po poprawnym uwierzytelnieniu.` |
| `curl.exe -i http://127.0.0.1:8080/` | 200 bez logowania | 200 |

Wniosek: dostęp do `panel` wymaga poprawnych danych z bazy, reszta serwisu pozostaje publiczna; dane Basic są tylko kodowane Base64, więc przez HTTP można je podsłuchać.

## Zadanie 3 - uprawnienia CGI

Program `cgi-bin/uprawnienia.cgi` (Python 3, LF) wypisuje `os.geteuid()`, `os.getegid()` i próbuje odczytać `/lab-data/ogolny.txt` oraz `/lab-data/poufny.txt`, przechwytując `OSError`.

Prawa plików:

```
docker compose exec web ls -ln /lab-data/
total 8
-rw-r-----    1 0        2               48 Nov  4 11:11 ogolny.txt
-rw-------    1 0        2               61 Nov  4 11:11 poufny.txt

docker compose exec web id daemon
uid=2(daemon) gid=2(daemon) groups=2(daemon),1(bin),2(daemon),4(adm)
```

Przed Basic na `cgi-bin` (`curl.exe -i http://127.0.0.1:8080/cgi-bin/uprawnienia.cgi`): HTTP 200

```
EUID: 2
EGID: 2
/lab-data/ogolny.txt: LAB05: dokument dostepny dla grupy procesu WWW.
/lab-data/poufny.txt: odmowa odczytu (Permission denied)
```

Reguła (etap 3 - dopisana do etapu 2):

```
<Directory "/usr/local/apache2/cgi-bin">
    AuthType Basic
    AuthName "Laboratorium 5"
    AuthBasicProvider file
    AuthUserFile "/auth/uzytkownicy"
    Require valid-user
</Directory>
```

| Wejście (GET) | Oczekiwany wynik | Wynik |
|---|---|---|
| `curl.exe -i http://127.0.0.1:8080/cgi-bin/uprawnienia.cgi` | 401 | 401 |
| `curl.exe -i -u student http://127.0.0.1:8080/cgi-bin/uprawnienia.cgi` | 200, bez zmiany UID/GID | 200 |

Odpowiedź z poprawnym hasłem:

```
EUID: 2
EGID: 2
/lab-data/ogolny.txt: LAB05: dokument dostepny dla grupy procesu WWW.
/lab-data/poufny.txt: odmowa odczytu (Permission denied)
```

Wniosek: odczyt `ogolny.txt` wynika z prawa `r` dla grupy 2 (`640`), odmowa dla `poufny.txt` z praw `600` właściciela 0; Basic decyduje tylko o uruchomieniu CGI, a proces nadal działa jako `daemon` (UID/GID 2).
