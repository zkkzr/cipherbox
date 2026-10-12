from common import is_letter

NAME = "affine"
DESC = "Affine cipher"
PARAMS = [("a", "5", "multiplier"), ("b", "8", "shift")]


def _crypt(text, a, b, decrypt):
    a, b = int(a), int(b)
    if a % 2 == 0 or a % 13 == 0:
        raise ValueError("a must be coprime with 26 (1,3,5,7,9,11,15,17,19,21,23,25)")
    inv = pow(a, -1, 26)
    out = []
    for c in text:
        if is_letter(c):
            base = 65 if c.isupper() else 97
            x = ord(c) - base
            y = (inv * (x - b)) % 26 if decrypt else (a * x + b) % 26
            out.append(chr(base + y))
        else:
            out.append(c)
    return "".join(out)


def encrypt(text, a, b):
    return _crypt(text, a, b, False)


def decrypt(text, a, b):
    return _crypt(text, a, b, True)
