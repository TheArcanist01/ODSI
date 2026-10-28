# Laboratorium 4 - omówienie kodu i algorytmów

Notatka do nauki przed odbiorem. Nie dołączać do repozytorium ani do raportu.

## Podstawy: czym jest funkcja skrótu

Funkcja skrótu (hash) zamienia dane dowolnej długości na wynik o stałej długości. SHA-256 zawsze daje 256 bitów = 32 bajty = 64 znaki hex, niezależnie od tego, czy na wejściu jest 1 bajt, czy 10 GB.

Dobra kryptograficzna funkcja skrótu ma trzy odporności:

| Własność           | Co jest trudne dla atakującego          | Koszt dla n-bitowego skrótu |
| ------------------ | --------------------------------------- | --------------------------- |
| Przeciwobraz       | mając y, znaleźć x takie, że h(x) = y   | ok. 2^n prób                |
| Drugi przeciwobraz | mając x, znaleźć inne x' z h(x') = h(x) | ok. 2^n prób                |
| Kolizja            | znaleźć dowolne x ≠ x' z h(x) = h(x')   | ok. 2^(n/2) prób            |

Dodatkowo funkcja jest deterministyczna (te same bajty dają zawsze ten sam skrót) i ma **efekt lawinowy**: zmiana jednego bitu wejścia zmienia średnio połowę bitów wyniku, w sposób nieprzewidywalny.

MD5 (128 b) i SHA-1 (160 b) mają znane praktyczne kolizje, więc nie nadają się do zabezpieczeń. SHA-256 i SHA3-256 są obecnie bezpieczne.

**Ważne:** skrót liczy się z dokładnych bajtów. Dlatego wszystkie pliki czytamy w trybie binarnym (`"rb"`). Gdyby Windows lub git zamienił `\n` (LF) na `\r\n` (CRLF), plik wyglądałby tak samo, ale miałby inne bajty, czyli zupełnie inny skrót. Plik `.gitattributes` z regułą `* -text` mówi gitowi, żeby nie ruszał końców wierszy.

---

## Zadanie 1 - sumy kontrolne (`zad1.py`)

### Cel

Pokazać, do czego służy suma kontrolna: wykrywanie, czy plik się zmienił (uszkodzenie przy pobieraniu, błąd dysku). Przy okazji zobaczyć efekt lawinowy i zrozumieć, dlaczego sama suma **nie chroni przed celowym atakiem**.

### Format `SHA256SUMS.txt`

To format programu `sha256sum`:

```
488e8ff2...96c2  dokumenty/budzet.csv
```

64 znaki hex, **dwie spacje**, ścieżka względem katalogu z plikiem sum.

### Kod krok po kroku

**`sha256_file(path)`**

```python
with open(path, "rb") as f:
    return hashlib.sha256(f.read()).hexdigest()
```

Otwiera plik binarnie, wczytuje wszystkie bajty, liczy SHA-256 i zwraca 64-znakowy napis hex. `hashlib` to biblioteka standardowa Pythona, więc niczego nie implementujemy sami (tak każe polecenie).

**`sha256_file_chunks(path, chunk_size=4096)`** (dodatkowe)
Tworzy obiekt `hashlib.sha256()` i w pętli dokłada do niego kolejne kawałki po 4096 B metodą `update()`, aż `read()` zwróci pusty ciąg (koniec pliku). Wynik jest identyczny jak przy wczytaniu całości, bo SHA-256 i tak przetwarza dane blokami po 64 B, a `update()` tylko dokłada dane do bufora. Przydaje się przy dużych plikach, które nie mieszczą się w pamięci. Na końcu `zadanie_1()` sprawdzamy, że dla `dane.bin` oba sposoby dają to samo (`True`).

**`check_sums(sums_path)`**

