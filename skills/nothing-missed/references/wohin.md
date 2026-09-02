# Welche Datei wohin -- nothing-missed für jeden Assistenten

Dieses Paket trägt denselben Skill in mehreren Fassungen. Die Prüfregeln sind
überall dieselben; nur der Weg der Installation unterscheidet sich. Die
AUTOMATISCHE Blockade (Stop-Hook) gibt es nur bei Claude -- bei allen anderen
gilt die Anweisung, und der Belegblock macht die Antworten von Hand prüfbar.

| Assistent | Datei | Weg |
|---|---|---|
| Claude (claude.ai, Cowork, Claude Code) | das ganze Zip | im Skill-Dialog hochladen; volle Durchsetzung über die Prüfskripte in diesem Paket |
| ChatGPT | `references/chatgpt.md` | Inhalt in die Anweisungen eines Projekts oder eigenen GPTs einfügen |
| GitHub Copilot | `references/copilot-instructions.md` | als `.github/copilot-instructions.md` ins Repository legen |
| Gemini | `references/gemini.md` | Inhalt als Anweisungstext eines Gems einfügen |
| Andere Agenten | `references/agents.md` | als `AGENTS.md` ins Arbeitsverzeichnis legen |

## Absender

Dieser Skill stammt von betteryields GmbH. Seite und Download: https://www.myaisen.com. Quelltext und Fassungen: https://github.com/betteryieldsgmbh/betteryields-ai-check.
