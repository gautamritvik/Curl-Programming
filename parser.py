from lexer import (
    KEYWORD, STRING, NUMBER, IDENTIFIER,
    PLUS, MINUS, TIMES, DIVIDE,
    EQ, NEQ, LT, GT, LTE, GTE,
    LBRACE, RBRACE, SEMICOLON, COMMA, COLON, ARROW, DOT,
    LINE_END, BLOCK_END, RAW_CODE
)

COMPARISON_OPS = {EQ, NEQ, LT, GT, LTE, GTE}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def consume(self, token_type, value=None):
        token = self.current()
        if token is None:
            expected = f"{token_type}" + (f" '{value}'" if value else "")
            raise SyntaxError(f"Unexpected end of input — expected {expected}")
        if token[0] != token_type:
            raise SyntaxError(f"Expected {token_type}{' ' + repr(value) if value else ''}, got {token[0]} {repr(token[1])}")
        if value is not None and token[1] != value:
            raise SyntaxError(f"Expected keyword '{value}', got '{token[1]}'")
        self.pos += 1
        return token

    def check(self, token_type, value=None):
        token = self.current()
        if not token:
            return False
        if token[0] != token_type:
            return False
        if value is not None and token[1] != value:
            return False
        return True

    # ── top-level ──────────────────────────────────────────────────────────

    def parse(self):
        statements = []
        while self.current() is not None:
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        return statements

    def parse_block(self):
        """Parse statements until BLOCK_END or a block-level keyword (elif/else)."""
        statements = []
        while self.current() is not None:
            if self.check(BLOCK_END):
                self.consume(BLOCK_END)
                break
            if self.check(KEYWORD, "elif") or self.check(KEYWORD, "else"):
                break
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        return statements

    # ── statements ─────────────────────────────────────────────────────────

    def parse_statement(self):
        token = self.current()
        if token is None:
            return None

        # module.method{arg}\  — e.g. ai.ask{"prompt"}\
        if token[0] == IDENTIFIER and self.peek() and self.peek()[0] == DOT:
            return self.parse_method_call_stmt()

        # pcAI.method{arg}\  — built-in AI module, no import needed
        if token[0] == KEYWORD and token[1] == "pcAI" and self.peek() and self.peek()[0] == DOT:
            return self.parse_pcai_method_call_stmt()

        if token[0] != KEYWORD:
            raise SyntaxError(f"Expected a Curl keyword, got {token[0]} {repr(token[1])}")

        dispatch = {
            "pcType":       self.parse_print,
            "pcAsk":        self.parse_input,
            "var":          self.parse_var_statement,
            "list":         self.parse_list_statement,
            "createFunc":   self.parse_func_def,
            "func":         self.parse_func_call,
            "if":           self.parse_if,
            "while":        self.parse_while,
            "for":          self.parse_for,
            "otherCoding":  self.parse_other_coding,
            "import":       self.parse_import,
            "pcAI":         self.parse_ai,
        }

        handler = dispatch.get(token[1])
        if handler is None:
            raise SyntaxError(f"Unexpected keyword at statement level: '{token[1]}'")
        return handler()

    def parse_print(self):
        self.consume(KEYWORD, "pcType")
        self.consume(LBRACE)
        expr = self.parse_concat_expr()
        self.consume(RBRACE)
        self.consume(LINE_END)
        return {"type": "print", "value": expr}

    def parse_input(self):
        self.consume(KEYWORD, "pcAsk")
        self.consume(LBRACE)
        prompt = self.consume(STRING)[1].strip('"')
        self.consume(ARROW)
        self.consume(RBRACE)
        self.consume(LINE_END)
        return {"type": "input", "prompt": prompt}

    def parse_var_statement(self):
        self.consume(KEYWORD, "var")
        self.consume(LBRACE)
        name = self.consume(IDENTIFIER)[1]

        if self.check(COMMA):
            # var{name, value}\  →  assignment
            self.consume(COMMA)
            value = self.parse_concat_expr()
            self.consume(RBRACE)
            self.consume(LINE_END)
            return {"type": "assign", "name": name, "value": value}
        else:
            # var{name}\  →  standalone reference (no-op)
            self.consume(RBRACE)
            self.consume(LINE_END)
            return {"type": "var_ref", "name": name}

    def parse_list_statement(self):
        # Standalone list{...}\  — unusual but spec mentions it
        items = self._parse_list_body()
        self.consume(LINE_END)
        return {"type": "list_stmt", "items": items}

    def parse_func_def(self):
        self.consume(KEYWORD, "createFunc")
        self.consume(LBRACE)
        name = self.consume(IDENTIFIER)[1]
        self.consume(RBRACE)
        self.consume(MINUS)
        body = self.parse_block()
        return {"type": "func_def", "name": name, "body": body}

    def parse_func_call(self):
        self.consume(KEYWORD, "func")
        self.consume(LBRACE)
        name = self.consume(IDENTIFIER)[1]
        self.consume(RBRACE)
        self.consume(LINE_END)
        return {"type": "func_call", "name": name}

    def parse_if(self):
        self.consume(KEYWORD, "if")
        self.consume(LBRACE)
        condition = self.parse_condition()
        self.consume(COMMA)
        self.consume(KEYWORD, "then")
        self.consume(RBRACE)
        self.consume(MINUS)
        then_body = self.parse_block()

        elif_clauses = []
        else_body = None

        while self.check(KEYWORD, "elif"):
            self.consume(KEYWORD, "elif")
            self.consume(LBRACE)
            elif_cond = self.parse_condition()
            self.consume(COMMA)
            self.consume(KEYWORD, "then")
            self.consume(RBRACE)
            self.consume(MINUS)
            elif_body = self.parse_block()
            elif_clauses.append({"condition": elif_cond, "body": elif_body})

        if self.check(KEYWORD, "else"):
            self.consume(KEYWORD, "else")
            self.consume(COLON)
            else_body = self.parse_block()

        return {
            "type": "if",
            "condition": condition,
            "then_body": then_body,
            "elif_clauses": elif_clauses,
            "else_body": else_body,
        }

    def parse_while(self):
        self.consume(KEYWORD, "while")
        self.consume(LBRACE)
        condition = self.parse_condition()
        self.consume(RBRACE)
        self.consume(MINUS)
        body = self.parse_block()
        return {"type": "while", "condition": condition, "body": body}

    def parse_for(self):
        # for{i, start, end}-  iterates i from start up to (not including) end
        self.consume(KEYWORD, "for")
        self.consume(LBRACE)
        var_name = self.consume(IDENTIFIER)[1]
        self.consume(COMMA)
        start = self.parse_math_expr()
        self.consume(COMMA)
        end = self.parse_math_expr()
        self.consume(RBRACE)
        self.consume(MINUS)
        body = self.parse_block()
        return {"type": "for", "var": var_name, "start": start, "end": end, "body": body}

    def parse_other_coding(self):
        self.consume(KEYWORD, "otherCoding")
        self.consume(LBRACE)
        lang = self.consume(STRING)[1].strip('"')
        self.consume(COMMA)
        code = self.consume(RAW_CODE)[1]
        self.consume(LINE_END)
        return {"type": "other_code", "language": lang, "code": code}

    def parse_method_call_stmt(self):
        module = self.consume(IDENTIFIER)[1]
        self.consume(DOT)
        method = self.consume(IDENTIFIER)[1]
        self.consume(LBRACE)
        arg = self.parse_concat_expr()
        self.consume(RBRACE)
        self.consume(LINE_END)
        return {"type": "method_call", "module": module, "method": method, "arg": arg}

    def parse_pcai_method_call_stmt(self):
        self.consume(KEYWORD, "pcAI")
        self.consume(DOT)
        method = self.consume(IDENTIFIER)[1]
        self.consume(LBRACE)
        arg = self.parse_concat_expr()
        self.consume(RBRACE)
        self.consume(LINE_END)
        return {"type": "method_call", "module": "pcAI", "method": method, "arg": arg}

    def parse_import(self):
        self.consume(KEYWORD, "import")
        self.consume(LBRACE)
        package = self.consume(STRING)[1].strip('"')
        if self.check(COMMA):
            self.consume(COMMA)
            nickname = self.consume(IDENTIFIER)[1]
        else:
            nickname = None  # will default to "pcAI" for AI package, or package name otherwise
        self.consume(RBRACE)
        self.consume(LINE_END)
        return {"type": "import", "package": package, "nickname": nickname}

    def parse_ai(self):
        self.consume(KEYWORD, "pcAI")
        self.consume(LBRACE)
        mode = self.consume(STRING)[1].strip('"')
        self.consume(COMMA)
        directions = self.consume(STRING)[1].strip('"')
        options = []
        while self.check(COMMA):
            self.consume(COMMA)
            opt = self.consume(STRING)[1].strip('"')
            options.append(opt)
        self.consume(RBRACE)
        self.consume(LINE_END)
        return {"type": "ai", "mode": mode, "directions": directions, "options": options}

    # ── expressions ────────────────────────────────────────────────────────

    def parse_concat_expr(self):
        """expr ('+' expr)*  — used inside pcType{}"""
        parts = [self.parse_math_expr()]
        while self.check(PLUS):
            self.consume(PLUS)
            parts.append(self.parse_math_expr())
        if len(parts) == 1:
            return parts[0]
        return {"type": "concat", "parts": parts}

    def parse_math_expr(self):
        """expr (('-' | '*' | '/') expr)*"""
        left = self.parse_expr()
        while self.current() and self.current()[0] in (MINUS, TIMES, DIVIDE):
            op = self.consume(self.current()[0])[1]
            right = self.parse_expr()
            left = {"type": "binop", "op": op, "left": left, "right": right}
        return left

    def parse_expr(self):
        """Single atom: string, number, var ref, input ref, list literal, func call."""
        token = self.current()
        if token is None:
            raise SyntaxError("Unexpected end of expression")

        if token[0] == STRING:
            self.pos += 1
            return {"type": "string", "value": token[1].strip('"')}

        if token[0] == NUMBER:
            self.pos += 1
            raw = token[1]
            return {"type": "number", "value": float(raw) if '.' in raw else int(raw)}

        if token[0] == KEYWORD:
            kw = token[1]

            # pcAI.method{arg} as an expression — e.g. var{x, pcAI.ask{"prompt"}}\
            if kw == "pcAI" and self.peek() and self.peek()[0] == DOT:
                self.pos += 1  # consume pcAI
                self.consume(DOT)
                method = self.consume(IDENTIFIER)[1]
                self.consume(LBRACE)
                arg = self.parse_concat_expr()
                self.consume(RBRACE)
                return {"type": "method_call", "module": "pcAI", "method": method, "arg": arg}

            if kw == "var":
                self.pos += 1
                self.consume(LBRACE)
                name = self.consume(IDENTIFIER)[1]
                self.consume(RBRACE)
                return {"type": "var_ref", "name": name}

            if kw == "input":
                self.pos += 1
                self.consume(LBRACE)
                self.consume(IDENTIFIER)  # 'ans'
                self.consume(RBRACE)
                return {"type": "input_ref"}

            if kw == "list":
                items = self._parse_list_body()
                return {"type": "list", "items": items}

            if kw == "func":
                self.pos += 1
                self.consume(LBRACE)
                name = self.consume(IDENTIFIER)[1]
                self.consume(RBRACE)
                return {"type": "func_call_expr", "name": name}

        # module.method{arg}  — e.g. ai.ask{"prompt"}
        if token[0] == IDENTIFIER:
            module = token[1]
            self.pos += 1
            if self.check(DOT):
                self.consume(DOT)
                method = self.consume(IDENTIFIER)[1]
                self.consume(LBRACE)
                arg = self.parse_concat_expr()
                self.consume(RBRACE)
                return {"type": "method_call", "module": module, "method": method, "arg": arg}
            return {"type": "var_ref", "name": module}

        raise SyntaxError(f"Unexpected token in expression: {token[0]} {repr(token[1])}")

    def _parse_list_body(self):
        """list{item; item; ...}  — shared by list expr and list statement."""
        self.consume(KEYWORD, "list")
        self.consume(LBRACE)
        items = [self.parse_expr()]
        while self.check(SEMICOLON):
            self.consume(SEMICOLON)
            items.append(self.parse_expr())
        self.consume(RBRACE)
        return items

    def parse_condition(self):
        """left op right, where op is ==, !=, <, >, <=, >=."""
        left = self.parse_expr()
        token = self.current()
        if token and token[0] in COMPARISON_OPS:
            op = self.consume(token[0])[1]
            right = self.parse_expr()
            return {"type": "condition", "left": left, "op": op, "right": right}
        return left
