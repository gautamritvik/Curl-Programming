import os
import json
import urllib.request
import urllib.error

_DEFAULT_SYSTEM = (
    "You are Curl-Bot, an AI assistant built into the Curl programming language. "
    "Curl is an open-source language created by Ritvik Gautam that runs on Python. "
    "You are helpful, concise, and friendly."
)

# Auto-compact after this many user+assistant message pairs in history
_COMPACT_THRESHOLD = 20


class CurlAIModule:
    """
    AI standard library for Curl.

    Configuration via environment variables:
      CURL_AI_KEY or OPENAI_API_KEY  — API key (not needed for local models)
      CURL_AI_BASE_URL               — base URL (default: https://api.openai.com/v1)
                                       set to http://localhost:11434/v1 for Ollama
      CURL_AI_MODEL                  — model name (default: gpt-4o-mini)

    Usage in Curl:
      import{"ai", ai}\
      ai.context{"You are a pirate who only speaks in rhymes."}\
      var{answer, ai.ask{"What is the capital of France?"}}\
      pcType{var{answer}}\
    """

    def __init__(self):
        self._system = _DEFAULT_SYSTEM
        self._history = []  # list of {"role": ..., "content": ...}

    def context(self, prompt):
        """Set a persistent system prompt (persona/context) for all subsequent AI calls."""
        self._system = str(prompt)
        self._history = []  # reset history when context changes
        return ""

    def reset(self, _=""):
        """Clear conversation history (start a fresh chat while keeping context)."""
        self._history = []
        return ""

    def _raw_request(self, messages):
        """Send a messages list to the API and return the reply string."""
        api_key = os.environ.get("CURL_AI_KEY") or os.environ.get("OPENAI_API_KEY", "")
        base_url = os.environ.get("CURL_AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        model = os.environ.get("CURL_AI_MODEL", "gpt-4o-mini")

        if not api_key and "openai.com" in base_url:
            raise RuntimeError(
                "No API key found. Set CURL_AI_KEY (or OPENAI_API_KEY) in your environment.\n"
                "For a free local model, install Ollama (https://ollama.com), run a model, then set:\n"
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
        """Summarize old history into a single assistant message to stay within limits."""
        summary_messages = [
            {"role": "system", "content": self._system},
            {
                "role": "user",
                "content": (
                    "Summarize the following conversation history into 3-5 bullet points "
                    "so it can be used as context going forward. Be concise.\n\n"
                    + "\n".join(
                        f"{m['role'].upper()}: {m['content']}" for m in self._history
                    )
                ),
            },
        ]
        summary = self._raw_request(summary_messages)
        self._history = [{"role": "assistant", "content": f"[Previous conversation summary]\n{summary}"}]

    def _request(self, prompt):
        """Send prompt with history, auto-compact when history is too long."""
        if len(self._history) >= _COMPACT_THRESHOLD:
            self._compact_history()

        self._history.append({"role": "user", "content": str(prompt)})

        messages = [{"role": "system", "content": self._system}] + self._history
        reply = self._raw_request(messages)

        self._history.append({"role": "assistant", "content": reply})
        return reply

    def ask(self, prompt):
        """Send a prompt (with conversation history) and return the response."""
        return self._request(prompt)

    def summarize(self, text):
        """Summarize text in 2-3 sentences (no history tracking)."""
        messages = [
            {"role": "system", "content": self._system},
            {"role": "user", "content": f"Summarize the following in 2-3 sentences:\n\n{text}"},
        ]
        return self._raw_request(messages)

    def analyze(self, text):
        """Analyze text and return key insights (no history tracking)."""
        messages = [
            {"role": "system", "content": self._system},
            {"role": "user", "content": f"Analyze the following and provide key insights:\n\n{text}"},
        ]
        return self._raw_request(messages)

    def sentiment(self, text):
        """Return the sentiment of text: positive, negative, or neutral (no history tracking)."""
        messages = [
            {"role": "system", "content": self._system},
            {
                "role": "user",
                "content": (
                    "What is the sentiment of this text? "
                    "Reply with only one word: positive, negative, or neutral.\n\n" + text
                ),
            },
        ]
        return self._raw_request(messages)

    def translate(self, text):
        """Translate text — include the target language in the text itself (no history tracking)."""
        messages = [
            {"role": "system", "content": self._system},
            {"role": "user", "content": f"Translate the following:\n\n{text}"},
        ]
        return self._raw_request(messages)
