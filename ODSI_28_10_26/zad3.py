import hashlib

VARIANTS = 1 << 13

def read_lines(path):
    with open(path, "rb") as f:
        return f.read().split(b"\n")[:-1]

def variant(lines, v):
    return b"".join(line + (b" " if (v >> i) & 1 else b"") + b"\n" for i, line in enumerate(lines))

def h24(data):
    return hashlib.sha256(data).hexdigest()[:6]

def main():
    original = read_lines("oryginal.txt")
    changed = read_lines("zmieniony.txt")

    first_variant = {}
    all_variants = {}
    for v in range(VARIANTS):
        h = h24(variant(original, v))
        first_variant.setdefault(h, v)
        all_variants.setdefault(h, []).append(v)

    original_h24 = h24(variant(original, 0))
    pair = None
    matching_original = 0
    all_pairs = 0

    for v in range(VARIANTS):
        h = h24(variant(changed, v))
        if pair is None and h in first_variant:
            pair = (first_variant[h], v, h)
        if h == original_h24:
            matching_original += 1
        all_pairs += len(all_variants.get(h, []))

    print(f"Found pair: v_original = {pair[0]}, v_changed = {pair[1]}, h24 = {pair[2]}")
    print(f"h24 of unchanged original: {original_h24}")
    print(f"Changed variants matching unchanged original: {matching_original} / {VARIANTS}")
    print(f"\nAll colliding pairs: {all_pairs}")
    print(f"Expected: {VARIANTS * VARIANTS / 2 ** 24:.1f}")

if __name__ == "__main__":
    main()
