"""cipherbox core: finds the cipher modules, parses parameters, handles text files and the CLI.

A cipher is any module in this folder that defines NAME, encrypt() and decrypt()
(optional: DESC, PARAMS, LOSSY). Files starting with "_" and the reserved modules below are skipped.
"""
import argparse
import codecs
import glob
import importlib
import os
import pkgutil
import re
import sys

import help as helptext
from common import shift_text

HERE = os.path.dirname(os.path.realpath(__file__))
RESERVED = {"cipherbox", "core", "shell", "help", "common"}

CIPHERS = {}   # name -> Cipher
SKIPPED = {}   # module name -> why it was not loaded


class Cipher:
    def __init__(self, name, desc, params, enc, dec, lossy=False):
        self.name, self.desc, self.params = name, desc, params
        self.enc, self.dec, self.lossy = enc, dec, lossy


# ───────────────────────── Module loader ─────────────────────────
def load_ciphers(directory=HERE):
    """Import every cipher module in `directory`. Broken or dependency-less modules are skipped, not fatal."""
    if CIPHERS or SKIPPED:
        return
    if directory not in sys.path:
        sys.path.insert(0, directory)
    for info in sorted(pkgutil.iter_modules([directory]), key=lambda m: m.name):
        mod_name = info.name
        if mod_name.startswith("_") or mod_name in RESERVED:
            continue
        try:
            mod = importlib.import_module(mod_name)
        except ImportError as e:
            dep = (getattr(e, "name", None) or "").split(".")[0]
            SKIPPED[mod_name] = (f"needs the Python package '{dep}' (pip install {dep})"
                                 if dep and dep != mod_name else f"import error: {e}")
            continue
        except Exception as e:
            SKIPPED[mod_name] = f"failed to load: {e}"
            continue
        if not all(hasattr(mod, a) for a in ("NAME", "encrypt", "decrypt")):
            continue  # a helper module, not a cipher
        CIPHERS[mod.NAME] = Cipher(mod.NAME, getattr(mod, "DESC", ""), list(getattr(mod, "PARAMS", [])),
                                   mod.encrypt, mod.decrypt, bool(getattr(mod, "LOSSY", False)))
    items = sorted(CIPHERS.items())  # list in alphabetical order by cipher name, not by file name
    CIPHERS.clear()
    CIPHERS.update(items)


# ───────────────────────── Parameters ─────────────────────────
PARAM_ALIASES = {"password": "key", "pass": "key", "passwd": "key", "pw": "key"}
IDENT = re.compile(r"[A-Za-z_]\w*")


def canon_param(name, names):
    """Map a typed parameter name onto one this cipher really has (password= -> key=)."""
    if name in names:
        return name
    alias = PARAM_ALIASES.get(name)
    return alias if alias in names else None


def unknown_param_msg(k, names):
    valid = ", ".join(names) if names else "this cipher takes no parameters"
    return f"unknown parameter '{k}' (valid: {valid})"


def looks_like_param(tok, names):
    """key=value that is a known parameter, or an unknown one (likely a typo) rather than a real file."""
    k, sep, _ = tok.partition("=")
    return bool(sep) and bool(IDENT.fullmatch(k)) and (canon_param(k, names) is not None or not os.path.exists(tok))


def run(name, mode, text, params):
    if name not in CIPHERS:
        raise ValueError(f"unknown cipher: {name} (see `list`)")
    c = CIPHERS[name]
    names = [k for k, _, _ in c.params]
    fixed = {}
    for k, v in params.items():
        ck = canon_param(k, names)
        if ck is None:
            raise ValueError(unknown_param_msg(k, names))
        fixed[ck] = v
    kw = {k: fixed.get(k, d) for k, d, _ in c.params}
    return (c.enc if mode == "enc" else c.dec)(text, **kw)


def brute_caesar(text):
    return [(k, shift_text(text, -k)) for k in range(1, 26)]


def print_list():
    w = max((len(n) for n in list(CIPHERS) + list(SKIPPED)), default=0)
    for n, c in CIPHERS.items():
        ps = ", ".join(f"{k}={d}" for k, d, _ in c.params)
        print(f"  {n:<{w}}  {c.desc}" + (f"   [{ps}]" if ps else ""))
    if SKIPPED:
        print("\nnot loaded:")
        for m, why in SKIPPED.items():
            print(f"  {m:<{w}}  {why}")


# ───────────────────────── Text files ─────────────────────────
def read_input(args):
    if args.text is not None:
        return args.text
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            return f.read().rstrip("\n")
    if not sys.stdin.isatty():
        return sys.stdin.read().rstrip("\n")
    sys.exit("No input text: pass it as an argument, use -f FILE, or pipe it via stdin")


def expand_paths(paths):
    """Expand globs ourselves so *.md also works on Windows shells."""
    out = []
    for p in paths:
        if any(ch in p for ch in "*?["):
            matches = sorted(glob.glob(p))
            if not matches:
                raise ValueError(f"no files match: {p}")
            out.extend(matches)
        else:
            out.append(p)
    return out


