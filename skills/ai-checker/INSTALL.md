# The AI checker — install it, use it

## What it does

Your AI claims something about a document. The checker does the arithmetic: every quote is
matched verbatim against the original, and it measures how much of the document the answer
touched at all. Out comes a verdict — **ACCEPTED** or **REJECTED** — with the checksums of
every file.

The AI is not judging itself. It only runs a program whose result anyone with the same two
files can reproduce.

You need **Python 3.11 or newer**. Nothing else.

## Install

Unpack the archive, copy the folder into place — one command in the terminal:

```bash
mkdir -p ~/.claude/skills && cp -r ai-checker ~/.claude/skills/
```

On Windows, in PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force .\ai-checker "$HOME\.claude\skills\"
```

On claude.ai you upload the archive as it is instead.

## Use it

Type `/ai-checker` and say what to check:

```
/ai-checker Summarise requirements.docx and check the summary
```

Or just say it — Claude reaches for it on its own:

```
Summarise the requirements spec for me. And check that afterwards.
```

That is all of it. The steps behind it — fetch the format, write the answer, run the
checker — are the AI's work; `SKILL.md` in the folder is its instruction, not yours.

## What comes back

A report the AI passes through rather than composes:

```
  points           : 8 of 8 backed by a real quote
  coverage         : 8 of 8 paragraphs cited
  checker SHA-256  : af566d43631bcb29defce79f6d04ed41233ca892d3a4a35b074bbb7aa8ab4e15
  verdict          : ACCEPTED
```

**How you can tell it really computed:** the `checker SHA-256` line. A report without
checksums is one the AI invented — exactly what the checker exists to prevent. Ask it which
command it ran.

**ACCEPTED does not mean "correct".** It means every statement stands in the document that
way, and nothing was skipped. Whether the statement is sound remains your call.

**REJECTED is the normal first round.** The report names every place, not a few examples.
The AI fixes those and runs the check again, until it holds.

## Other assistants

The same check, a different door. The instructions sit in the subfolder
`ai-checker/andere-assistenten/`:

| Your assistant | The file | Where it goes |
|---|---|---|
| ChatGPT (Custom GPT or chat) | `ANWEISUNG-ChatGPT.md` | paste the text, upload `betteryields-ai-check.py` |
| GitHub Copilot | `copilot-instructions.md` | into `.github/` of your project, script beside it |
| Codex, Cursor, Windsurf and others | `AGENTS.md` | into the project directory |

Unpack the archive in the directory you work in, then these commands fit:

```bash
mkdir -p .github && cp ai-checker/andere-assistenten/copilot-instructions.md .github/ && cp ai-checker/betteryields-ai-check.py .github/
```

```bash
cp ai-checker/andere-assistenten/AGENTS.md .
```

Copilot can only run the check in **agent mode** — only that mode may use a terminal. In ask
mode it says so instead of guessing.