1. `base_dir` to katalog, w którym leży `SHA256SUMS.txt`. Ścieżki w pliku są względem niego, więc do niego doklejamy `rel_path`.
2. Plik czytamy binarnie, dekodujemy UTF-8 i dzielimy na wiersze (`splitlines()` radzi sobie i z LF, i z CRLF).
3. Puste wiersze pomijamy.
4. `line[:64]` to oczekiwany skrót (64 znaki), `line[66:]` to ścieżka (pomijamy 2 spacje na pozycjach 64 i 65). `.lower()` na wypadek wielkich liter w hex.
5. W bloku `try` liczymy skrót pliku:
   - zgodny → `OK`,
   - inny → `BŁĄD` (plik zmieniony; u nas `budzet.csv`),
   - `FileNotFoundError` → `BRAK` (u nas `harmonogram.txt`). Wyjątek jest złapany, więc brak pliku **nie przerywa programu**, tylko pętla idzie dalej.

**`bit_difference(a, b)`**

```python
x = int.from_bytes(a, "big") ^ int.from_bytes(b, "big")
return bin(x).count("1")
```

Zamienia oba 32-bajtowe skróty na wielkie liczby całkowite, robi XOR (bit wyniku = 1 tam, gdzie bity się różnią) i liczy jedynki w zapisie binarnym. To jest **odległość Hamminga**.

### Wyniki i interpretacja

- `budzet.csv` → BŁĄD, `harmonogram.txt` → BRAK, pozostałe → OK (tak samo jak `sha256sum -c`).
- „Ala ma kota.” i „Ola ma kota.” różnią się jedną literą, a skróty różnią się na **131 z 256 bitów**, czyli ok. 51%. To efekt lawinowy: po skrócie nie da się poznać, że wejścia były podobne.

### Pytanie przy odbiorze: dlaczego suma obok pliku nie chroni przed podmianą?

SHA-256 nie ma żadnego klucza, każdy może go policzyć. Jeśli atakujący może podmienić plik, to może też policzyć nowy skrót i podmienić wpis w `SHA256SUMS.txt`. Weryfikacja przejdzie wtedy jako OK.

Co zamiast:

| Mechanizm               | Błąd przypadkowy | Celowa podmiana                                               |
| ----------------------- | ---------------- | ------------------------------------------------------------- |
| Suma SHA-256 obok pliku | wykrywa          | nie wykrywa                                                   |
| HMAC z tajnym kluczem   | wykrywa          | wykrywa, bo bez klucza nie da się policzyć poprawnego HMAC    |
| Podpis cyfrowy          | wykrywa          | wykrywa; podpisuje się kluczem prywatnym, sprawdza publicznym |

Sama suma też wystarcza, jeśli pochodzi z **zaufanego, niezależnego źródła** (np. ze strony HTTPS producenta, a plik z mirrora).

---

## Zadanie 2 - przechowywanie haseł (`zad2.py`)

### Cel

Pokazać poprawny sposób przechowywania haseł w bazie: nie jawnie, nie samym SHA-256, tylko wolną funkcją wyprowadzania klucza (PBKDF2) z **solą** i dużą **liczbą iteracji**, a do tego porównanie skrótów w stałym czasie.

### Dlaczego nie jawnie i nie samym SHA-256

- Hasła jawne: wyciek bazy od razu ujawnia wszystkie konta.
- `SHA-256(hasło)`:
  - jest bardzo szybki (miliardy prób na sekundę na GPU), więc łatwo sprawdzać słowniki;
  - te same hasła dają te same skróty: widać, kto ma takie samo hasło, i działają gotowe tablice (rainbow tables) dla popularnych haseł.

### Algorytm PBKDF2-HMAC-SHA256

- **HMAC-SHA256(klucz, dane)** to SHA-256 użyty z kluczem (dwa zagnieżdżone haszowania z kluczem zmieszanym ze stałymi `ipad`/`opad`).
- **PBKDF2** w uproszczeniu:
  
  ```
  U1 = HMAC(hasło, sól || 00000001)
  U2 = HMAC(hasło, U1)
  ...
  Uc = HMAC(hasło, U(c-1))
  wynik = U1 XOR U2 XOR ... XOR Uc
  ```
  
  gdzie `c` to liczba iteracji. Wynik ma 32 B (jeden blok SHA-256). Każda próba hasła kosztuje więc `c` obliczeń HMAC, a nie jedno.

