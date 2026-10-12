from common import shift_text

NAME = "rot13"
DESC = "ROT13"
PARAMS = []


def encrypt(text):
    return shift_text(text, 13)


decrypt = encrypt  # self-inverse
