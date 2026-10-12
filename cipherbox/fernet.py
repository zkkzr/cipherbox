"""Fernet (AES-128-CBC + HMAC-SHA256). Authenticated: wrong password / modified data -> error.
Needs `pip install cryptography`; without it the module is skipped and listed under "not loaded"."""
import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken

NAME = "fernet"
DESC = "AES-128-CBC + HMAC (Fernet), password in key=; wrong password -> error"
PARAMS = [("key", "", "password")]


def _fkey(password, salt):
    return base64.urlsafe_b64encode(hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000, 32))


def encrypt(text, key):
    if not key:
        raise ValueError("fernet needs a password: add key=YOURPASSWORD")
    salt = os.urandom(16)
    token = Fernet(_fkey(key, salt)).encrypt(text.encode())
    return base64.urlsafe_b64encode(salt + token).decode()


def decrypt(text, key):
    # An empty password is accepted here on purpose: earlier cipherbox versions silently ignored
    # key= for fernet and encrypted with an EMPTY password, and those files must stay readable.
    try:
        raw = base64.urlsafe_b64decode(text.strip())
    except Exception:
        raw = b""
    if len(raw) < 17:
        raise ValueError("input is not valid fernet output (corrupted, or not encrypted with fernet)")
    try:
        return Fernet(_fkey(key, raw[:16])).decrypt(raw[16:]).decode()
    except InvalidToken:
        hint = ("no password given - add key=YOURPASSWORD" if not key else
                "files made by an older cipherbox without a working key= used an EMPTY password: retry without key=")
        raise ValueError(f"authentication failed: wrong password, or the data was modified/corrupted. {hint}. "
                         "(The `aes` cipher prints garbage instead of an error.)")
