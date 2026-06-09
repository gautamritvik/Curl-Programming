import os
import re
import json
import urllib.request
import urllib.error

# ── ANSI terminal codes ───────────────────────────────────────────────────────
_R  = "\033[0m"   # reset
_B  = "\033[1m"   # bold
_I  = "\033[3m"   # italic
_U  = "\033[4m"   # underline
_CY = "\033[36m"  # cyan  (inline code)
_DM = "\033[2m"   # dim   (horizontal rules)

def _md(text):
    """Convert basic Markdown to ANSI escape codes for terminal display."""
    out = []
    for line in text.split("\n"):
        # headings
        if line.startswith("### "):
            line = f"{_B}{line[4:]}{_R}"
        elif line.startswith("## "):
            line = f"{_B}{_U}{line[3:]}{_R}"
        elif line.startswith("# "):
            line = f"{_B}{_U}{line[2:]}{_R}"
        # horizontal rule
        elif re.fullmatch(r'[-*_]{3,}', line.strip()):
            line = f"{_DM}{'─' * 40}{_R}"
        else:
            # bullet points
            line = re.sub(r'^(\s*)[-*] ', r'\1• ', line)
            # bold + italic
            line = re.sub(r'\*\*\*(.+?)\*\*\*', lambda m: f"{_B}{_I}{m.group(1)}{_R}", line)
            # bold
            line = re.sub(r'\*\*(.+?)\*\*', lambda m: f"{_B}{m.group(1)}{_R}", line)
            # italic
            line = re.sub(r'\*(.+?)\*', lambda m: f"{_I}{m.group(1)}{_R}", line)
            # inline code
            line = re.sub(r'`([^`]+)`', lambda m: f"{_CY}{m.group(1)}{_R}", line)
        out.append(line)
    return "\n".join(out)


# ── module constants ──────────────────────────────────────────────────────────
_DEFAULT_SYSTEM = """\
You are Curl-Bot, an AI assistant built into the Curl programming language.
Curl is an open-source programming language created by Ritvik Gautam that runs on Python.
You are helpful, concise, and friendly.
Respond in plain text only — no Markdown, no asterisks, no bullet symbols, no backticks.

=== CURL LANGUAGE REFERENCE ===

Every statement ends with a backslash (\\).
Blocks open with - and close with --\\.

PRINT:
  pcType{"Hello, world!"}\
  pcType{"Hello " + var{name}}\

INPUT (stores in input{ans}):
  pcAsk{"What is your name? >>"}\

VARIABLES:
  var{name, "Ritvik"}\        — assign string
  var{score, 100}\            — assign number
  var{greeting, "Hi " + var{name}}\
  pcType{var{name}}\          — print variable

LISTS:
  list{1; 2; 3}\

FUNCTIONS:
  createFunc{greet}-
      pcType{"Hello!"}\
  --\\
  func{greet}\               — call the function

IF / ELIF / ELSE:
  if{var{x} == 10, then}-
      pcType{"ten"}\
  --\\

  if{var{x} == 10, then}-
      pcType{"ten"}\
  else:
      pcType{"not ten"}\
  --\\

  if{var{x} > 10, then}-
      pcType{"big"}\
  elif{var{x} == 10, then}-
      pcType{"exact"}\
  --\\--\\

OPERATORS:
  ==  equals         !=  not equals
  <   less than      >   greater than
  <=  less/equal     >=  greater/equal
  +   concatenate or add
  -   subtract       *   multiply      /  divide
  \\   end of line    -   open block    --\\ close block
  {}  argument list  ""  string data   ;  list separator
  ,   parameter sep

OTHER LANGUAGE BLOCKS:
  otherCoding{"Python",
      print("hi")
  }\\

  otherCoding{"JavaScript",
      console.log("hi")
  }\\

AI MODULE (built-in, no import needed):
  pcAI.context{"You are a pirate."}\\   — set bot persona (resets history)
  var{r, pcAI.ask{"What is 2+2?"}}\\    — ask a question (history kept)
  pcType{var{r}}\\
  pcAI.chat{""}\\                        — start interactive chat loop (type exit to quit)
  pcAI.reset{""}\\                       — clear conversation history
  pcAI.summarize{"some long text"}\\
  pcAI.analyze{"some data"}\\
  pcAI.sentiment{"I love this!"}\\       — returns: positive / negative / neutral
  pcAI.translate{"Bonjour to English"}\\

IMPORTS:
  import{"math", m}\\                  — any Python stdlib or installed package

=== END OF CURL REFERENCE ===
"""

_COMPACT_THRESHOLD = 20   # auto-compact after this many messages in history


