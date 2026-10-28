import hashlib
import os

def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def sha256_file_chunks(path, chunk_size=4096):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def check_sums(sums_path):
    base_dir = os.path.dirname(os.path.abspath(sums_path))
    with open(sums_path, "rb") as f:
        lines = f.read().decode("utf-8").splitlines()

    for line in lines:
        if not line.strip():
            continue
        expected = line[:64].lower()
        rel_path = line[66:]
        try:
            status = "OK" if sha256_file(os.path.join(base_dir, rel_path)) == expected else "BŁĄD"
        except FileNotFoundError:
            status = "BRAK"
        print(f"  {rel_path}: {status}")

def bit_difference(a, b):
    x = int.from_bytes(a, "big") ^ int.from_bytes(b, "big")
    return bin(x).count("1")

def zadanie_1():
    print("Checksums:")
    check_sums("SHA256SUMS.txt")

    h1 = hashlib.sha256("Ala ma kota.".encode("ascii")).digest()
    h2 = hashlib.sha256("Ola ma kota.".encode("ascii")).digest()
    print(f"\nSHA-256('Ala ma kota.'): {h1.hex()}")
    print(f"SHA-256('Ola ma kota.'): {h2.hex()}")
    print(f"Different bits: {bit_difference(h1, h2)} / 256")

    path = os.path.join("dokumenty", "dane.bin")
    print(f"\ndane.bin whole == chunks of 4096 B? {sha256_file(path) == sha256_file_chunks(path)}")

if __name__ == "__main__":
    zadanie_1()
