"""Sejf sekretow i kalkulator - wersja poprawiona (laboratorium 7).

Zad. 1-2: zapytanie SQL z parametrem zamiast sklejania napisu; uzytkownik widzi
ogolny komunikat, szczegoly trafiaja do logu serwera.
Zad. 3: kalkulator liczony wlasnym parserem (liczba operator liczba), bez eval.

Uruchamiaj wylacznie lokalnie, w kontenerze z pakietu. Dane sa fikcyjne.
"""
import re
import sqlite3

from flask import Flask, render_template, request

app = Flask(__name__)
BAZA = "file:/dane/sekrety.db?mode=ro"

# Zapytanie jest stale; wartosc klucza trafia osobno jako parametr ?.
ZAPYTANIE = "SELECT wlasciciel, sekret FROM sekrety WHERE klucz = ?"

# Parser kalkulatora: liczba, operator, liczba (spacje wokol operatora dozwolone).
WZORZEC = re.compile(r"\s*(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)\s*")
OPERACJE = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}


class BledneWejscie(Exception):
    """Wejscie niezgodne z dozwolona gramatyka lub dzielenie przez zero."""


def oblicz(wyrazenie):
    if not wyrazenie or len(wyrazenie) > 100:
        raise BledneWejscie("nieprawidlowe dane")
    dopasowanie = WZORZEC.fullmatch(wyrazenie)
    if not dopasowanie:
        raise BledneWejscie("nieprawidlowe dane")
    a = float(dopasowanie.group(1))
    operator = dopasowanie.group(2)
    b = float(dopasowanie.group(3))
    if operator == "/" and b == 0:
        raise BledneWejscie("dzielenie przez zero")
    return OPERACJE[operator](a, b)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sekret")
def sekret():
    klucz = request.args.get("klucz", "")
    wiersze, blad = [], None
    if klucz:
        try:
            with sqlite3.connect(BAZA, uri=True) as db:
                wiersze = db.execute(ZAPYTANIE, (klucz,)).fetchall()
        except sqlite3.Error:
            app.logger.exception("Blad zapytania do bazy sekretow")
            blad = "Wystapil blad podczas obslugi zapytania."
    return render_template(
        "sekret.html", klucz=klucz, zapytanie=ZAPYTANIE, wiersze=wiersze, blad=blad
    )


@app.route("/kalkulator")
def kalkulator():
    # Brak parametru -> tylko formularz (HTTP 200). Pusty parametr -> bledne wejscie.
    if "wyrazenie" not in request.args:
        return render_template("kalkulator.html", wyrazenie="", wynik=None)
    wyrazenie = request.args.get("wyrazenie", "")
    try:
        wynik = oblicz(wyrazenie)
    except BledneWejscie as exc:
        return f"Bledne wejscie: {exc}", 400
    return render_template("kalkulator.html", wyrazenie=wyrazenie, wynik=wynik)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