class CurlAIModule:
    """
    AI standard library for Curl.

    Env vars:
      CURL_AI_KEY / OPENAI_API_KEY  — API key
      CURL_AI_BASE_URL              — base URL  (default: https://api.openai.com/v1)
      CURL_AI_MODEL                 — model     (default: gpt-4o-mini)

    Methods (Curl syntax):
      ai.context{"system prompt"}\       — set bot persona
      ai.ask{"prompt"}\                  — one-shot question (history kept)
      ai.chat{""}\                       — interactive chat loop (exit to quit)
      ai.reset{""}\                      — clear history
      ai.summarize{"text"}\
      ai.analyze{"text"}\
      ai.sentiment{"text"}\
      ai.translate{"text to English"}\
    """

    def __init__(self):
        self._system = _DEFAULT_SYSTEM
        self._history = []

    # ── configuration ─────────────────────────────────────────────────────────

    def context(self, prompt):
        """Set a persistent system prompt (persona) for all subsequent calls."""
        self._system = str(prompt)
        self._history = []
        return ""

    def reset(self, _=""):
        """Clear conversation history while keeping the current context."""
        self._history = []
        return ""

    # ── internal ──────────────────────────────────────────────────────────────

    def _raw_request(self, messages):
        api_key  = os.environ.get("CURL_AI_KEY") or os.environ.get("OPENAI_API_KEY", "")
        base_url = os.environ.get("CURL_AI_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
        model    = os.environ.get("CURL_AI_MODEL", "deepseek/deepseek-chat-v3-0324")

        if not api_key:
            raise RuntimeError(
                "No API key found. Set CURL_AI_KEY in your environment.\n"
                "\n"
                "Recommended — free models via OpenRouter:\n"
                "  1. Get a free key at https://openrouter.ai/keys\n"
                "  2. export CURL_AI_KEY=sk-or-your_key_here\n"
                "  (default model: deepseek/deepseek-chat-v3-0324)\n"
                "\n"
                "To use OpenAI:\n"
                "  export CURL_AI_KEY=your_openai_key\n"
                "  export CURL_AI_BASE_URL=https://api.openai.com/v1\n"
                "  export CURL_AI_MODEL=gpt-4o-mini\n"
                "\n"
                "To run fully locally for free (no key needed):\n"
                "  Install Ollama from https://ollama.com, then:\n"
                "  export CURL_AI_BASE_URL=http://localhost:11434/v1\n"
                "  export CURL_AI_MODEL=llama3.2"
            )

        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.7,
        }).encode()

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=payload,
            headers=headers,
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                return result["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")
            raise RuntimeError(f"AI request failed ({e.code}): {body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"AI connection failed: {e.reason}")

    def _compact_history(self):
        summary_messages = [
            {"role": "system", "content": self._system},
            {
                "role": "user",
                "content": (
                    "Summarize the following conversation in 3-5 bullet points "
                    "to use as context going forward. Be concise.\n\n"
                    + "\n".join(f"{m['role'].upper()}: {m['content']}" for m in self._history)
                ),
            },
        ]
        summary = self._raw_request(summary_messages)
        self._history = [{"role": "assistant", "content": f"[Previous conversation summary]\n{summary}"}]

    def _request(self, prompt):
        if len(self._history) >= _COMPACT_THRESHOLD:
            self._compact_history()
        self._history.append({"role": "user", "content": str(prompt)})
        messages = [{"role": "system", "content": self._system}] + self._history
        reply = self._raw_request(messages)
        self._history.append({"role": "assistant", "content": reply})
        return reply

    # ── public methods ────────────────────────────────────────────────────────

    def ask(self, prompt):
        """Send a prompt (history kept) and return the response."""
        return _md(self._request(prompt))

    def chat(self, _=""):
        """Start an interactive chat loop. Type 'exit' to quit."""
        print(f"\n{_B}Curl-Bot Chat{_R}  —  type {_CY}exit{_R} to quit\n")
        while True:
            try:
                user_input = input(f"{_B}You:{_R} ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            if not user_input:
                continue
            reply = self._request(user_input)
            print(f"\n{_B}Curl-Bot:{_R} {_md(reply)}\n")
        return ""

    def summarize(self, text):
        messages = [
            {"role": "system", "content": self._system},
            {"role": "user", "content": f"Summarize in 2-3 sentences:\n\n{text}"},
        ]
        return _md(self._raw_request(messages))

    def analyze(self, text):
        messages = [
            {"role": "system", "content": self._system},
            {"role": "user", "content": f"Analyze and provide key insights:\n\n{text}"},
        ]
        return _md(self._raw_request(messages))

    def sentiment(self, text):
        messages = [
            {"role": "system", "content": self._system},
            {
                "role": "user",
                "content": (
                    "What is the sentiment? Reply with ONE word only: positive, negative, or neutral.\n\n"
                    + text
                ),
            },
        ]
        return self._raw_request(messages)  # raw — used in comparisons

    def translate(self, text):
        messages = [
            {"role": "system", "content": self._system},
            {"role": "user", "content": f"Translate the following:\n\n{text}"},
        ]
        return _md(self._raw_request(messages))
