# Curl Programming Language

[![PyPI version](https://img.shields.io/pypi/v/curl-programming-lang.svg)](https://pypi.org/project/curl-programming-lang/)
[![License](https://img.shields.io/github/license/gautamritvik/Curl-Programming.svg)](https://github.com/gautamritvik/Curl-Programming/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/curl-programming-lang.svg)](https://pypi.org/project/curl-programming-lang/)
[![Curl-Bot](https://img.shields.io/badge/AI%20Model-Curl--Bot-blue)](https://huggingface.co/gautamritvik/Curl-Bot)

Curl is an open-source programming language built on Python technology, designed to be simple and expressive. Every statement uses a `keyword{...}\` style, and blocks are opened with `-` and closed with `--\`.

---

## Why Curl?

Most programming languages treat AI as an afterthought — a third-party library you install, a client you configure, boilerplate you copy from a docs page. By the time you write `response.choices[0].message.content`, you've already forgotten what you were building.

Curl does it differently. `pcAI` is part of the language itself, the same way `print` is part of Python. There is no setup, no import, no client object. From the very first line of your program, you can ask a question and get an answer:

```
pcAI.ask{"What should I name this variable?"}\
```

That's the entire program. Not a demo — that actually runs.

This is what makes Curl different from every other language: **AI is native syntax, not a library.** You don't bolt it on at the end. You design around it from the start. Want a bot that remembers what you said three messages ago? It already does. Want to give it a personality? One line. Want to drop into a full interactive chat from inside a script? One line. Want to run it against your own local model with no API key at all? Point one environment variable at Ollama and you're done.

Curl is for people who want to build AI-powered programs without wading through infrastructure. For students writing their first script. For developers who want to prototype an idea in ten minutes instead of an afternoon. For anyone who's ever thought *I just want to ask the computer a question* and had to install four packages first.

Other languages got AI added to them. Curl was designed with it at the center.

---

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

### Loops — `while` / `for`

**While loop** — repeats while a condition is true:

```
var{x, 0}\
while{var{x} < 5}-
    pcType{var{x}}\
    var{x, var{x} + 1}\
--\
```

**For loop** — iterates a variable from start up to (not including) end:

```
for{i, 0, 5}-
    pcType{var{i}}\
--\
```

> The loop variable `i` is available inside the block as `var{i}`.

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

### AI — `pcAI` + Curl-Bot

`pcAI` is a **built-in AI module** — no import required. It defaults to **DeepSeek** via OpenRouter (free).

**Setup — get a free key at [openrouter.ai/keys](https://openrouter.ai/keys), then:**

```
export CURL_AI_KEY=sk-or-your_key_here
```

That's all. `pcAI` defaults to Curl-Bot automatically.

**Ask a question:**

```
var{reply, pcAI.ask{"What is the capital of France?"}}\
pcType{var{reply}}\
```

**Interactive chat loop** (type `exit` to quit):

```
pcAI.chat{""}\
```

**Set a custom persona:**

```
pcAI.context{"You are a friendly pirate who answers in rhymes."}\
var{reply, pcAI.ask{"What is 2 + 2?"}}\
pcType{var{reply}}\
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

**Want to use a different model?** Override with env vars:

| Variable | Default | Description |
|---|---|---|
| `CURL_AI_KEY` | *(required)* | OpenRouter key, OpenAI key, etc. |
| `CURL_AI_BASE_URL` | `https://openrouter.ai/api/v1` | API base URL |
| `CURL_AI_MODEL` | `deepseek/deepseek-chat-v3-0324` | Model name |

Works with **OpenRouter** (recommended, free models available), **OpenAI**, **Ollama**, or any OpenAI-compatible API.

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
