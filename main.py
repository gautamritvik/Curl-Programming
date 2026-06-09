import sys
import platform
from importlib.metadata import version as _pkg_version, PackageNotFoundError
from lexer import curl_tokenize
from interpreter import execute
from parser import Parser

try:
    __version__ = _pkg_version("curl-programming-lang")
except PackageNotFoundError:
    __version__ = "dev"


def main():
    if len(sys.argv) < 2:
        repl()
    else:
        run_file(sys.argv[1])


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
    # Enables arrow keys (left/right cursor movement) and
    # up/down history navigation in the REPL prompt.
    try:
        import readline
    except ImportError:
        pass  # Windows — basic input still works, just no arrow keys

    print(f"Curl {__version__} ({platform.system()}) on {sys.platform}")
    print('Type "help" for more information, "exit" to quit.')

    env = {
        "variables": {},
        "functions": {},
        "imports": {},
        "last_input": None,
    }

    buffer = []
    depth = 0            # how many - blocks deep we are
    in_other_coding = False  # inside an otherCoding{} raw block

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
        # Collect lines verbatim until the closing }\ on its own line
        if in_other_coding:
            buffer.append(line)
            if stripped == "}\\":
                in_other_coding = False
                _repl_exec("\n".join(buffer), env)
                buffer = []
            continue

        # ── top-level REPL commands (only when outside all blocks) ─────────
        if depth == 0:
            if stripped in ("exit", "quit", "exit()", "quit()"):
                print("Goodbye!")
                break
            if stripped == "help":
                _repl_help()
                continue
            if stripped == "":
                continue

        buffer.append(line)

        # ── otherCoding opener (no \ at end, special block syntax) ─────────
        if depth == 0 and stripped.startswith("otherCoding"):
            in_other_coding = True
            continue

        # ── block opener: ends with - but not --\ ──────────────────────────
        if stripped.endswith("-") and not stripped.endswith("--\\"):
            depth += 1
            continue

        # ── block closer(s): count --\ on this line ────────────────────────
        closes = stripped.count("--\\")
        if closes:
            depth = max(0, depth - closes)

        # ── execute when back at depth 0 and line ends with \ ──────────────
        if depth == 0 and stripped.endswith("\\"):
            _repl_exec("\n".join(buffer), env)
            buffer = []
            continue

        # ── bad input at depth 0: line didn't end correctly ────────────────
        if depth == 0:
            print(f"  Syntax Error: statement must end with \\")
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
    print("""
Curl — Quick Reference
─────────────────────────────
  pcType{"text"}\\              Print to console
  pcAsk{"prompt?">>}\\          Ask for input (access with input{ans})
  var{name, "value"}\\          Create a variable
  var{name}                    Reference a variable
  list{"a"; "b"; "c"}         Create a list
  createFunc{name}-            Define a function
      ...
  --\\                          End a block
  func{name}\\                  Call a function
  if{var{x} == "y", then}-    Conditional
  import{"math", m}\\           Import a Python package
  otherCoding{"Python",        Embed code in another language
      ...
  }\\
  exit                         Quit the REPL
─────────────────────────────""")


if __name__ == "__main__":
    main()
