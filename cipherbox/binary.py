NAME = "binary"
DESC = "Binary (8 bits per byte)"
PARAMS = []


def encrypt(text):
    return " ".join(f"{b:08b}" for b in text.encode())


def decrypt(text):
    return bytes(int(x, 2) for x in text.split()).decode("utf-8", "replace")
