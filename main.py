import sys
from lexer import curl_tokenize
from parser import Parser
from interpreter import execute


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <file.curl>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found — '{file_path}'")
        sys.exit(1)

    tokens = curl_tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    execute(ast)

    print("\n{You were using Curl 1.0.0 \U0001f609}")


if __name__ == "__main__":
    try:
        main()
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
else:
    print("FATAL: __name__ does not equal '__main__' — cannot start Curl.")
