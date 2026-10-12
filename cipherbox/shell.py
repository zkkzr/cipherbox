"""Interactive side of cipherbox: the [cipherbox]# shell, Ctrl+F cipher search and the numbered menu."""
import glob
import os
import shlex
import sys

import help as helptext
from core import (CIPHERS, brute_caesar, canon_param, crypt_files, expand_paths, looks_like_param,
                  read_text_file, run, unknown_param_msg, print_list)

FILE_FLAGS = ("-f", "--file")
OUT_FLAGS = ("-o", "--output")
ALL_FLAGS = ["-f", "-o", "-p", "--force", "--encoding"]


def search_ciphers(query):
    """Cipher names matching every word in the query (name, description or parameter names);
    falls back to fuzzy subsequence matching on the name (e.g. "vgn" -> vigenere)."""
    words = query.lower().split()
    hits = []
    for n, c in CIPHERS.items():
        hay = " ".join([n, c.desc] + [k for k, _, _ in c.params]).lower()
        if all(w in hay for w in words):
            hits.append(n)
    if not hits and words:
        q = "".join(words)

        def subseq(sub, text):
            it = iter(text)
            return all(ch in it for ch in sub)

        hits = [n for n in CIPHERS if subseq(q, n)]
    return hits


def parse_rest(rest, names=()):
    """Parse shell arguments.
    Returns (text, params, None) for plain text or (None, params, file_options) when -f is used."""
    text, params, files = [], {}, []
    out, force, encoding, saw_f, i = None, False, "utf-8", False, 0
    while i < len(rest):
        t = rest[i]
        if t in FILE_FLAGS:
            saw_f = True
            i += 1
            while i < len(rest) and not rest[i].startswith("-") and not looks_like_param(rest[i], names):
                files.append(rest[i]); i += 1
            continue
        if t in OUT_FLAGS and i + 1 < len(rest):
            out = rest[i + 1]; i += 2; continue
        if t == "--force":
            force = True; i += 1; continue
        if t == "--encoding" and i + 1 < len(rest):
            encoding = rest[i + 1]; i += 2; continue
        if t in ("-p", "--param") and i + 1 < len(rest) and "=" in rest[i + 1]:
            k, v = rest[i + 1].split("=", 1)
            ck = canon_param(k, names)
            if ck is None:
                raise ValueError(unknown_param_msg(k, names))
            params[ck] = v; i += 2; continue
        k, sep, v = t.partition("=")
        ck = canon_param(k, names) if sep else None
        if ck:
            params[ck] = v
        else:
            text.append(t)
        i += 1
    if saw_f:
        if not files:
            raise ValueError("-f needs at least one file")
        bad = [t for t in text if looks_like_param(t, names)]
        if bad:
            raise ValueError(unknown_param_msg(bad[0].partition("=")[0], names))
        if text:
            raise ValueError("give either text or -f FILE, not both")
        return None, params, {"files": files, "out": out, "force": force, "encoding": encoding}
    if not text:
        raise ValueError("no text given (pass it directly or use -f FILE)")
    return " ".join(text), params, None


def path_opts(text):
    return sorted(m + (os.sep if os.path.isdir(m) else " ") for m in glob.glob(os.path.expanduser(text) + "*"))


def menu():
    names = list(CIPHERS)
    print("=== cipherbox (local, offline) ===  Ctrl+C to exit")
    while True:
        try:
            print()
            for i, n in enumerate(names, 1):
                print(f"{i:>3}. {n:<10} {CIPHERS[n].desc}")
            print("  b. Caesar brute force")
            ch = input("\nChoice (number/name): ").strip().lower()
            if ch == "b":
                for k, r in brute_caesar(input("Text: ")):
                    print(f"  shift {k:>2}: {r}")
                continue
            name = names[int(ch) - 1] if ch.isdigit() and 1 <= int(ch) <= len(names) else ch
            if name not in CIPHERS:
                print("No such cipher."); continue
            mode = "enc" if input("[e]ncrypt / [d]ecrypt: ").strip().lower().startswith("e") else "dec"
            params = {}
            for k, d, h in CIPHERS[name].params:
                v = input(f"{k} ({h}) [{d}]: ").strip()
                if v:
                    params[k] = v
            print("\n>>>", run(name, mode, input("Text: "), params))
        except (KeyboardInterrupt, EOFError):
            print(); return
        except Exception as e:
            print(f"Error: {e}")


