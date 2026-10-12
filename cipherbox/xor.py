NAME = "xor"
DESC = "XOR with a key (hex output)"
PARAMS = [("key", "key", "key")]


def _xor(data, key):
    kb = key.encode()
    if not kb:
        raise ValueError("empty key")
    return bytes(b ^ kb[i % len(kb)] for i, b in enumerate(data))


def encrypt(text, key):
    return _xor(text.encode(), key).hex()


def decrypt(text, key):
    return _xor(bytes.fromhex("".join(text.split())), key).decode("utf-8", "replace")
