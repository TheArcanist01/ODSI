import os
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

LOGIN = "TheArcanist01"
NONCE_SIZE = 12
TAG_SIZE = 16

OAEP = padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None,
)

def parse(data, key_size):
    if len(data) < 2:
        raise ValueError(f"file too short for header ({len(data)} B)")
    length = int.from_bytes(data[:2], "big")
    if length != key_size:
        raise ValueError(f"L = {length} differs from RSA modulus length {key_size} B")
    if len(data) < 2 + length + NONCE_SIZE + TAG_SIZE:
        raise ValueError(f"file truncated: {len(data)} B < {2 + length + NONCE_SIZE + TAG_SIZE} B")
    encrypted_key = data[2:2 + length]
    nonce = data[2 + length:2 + length + NONCE_SIZE]
    ciphertext = data[2 + length + NONCE_SIZE:]
    return length, encrypted_key, nonce, ciphertext

def decrypt(data, private_key):
    length, encrypted_key, nonce, ciphertext = parse(data, private_key.key_size // 8)
    aes_key = private_key.decrypt(encrypted_key, OAEP)
    if len(aes_key) != 32:
        raise ValueError(f"AES key has {len(aes_key)} B instead of 32 B")
    try:
        plaintext = AESGCM(aes_key).decrypt(nonce, ciphertext, None)
    except InvalidTag:
        raise ValueError("invalid GCM tag")
    return length, plaintext

def encrypt(plaintext, public_key):
    aes_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(NONCE_SIZE)
    encrypted_key = public_key.encrypt(aes_key, OAEP)
    ciphertext = AESGCM(aes_key).encrypt(nonce, plaintext, None)
    return len(encrypted_key).to_bytes(2, "big") + encrypted_key + nonce + ciphertext

def main():
    password = os.environ.get("LAB8_HASLO")
    if not password:
        print("Set LAB8_HASLO environment variable (password for klucz_prywatny.pem).")
        return

    package_dir = "pliki-dla-studentow"
    with open(os.path.join(package_dir, "klucz_prywatny.pem"), "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=password.encode())
    with open(os.path.join(package_dir, "klucz_prowadzacego.pem"), "rb") as f:
        teacher_key = serialization.load_pem_public_key(f.read())
    with open(os.path.join(package_dir, "paczka.bin"), "rb") as f:
        package = f.read()

    length, plaintext = decrypt(package, private_key)
    text = plaintext.decode("utf-8")
    print(f"paczka.bin: {len(package)} B, L = {length}")
    print(f"Decrypted text:\n{text}")

    control_line = next(line for line in text.splitlines() if "kontrolne" in line)
    control_word = control_line.split(":", 1)[1].strip()

    response = encrypt(f"{control_word}\n{LOGIN}".encode("utf-8"), teacher_key)
    with open("odpowiedz.bin", "wb") as f:
        f.write(response)
    parse(response, teacher_key.key_size // 8)
    print(f"odpowiedz.bin: {len(response)} B, L = {int.from_bytes(response[:2], 'big')}")

    changed = bytearray(package)
    changed[2 + length + NONCE_SIZE] ^= 0x01
    with open("paczka_zmieniona.bin", "wb") as f:
        f.write(changed)

    tests = [
        ("changed ciphertext byte", bytes(changed)),
        ("changed tag byte", package[:-1] + bytes([package[-1] ^ 0x01])),
        ("truncated (no tag)", package[:-TAG_SIZE]),
        ("truncated < L + 30 B", package[:2 + length + 20]),
        ("wrong L in header", (length - 1).to_bytes(2, "big") + package[2:]),
        ("1 B file", package[:1]),
    ]
    print("\nModified files:")
    for name, data in tests:
        try:
            decrypt(data, private_key)
            print(f"  {name}: ACCEPTED")
        except ValueError as error:
            print(f"  {name}: REJECTED ({error})")

if __name__ == "__main__":
    main()
