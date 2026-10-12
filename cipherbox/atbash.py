from common import is_letter

NAME = "atbash"
DESC = "Atbash (A<->Z)"
PARAMS = []


def encrypt(text):
    out = []
    for c in text:
        if is_letter(c):
            base = 65 if c.isupper() else 97
            out.append(chr(base + 25 - (ord(c) - base)))
        else:
            out.append(c)
    return "".join(out)


decrypt = encrypt  # self-inverse
