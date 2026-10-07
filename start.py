from hashlib import sha256

teksty = ["Ala ma kota", "Ala ma kota!"]
for tekst in teksty:
	skrot = sha256(tekst.encode("utf-8")).hexdigest()
	print(tekst)
	print(skrot)
