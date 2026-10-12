"""Template for a new cipher module.

Copy this file to e.g. `mycipher.py` (the name must not start with "_" and must not clash with a
Python module such as base64.py or string.py). cipherbox finds it automatically on the next start;
there is nothing else to register or edit.
"""
NAME = "mycipher"      # the name used in commands:  enc mycipher ...
DESC = "One-line description (shown by `list` and searchable with Ctrl+F)"
PARAMS = [("key", "secret", "what this parameter is")]   # (name, default, hint); use [] for none
# LOSSY = True         # uncomment if decrypting cannot restore the original text exactly


def encrypt(text, key):
    return key + ":" + text[::-1]


def decrypt(text, key):
    if not text.startswith(key + ":"):
        raise ValueError("wrong key")
    return text[len(key) + 1:][::-1]
