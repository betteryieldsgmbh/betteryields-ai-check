# Der AI-Checker — einbauen und benutzen

## Was er macht

Ihre KI behauptet etwas über ein Dokument. Der Checker rechnet nach: jedes Zitat wird
wörtlich gegen das Original geprüft, und er misst, wie viel vom Dokument die Antwort
überhaupt berührt hat. Heraus kommt ein Urteil — **ACCEPTED** oder **REJECTED** — mit den
Prüfsummen aller Dateien.

Die KI prüft sich dabei nicht selbst. Sie führt nur ein Programm aus, dessen Ergebnis
jeder mit denselben zwei Dateien nachstellen kann.

Sie brauchen **Python 3.11 oder neuer**. Sonst nichts.

## Einbauen

Archiv entpacken, den Ordner an seinen Platz kopieren — ein Befehl im Terminal:

```bash
mkdir -p ~/.claude/skills && cp -r ai-checker ~/.claude/skills/
```

Windows, in PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force .\ai-checker "$HOME\.claude\skills\"
```

Auf claude.ai laden Sie stattdessen das Archiv hoch, so wie es ist.

## Benutzen

Sie tippen `/ai-checker` und sagen dahinter, was geprüft werden soll:

```
/ai-checker Fasse lastenheft.docx zusammen und prüfe die Zusammenfassung
```

Oder Sie sagen es einfach so — Claude greift von selbst danach:

```
Fasse mir das Lastenheft zusammen. Und prüf das nach.
```

Mehr ist es nicht. Die Schritte dahinter — Format holen, Antwort schreiben, Prüfer
starten — macht die KI; die Datei `SKILL.md` im Ordner ist ihre Anweisung dafür, nicht
Ihre.

## Was zurückkommt

Ein Bericht, den die KI nicht formuliert, sondern durchreicht:

```
  points           : 8 of 8 backed by a real quote
  coverage         : 8 of 8 paragraphs cited
  checker SHA-256  : af566d43631bcb29defce79f6d04ed41233ca892d3a4a35b074bbb7aa8ab4e15
  verdict          : ACCEPTED
```

**Woran Sie merken, dass wirklich gerechnet wurde:** an der Zeile `checker SHA-256`. Kommt
ein Bericht ohne Prüfsummen, hat die KI ihn erfunden — genau das, was der Checker
verhindern soll. Fragen Sie dann nach dem Befehl, den sie ausgeführt hat.

**ACCEPTED heißt nicht „richtig".** Es heißt: jede Aussage steht so im Dokument, und nichts
wurde übergangen. Ob die Aussage klug ist, entscheiden weiter Sie.

**REJECTED ist der Normalfall in der ersten Runde.** Der Bericht nennt jede Stelle, nicht
ein paar Beispiele. Die KI bessert nach und lässt erneut prüfen, bis es steht.

## Andere Assistenten

Dieselbe Prüfung, andere Tür. Die Anweisungen liegen im Unterordner
`ai-checker/andere-assistenten/`:

| Ihr Assistent | Die Datei | Wohin damit |
|---|---|---|
| ChatGPT (Custom GPT oder Chat) | `ANWEISUNG-ChatGPT.md` | Text hineinkopieren, `betteryields-ai-check.py` als Datei hochladen |
| GitHub Copilot | `copilot-instructions.md` | nach `.github/` im Projekt, Skript daneben |
| Codex, Cursor, Windsurf und andere | `AGENTS.md` | ins Projektverzeichnis |

Entpacken Sie das Archiv dafür in dem Verzeichnis, in dem Sie arbeiten; dann stimmen diese
Befehle:

```bash
mkdir -p .github && cp ai-checker/andere-assistenten/copilot-instructions.md .github/ && cp ai-checker/betteryields-ai-check.py .github/
```

```bash
cp ai-checker/andere-assistenten/AGENTS.md .
```

Copilot kann nur im **Agent-Modus** prüfen — nur der darf ein Terminal benutzen. Im
Ask-Modus sagt er das und rät nicht.
