// Podgląd tekstu z fragmentu adresu (po znaku #).
// textContent wstawia dane jako zwykły tekst, więc znaczniki HTML ani kod JS
// nie są interpretowane (w przeciwieństwie do innerHTML).
document.getElementById("podglad").textContent =
  decodeURIComponent(location.hash.slice(1));
