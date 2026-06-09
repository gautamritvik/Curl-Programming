import os
import json
import urllib.request
import urllib.error


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
      var{answer, ai.ask{"What is the capital of France?"}}\
      pcType{var{answer}}\
    """

    def _request(self, prompt):
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
            "messages": [{"role": "user", "content": str(prompt)}],
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

    def ask(self, prompt):
        """Send a prompt and return the response as a string."""
        return self._request(prompt)

    def summarize(self, text):
        """Summarize text in 2-3 sentences."""
        return self._request(f"Summarize the following in 2-3 sentences:\n\n{text}")

    def analyze(self, text):
        """Analyze text and return key insights."""
        return self._request(f"Analyze the following and provide key insights:\n\n{text}")

    def sentiment(self, text):
        """Return the sentiment of text: positive, negative, or neutral."""
        return self._request(
            f"What is the sentiment of this text? "
            f"Reply with only one word: positive, negative, or neutral.\n\n{text}"
        )

    def translate(self, text):
        """Translate text — include the target language in the text itself."""
        return self._request(f"Translate the following:\n\n{text}")
