# Laboratorium 6 - Cross-Site Scripting (poprawiona aplikacja)

Poprawiona, zabezpieczona wersja aplikacji „Tablica ogłoszeń" znajduje się w
katalogu `pliki-dla-studentow/aplikacja/`. Zmieniono tylko pliki wskazane w
zadaniach; środowisko (Docker) pozostaje bez zmian.

## Wymagane środowisko

Docker z kontenerami Linux, Docker Compose, przeglądarka z narzędziami
deweloperskimi oraz `curl` (w Windows `curl.exe`). Wyłącznie standardowa
biblioteka Pythona oraz Flask 3.1.3 instalowany w obrazie (zob. `Dockerfile`).

## Uruchomienie

Wszystkie polecenia wykonuj w katalogu `pliki-dla-studentow`:

```
docker compose up -d
```

- Aplikacja: `http://127.0.0.1:8080` (konta: `anna`/`anna-lab6`, `student`/`student-lab6`).
- Zbieracz (serwer napastnika): `http://localhost:8081`, log: `docker compose logs zbieracz`.
- Po każdej zmianie kodu: `docker compose restart web`. Zatrzymanie: `docker compose down`.

## Wprowadzone poprawki (XSS)

| Plik                                                               | Zmiana                                                                          |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| `aplikacja/app.py`, w. 37                                          | `fraza` kodowane przez `escape()` przed wstawieniem do HTML (XSS odbity)        |
| `aplikacja/app.py`, w. 10                                          | `SESSION_COOKIE_HTTPONLY = True` (ciasteczko sesji niedostępne dla JS)          |
| `aplikacja/app.py`, `@app.after_request`                           | nagłówek `Content-Security-Policy` na każdej odpowiedzi                         |
| `aplikacja/templates/tablica.html`                                 | usunięty filtr `                                                                |
| `aplikacja/templates/podglad.html` + `aplikacja/static/podglad.js` | skrypt przeniesiony do pliku zewnętrznego, `innerHTML` zastąpione `textContent` |

Pełne ładunki, polecenia i wyniki przed/po: `dowody.md`.