def read_text_file(path, encoding="utf-8"):
    """Read a text file exactly (line endings preserved). Refuses binary files."""
    if os.path.isdir(path):
        raise ValueError(f"{path}: is a directory (pass files, or a glob like {path}/*.txt)")
    if not os.path.isfile(path):
        raise ValueError(f"{path}: no such file")
    with open(path, "rb") as f:
        data = f.read()
    if b"\x00" in data and not encoding.lower().replace("_", "-").startswith("utf-16"):
        raise ValueError(f"{path}: looks like a binary file, not text")
    codec = "utf-8-sig" if encoding.lower().replace("_", "-") in ("utf-8", "utf8") else encoding  # drops a BOM
    try:
        return data.decode(codec)
    except UnicodeDecodeError:
        raise ValueError(f"{path}: not valid {encoding} text (try --encoding cp1251, utf-16, ...)")


def default_out(path, mode):
    """notes.txt -> notes.enc.txt / notes.dec.txt ; notes.enc.txt -> notes.dec.txt"""
    base, ext = os.path.splitext(path)
    if mode == "dec" and base.endswith(".enc"):
        base = base[:-4]
    return f"{base}.{mode}{ext}"


def crypt_files(name, mode, files, params, out=None, force=False, encoding="utf-8"):
    """Encrypt/decrypt text files. Returns the number of files that failed."""
    try:
        codecs.lookup(encoding)
    except LookupError:
        raise ValueError(f"unknown encoding: {encoding}")
    if name not in CIPHERS:
        raise ValueError(f"unknown cipher: {name} (see `list`)")
    lossy = CIPHERS[name].lossy
    files = expand_paths(files)
    if out not in (None, "-") and len(files) > 1:
        raise ValueError("-o works with a single input file only")
    if lossy and mode == "enc":
        print(f"note: {name} is lossy - the original text cannot be fully restored", file=sys.stderr)
    failed = 0
    for path in files:
        try:
            text = read_text_file(path, encoding)
            try:
                result = run(name, mode, text, params)
            except Exception:
                if mode == "dec" and text != text.strip():  # e.g. an editor added a trailing newline
                    result = run(name, mode, text.strip(), params)
                else:
                    raise
            if out == "-":
                print(result)
                continue
            dest = out or default_out(path, mode)
            if lossy and mode == "enc" and os.path.abspath(dest) == os.path.abspath(path):
                raise ValueError("refusing to overwrite the original with a lossy cipher")
            if os.path.exists(dest) and not force:
                raise ValueError(f"{dest} already exists (use --force to overwrite)")
            with open(dest, "wb") as f:
                f.write(result.encode(encoding))
            print(f"{path} -> {dest}")
        except Exception as e:
            failed += 1
            print(f"Error: {e}" if str(e).startswith(path) else f"Error: {path}: {e}", file=sys.stderr)
    return failed


# ───────────────────────── Command line ─────────────────────────
def main(argv=None):
    load_ciphers()
    ap = argparse.ArgumentParser(prog="cipherbox", description=helptext.CLI_DESCRIPTION,
                                 epilog=helptext.CLI_EPILOG,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("list", help="list ciphers")
    sub.add_parser("menu", help="numbered menu")
    sub.add_parser("shell", help="interactive shell (default)")
    for m, h in (("enc", "encrypt"), ("dec", "decrypt")):
        p = sub.add_parser(m, help=h)
        p.add_argument("cipher")
        p.add_argument("text", nargs="?")
        p.add_argument("-f", "--file", nargs="+", metavar="FILE", help="text file(s) to process; globs allowed")
        p.add_argument("-o", "--output", metavar="OUT", help='output path ("-" prints to screen); single file only')
        p.add_argument("--force", action="store_true", help="overwrite existing output files")
        p.add_argument("--encoding", default="utf-8", help="file encoding (default: utf-8)")
        p.add_argument("-p", "--param", action="append", default=[], metavar="KEY=VALUE")
    b = sub.add_parser("brute", help="try every Caesar shift")
    b.add_argument("text", nargs="?")
    b.add_argument("-f", "--file")
    args, extra = ap.parse_known_args(argv)
    # allow `enc aes "text" key=secret` (key=value without -p), like in the shell
    stray = [t for t in extra if t.startswith("-") or "=" not in t]
    if stray:
        ap.error("unrecognized arguments: " + " ".join(stray))

    try:
        if args.cmd in (None, "shell"):
            import shell
            shell.run_shell()
        elif args.cmd == "menu":
            import shell
            shell.menu()
        elif args.cmd == "list":
            print_list()
        elif args.cmd == "brute":
            for k, r in brute_caesar(read_input(args)):
                print(f"shift {k:>2}: {r}")
        else:
            params = dict(p.split("=", 1) for p in list(getattr(args, "param", [])) + extra if "=" in p)
            if args.file:
                if args.text is not None:
                    raise ValueError("give either TEXT or -f FILE, not both")
                if args.cipher not in CIPHERS:
                    raise ValueError(f"unknown cipher: {args.cipher} (see `list`)")
                names = [k for k, _, _ in CIPHERS[args.cipher].params]
                files = []
                for tok in args.file:  # `-f` takes many values, so also accept key=value among them
                    if looks_like_param(tok, names):
                        k, v = tok.split("=", 1)
                        ck = canon_param(k, names)
                        if ck is None:
                            raise ValueError(unknown_param_msg(k, names))
                        params[ck] = v
                    else:
                        files.append(tok)
                if not files:
                    raise ValueError("no input files given")
                if crypt_files(args.cipher, args.cmd, files, params, args.output, args.force, args.encoding):
                    sys.exit(1)
            else:
                print(run(args.cipher, args.cmd, read_input(args), params))
    except Exception as e:
        sys.exit(f"Error: {e}")
