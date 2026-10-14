
from pathlib import Path

INPUT_FILE = Path("tekst_pl.txt")
OUTPUT_FILE = Path("vigenere.bin")


def encrypt(data: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("Key must not be empty.")
    return bytes((byte + key[i % len(key)]) % 256 for i, byte in enumerate(data))


def decrypt(data: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("Key must not be empty.")
    return bytes((byte - key[i % len(key)]) % 256 for i, byte in enumerate(data))


def show_chunks(data: bytes) -> None:
    print(" ".join(data[i:i + 5].hex() for i in range(0, len(data), 5)))


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    plaintext = INPUT_FILE.read_bytes()
    key = b"ZAMEK"

    ciphertext = encrypt(plaintext, key)
    OUTPUT_FILE.write_bytes(ciphertext)

    recovered = decrypt(ciphertext, key)
    assert recovered == plaintext

    assert encrypt(b"", key) == b""
    assert decrypt(b"", key) == b""
    assert decrypt(encrypt(bytes([0, 255]), key), key) == bytes([0, 255])

    print(f"File encryption verified; {len(plaintext)} bytes processed.")

    sample = b"BRAMABRAMABRAMA"

    for key in (b"SZYFR", b"KOD"):
        ciphertext = encrypt(sample, key)
        print(f"{key.decode()}:")
        show_chunks(ciphertext)


if __name__ == "__main__":
    main()
