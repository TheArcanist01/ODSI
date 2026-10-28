import hashlib
import hmac
import secrets
import time

def load_database(path):
    database = {}
    with open(path, "rb") as f:
        for line in f.read().decode("utf-8").splitlines():
            if not line.strip():
                continue
            login, iterations, salt, digest = line.split(":")
            database[login] = (int(iterations), bytes.fromhex(salt), bytes.fromhex(digest))
    return database

def pbkdf2(password, salt, iterations):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)

def weryfikuj(database, login, password):
    record = database.get(login)
    if record is None:
        return False
    iterations, salt, stored = record
    return hmac.compare_digest(pbkdf2(password, salt, iterations), stored)

def dodaj(database, login, password, iterations=600000):
    salt = secrets.token_bytes(16)
    digest = pbkdf2(password, salt, iterations)
    database[login] = (iterations, salt, digest)
    return f"{login}:{iterations}:{salt.hex()}:{digest.hex()}"

def measure(iterations, calls):
    salt = bytes(16)
    start = time.perf_counter()
    for _ in range(calls):
        pbkdf2("abcdef", salt, iterations)
    return (time.perf_counter() - start) / calls

if __name__ == "__main__":
    database = load_database("hasla.txt")

    tests = [
        ("anna", "Kasztan-2026"),
        ("anna", "kasztan-2026"),
        ("piotr", "Żółw na łące"),
        ("kasia", "Kasztan-2026"),
    ]
    print("Verification tests:")
    for login, password in tests:
        print(f"  weryfikuj({login}, {password}): {weryfikuj(database, login, password)}")

    password = "WspolneHaslo!1"
    dodaj(database, "test1", password)
    dodaj(database, "test2", password)
    _, salt1, digest1 = database["test1"]
    _, salt2, digest2 = database["test2"]
    print("\nNew accounts with the same password:")
    print(f"  Salt 1 == Salt 2: {salt1 == salt2}")
    print(f"  Digest 1 == Digest 2: {digest1 == digest2}")
    print(f"  weryfikuj(test1): {weryfikuj(database, 'test1', password)}")
    print(f"  weryfikuj(test2): {weryfikuj(database, 'test2', password)}")

    weak = [login for login, (iterations, _, _) in database.items() if iterations < 600000]
    print(f"\nLogins with < 600000 iterations: {', '.join(weak)}")

    candidates = 26 ** 6
    t1 = measure(1, 10000)
    t600 = measure(600000, 5)
    print(f"PBKDF2 1 iteration: {t1 * 1e6:.2f} us, 26^6 passwords: {candidates * t1 / 60:.1f} min")
    print(f"PBKDF2 600000 iterations: {t600:.3f} s, 26^6 passwords: {candidates * t600 / 86400:.0f} days")
