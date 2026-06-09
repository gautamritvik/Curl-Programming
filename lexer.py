import re

KEYWORD = "KEYWORD"
STRING = "STRING"
NUMBER = "NUMBER"
IDENTIFIER = "IDENTIFIER"
PLUS = "PLUS"
MINUS = "MINUS"
TIMES = "TIMES"
DIVIDE = "DIVIDE"
EQ = "EQ"
NEQ = "NEQ"
LT = "LT"
GT = "GT"
LTE = "LTE"
GTE = "GTE"
ASSIGN = "ASSIGN"
DOT = "DOT"
LBRACE = "LBRACE"
RBRACE = "RBRACE"
SEMICOLON = "SEMICOLON"
COMMA = "COMMA"
COLON = "COLON"
ARROW = "ARROW"
LINE_END = "LINE_END"
BLOCK_END = "BLOCK_END"
RAW_CODE = "RAW_CODE"

KEYWORDS = {
    "pcType", "pcAsk", "var", "list", "createFunc", "func",
    "if", "elif", "else", "then", "pcAI", "otherCoding", "import", "input",
    "while", "for"
}

TOKEN_PATTERNS = [
    (BLOCK_END,   r'--\\'),
    (LINE_END,    r'\\'),
    (EQ,          r'=='),
    (NEQ,         r'!='),
    (LTE,         r'<='),
    (GTE,         r'>='),
    (ARROW,       r'>>'),
    (LT,          r'<'),
    (GT,          r'>'),
    (PLUS,        r'\+'),
    (MINUS,       r'-'),
    (TIMES,       r'\*'),
    (DIVIDE,      r'/'),
    (ASSIGN,      r'='),
    (DOT,         r'\.'),
    (LBRACE,      r'\{'),
    (RBRACE,      r'\}'),
    (SEMICOLON,   r';'),
    (COMMA,       r','),
    (COLON,       r':'),
    (STRING,      r'"[^"]*"'),
    (NUMBER,      r'\d+(?:\.\d+)?'),
    (IDENTIFIER,  r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('WHITESPACE', r'\s+'),
]


def curl_tokenize(code):
    tokens = []
    pos = 0

    while pos < len(code):
        # Special handling: otherCoding blocks contain raw code that shouldn't be tokenized
        match = re.match(r'otherCoding\b', code[pos:])
        if match:
            tokens.append((KEYWORD, 'otherCoding'))
            pos += match.end()

            # Skip whitespace, consume '{'
            ws = re.match(r'\s*', code[pos:])
            pos += ws.end()
            if pos >= len(code) or code[pos] != '{':
                raise SyntaxError("Expected '{' after otherCoding")
            tokens.append((LBRACE, '{'))
            pos += 1

            # Skip whitespace, consume language string
            ws = re.match(r'\s*', code[pos:])
            pos += ws.end()
            lang_match = re.match(r'"([^"]*)"', code[pos:])
            if not lang_match:
                raise SyntaxError("Expected language name string in otherCoding")
            tokens.append((STRING, lang_match.group(0)))
            pos += lang_match.end()

            # Skip whitespace, consume ','
            ws = re.match(r'\s*', code[pos:])
            pos += ws.end()
            if pos >= len(code) or code[pos] != ',':
                raise SyntaxError("Expected ',' after language name in otherCoding")
            tokens.append((COMMA, ','))
            pos += 1

            # Capture everything until }\  on its own line
            close_match = re.search(r'\n[ \t]*\}\\', code[pos:])
            if not close_match:
                raise SyntaxError("Unclosed otherCoding block — expected }\\  on its own line")
            raw_code = code[pos:pos + close_match.start()].strip('\n')
            tokens.append((RAW_CODE, raw_code))
            pos += close_match.end()
            tokens.append((LINE_END, '\\'))
            continue

        matched = False
        for token_type, pattern in TOKEN_PATTERNS:
            m = re.match(pattern, code[pos:])
            if m:
                if token_type != 'WHITESPACE':
                    value = m.group()
                    if token_type == IDENTIFIER and value in KEYWORDS:
                        token_type = KEYWORD
                    tokens.append((token_type, value))
                pos += m.end()
                matched = True
                break

        if not matched:
            raise SyntaxError(f"Unknown character: {code[pos]!r} at position {pos}")

    return tokens
