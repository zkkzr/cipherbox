import base64

NAME = "base32"
DESC = "Base32"
PARAMS = []


def encrypt(text):
    return base64.b32encode(text.encode()).decode()


def decrypt(text):
    return base64.b32decode(text).decode("utf-8", "replace")
