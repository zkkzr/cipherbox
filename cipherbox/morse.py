NAME = "morse"
DESC = "Morse code (Latin letters; word separator = /)"
PARAMS = []
LOSSY = True  # case is lost, unknown characters become "?"

MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....",
    "I": "..", "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.",
    "Q": "--.-", "R": ".-.", "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "!": "-.-.--", "/": "-..-.", ":": "---...",
}
REVERSE = {v: k for k, v in MORSE.items()}


def encrypt(text):
    return " ".join("/" if c == " " else MORSE.get(c.upper(), "?") for c in text)


def decrypt(text):
    return "".join(" " if w == "/" else REVERSE.get(w, "?") for w in text.split())
