from common import is_letter

NAME = "a1z26"
DESC = "A1Z26 (A=1 ... Z=26)"
PARAMS = []
LOSSY = True  # case is lost


def encrypt(text):
    return " ".join(str(ord(c.lower()) - 96) if is_letter(c) else ("/" if c == " " else c) for c in text)


def decrypt(text):
    out = []
    for w in text.split():
        out.append(" " if w == "/" else chr(96 + int(w)) if w.isdigit() and 1 <= int(w) <= 26 else w)
    return "".join(out)
