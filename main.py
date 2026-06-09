import sys
import platform
from lexer import curl_tokenize
from interpreter import execute
from parser import Parser


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
        print("{You cut off Curl 1.0.0 while it was trying to work! \U0001f61e}")
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

    print("\n{You were using Curl 1.0.0 \U0001f609}")


def repl():
    print(f"Curl 1.0.0 ({platform.system()}) on {sys.platform}")
    print('Type "help" for more information, "exit" to quit.')

    env = {
        "variables": {},
        "functions": {},
        "imports": {},
        "last_input": None,
    }

    buffer = []
    depth = 0  # tracks how many blocks deep we are

    while True:
        try:
            prompt = "... " if depth > 0 else ">>> "
            line = input(prompt)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            buffer = []
            depth = 0
            continue

        stripped = line.strip()

        # Top-level commands
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

        # A line ending with - (but not --\) opens a new block
        if stripped.endswith("-") and not stripped.endswith("--\\"):
            depth += 1

        # Count how many --\ block-closers are on this line
        closes = stripped.count("--\\")
        if closes:
            depth = max(0, depth - closes)

        # Execute when depth returns to 0 and line ends with \ (includes --\)
        if depth == 0 and stripped.endswith("\\"):
            code = "\n".join(buffer)
            buffer = []
            _repl_exec(code, env)


def _repl_exec(code, env):
    try:
        tokens = curl_tokenize(code)
        ast = Parser(tokens).parse()
        execute(ast, env)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except NameError as e:
        print(f"Name Error: {e}")
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def _repl_help():
    print("""
Curl 1.0.0 — Quick Reference
─────────────────────────────
  pcType{"text"}\              Print to console
  pcAsk{"prompt?">>}\          Ask for input (access with input{ans})
  var{name, "value"}\          Create a variable
  var{name}\                   Reference a variable
  list{"a"; "b"; "c"}         Create a list
  createFunc{name}-            Define a function
      ...
  --\\                          End a block
  func{name}\                  Call a function
  if{var{x} == "y", then}-    Conditional
  import{"math", m}\           Import a Python package
  otherCoding{"Python",        Run code in another language
      ...
  }\\
  exit                         Quit the REPL
─────────────────────────────""")


if __name__ == "__main__":
    main()
