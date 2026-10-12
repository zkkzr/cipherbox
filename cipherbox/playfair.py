import string

from common import is_letter

NAME = "playfair"
DESC = "Playfair (UPPERCASE output, J=I, no spaces)"
PARAMS = [("key", "KEYWORD", "keyword")]
LOSSY = True  # case, spaces and punctuation are lost


def _table(key):
    seen = []
    for c in (key.upper() + string.ascii_uppercase).replace("J", "I"):
        if is_letter(c) and c not in seen:
            seen.append(c)
    return seen


def _pairs(text):
    t = [c for c in text.upper().replace("J", "I") if is_letter(c)]
    pairs, i = [], 0
    while i < len(t):
        a = t[i]
        b = t[i + 1] if i + 1 < len(t) else "X"
        if a == b:
            pairs.append((a, "X")); i += 1
        else:
            pairs.append((a, b)); i += 2
    return pairs


def _crypt(text, key, d):
    tb = _table(key)
    pos = {c: divmod(i, 5) for i, c in enumerate(tb)}
    out = []
    for a, b in _pairs(text):
        (r1, c1), (r2, c2) = pos[a], pos[b]
        if r1 == r2:
            c1, c2 = (c1 + d) % 5, (c2 + d) % 5
        elif c1 == c2:
            r1, r2 = (r1 + d) % 5, (r2 + d) % 5
        else:
            c1, c2 = c2, c1
        out.append(tb[r1 * 5 + c1] + tb[r2 * 5 + c2])
    return "".join(out)


def encrypt(text, key):
    return _crypt(text, key, 1)


def decrypt(text, key):
    return _crypt(text, key, -1)
