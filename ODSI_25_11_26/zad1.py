import math
import os
import time

BLOCK_SIZE = 4

def mod_pow(base, exponent, modulus):
    result = 1
    base %= modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent //= 2
    return result

def factorize(n):
    if n % 2 == 0:
        return 2, n // 2
    limit = math.isqrt(n)
    d = 3
    while d <= limit:
        if n % d == 0:
            return d, n // d
        d += 2
    return None

def load_key(path):
    values = {}
    with open(path, "rb") as f:
        for line in f.read().decode("ascii").splitlines():
            if "=" in line:
                name, value = line.split("=", 1)
                values[name.strip()] = value.strip()
    n = int(values["n"])
    e = int(values["e"])
    c = [int(x) for x in values["c"].split(",") if x.strip()]
    return n, e, c

def main():
    tests = [
        ((4, 13, 497), 445),
        ((65, 17, 3233), 2790),
        ((2790, 2753, 3233), 65),
        ((12345, 0, 497), 1),
        ((0, 0, 2), 1),
    ]
    print("Modular exponentiation tests:")
    for (a, b, m), expected in tests:
        print(f"  {a}^{b} mod {m} = {mod_pow(a, b, m)} (expected {expected})")
        assert mod_pow(a, b, m) == expected

    n, e, c = load_key(os.path.join("pliki-dla-studentow", "male_rsa.txt"))
    print(f"\nn = {n} ({n.bit_length()} bits), e = {e}, blocks: {len(c)}")

    start = time.perf_counter()
    p, q = factorize(n)
    factor_time = time.perf_counter() - start
    print(f"p = {p}, q = {q}")
    print(f"p * q == n? {p * q == n}")
    print(f"Factorization time: {factor_time:.3f} s")

    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    print(f"\nphi(n) = {phi}")
    print(f"d = {d}")
    print(f"(e * d) mod phi = {(e * d) % phi}")

    data = b"".join(mod_pow(block, d, n).to_bytes(BLOCK_SIZE, "big") for block in c)
    plaintext = data.decode("utf-8")
    print(f"\nDecrypted text: {plaintext!r}")

if __name__ == "__main__":
    main()
