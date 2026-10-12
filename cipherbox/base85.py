import base64

NAME = "base85"
DESC = "Base85"
PARAMS = []


def encrypt(text):
    return base64.b85encode(text.encode()).decode()


def decrypt(text):
    return base64.b85decode(text).decode("utf-8", "replace")
