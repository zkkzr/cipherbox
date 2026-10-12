NAME = "reverse"
DESC = "Reverse the string"
PARAMS = []


def encrypt(text):
    return text[::-1]


decrypt = encrypt  # self-inverse
