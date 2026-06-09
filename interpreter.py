import importlib
from ai_module import CurlAIModule


def execute(ast, env=None):
    if env is None:
        env = {
            "variables": {},
            "functions": {},
            "imports": {"pcAI": CurlAIModule()},  # built-in, no import needed
            "last_input": None,
        }
    for stmt in ast:
        _exec_stmt(stmt, env)


def _exec_stmt(stmt, env):
    t = stmt["type"]

    if t == "print":
        print(_eval(stmt["value"], env))

    elif t == "input":
        env["last_input"] = input(stmt["prompt"] + " ")

    elif t == "assign":
        env["variables"][stmt["name"]] = _eval(stmt["value"], env)

    elif t == "var_ref":
        pass  # standalone var{name}\ — no-op

    elif t == "list_stmt":
        pass  # standalone list{...}\ — no-op

    elif t == "func_def":
        env["functions"][stmt["name"]] = stmt["body"]

    elif t == "func_call":
        _call_func(stmt["name"], env)

    elif t == "if":
        if _eval_condition(stmt["condition"], env):
            execute(stmt["then_body"], _child_env(env))
        else:
            ran = False
            for clause in stmt["elif_clauses"]:
                if _eval_condition(clause["condition"], env):
                    execute(clause["body"], _child_env(env))
                    ran = True
                    break
            if not ran and stmt["else_body"] is not None:
                execute(stmt["else_body"], _child_env(env))

    elif t == "while":
        while _eval_condition(stmt["condition"], env):
            execute(stmt["body"], env)

    elif t == "for":
        start = int(_eval(stmt["start"], env))
        end   = int(_eval(stmt["end"], env))
        for i in range(start, end):
            env["variables"][stmt["var"]] = i
            execute(stmt["body"], env)

    elif t == "other_code":
        _exec_other(stmt["language"], stmt["code"], env)

    elif t == "import":
        nickname = stmt["nickname"]
        if stmt["package"] == "pcAI":
            env["imports"][nickname or "pcAI"] = CurlAIModule()
        else:
            if not nickname:
                nickname = stmt["package"]
            try:
                mod = importlib.import_module(stmt["package"])
                env["imports"][nickname] = mod
            except ImportError as e:
                raise ImportError(f"Could not import '{stmt['package']}': {e}")

    elif t == "method_call":
        _eval(stmt, env)  # execute and discard return value

    elif t == "ai":
        print(f"[pcAI — mode: {stmt['mode']} | {stmt['directions']}]")

    else:
        raise RuntimeError(f"Unknown statement type: {t!r}")


def _call_func(name, env):
    if name not in env["functions"]:
        raise NameError(f"Function '{name}' is not defined")
    execute(env["functions"][name], _child_env(env))


def _child_env(env):
    return {
        "variables": dict(env["variables"]),
        "functions": env["functions"],
        "imports": env["imports"],
        "last_input": env["last_input"],
    }


def _eval(expr, env):
    t = expr["type"]

    if t == "string":
        return expr["value"]

    if t == "number":
        return expr["value"]

    if t == "var_ref":
        name = expr["name"]
        if name not in env["variables"]:
            raise NameError(f"Variable '{name}' is not defined")
        return env["variables"][name]

    if t == "input_ref":
        if env["last_input"] is None:
            raise RuntimeError("No input has been received yet (use pcAsk first)")
        return env["last_input"]

    if t == "list":
        return [_eval(item, env) for item in expr["items"]]

    if t == "concat":
        return "".join(str(_eval(p, env)) for p in expr["parts"])

    if t == "binop":
        left = _eval(expr["left"], env)
        right = _eval(expr["right"], env)
        op = expr["op"]
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right
        raise RuntimeError(f"Unknown binary operator: {op!r}")

    if t == "func_call_expr":
        _call_func(expr["name"], env)
        return None

    if t == "method_call":
        module_name = expr["module"]
        method_name = expr["method"]
        arg = _eval(expr["arg"], env)
        if module_name not in env["imports"]:
            raise NameError(f"'{module_name}' is not imported — use import{{\"ai\", {module_name}}}\\")
        module = env["imports"][module_name]
        if not hasattr(module, method_name):
            raise AttributeError(f"'{module_name}' has no method '{method_name}'")
        return getattr(module, method_name)(arg)

    raise RuntimeError(f"Unknown expression type: {t!r}")


def _eval_condition(cond, env):
    if cond["type"] != "condition":
        return bool(_eval(cond, env))
    left = _eval(cond["left"], env)
    right = _eval(cond["right"], env)
    op = cond["op"]
    if op == "==":  return left == right
    if op == "!=":  return left != right
    if op == "<":   return left < right
    if op == ">":   return left > right
    if op == "<=":  return left <= right
    if op == ">=":  return left >= right
    raise RuntimeError(f"Unknown comparison operator: {op!r}")


def _exec_other(language, code, env):
    lang = language.lower()
    if lang == "python":
        globs = {"__builtins__": __builtins__}
        globs.update(env["variables"])
        exec(code, globs)
        for key, val in globs.items():
            if not key.startswith("__"):
                env["variables"][key] = val
    elif lang in ("javascript", "node.js"):
        import subprocess, shutil
        node = shutil.which("node")
        if not node:
            print("[otherCoding JavaScript] Node.js not found — skipping")
            return
        result = subprocess.run([node, "-e", code], capture_output=True, text=True)
        if result.stdout:
            print(result.stdout, end="")
        if result.returncode != 0:
            raise RuntimeError(f"JavaScript error: {result.stderr.strip()}")
    elif lang in ("java", "c", "c++"):
        print(f"[otherCoding {language}] Compilation-based languages are not supported at runtime")
    else:
        raise RuntimeError(f"Unsupported otherCoding language: {language!r}")
