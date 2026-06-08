class CurlError(Exception):
    pass

class CurlSyntaxError(CurlError):
    def __init__(self, message, line=None, char=None):
        self.message = message
        self.line = line
        self.char = char

    def __str__(self):
        location = f" at line {self.line}, char {self.char}" if self.line and self.char else ""
        return f"SyntaxError{location}: {self.message}"

class CurlNameError(CurlError):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"NameError: {self.message}"

class CurlTypeError(CurlError):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"TypeError: {self.message}"
