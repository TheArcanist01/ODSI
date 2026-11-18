# Laboratorium 7 - SQL Injection i Code Injection (poprawiona aplikacja)

Poprawiona, zabezpieczona wersja aplikacji „Sejf sekretów" z kalkulatorem znajduje
się w katalogu `pliki-dla-studentow/aplikacja/`. Zmieniono wyłącznie `aplikacja/app.py`;
środowisko (Docker, `Dockerfile`, `compose.yaml`, `utworz_baze.py`) pozostaje bez zmian,
zgodnie z `START.md`.

## Wymagane środowisko

Docker z kontenerami Linux i Docker Compose, przeglądarka oraz `curl` (w Windows `curl.exe`).
Obraz `python:3.12-alpine`, Flask 3.1.3 (zob. `Dockerfile`). Baza `/dane/sekrety.db`
powstaje podczas budowy obrazu i jest tylko do odczytu; kontener działa jako użytkownik
`app` z systemem plików tylko do odczytu. Dane w bazie są fikcyjne.

## Uruchomienie

Wszystkie polecenia wykonuj w katalogu `pliki-dla-studentow`:

```
docker compose up -d
curl -i "http://127.0.0.1:8080/sekret?klucz=1234"
curl -G --data-urlencode "wyrazenie=2*21" http://127.0.0.1:8080/kalkulator
```

Po każdej zmianie kodu: `docker compose restart web`. Logi: `docker compose logs --tail 30 web`.
Zatrzymanie: `docker compose down`.

## Wprowadzone poprawki

| Miejsce w `aplikacja/app.py` | Zmiana |
| --- | --- |
| trasa `/sekret` | sklejanie napisu zastąpione stałym zapytaniem `SELECT ... WHERE klucz = ?` i krotką `(klucz,)` przekazaną do `execute` (Zad. 1-2) |
| trasa `/sekret`, obsługa wyjątku | użytkownik widzi ogólny komunikat; szczegóły wyjątku SQLite zapisywane przez `app.logger.exception(...)` (Zad. 2) |
| trasa `/kalkulator`, funkcja `oblicz` | `eval` zastąpiony własnym parserem `liczba operator liczba`; operatory ze słownika `+ - * /`; limit 100 znaków; dzielenie przez zero i złe wejście → HTTP 400; brak parametru → formularz (HTTP 200) (Zad. 3) |

Pełne ładunki, polecenia i wyniki przed/po: `dowody.md`.
