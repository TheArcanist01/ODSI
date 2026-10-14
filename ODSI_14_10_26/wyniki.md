### Zadanie 1 - Szyfr Cezara

- Rezultat wywołania kodu:
  
  ```
  k=230, score=100.00%, preview='Wkh#Qljkw#Ihuu|\r\rWkh#qljkw#ihuu|#ohiw#wkh#kduerxu#dw#hohyhq/#dv#lw#kdg#grqh#hyhu|#hyhqlqj#iru#dv#orqj#dv#dq|rqh#lq#wkh#w'
  k=233, score=100.00%, preview='The Night Ferry\n\nThe night ferry left the harbour at eleven, as it had done every evening for as long as anyone in the t'
  k=228, score=99.48%, preview='Ymj%Snlmy%Kjww~\x0f\x0fYmj%snlmy%kjww~%qjky%ymj%mfwgtzw%fy%jqj{js1%fx%ny%mfi%itsj%j{jw~%j{jsnsl%ktw%fx%qtsl%fx%fs~tsj%ns%ymj%y'
  k=229, score=99.48%, preview='Xli$Rmklx$Jivv}\x0e\x0eXli$rmklx$jivv}$pijx$xli$levfsyv$ex$ipizir0$ew$mx$leh$hsri$iziv}$izirmrk$jsv$ew$psrk$ew$er}sri$mr$xli$x'
  k=231, score=99.48%, preview='Vjg"Pkijv"Hgtt{\x0c\x0cVjg"pkijv"hgtt{"nghv"vjg"jctdqwt"cv"gngxgp."cu"kv"jcf"fqpg"gxgt{"gxgpkpi"hqt"cu"nqpi"cu"cp{qpg"kp"vjg"v'
  Choose key (0-255): 233
  Saved to cezar.txt (key=233, score=100.00%)
  ```

- Sensowny angielski tekst otrzymano po przesunięciu o 233.

- Przesunięcie o 230 również dało tekst, w którym udział bajtów odpowiadających znakom ASCII wynosił 100%. Tekst jednak nie był sensownym angielskim tekstem, a jedynie ciągiem przypadkowych znaków - użytkownik musi rozstrzygnąć, które przesunięcie jest tym poprawnym. Jest to dowód na to, że sama entropia nie wystarcza do rozstrzygnięcia poprawnego przesunięcia.

### Zadanie 2 - Szyfr Vigenere

- Rezultat wywołania kodu:
  
  ```
  File encryption verified; 2867 bytes processed.
  SZYFR:
  95ac9a9393 95ac9a9393 95ac9a9393
  KOD:
  8da1859890 869d90918c 91968c9c85
  ```

- Dla klucza SZYFR długość klucza wynosi 5 bajtów, tak samo jak długość powtarzającego się w szyfrowanym ciągu fragmentu BRAMA. Każde wystąpienie tekstu zaczyna się więc w tym samym miejscu cyklu klucza i daje identyczny pięciobajtowy fragment kryptogramu. Dla klucza KOD klucz jest krótszy, więc pięciobajtowe fragmenty różnią się między sobą.

- Powtarzające się fragmenty kryptogramu mogą dać atakującemu informację na temat powtarzalności szyfrowanego tekstu oraz długości klucza.

### Zadanie 3 - Szyfr RC4

- Rezultat wywołania kodu:
  
  ```
  Recovered key:              tat
  Total attempts:             17576
  Search time:                8.5798 seconds
  Ciphertext entropy:         7.9271 bits/byte
  Full decrypted entropy:     4.3259 bits/byte
  Top 5 candidates ranking:
    1. Key: 'tat' | Entropy: 4.3910
    2. Key: 'neg' | Entropy: 7.4304
    3. Key: 'mcn' | Entropy: 7.4512
    4. Key: 'oxo' | Entropy: 7.4536
    5. Key: 'tnx' | Entropy: 7.4592
  ```

- Ponowne szyfrowanie może odtworzyć kryptogram nawet dla błędnego klucza, ponieważ oparte jest na operacji XOR. Ta operacja jest symetryczna i odwracalna, więc może dać ten sam rezultat dla dwóch różnych kluczy.

- Ranking entropii działa skutecznie dla tekstu naturalnego, jednak byłby nieskuteczny dla pliku, w którym entropia po odszyfrowaniu nie jest wyraźnie niższa od entropii kryptogramu, np. pliku skompresowanego lub wykonywalnego.
