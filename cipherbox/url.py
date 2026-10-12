import urllib.parse

NAME = "url"
DESC = "URL encoding"
PARAMS = []


def encrypt(text):
    return urllib.parse.quote(text, safe="")


def decrypt(text):
    return urllib.parse.unquote(text)
