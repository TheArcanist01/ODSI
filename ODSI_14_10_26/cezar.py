
from pathlib import Path

INPUT_FILE = Path("cezar.bin")
OUTPUT_FILE = Path("cezar.txt")
ALLOWED = set(range(32, 127)) | {9, 10, 13}


def decrypt(data: bytes, key: int) -> bytes:
    return bytes((byte - key) % 256 for byte in data)


def score(data: bytes) -> float:
    return sum(byte in ALLOWED for byte in data) / len(data) if data else 0.0


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    ciphertext = INPUT_FILE.read_bytes()

    if not ciphertext:
        print("Input file is empty.")
        return

    candidates = []

    for key in range(256):
        plaintext = decrypt(ciphertext, key)
        candidates.append((score(plaintext), key, plaintext))

    candidates.sort(key=lambda item: (-item[0], item[1]))

    for rating, key, plaintext in candidates[:5]:
        print(f"k={key}, score={rating:.2%}, preview={plaintext[:120].decode('latin-1')!r}")

    while True:
        try:
            key = int(input("Choose key (0-255): "))
            if 0 <= key <= 255:
                break
        except ValueError:
            pass
        print("Enter an integer from 0 to 255.")

    plaintext = decrypt(ciphertext, key)
    OUTPUT_FILE.write_bytes(plaintext)
    print(f"Saved to {OUTPUT_FILE} (key={key}, score={score(plaintext):.2%})")


if __name__ == "__main__":
    main()
