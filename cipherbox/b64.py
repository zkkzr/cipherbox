import base64

NAME = "base64"
DESC = "Base64"
PARAMS = []


def encrypt(text):
    return base64.b64encode(text.encode()).decode()


def decrypt(text):
    return base64.b64decode(text).decode("utf-8", "replace")
