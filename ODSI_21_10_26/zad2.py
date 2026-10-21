import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200000,
    )
    return kdf.derive(password)

def encrypt(plaintext, password):
    salt = os.urandom(16)
    iv = os.urandom(16)
    key = derive_key(password, salt)
    
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    
    return salt, iv, ciphertext

def decrypt(salt, iv, ciphertext, password):
    key = derive_key(password, salt)
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()
    
    return plaintext

if __name__ == "__main__":
    password = b"ExamplePassword"
        
    tests = {
        "Empty data (0 B)": b"",
        "Exactly 16B": b"0123456789ABCDEF",
        "wiadomosc.txt": open("wiadomosc.txt", "rb").read()
    }
    
    for name, data in tests.items():
        salt, iv, ct = encrypt(data, password)
        dt = decrypt(salt, iv, ct, password)
        print(f"Test: {name}")
        print(f"  Length: {len(ct)} B")
        print(f"  Bytes identical before encryption and after decryption: {data == dt}")
        
    salt1, iv1, ct1 = encrypt(tests["Exactly 16B"], password)
    salt2, iv2, ct2 = encrypt(tests["Exactly 16B"], password)
    print("\nNew salt and IV:")
    print(f"  Salt 1 == Salt 2: {salt1 == salt2}")
    print(f"  IV 1 == IV 2: {iv1 == iv2}")
    print(f"  Ciphertext 1 == Ciphertext 2: {ct1 == ct2}")