### Format bazy `hasla.txt`

```
login:iteracje:sól_hex:skrót_hex
```

np. `anna:600000:3a6d...:2632...`. Sól ma 16 B (32 znaki hex), skrót 32 B (64 znaki hex). Sól i liczba iteracji są **jawne**, bo muszą być znane przy weryfikacji. Ich bezpieczeństwo nie zależy od tajności.

### Kod krok po kroku

**`load_database(path)`**
Czyta plik, dzieli każdy wiersz po `:` na 4 pola i buduje słownik:

```
login -> (iteracje: int, sól: bytes, skrót: bytes)
```

`bytes.fromhex()` zamienia napis hex na surowe bajty.

**`pbkdf2(password, salt, iterations)`**

```python
hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)
```

Biblioteczna implementacja PBKDF2. Hasło kodujemy w **UTF-8**. Ma to znaczenie dla „Żółw na łące”, bo polskie znaki zajmują po 2 bajty. Inne kodowanie (np. cp1250) dałoby inne bajty, a więc inny skrót i `False`. Dlatego plik źródłowy musi być zapisany w UTF-8.

**`weryfikuj(database, login, password)`**

1. `database.get(login)` → jeśli brak loginu, zwraca `False` (przypadek `kasia`).
2. Bierze z rekordu **jego własną** sól i liczbę iteracji, liczy PBKDF2 z podanego hasła.
3. Porównuje wynik z zapisanym skrótem funkcją `hmac.compare_digest`.

**Dlaczego `hmac.compare_digest`, a nie `==`?**
Zwykłe `==` przerywa porównanie na pierwszym różnym bajcie, więc czas odpowiedzi zależy od tego, ile bajtów się zgadza. Atakujący mierzący czasy mógłby odgadywać wynik bajt po bajcie (**atak czasowy**, timing attack). `compare_digest` zawsze porównuje wszystkie bajty, więc czas jest stały.

**`dodaj(database, login, password, iterations=600000)`**

1. `secrets.token_bytes(16)` → 16 losowych bajtów z **kryptograficznie bezpiecznego** generatora (systemowy CSPRNG). Moduł `random` się do tego nie nadaje, bo jest przewidywalny.
2. Liczy PBKDF2 z 600 000 iteracji (wartość rekomendowana przez OWASP dla PBKDF2-HMAC-SHA256).
3. Zapisuje rekord do słownika i zwraca go jako napis w formacie bazy. Zapis do pliku nie był wymagany.

**`measure(iterations, calls)`** (dodatkowe)
Mierzy `time.perf_counter()` przed i po `calls` wywołaniach PBKDF2 i zwraca średni czas jednego wywołania.

**Część główna**

- 4 testy weryfikacji:
  - `anna` / `Kasztan-2026` → True,
  - `anna` / `kasztan-2026` → False (inna wielkość litery = inne bajty = zupełnie inny skrót),
  - `piotr` / `Żółw na łące` → True,
  - `kasia` → False (nie ma takiego loginu).
- Konta `test1` i `test2` z tym samym hasłem: **sole różne → skróty różne**, a mimo to oba się weryfikują.
- Dodatkowo:
  - loginy z mniej niż 600 000 iteracji: `marek` (1000) i `zofia` (10 000), czyli słabo chronione;
  - szacunek ataku siłowego na 26⁶ ≈ 3,1·10⁸ haseł (6 małych liter): przy 1 iteracji ok. 10 minut, przy 600 000 iteracji ok. roku na jednym rdzeniu. Wzór: liczba kandydatów × czas jednej próby.

### Pytanie przy odbiorze: co daje sól, a co liczba iteracji?

