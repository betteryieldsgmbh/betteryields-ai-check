# betteryields AI-Check

Three free skills that make AI answers checkable. Deutsche Fassung weiter unten.

| Skill | What it enforces | Folder |
|---|---|---|
| **ai-checker** | An answer about a document is verified against the document itself, quote by quote, with a hard ACCEPTED/REJECTED verdict | [`skills/ai-checker`](skills/ai-checker) |
| **source-required** | No number without its source: every claim is marked as measured, judgement or unverified; works in any language via the `[QC]` evidence block | [`skills/source-required`](skills/source-required) |
| **nothing-missed** | No document from memory: intake list from the conversation first, hand-over with a reference per item (`INTAKE:` / `REF:`) | [`skills/nothing-missed`](skills/nothing-missed) |
| **show-your-work** | The workshop report for AI: every hand-over names the exact object delivered, the check that ran on that same object and the full scale of the result (`[SHIPPED]` block) | [`skills/show-your-work`](skills/show-your-work) |

All four run with Claude; source-required, nothing-missed and show-your-work also ship paste-in
variants for ChatGPT, GitHub Copilot and Gemini (see `references/wohin.md` in each
folder). The sections below describe the ai-checker in detail.

## What it does

Your assistant summarises a contract, an insurance policy, a quarterly report or a
slide deck. Sounds convincing. Did it actually read the file? This checker verifies
the answer against the document itself, quote by quote. It prints a report with a
hard verdict: ACCEPTED or REJECTED. Every report carries the SHA-256 of every input,
so anyone can repeat the run and get the same verdict. The assistant runs the script;
the script does the judging.

Works on docx, pdf, xlsx and pptx. Needs Python 3.11 or newer and nothing else.
Everything runs locally; no file leaves the machine.

## Install in Claude Code

```
/plugin marketplace add betteryieldsgmbh/betteryields-ai-check
/plugin install betteryields-ai-check@betteryields
```

Then ask Claude to check any answer about an uploaded document, or type `/ai-checker`.

## Install in claude.ai or other assistants

Download the packaged version from <https://www.myaisen.com> and follow the
instructions inside: `INSTALL.md` covers claude.ai. The folder
`andere-assistenten` covers ChatGPT, GitHub Copilot and agents that read `AGENTS.md`.
The same files ship in this repository under `skills/ai-checker/`.

## Verify what you got

The content of `skills/ai-checker/` is byte-identical to the released
`Betteryields_AI-Check_Skill.zip` of the kit release named below. The release
publishes a `kit-manifest.json` with the SHA-256 of every artifact; compare with
`sha256sum` if you want proof instead of trust.

Current release: kit 23.0, checker 4.12.

---

# betteryields AI-Check (Deutsch)

## Was es tut

Ihr Assistent fasst einen Vertrag, eine Versicherungspolice, einen Quartalsbericht
oder eine Präsentation zusammen. Klingt überzeugend. Hat er die Datei wirklich
gelesen? Dieses Prüfprogramm vergleicht die Antwort Zitat für Zitat mit dem
Dokument selbst und druckt einen Bericht mit einem harten Urteil: ACCEPTED oder
REJECTED. Jeder Bericht trägt die SHA-256-Prüfsummen aller Eingaben, damit jeder
den Lauf wiederholen kann und dasselbe Urteil erhält. Der Assistent führt das
Programm aus; das Programm urteilt.

Geprüft werden docx, pdf, xlsx und pptx. Vorausgesetzt wird Python 3.11 oder
neuer, sonst nichts. Alles läuft lokal; keine Datei verlässt den Rechner.

## Einrichten in Claude Code

```
/plugin marketplace add betteryieldsgmbh/betteryields-ai-check
/plugin install betteryields-ai-check@betteryields
```

Danach bitten Sie Claude, eine Antwort zu einem hochgeladenen Dokument zu prüfen,
oder tippen `/ai-checker`.

## Einrichten in claude.ai oder anderen Assistenten

Laden Sie das fertige Paket von <https://www.myaisen.com> herunter und folgen Sie
der beiliegenden Anleitung: `INSTALLIEREN.md` beschreibt claude.ai, der Ordner
`andere-assistenten` beschreibt ChatGPT, GitHub Copilot und Agenten, die
`AGENTS.md` lesen. Dieselben Dateien liegen in diesem Repository unter
`skills/ai-checker/`.

## Nachprüfen statt glauben

Der Inhalt von `skills/ai-checker/` ist byte-gleich mit dem veröffentlichten
`Betteryields_AI-Check_Skill.zip` der unten genannten Kit-Ausgabe. Die
Veröffentlichung trägt eine `kit-manifest.json` mit den SHA-256-Prüfsummen aller
Artefakte; vergleichen Sie mit `sha256sum`, wenn Sie einen Beleg wollen.

Aktuelle Ausgabe: Kit 23.0, Prüfprogramm 4.12.

## Lizenz

MIT, siehe [LICENSE](LICENSE).

## Work-discipline skills: source-required, nothing-missed and show-your-work

Two further skills ship in `skills/`, usable with any assistant:

- **source-required** -- no number without its source: every claim is marked
  as measured (with source), judgement or unverified; denials need named
  attempts, absence claims need a search space, handovers need complete,
  self-verified addresses. Language-free via the `[QC]` evidence block.
- **show-your-work** -- the workshop report for AI: every hand-over names the
  object delivered, the check that ran on that same object and the full scale
  of the result, as a `[SHIPPED]` block the enclosed script enforces.
- **nothing-missed** -- no document from memory: pull the numbered intake
  list from the conversation first, write against it, hand over with a
  per-item reference (`INTAKE:` / `REF:` in any language).

Each folder is ready for the claude.ai skill upload (zip the folder, one
top-level directory with `SKILL.md` inside). `references/wohin.md` in each
skill explains which file to paste into ChatGPT, GitHub Copilot or Gemini;
the enforcement hooks for Claude Code live under `scripts/`.

Deutsch: beide Ordner sind fertig für den Skill-Upload von Claude; die Datei
`references/wohin.md` je Skill erklärt, welche Fassung in ChatGPT, Copilot
oder Gemini gehört.
