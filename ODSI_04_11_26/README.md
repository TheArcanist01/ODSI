## Wymagania

Docker Desktop (WSL 2) z Docker Compose oraz Python 3 - wyłącznie biblioteka standardowa.

## Pliki

- `pliki-dla-studentow/konfiguracja/dostep.conf` - reguły dostępu (zadania 1-3)
- `pliki-dla-studentow/cgi-bin/uprawnienia.cgi` - program CGI (zadanie 3)
- `pliki-dla-studentow/zad1.py`, `zad2.py`, `zad3.py` - uruchomienie serwera, wprowadzenie reguł etapami i pomiary
- `pliki-dla-studentow/common.py` - funkcje wspólne

## Wywołanie plików

W katalogu `pliki-dla-studentow`, przy uruchomionym Docker Desktop:

```
python zad1.py
python zad2.py
python zad3.py
```

`zad2.py` tworzy bazę `auth/uzytkownicy` poleceniem `htpasswd` (hasło podawane interaktywnie) i pyta ponownie o hasło do testów. `zad3.py` pyta o to samo hasło. Baza haseł nie trafia do repozytorium.

Ręcznie:

```
docker compose up -d --build web
docker compose run --rm --no-deps narzedzia -cB /auth/uzytkownicy student
docker compose exec web httpd -t
docker compose restart web
curl.exe -i http://127.0.0.1:8080/materialy/
curl.exe -i -u student http://127.0.0.1:8080/cgi-bin/uprawnienia.cgi
```
