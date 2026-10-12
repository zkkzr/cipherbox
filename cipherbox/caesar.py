from common import shift_text

NAME = "caesar"
DESC = "Caesar cipher"
PARAMS = [("shift", "3", "shift amount")]


def encrypt(text, shift):
    return shift_text(text, int(shift))


def decrypt(text, shift):
    return shift_text(text, -int(shift))
