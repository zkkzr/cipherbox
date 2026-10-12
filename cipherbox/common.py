"""Helpers shared by the classical-cipher modules (not a cipher itself)."""


def is_letter(c):
    return c.isascii() and c.isalpha()


def shift_text(text, k):
    """Shift Latin letters by k positions, keeping case; everything else is left alone."""
    out = []
    for c in text:
        if is_letter(c):
            base = 65 if c.isupper() else 97
            out.append(chr((ord(c) - base + k) % 26 + base))
        else:
            out.append(c)
    return "".join(out)


def key_nums(key):
    """Letters of a keyword as numbers 0-25."""
    nums = [ord(c.lower()) - 97 for c in key if is_letter(c)]
    if not nums:
        raise ValueError("key must contain Latin letters")
    return nums
