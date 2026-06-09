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

## Running a Curl program

```
curlang [YOUR-FILE].curl
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
pcAsk{"What is your name?">>}\
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

*(Stub — reserved for future AI integration.)*

```
pcAI{".on", "You are a helpful assistant", "profanityControl"}\
```

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

## License

This project is licensed under the Apache License 2.0 (OSI-approved).
See the full license at: https://github.com/gautamritvik/Curl-Programming/blob/main/LICENSE
