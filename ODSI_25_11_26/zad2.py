import os
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

LOGIN = "TheArcanist01"
PRIVATE_KEY_FILE = "moj_klucz_prywatny.pem"
PUBLIC_KEY_FILE = "moj_klucz_publiczny.pem"

PSS = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32)

def verify(public_key, data, signature):
    try:
        public_key.verify(signature, data, PSS, hashes.SHA256())
        return True
    except InvalidSignature:
        return False
    except ValueError:
        return False

def status(result):
    return "OK" if result else "ERROR"

def load_or_generate_key():
    if os.path.exists(PRIVATE_KEY_FILE):
        with open(PRIVATE_KEY_FILE, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ))
    return private_key

def main():
    package_dir = "pliki-dla-studentow"
    with open(os.path.join(package_dir, "klucz_podpisu.pem"), "rb") as f:
        signer_key = serialization.load_pem_public_key(f.read())

    print("Documents:")
    documents_dir = os.path.join(package_dir, "dokumenty")
    for name in sorted(os.listdir(documents_dir)):
        if not name.endswith(".txt"):
            continue
        with open(os.path.join(documents_dir, name), "rb") as f:
            data = f.read()
        with open(os.path.join(documents_dir, name + ".sig"), "rb") as f:
            signature = f.read()
        print(f"  {name}: {status(verify(signer_key, data, signature))}")

    private_key = load_or_generate_key()
    with open(PUBLIC_KEY_FILE, "wb") as f:
        f.write(private_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ))

    message = f"Laboratorium 8: {LOGIN}".encode("utf-8")
    with open("podpis.txt", "wb") as f:
        f.write(message)
    with open("podpis.txt.sig", "wb") as f:
        f.write(private_key.sign(message, PSS, hashes.SHA256()))

    with open(PUBLIC_KEY_FILE, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    with open("podpis.txt", "rb") as f:
        data = f.read()
    with open("podpis.txt.sig", "rb") as f:
        signature = f.read()
    print(f"\nOwn key: RSA {public_key.key_size} bits, signature: {len(signature)} B")
    print(f"podpis.txt: {data!r}")
    print(f"  Verification before change: {status(verify(public_key, data, signature))}")

    changed = bytearray(data)
    changed[0] ^= 0x01
    with open("podpis_zmieniony.txt", "wb") as f:
        f.write(changed)
    print(f"podpis_zmieniony.txt: {bytes(changed)!r}")
    print(f"  Verification after change: {status(verify(public_key, bytes(changed), signature))}")

if __name__ == "__main__":
    main()