def run_shell():
    try:
        import readline
    except ImportError:  # Windows without pyreadline3
        readline = None
    top = ["list", "enc", "dec", "brute", "search", "menu", "help", "exit", "quit"]
    st = {"search": False, "last": []}   # search-mode flag and the last numbered results
    prefill = {"text": ""}               # text pre-typed at the next prompt (after picking a cipher)

    if readline:
        def completer(text, state):
            try:
                if st["search"]:
                    opts = [n + " " for n in CIPHERS if n.startswith(text)]
                    return opts[state] if state < len(opts) else None
                parts = readline.get_line_buffer().split(" ")
                idx = len(parts) - 1
                opts, is_path = [], False
                if idx == 0:
                    opts = [c + " " for c in top]
                elif parts[0] == "help" and idx == 1:
                    opts = ["modules "]
                elif parts[0] in ("enc", "dec") and idx == 1:
                    opts = [n + " " for n in CIPHERS]
                elif parts[0] in ("enc", "dec", "brute"):
                    cipher = CIPHERS.get(parts[1]) if parts[0] in ("enc", "dec") else None
                    param_opts = [k + "=" for k, _, _ in cipher.params] if cipher else []
                    flag_pos = [j for j, p in enumerate(parts[:-1]) if p in FILE_FLAGS + OUT_FLAGS]
                    if text.startswith("-"):
                        opts = [f + " " for f in ALL_FLAGS]
                    elif flag_pos:
                        j = flag_pos[-1]
                        between = parts[j + 1:-1]
                        if parts[j] in OUT_FLAGS and not between:
                            is_path = True
                        elif parts[j] in FILE_FLAGS and all(not p.startswith("-") and "=" not in p for p in between):
                            is_path = True
                    if is_path:
                        opts = path_opts(text) + [o for o in param_opts if o.startswith(text)]
                    elif not text.startswith("-"):
                        opts = param_opts
                if not is_path:
                    opts = [o for o in opts if o.startswith(text)]
                return opts[state] if state < len(opts) else None
            except Exception:
                return None

        readline.set_completer_delims(" \t\n")
        readline.set_completer(completer)
        readline.parse_and_bind("bind ^I rl_complete" if "libedit" in (readline.__doc__ or "") else "tab: complete")

        # Ctrl+F acts like typing `search` + Enter (GNU readline macro: clear line, type, accept).
        # Note: this replaces readline's default Ctrl+F "move right" (the Right arrow still works).
        try:
            if "libedit" not in (readline.__doc__ or ""):
                readline.parse_and_bind(r'"\C-f": "\C-a\C-ksearch\C-m"')
        except Exception:
            pass

        def _startup_hook():
            if prefill["text"]:
                readline.insert_text(prefill["text"])
                prefill["text"] = ""

        readline.set_startup_hook(_startup_hook)

    # Blue "[cipherbox]" prompt like iwctl's "[iwd]#". Colors only on a real terminal;
    # set NO_COLOR=1 to disable. \001/\002 tell readline the escape codes have zero width.
    color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    if color and os.name == "nt":
        os.system("")  # enables ANSI escape codes in Windows 10+ consoles

    def prompt_for(label):
        if not color:
            return f"[{label}]# "
        o, c = ("\001", "\002") if readline else ("", "")
        return f"{o}\033[1;34m{c}[{label}]{o}\033[0m{c}# "

    def show_results(names):
        st["last"] = names
        w = max(len(n) for n in names)
        for i, n in enumerate(names, 1):
            c = CIPHERS[n]
            ps = ", ".join(f"{k}={d}" for k, d, _ in c.params)
            print(f"  {i:>2}) {n:<{w}}  {c.desc}" + (f"   [{ps}]" if ps else ""))
        print(helptext.SEARCH_FOOTER)

    def pick(name):
        c = CIPHERS[name]
        st["search"], st["last"] = False, []
        hint = " ".join(f"{k}={d}" for k, d, _ in c.params)
        print(f"{name}: {c.desc}")
        print(f"  usage: enc {name} <text>" + (f" {hint}" if hint else "") + "   (or: -f FILE)")
        prefill["text"] = f"enc {name} "

    def handle_search(line):
        low = line.strip().lower()
        if low in ("q", "quit", "exit", "back", "search", "find", "/"):
            st["search"], st["last"] = False, []
            return
        if low.isdigit() and st["last"]:
            i = int(low)
            if 1 <= i <= len(st["last"]):
                pick(st["last"][i - 1])
            else:
                print(f"No result number {i}")
            return
        if low in CIPHERS:
            pick(low)
            return
        names = search_ciphers(low)
        if names:
            show_results(names)
        else:
            st["last"] = []
            print(f"No ciphers match '{line.strip()}'")

    print(helptext.WELCOME)
    while True:
        searching = st["search"]
        try:
            line = input(prompt_for("cipherbox search" if searching else "cipherbox")).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            if searching:  # Ctrl+C / Ctrl+D leaves search mode first
                st["search"], st["last"] = False, []
                continue
            return
        if searching:
            handle_search(line)
            continue
        if not line:
            continue
        try:
            tok = shlex.split(line)
            cmd, rest = tok[0], tok[1:]
            if cmd in ("exit", "quit", "q"):
                return
            elif cmd == "help":
                print(helptext.ADD_MODULE_HELP if rest[:1] == ["modules"] else helptext.SHELL_HELP)
            elif cmd == "list":
                print_list()
            elif cmd == "menu":
                menu()
            elif cmd in ("search", "find"):
                st["search"] = True
                if rest:
                    handle_search(" ".join(rest))
                else:
                    print(helptext.SEARCH_INTRO)
            elif cmd == "brute":
                text, _, fopts = parse_rest(rest)
                if fopts:
                    text = read_text_file(expand_paths(fopts["files"])[0], fopts["encoding"]).rstrip("\n")
                for k, r in brute_caesar(text):
                    print(f"  shift {k:>2}: {r}")
            elif cmd in ("enc", "dec"):
                if not rest:
                    raise ValueError(f"usage: {cmd} <cipher> <text | -f FILE...> [key=val ...]")
                name = rest[0]
                if name not in CIPHERS:
                    raise ValueError(f"unknown cipher: {name} (see `list`)")
                names = [k for k, _, _ in CIPHERS[name].params]
                text, params, fopts = parse_rest(rest[1:], names)
                if fopts:
                    crypt_files(name, cmd, fopts["files"], params, fopts["out"], fopts["force"], fopts["encoding"])
                else:
                    print(run(name, cmd, text, params))
            else:
                print(f"Unknown command: {cmd} (type `help`)")
        except Exception as e:
            print(f"Error: {e}")
