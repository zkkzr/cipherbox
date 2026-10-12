from common import is_letter, key_nums

NAME = "vigenere"
DESC = "Vigenere cipher"
PARAMS = [("key", "key", "keyword")]


def _crypt(text, key, sign):
    k, i, out = key_nums(key), 0, []
    for c in text:
        if is_letter(c):
            base = 65 if c.isupper() else 97
            out.append(chr((ord(c) - base + sign * k[i % len(k)]) % 26 + base))
            i += 1
        else:
            out.append(c)
    return "".join(out)


def encrypt(text, key):
    return _crypt(text, key, 1)


def decrypt(text, key):
    return _crypt(text, key, -1)
