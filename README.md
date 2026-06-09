# Curl Programming Language

Curl is an open-source programming language built on Python technology, designed to be simple and expressive. Every statement uses a `keyword{...}\` style, and blocks are opened with `-` and closed with `--\`.

## Requirements

- Python 3.7+
- Node.js *(optional — only needed for `otherCoding{"JavaScript", ...}` blocks)*

## Installation

**From PyPI (recommended):**

```
pip install curl-programming-lang
```

**To upgrade:**

```
pip install --upgrade curl-programming-lang
```

**From source:**

```
git clone https://github.com/gautamritvik/Curl-Programming.git
cd Curl-Programming
pip install -e .
```

---

## Running the Curl terminal (REPL)

```
curlang
```

## Running a Curl program

```
curlang [YOUR-FILE].curl
```

## CLI flags

```
curlang --version    show version
curlang --license    show license
curlang --credits    show credits
curlang --help       show help
```

---

## Syntax Reference

### Print — `pcType`

Outputs text to the console. Supports string concatenation with `+`.

```
pcType{"Hello, World!"}\
pcType{"Hello, " + var{name} + "!"}\
```

---

### Input — `pcAsk`

Prompts the user for input. The result is accessed anywhere with `input{ans}`.

```
pcAsk{"What is your name? >>"}\
pcType{"You said: " + input{ans}}\
```

---

### Variables — `var`

Assign a value with `var{name, value}\`. Reference it later with `var{name}`.

```
var{name, "Ritvik"}\
pcType{var{name}}\
```

Variables can hold strings, numbers, or lists.

---

### Lists — `list`

Create a list with items separated by `;`. Typically assigned to a variable.

```
var{colors, list{"red"; "green"; "blue"}}\
pcType{var{colors}}\
```

---

### Functions — `createFunc` / `func`

Define a function with `createFunc{name}-` and close it with `--\`. Call it with `func{name}\`.

```
createFunc{greet}-
    pcType{"Hello from greet!"}\
--\

func{greet}\
```

---

### Conditionals — `if` / `elif` / `else`

**Simple if:**

```
if{var{score} >= 90, then}-
    pcType{"Grade: A"}\
--\
```

**If / else:**

```
if{var{score} >= 90, then}-
    pcType{"Grade: A"}\
else:
    pcType{"Grade: B or below"}\
--\
```

**If / elif / else:**

```
if{var{score} >= 90, then}-
    pcType{"Grade: A"}\
elif{var{score} >= 80, then}-
    pcType{"Grade: B"}\
else:
    pcType{"Grade: C or below"}\
--\
```

> For `if`+`elif` chains without an `else`, close with `--\--\`.

**Supported comparison operators:** `==`  `!=`  `<`  `>`  `<=`  `>=`

---

### Embedded code blocks — `otherCoding`

Run a block of code written in another language. The closing `}\` must be on its own line.

```
otherCoding{"Python",

x = 10
print("x =", x)

}\
```

**Supported languages:**

| Language | Status |
|---|---|
| Python | Fully supported |
| JavaScript / Node.js | Supported (requires Node.js) |
| Java, C, C++ | Not supported at runtime |

---

### Import — `import`

Import a Python package and give it a nickname.

```
import{"math", m}\
```

---

### AI — `pcAI`

`pcAI` is a **built-in AI module** — no import required. It supports conversation history, system prompts, and an interactive chat mode.

Configure it with environment variables:

| Variable | Default | Description |
|---|---|---|
| `CURL_AI_KEY` or `OPENAI_API_KEY` | *(none)* | Your API key |
| `CURL_AI_BASE_URL` | `https://api.openai.com/v1` | API base URL |
| `CURL_AI_MODEL` | `gpt-4o-mini` | Model name |

Works with **OpenAI**, **OpenRouter**, **Ollama**, or any OpenAI-compatible API.

**Ask a question:**

```
var{reply, pcAI.ask{"What is the capital of France?"}}\
pcType{var{reply}}\
```

**Set a persona (system prompt):**

```
pcAI.context{"You are a friendly pirate who answers in rhymes."}\
var{reply, pcAI.ask{"What is 2 + 2?"}}\
pcType{var{reply}}\
```

**Interactive chat loop** (type `exit` to quit):

```
pcAI.chat{""}\
```

**Other methods:**

```
var{s, pcAI.summarize{"some long text"}}\
var{a, pcAI.analyze{"some data"}}\
var{mood, pcAI.sentiment{"I love this!"}}\
var{t, pcAI.translate{"Bonjour — translate to English"}}\
pcAI.reset{""}\
```

> Conversation history is kept across `pcAI.ask` calls and auto-compacts when it gets long.

---

## Symbols

| Symbol | Meaning |
|---|---|
| `\` | End of a statement |
| `-` | Start of a block |
| `--\` | End of a block |
| `{}` | Argument container |
| `""` | String / text data |
| `;` | Separator inside lists |
| `,` | Separator between parameters |
| `==` | Equals |
| `!=` | Not equals |
| `=` | Assignment |
| `+` | Concatenation / addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |

---

## Example program

```
var{name, "Ritvik"}\
pcType{"Hello, " + var{name} + "!"}\

var{score, 95}\
if{var{score} >= 90, then}-
    pcType{"You got an A!"}\
else:
    pcType{"Keep trying!"}\
--\

createFunc{sayBye}-
    pcType{"Goodbye, " + var{name} + "!"}\
--\

func{sayBye}\
```

---

## Example AI program

```
pcAI.context{"You are a helpful tutor."}\
var{answer, pcAI.ask{"Explain what a variable is in one sentence."}}\
pcType{var{answer}}\
```

---

## License

This project is licensed under the Apache License 2.0 (OSI-approved).
See the full license at: https://github.com/gautamritvik/Curl-Programming/blob/main/LICENSE
