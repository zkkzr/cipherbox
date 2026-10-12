#!/usr/bin/env python3
"""cipherbox - entry point. The work is done by core.py; every cipher lives in its own module."""
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))  # realpath: also works through a symlink
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from core import main  # noqa: E402

if __name__ == "__main__":
    main()
