NAME = "railfence"
DESC = "Rail fence cipher"
PARAMS = [("rails", "3", "number of rails")]


def _order(length, n):
    if n < 2:
        raise ValueError("rails must be >= 2")
    cycle = 2 * (n - 1)
    rails = [(i % cycle if i % cycle < n else cycle - i % cycle) for i in range(length)]
    return sorted(range(length), key=lambda i: rails[i])


def encrypt(text, rails):
    order = _order(len(text), int(rails))
    return "".join(text[i] for i in order)


def decrypt(text, rails):
    order = _order(len(text), int(rails))
    res = [""] * len(text)
    for j, i in enumerate(order):
        res[i] = text[j]
    return "".join(res)