- **Sól** (losowa, jawna, inna dla każdego konta) sprawia, że te same hasła dają różne skróty. Atakujący nie użyje gotowych tablic, nie zobaczy, kto ma takie samo hasło, i musi łamać każde konto osobno.
- **Liczba iteracji** sprawia, że każda pojedyncza próba hasła jest kosztowna (tu 600 000 razy droższa). Atak słownikowy lub siłowy staje się wielokrotnie wolniejszy, a dla użytkownika 0,1 s przy logowaniu jest niezauważalne.

Sól **nie** spowalnia łamania jednego konta, robią to tylko iteracje. Iteracje **nie** ukrywają takich samych haseł, robi to tylko sól. Potrzebne są obie.

---

## Zadanie 3 - kolizje i paradoks urodzinowy (`zad3.py`)

### Cel

Pokazać w praktyce, że znalezienie **kolizji** (dowolnej pary o tym samym skrócie) jest dużo łatwiejsze niż dopasowanie do **ustalonego** skrótu. Stoi za tym paradoks urodzinowy. Do tego scenariusz ataku: atakujący przygotowuje dwa dokumenty (uczciwy i zmieniony), które wyglądają normalnie, a mają ten sam skrót. Ofiara podpisuje wersję uczciwą, a podpis pasuje też do zmienionej.

### Model skrótu h24

Prawdziwego SHA-256 nie da się zderzyć, więc używamy jego skróconej wersji:

```python
def h24(data):
    return hashlib.sha256(data).hexdigest()[:6]
```

Pierwsze 3 bajty = 24 bity = 6 znaków hex. Możliwych wartości jest 2²⁴ ≈ 16,8 mln.

### Atak białych znaków: warianty dokumentu

Oba pliki mają po 13 wierszy. Dla każdego wiersza można dopisać spację przed `\n` albo nie. Spacji na końcu wiersza nie widać, więc treść dokumentu dla człowieka się nie zmienia, ale bajty (i skrót) już tak.

13 wierszy × (spacja / brak spacji) daje 2¹³ = **8192** warianty. Numer wariantu `v` (0…8191) traktujemy jak maskę bitową: bit `i` równy 1 oznacza spację w wierszu `i`.

Przykład: `v = 5 = 0b101` → spacja w wierszach 0 i 2.

### Kod krok po kroku

**`read_lines(path)`**

```python
f.read().split(b"\n")[:-1]
```

Czyta bajty i dzieli po `\n`. Plik kończy się `\n`, więc ostatni element jest pusty i go odcinamy. Zostaje 13 wierszy **bez** `\n`.

**`variant(lines, v)`**

```python
b"".join(line + (b" " if (v >> i) & 1 else b"") + b"\n" for i, line in enumerate(lines))
```

Dla każdego wiersza `i`: `(v >> i) & 1` wyciąga i-ty bit liczby `v`. Jeśli jest 1, dokleja spację. Potem dokleja `\n` z powrotem. Wariant 0 odtwarza plik bajt w bajt.

**`main()`**

*Krok 1: słownik wariantów oryginału.*
Dla każdego z 8192 wariantów oryginału liczy h24.

- `first_variant` (`h24 → v`) zapamiętuje tylko pierwszy wariant o danym skrócie (`setdefault` nie nadpisuje istniejącego klucza). Tego wymaga polecenie.
- `all_variants` (`h24 → [lista v]`) zapamiętuje wszystkie warianty. Służy do części dodatkowej (liczenie wszystkich par).

Wyszukiwanie w słowniku trwa O(1), więc zamiast porównywać 8192 × 8192 ≈ 67 mln par, robimy 8192 + 8192 obliczeń skrótu.

*Krok 2 i 3: jedna pętla po wariantach zmienionego dokumentu.*
Dla każdego `v` liczymy h24 zmienionego wariantu i:

- jeśli jeszcze nie mamy pary, a ten skrót jest w słowniku oryginału, zapamiętujemy parę `(v_oryginał, v_zmieniony, h24)`. To **kolizja**;
- jeśli skrót równa się h24 **niezmienionego** oryginału (wariant 0), zwiększamy licznik. To próba **drugiego przeciwobrazu** (dopasowania do ustalonego skrótu);
- dodatkowo do `all_pairs` dodajemy, ile wariantów oryginału ma ten sam skrót. To liczba wszystkich par kolizyjnych.

