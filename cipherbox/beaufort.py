from common import is_letter, key_nums

NAME = "beaufort"
DESC = "Beaufort cipher (self-inverse)"
PARAMS = [("key", "key", "keyword")]


def encrypt(text, key):
    k, i, out = key_nums(key), 0, []
    for c in text:
        if is_letter(c):
            base = 65 if c.isupper() else 97
            out.append(chr((k[i % len(k)] - (ord(c) - base)) % 26 + base))
            i += 1
        else:
            out.append(c)
    return "".join(out)


decrypt = encrypt  # self-inverse
