import math
from collections import Counter
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

def calculate_entropy(data):
    if not data:
        return 0.0
    length = len(data)
    entropy = 0.0
    counts = Counter(data)
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def main():
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    keys = [(char, (char * 16).encode('ascii')) for char in alphabet]
    
    with open("slaby_ecb.bin", "rb") as f:
        ciphertext = f.read()
        
    sample = ciphertext[:min(4096, len(ciphertext))]
    results = []
    
    for char, key in keys:
        cipher = Cipher(algorithms.AES(key), modes.ECB())
        decryptor = cipher.decryptor()
        decrypted_sample = decryptor.update(sample) + decryptor.finalize()
        entropy = calculate_entropy(decrypted_sample)
        results.append((char, entropy, key))
        
    results.sort(key=lambda x: x[1])
    
    print("Top 5 candidates:")
    for i in range(min(5, len(results))):
        print(f"Rank {i+1}: Char '{results[i][0]}', Entropy: {results[i][1]:.4f}")
        
    best_char, best_entropy, best_key = results[0]
    print(f"\nBest key character: '{best_char}'")
    
    cipher_best = Cipher(algorithms.AES(best_key), modes.ECB())
    decryptor_best = cipher_best.decryptor()
    full_padded = decryptor_best.update(ciphertext) + decryptor_best.finalize()
    
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(full_padded) + unpadder.finalize()
    
    first_line = plaintext.split(b'\n')[0].decode('utf-8', errors='ignore')
    print(f"First line: {first_line}")

if __name__ == "__main__":
    main()