### Wyniki

- Para: **v_oryginał = 7282, v_zmieniony = 1761, h24 = aac6b9**. Te dwa dokumenty o różnej treści mają ten sam skrót h24.
- Do h24 niezmienionego oryginału (`9a8fd6`) pasuje **0 z 8192** zmienionych wariantów.
- Wszystkich par kolizyjnych jest **3**, a oczekiwano **8192 · 8192 / 2²⁴ = 4**. To zgodne z teorią, bo przy losowym zjawisku 3 zamiast 4 to normalny rozrzut.

### Skąd te liczby: paradoks urodzinowy

- **Dopasowanie do ustalonego skrótu:** każdy z 8192 wariantów ma szansę 1/2²⁴ na trafienie w konkretną wartość. Oczekiwana liczba trafień to 8192 / 16 777 216 ≈ **0,0005**, więc praktycznie zero. Żeby mieć realną szansę, trzeba ok. **2²⁴ ≈ 16,8 mln** prób (2^n).
- **Dowolna para:** porównujemy każdy z 8192 wariantów zmienionych z każdym z 8192 oryginalnych, czyli 8192² ≈ 67 mln par. Każda para ma szansę 1/2²⁴, więc oczekiwanie wynosi 67 mln / 16,8 mln = **4 kolizje**. Wystarczy ok. **2¹² = 4096** wariantów z każdej strony (2^(n/2)).

Analogia urodzinowa: w grupie 23 osób szansa, że **jakieś dwie** mają urodziny tego samego dnia, przekracza 50%. Szansa, że ktoś ma urodziny **w Twoje** urodziny, jest wtedy tylko ok. 6%. Par jest dużo więcej niż osób.

### Pytanie przy odbiorze: dlaczego kolizję znaleźć łatwiej niż przeciwobraz?

Przy szukaniu kolizji każdy nowy wariant porównujemy ze **wszystkimi** dotychczasowymi, więc liczba sprawdzanych par rośnie kwadratowo (k²). Przy dopasowaniu do ustalonego skrótu każdy wariant ma tylko **jedną** szansę. Dlatego kolizja kosztuje ok. 2^(n/2) prób, a przeciwobraz ok. 2^n.

Wniosek praktyczny: funkcja skrótu musi mieć dwa razy więcej bitów niż żądany poziom bezpieczeństwa. SHA-256 daje 128 bitów odporności na kolizje (2¹²⁸ prób, nieosiągalne), h24 tylko 12 bitów (4096 prób, czyli ułamek sekundy).

---

## Ściąga: najważniejsze funkcje z biblioteki

| Funkcja                                                         | Do czego                           |
| --------------------------------------------------------------- | ---------------------------------- |
| `hashlib.sha256(dane).hexdigest()`                              | SHA-256 jako 64 znaki hex          |
| `hashlib.sha256(dane).digest()`                                 | SHA-256 jako 32 surowe bajty       |
| `h = hashlib.sha256(); h.update(kawałek)`                       | liczenie skrótu kawałkami          |
| `hashlib.pbkdf2_hmac("sha256", hasło, sól, iteracje, dklen=32)` | PBKDF2-HMAC-SHA256                 |
| `hmac.compare_digest(a, b)`                                     | porównanie w stałym czasie         |
| `secrets.token_bytes(16)`                                       | bezpieczne losowe bajty (sól)      |
| `bytes.fromhex(s)` / `b.hex()`                                  | zamiana hex ↔ bajty                |
| `int.from_bytes(b, "big")`                                      | bajty → liczba (do XOR)            |
| `bin(x).count("1")`                                             | liczba jedynek (różniące się bity) |
| `(v >> i) & 1`                                                  | i-ty bit liczby v                  |
