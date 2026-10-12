NAME = "rot47"
DESC = "ROT47 (printable ASCII)"
PARAMS = []


def encrypt(text):
    return "".join(chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c for c in text)


decrypt = encrypt  # self-inverse
