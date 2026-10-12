"""AES-256-CTR with a password (PBKDF2-HMAC-SHA256).
Use `fernet` if you want integrity checking.
Needs `pip install cryptography`; without it the module is skipped and listed under "not loaded"."""
import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

NAME = "aes"
DESC = "AES-256-CTR, password in key=; wrong password -> garbage, no error"
PARAMS = [("key", "", "password")]


def _derive(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000, 32)


def _ctr(data, key, nonce):  # CTR is symmetric: the same operation encrypts and decrypts
    op = Cipher(algorithms.AES(key), modes.CTR(nonce)).encryptor()
    return op.update(data) + op.finalize()


def _need_password(key):
    if not key:
        raise ValueError("aes needs a password: add key=YOURPASSWORD")


def encrypt(text, key):
    _need_password(key)
    salt, nonce = os.urandom(16), os.urandom(16)
    return base64.b64encode(salt + nonce + _ctr(text.encode(), _derive(key, salt), nonce)).decode()


def decrypt(text, key):
    _need_password(key)
    try:
        raw = base64.b64decode(text)
    except Exception:
        raw = b""
    if len(raw) < 32:
        raise ValueError("input is not valid aes output (corrupted, or not encrypted with aes)")
    salt, nonce, body = raw[:16], raw[16:32], raw[32:]
    return _ctr(body, _derive(key, salt), nonce).decode("utf-8", "replace")
