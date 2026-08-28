---
name: ai-checker
description: Prove that an answer about an uploaded document is actually anchored in that document. Use whenever someone asks you to summarise, review, compare, audit or extract from a docx, pdf, xlsx or pptx and the answer has to be trustworthy -- for example bills of material against a substance rule, requirement specifications, insurance policies, quarterly reports, board slides, or two versions of the same document. Also use it when someone asks you to check an answer that another AI produced.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/betteryields-ai-check.py *)
---

# betteryields AI-Check

> **This file is for you, the assistant, not for the person reading over your
> shoulder.** They type `/ai-checker` or simply ask you to check something; every
> step below is yours to carry out. If they ask what to do, the short answer is:
> nothing -- name the document and let it run.

A deterministic checker verifies your answer against the document, quote by
quote, and prints a report with the SHA-256 of every input. You run it. You do
not judge your own work -- the script does the judging, and anyone can repeat it.

`betteryields-ai-check.py` sits next to this file. It needs Python 3.11 or newer
and nothing else.

**Run it by its full path, never by its bare name.** Your working directory is the
person's project, not this folder, so `python3 betteryields-ai-check.py` fails with
"No such file or directory". The commands below carry the full path already: in
Claude Code it is filled in for you, and in any other tool you replace the folder
part with wherever the skill was unpacked. On Windows the command is `python`, not
`python3`.

## The one rule that cannot be bent

**Never write, paraphrase, complete or summarise a report you did not receive
from the script.** If you cannot run it, say so plainly and stop. A fabricated
report is worse than no check at all: it is the exact failure this tool exists
to catch, and the person reading it has no way to tell.

Show the report as the script printed it. It contains the checksums that let
someone else repeat the run and get the same verdict.

## How to run a check

1. **Pick the mode** from the table below.
2. **Get the instruction from the script, do not write it yourself:**
   `python3 ${CLAUDE_SKILL_DIR}/betteryields-ai-check.py prompt <mode>`
   It prints the exact format the checker parses. A copy in your own words drifts
   away from the checker on its next release.
3. **Write your answer in that format** and save it as a UTF-8 text file.
4. **Run the check:**
   `python3 ${CLAUDE_SKILL_DIR}/betteryields-ai-check.py <answer.txt> <document> [second document]`
5. **Show the report unchanged.**
6. **If REJECTED: fix exactly what the report names, then run it again.** The
   report names every place, not a sample. Repeat until ACCEPTED or until the
   person tells you to stop; say how many rounds it took.

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
`python3 ${CLAUDE_SKILL_DIR}/betteryields-ai-check.py generate questions <document>`,
`generate tasks`, or `generate exam <answer.txt> <document>`. Never paste a key
into the chat you are testing.

## What ACCEPTED means, and what it does not

ACCEPTED means every statement is anchored in the document and nothing was
skipped. It does **not** mean the answer is true, complete in judgement, or
useful. It means it can be checked -- which is the part an AI cannot fake.

WARNING means the document could not be read well enough for a fair verdict.
That is a statement about the DOCUMENT, never about the answer.

## When the person asks for proof

The report's audit log carries the SHA-256 of the document, of the answer and of
the checker itself. Anyone with the same two files can run the same command and
must get the same report. That, not your assurance, is the proof.
