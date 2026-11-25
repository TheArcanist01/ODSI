from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from zad1 import mod_pow

def extended_gcd(a, b):
    x0, y0, x1, y1 = 1, 0, 0, 1
    while b:
        q, a, b = a // b, b, a % b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0

def mod_inverse(e, m):
    g, x, _ = extended_gcd(e, m)
    return x % m if g == 1 else None

def library_inverse(e, m):
    try:
        return pow(e, -1, m)
    except ValueError:
        return None

def main():
    print("Modular inverse:")
    for e, m in [(17, 3120), (65537, 1466053951600), (3, 10), (6, 9), (2, 4)]:
        own = mod_inverse(e, m)
        library = library_inverse(e, m)
        print(f"  {e} mod {m}: own = {own}, library = {library}, equal? {own == library}")

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    oaep = padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    print(f"\nOAEP limit from formula: {256 - 2 * 32 - 2} B")
    for size in (190, 191):
        try:
            ciphertext = key.public_key().encrypt(b"A" * size, oaep)
            print(f"  {size} B: OK ({len(ciphertext)} B ciphertext)")
        except ValueError as error:
            print(f"  {size} B: REJECTED ({error})")

    n, e = 1466056398307, 65537
    m = int.from_bytes(b"Test", "big")
    c1 = mod_pow(m, e, n)
    c2 = mod_pow(m, e, n)
    print(f"\nTextbook RSA: {c1} / {c2}, equal? {c1 == c2}")
    c1 = key.public_key().encrypt(b"Test", oaep)
    c2 = key.public_key().encrypt(b"Test", oaep)
    print(f"RSA-OAEP: {c1[:8].hex()}... / {c2[:8].hex()}..., equal? {c1 == c2}")

if __name__ == "__main__":
    main()
