import sys
import platform
import argparse
from importlib.metadata import version as _pkg_version, PackageNotFoundError
from lexer import curl_tokenize
from interpreter import execute
from parser import Parser

try:
    __version__ = _pkg_version("curl-programming-lang")
except PackageNotFoundError:
    __version__ = "dev"

_COPYRIGHT = f"Copyright (c) 2024-2026 Ritvik Gautam. All rights reserved."

_LICENSE = """\
Curl is distributed under the Apache License, Version 2.0.

You may obtain a copy of the License at:
    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

Full license: https://github.com/gautamritvik/Curl-Programming/blob/main/LICENSE"""

_CREDITS = """\
Curl Programming Language
  Created by Ritvik Gautam
  Built on Python technology
  Source: https://github.com/gautamritvik/Curl-Programming
  PyPI:   https://pypi.org/project/curl-programming-lang/"""


def main():
    parser = argparse.ArgumentParser(
        prog="curlang",
        description="Curl programming language interpreter",
        add_help=False,
    )
    parser.add_argument("file", nargs="?", help="Curl source file to run (.curl)")
    parser.add_argument("-c", metavar="cmd", help="Run a single Curl statement")
    parser.add_argument("-V", "--version", action="store_true", help="Show version and exit")
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")
    parser.add_argument("--license", action="store_true", help="Show license information and exit")
    parser.add_argument("--copyright", action="store_true", help="Show copyright notice and exit")
    parser.add_argument("--credits", action="store_true", help="Show credits and exit")

    args = parser.parse_args()

    if args.version:
        print(f"Curl {__version__}")
        return

    if args.help:
        print(f"Curl {__version__} — command-line options\n")
        parser.print_help()
        return

    if args.license:
        print(_LICENSE)
        return

    if args.copyright:
        print(_COPYRIGHT)
        return

    if args.credits:
        print(_CREDITS)
        return

    if args.c:
        _run_code(args.c)
    elif args.file:
        run_file(args.file)
    else:
        repl()


def _run_code(code):
    try:
        tokens = curl_tokenize(code)
        ast = Parser(tokens).parse()
        execute(ast)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)
    except NameError as e:
        print(f"Name Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_file(file_path):
    try:
        with open(file_path, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found — '{file_path}'")
        sys.exit(1)

    try:
        tokens = curl_tokenize(code)
        ast = Parser(tokens).parse()
        execute(ast)
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
        print(f"{{You cut off Curl {__version__} while it was trying to work! \U0001f61e}}")
        sys.exit(1)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)
    except NameError as e:
        print(f"Name Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"\n{{You were using Curl {__version__} \U0001f609}}")


def repl():
    try:
        import readline
    except ImportError:
        pass  # Windows — basic input still works, just no arrow keys

    print(f"Curl {__version__} ({platform.system()}) on {sys.platform}")
    print('Type "help", "copyright", "credits" or "license" for more information.')

    env = {
        "variables": {},
        "functions": {},
        "imports": {},
        "last_input": None,
    }

    buffer = []
    depth = 0
    in_other_coding = False

    while True:
        try:
            prompt = "... " if (depth > 0 or in_other_coding) else ">>> "
            line = input(prompt)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            buffer = []
            depth = 0
            in_other_coding = False
            continue

        stripped = line.strip()

        # ── otherCoding raw-code mode ──────────────────────────────────────
        if in_other_coding:
            buffer.append(line)
            if stripped == "}\\":
                in_other_coding = False
                _repl_exec("\n".join(buffer), env)
                buffer = []
            continue

        # ── top-level REPL commands ────────────────────────────────────────
        if depth == 0:
            if stripped in ("exit", "quit", "exit()", "quit()"):
                print("Goodbye!")
                break
            if stripped == "help":
                _repl_help()
                continue
            if stripped == "license":
                print(_LICENSE)
                continue
            if stripped == "copyright":
                print(_COPYRIGHT)
                continue
            if stripped == "credits":
                print(_CREDITS)
                continue
            if stripped in ("version", "__version__"):
                print(f"Curl {__version__}")
                continue
            if stripped == "":
                continue

        buffer.append(line)

        # ── otherCoding opener ─────────────────────────────────────────────
        if depth == 0 and stripped.startswith("otherCoding"):
            in_other_coding = True
            continue

        # ── block opener: ends with - but not --\ ──────────────────────────
        if stripped.endswith("-") and not stripped.endswith("--\\"):
            depth += 1
            continue

        # ── block closer(s) ────────────────────────────────────────────────
        closes = stripped.count("--\\")
        if closes:
            depth = max(0, depth - closes)

        # ── execute when back at depth 0 and line ends with \ ──────────────
        if depth == 0 and stripped.endswith("\\"):
            _repl_exec("\n".join(buffer), env)
            buffer = []
            continue

        # ── bad input at depth 0 ───────────────────────────────────────────
        if depth == 0:
            print("  Syntax Error: statement must end with \\")
            buffer = []


def _repl_exec(code, env):
    try:
        tokens = curl_tokenize(code)
        ast = Parser(tokens).parse()
        execute(ast, env)
    except SyntaxError as e:
        print(f"  Syntax Error: {e}")
    except NameError as e:
        print(f"  Name Error: {e}")
    except RuntimeError as e:
        print(f"  Runtime Error: {e}")
    except Exception as e:
        print(f"  Error: {e}")


def _repl_help():
    print(f"""
Curl {__version__} — Quick Reference
─────────────────────────────────────
Language syntax:
  pcType{{"text"}}\\              Print to console
  pcAsk{{"prompt?">>}}\\          Ask for input  →  input{{ans}}
  var{{name, "value"}}\\          Assign a variable
  var{{name}}                    Reference a variable
  list{{"a"; "b"; "c"}}         Create a list
  createFunc{{name}}-            Define a function
      ...
  --\\                           End a block
  func{{name}}\\                  Call a function
  if{{var{{x}} == "y", then}}-   Conditional (elif / else supported)
  import{{"math", m}}\\           Import a Python package
  otherCoding{{"Python",         Embed code in another language
      ...
  }}\\

REPL commands:
  help          Show this message
  license       Show license information
  copyright     Show copyright notice
  credits       Show credits
  version       Show version
  exit / quit   Leave the REPL
─────────────────────────────────────""")


if __name__ == "__main__":
    main()
