# betteryields AI-Check

A deterministic checker verifies an answer about a document against that document,
quote by quote, and prints a report with the SHA-256 of every input. The script
judges; you run it. Anyone with the same two files can repeat the run and must get
the same report.

Use it whenever you summarise, review, compare, audit or extract from a `.docx`,
`.pdf`, `.xlsx` or `.pptx` and the answer has to be trustworthy -- and whenever
someone asks you to check an answer another AI produced.

`ai-checker/betteryields-ai-check.py` sits beside this file. It needs
Python 3.11 or newer and nothing else. Run it by its path from where this file
lies; on Windows the command is `python`, not `python3`.

## The one rule that cannot be bent

**Never write, paraphrase, complete or summarise a report you did not receive from
the script.** If you cannot run it, say so plainly and stop. A fabricated report is
worse than no check at all: it is the exact failure this tool exists to catch, and
the person reading it has no way to tell.

Show the report as the script printed it. It carries the checksums.

## How to run a check

1. **Pick the mode** from the table below.
2. **Get the instruction from the script, do not write it yourself:**
   `python3 ai-checker/betteryields-ai-check.py prompt <mode>`
   It prints the exact format the checker parses. A copy in your own words drifts
   away from the checker on its next release.
3. **Write your answer in that format** and save it as a UTF-8 text file.
4. **Run the check:**
   `python3 ai-checker/betteryields-ai-check.py <answer.txt> <document> [second document]`
5. **Show the report unchanged.**
6. **If REJECTED: fix exactly what the report names, then run it again.** The report
   names every place, not a sample. Repeat until ACCEPTED or until the person tells
   you to stop; say how many rounds it took.

Exit codes: 0 accepted, 1 rejected, 2 warning or no verdict, 3 usage error.

## Which mode

| Mode | The question it answers | Files |
|---|---|---|
| `fidelity` | Is every statement of my summary anchored, and is the whole document covered? | answer + document |
| `located-evidence` | Does every claim name the place it stands in, and is the quote really there? | answer + document |
| `table-rules` | Which rows break the rule -- and did the answer name all of them? | answer + table (xlsx, csv) |
| `review` | What changed between two versions, and was anything missed? | answer + old + new |
| `presentation` | Is every claim on every slide backed by the source? | answer + source + deck |
| `requirements` | Does every requirement carry a status and real evidence? | answer + specification + offer |
| `sycophancy` | Does the AI fold when the questioner pushes? | answer + key |
| `drift` | Does the same model still give the same values today? | answer + key |
| `exam` | Did a second model verify the first one's points? | answer + key |

The last three compare against a key the script generates:
`python3 ai-checker/betteryields-ai-check.py generate questions <document>`,
`generate tasks`, or `generate exam <answer.txt> <document>`. Never paste a key into
the chat you are testing.

## What ACCEPTED means, and what it does not

ACCEPTED means every statement is anchored in the document and nothing was skipped.
It does **not** mean the answer is true, complete in judgement, or useful. It means
it can be checked -- which is the part an AI cannot fake.

WARNING means the document could not be read well enough for a fair verdict. That is
a statement about the DOCUMENT, never about the answer.
