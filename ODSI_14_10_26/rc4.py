from collections import Counter
import itertools
import math
import time


def rc4_ksa(key):
  s = list(range(256))
  j = 0
  key_len = len(key)
  for i in range(256):
    j = (j + s[i] + key[i % key_len]) % 256
    s[i], s[j] = s[j], s[i]
  return s


def rc4_prga(s, length):
  s = s.copy()
  i = 0
  j = 0
  stream = bytearray(length)
  for n in range(length):
    i = (i + 1) % 256
    j = (j + s[i]) % 256
    s[i], s[j] = s[j], s[i]
    stream[n] = s[(s[i] + s[j]) % 256]
  return stream


def rc4_crypt(key, data):
  return bytes(
      b1 ^ b2 for b1, b2 in zip(data, rc4_prga(rc4_ksa(key), len(data)))
  )


def calculate_entropy(data):
  if not data:
    return 0.0
  counter = Counter(data)
  length = len(data)
  return -sum((c / length) * math.log2(c / length) for c in counter.values())


def main():
  with open("rc4.bin", "rb") as f:
    ciphertext = f.read()

  start_time = time.time()
  keys = [
      "".join(p) for p in itertools.product("abcdefghijklmnopqrstuvwxyz", repeat=3)
  ]
  sample = ciphertext[: min(512, len(ciphertext))]

  results = sorted(
      [
          (calculate_entropy(rc4_crypt(k.encode(), sample)), k)
          for k in keys
      ],
      key=lambda x: (x[0], x[1]),
  )

  search_time = time.time() - start_time
  total_attempts = len(keys)

  best_key_str = results[0][1]
  best_key_bytes = best_key_str.encode()
  full_decrypted = rc4_crypt(best_key_bytes, ciphertext)

  with open("rc4.txt", "wb") as f:
    f.write(full_decrypted)

  cipher_entropy = calculate_entropy(ciphertext)
  plain_entropy = calculate_entropy(full_decrypted)

  print("=" * 45)
  print("RC4 ANALYSIS REPORT")
  print("=" * 45)
  print(f"Recovered key:              {best_key_str}")
  print(f"Total attempts:             {total_attempts}")
  print(f"Search time:                {search_time:.4f} seconds")
  print(f"Ciphertext entropy:         {cipher_entropy:.4f} bits/byte")
  print(f"Full decrypted entropy:     {plain_entropy:.4f} bits/byte")
  print("Top 5 candidates ranking:")
  for idx, (ent, k) in enumerate(results[:5], 1):
    print(f"  {idx}. Key: '{k}' | Entropy: {ent:.4f}")
  print("=" * 45)


if __name__ == "__main__":
  main()