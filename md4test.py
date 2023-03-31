import hashlib
input = bytes.fromhex("0101")
hash = hashlib.new('md4',input).hexdigest()
print(hash)
print(input)