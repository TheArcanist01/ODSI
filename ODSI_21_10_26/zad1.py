import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def zadanie_1():
    
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")    
    single_block = b"0123456789ABCDEF"
    plaintext = single_block * 4
    
    print(f"Plain text (hex): {plaintext.hex()}")
    print(f"Input blocks: {len(plaintext) // 16}\n")

    cipher_ecb = Cipher(algorithms.AES(key), modes.ECB())
    encryptor_ecb = cipher_ecb.encryptor()
    ciphertext_ecb = encryptor_ecb.update(plaintext) + encryptor_ecb.finalize()

    iv = os.urandom(16)
    cipher_cbc = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor_cbc = cipher_cbc.encryptor()
    ciphertext_cbc = encryptor_cbc.update(plaintext) + encryptor_cbc.finalize()

    print(f"Generated IV (hex): {iv.hex()}\n")

    blocks_ecb = [ciphertext_ecb[i:i+16] for i in range(0, len(ciphertext_ecb), 16)]
    blocks_cbc = [ciphertext_cbc[i:i+16] for i in range(0, len(ciphertext_cbc), 16)]

    print("ECB:")
    for idx, block in enumerate(blocks_ecb):
        print(f"  Block {idx + 1}: {block.hex()}")

    print("CBC")
    for idx, block in enumerate(blocks_cbc):
        print(f"  Blok {idx + 1}: {block.hex()}")

    all_ecb_equal = all(b == blocks_ecb[0] for b in blocks_ecb)
    print(f"ECB blocks equal? {all_ecb_equal}")

    all_cbc_equal = all(b == blocks_cbc[0] for b in blocks_cbc)
    print(f"CBC blocks equal? {all_cbc_equal}\n")
    
    decryptor_ecb = cipher_ecb.decryptor()
    decrypted_ecb = decryptor_ecb.update(ciphertext_ecb) + decryptor_ecb.finalize()
    
    decryptor_cbc = cipher_cbc.decryptor()
    decrypted_cbc = decryptor_cbc.update(ciphertext_cbc) + decryptor_cbc.finalize()

    print(f"Decrypted ECB == original text? {decrypted_ecb == plaintext}")
    print(f"Decrypted CBC == original text? {decrypted_cbc == plaintext}")

if __name__ == "__main__":
    zadanie_1()