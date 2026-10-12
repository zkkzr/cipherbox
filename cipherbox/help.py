"""All user-facing help text for cipherbox."""

WELCOME = "cipherbox - type `help` for help, Tab to autocomplete, Ctrl+F (or `search`) to find a cipher, `exit` to quit"

CLI_DESCRIPTION = "cipherbox - a local, offline collection of ciphers and encodings"

CLI_EPILOG = """\
examples:
  cipherbox.py                              interactive shell ([cipherbox]#); Ctrl+F or `search` finds a cipher
  cipherbox.py list
  cipherbox.py enc caesar "Hello" -p shift=5
  cipherbox.py dec vigenere "Rijvs" -p key=abc
  cipherbox.py brute "Khoor Zruog"          try every Caesar shift
  echo "secret" | cipherbox.py enc base64
  cipherbox.py enc base64 -f notes.txt      -> notes.enc.txt
  cipherbox.py dec base64 -f notes.enc.txt  -> notes.dec.txt
  cipherbox.py enc aes -f a.md b.txt key=secret
  cipherbox.py enc xor -f "*.md" key=secret

file options: -o OUT ("-" prints to the screen), --force, --encoding cp1251
Any UTF-8 text file works (.txt .md .csv .json .py ...); binary files are refused.
Add your own cipher: drop a module into this folder (see _template.py, or `help modules` in the shell).
"""

SHELL_HELP = """Commands:
  list                                   list ciphers and their parameters
  enc <cipher> <text> [key=val ...]      encrypt text
  dec <cipher> <text> [key=val ...]      decrypt text
  enc|dec <cipher> -f FILE... [options]  encrypt/decrypt text files (globs like *.md work)
  brute <text>                           try every Caesar shift
  search [query]                         find a cipher by name/description (or press Ctrl+F)
  menu                                   numbered menu
  help [modules] | exit

File options:
  -o OUT          output path ("-" prints to the screen); single input file only
  --force         overwrite existing output files
  --encoding ENC  file encoding (default utf-8; e.g. cp1251, utf-16)
  Default output: notes.txt -> notes.enc.txt (enc) or notes.dec.txt (dec).
  Originals are left untouched. Works with any UTF-8 text file (.txt .md .csv .json ...).

Examples:
  enc caesar "Hello World" shift=5
  dec vigenere Rijvs key=abc
  enc base64 -f notes.txt
  enc xor -f *.md key=secret
  enc aes -f notes.txt key=mypassword
  dec xor -f notes.enc.txt -o restored.txt key=secret

aes vs fernet (both take the password in key=; password= also works):
  aes     no integrity check: a wrong password prints garbage, never an error
  fernet  authenticated: a wrong password or modified data is reported as an error

Quote text that contains spaces. Tab completes commands, ciphers, parameters and file names."""

ADD_MODULE_HELP = """Adding a cipher:
  1. Copy _template.py to a new file in the cipherbox folder, e.g. mycipher.py
     (never name it like a Python module, e.g. base64.py or string.py - that breaks imports)
  2. Set NAME, DESC, PARAMS and write encrypt(text, ...) / decrypt(text, ...)
  3. Restart cipherbox - the module is picked up automatically (check with `list`)

Files starting with "_" are ignored. cipherbox.py, core.py, shell.py, help.py and common.py
are not ciphers. A module that needs a missing Python package is skipped and shown under
"not loaded" in `list`."""

SEARCH_INTRO = "Search: type part of a cipher name or description (e.g. vig, base, key). Empty = list all, q = back."

SEARCH_FOOTER = "  number = select, new text = refine, empty = list all, q = back"
