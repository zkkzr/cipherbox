NAME = "base16"
DESC = "Base16 / hex"
PARAMS = []


def encrypt(text):
    return text.encode().hex()


def decrypt(text):
    return bytes.fromhex("".join(text.split())).decode("utf-8", "replace")
