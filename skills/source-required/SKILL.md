---
name: source-required
description: Use before stating any number, count, date, status or fact about files, repositories or measurements. Every claim carries its source or is labelled as judgement or unverified. Prevents the failure where a plausible guess is written down as a measured fact.
license: MIT
metadata:
  author: betteryields GmbH
  version: "1.0"
---

# Source required: keine Zahl ohne ihre Quelle

## Warum es diesen Skill gibt

An einem einzigen Abend wurden drei Behauptungen als falsch entlarvt, die als
Tatsache dastanden: eine nie gemessene Aussage über Prüfungen in einem
Repository, eine frei erfundene Zeile in einer Tabelle, eine Erklärung, die
hingeschrieben war, bevor sie gemessen wurde. Jedes Mal fand es der Leser,
nicht der Assistent.

**Die Lücke ist nicht Schlamperei, sie ist im Aufbau:** übliche Prüfungen
kontrollieren Dateien. Keine prüft die Sätze, die an den Leser gehen. Einer
Zahl sieht man nicht an, ob sie gezählt oder geraten ist.

## Die Regel

Jede Zahl, jedes Datum, jede Menge, jeder Zustand und jede Aussage über eine
Datei, ein Repository oder eine Messung trägt eine von drei Marken:

| Marke | Wann | Was dabeisteht |
|---|---|---|
| **gemessen** | ein Befehl oder eine Datei hat den Wert geliefert | woraus: Datei und Zeile, Befehl, Protokoll, Commit |
| **Urteil** | eine Einschätzung, Einordnung oder Empfehlung | dass es eine ist -- und woran sie sich stützt |
| **ungeprüft** | übernommen, vermutet, aus dem Gedächtnis | dass es nicht geprüft ist, und was es kosten würde, es zu prüfen |

Es gibt keine vierte Möglichkeit. Eine Zahl ohne Marke ist ein Fehler, kein
Stilproblem.

## Die fünf Fragen vor jeder Zahl

1. **Habe ich das ausgeführt?** Wenn nein, ist es keine Messung. Auch dann
   nicht, wenn es offensichtlich stimmt.
2. **Löst die Quelle auf?** Ein genannter Pfad, Commit oder Zweig muss
   existieren. Eine Dateiaussage nennt Zweig und Commit und ob sie auf main ist,
   und zwar gegen ORIGIN geprüft, nie gegen die Arbeitskopie.
3. **Was füllt die Lücke?** Wenn ein Wert fehlt, bleibt die Lücke offen und
   heißt "nicht gemessen". Sie wird nie mit einem plausiblen Wert gefüllt --
   ein plausibler Wert ist genau das, was niemand mehr nachprüft.
4. **Wie weit trägt die Messung?** Eine Behauptung, dass etwas NICHT
   existiert oder nicht geht, ist nur so weit gemessen, wie gesucht wurde.
   Sie nennt darum immer den Suchraum ("durchsucht: alle Branches beider
   Repos") -- ohne Suchraum heißt sie ungeprüft. Aus "ich habe X nicht
   gefunden" wird sonst unbemerkt "X gibt es nicht".

   Dieselbe Pflicht trifft zwei Geschwister der Abwesenheits-Behauptung:
   "kann ich nicht / geht nicht" gilt erst mit benannten Versuchen samt
   Fehlermeldung ("versucht: ..., abgewiesen mit ..."), und ein
   Arbeitsschritt wird erst dann an den Nutzer weitergereicht, wenn die
   eigenen Versuche dastehen. Die Arbeit gehört der Sitzung.
5. **Funktioniert die Übergabe?** Jeder ausgehändigte Zugangspunkt --
   Adresse, Pfad, Befehl -- ist selbst beschritten und zeigt auf das
   Ergebnis, nicht in dessen Nähe ("geprüft: Adresse zeigt X"). Und er
   steht VOLLSTÄNDIG da: eine mit Auslassungspunkten abgekürzte Adresse
   ist keine Adresse, sie ist Leseraufgabe.

## Der Belegblock: dieselbe Regel in jeder Sprache

Die Marken oben sind deutsche Wörter. Damit die Regel auch in englischen,
französischen oder anderssprachigen Antworten prüfbar bleibt, gibt es den
sprachfreien Belegblock: ein kleiner Block aus festen Token, den der Hook
strukturell prüft, egal in welcher Sprache die Prosa drumherum steht.

```
[QC]
CLAIM: tests/test_app.py has 32 tests | MARK: MEASURED | SRC: tests/test_app.py
CLAIM: approach B is the better one | MARK: JUDGEMENT
CLAIM: CI is probably green | MARK: UNVERIFIED
DENIAL: cannot reach the registry | TRIED: curl -sS registry.example, refused with 403
ABSENT: no install guide exists | SEARCHED: all branches of both repos
HANDOFF: owner must click the consent screen | TRIED: API create rejected with admin_required
DEPLOYED: report page is live | VERIFIED: opened the URL, table renders with data
[/QC]
```

Die Zeilenarten und ihre Pflichtfelder:

| Zeile | Pflicht | Bedeutung |
|---|---|---|
| `CLAIM` | `MARK: MEASURED\|JUDGEMENT\|UNVERIFIED`; bei `MEASURED` zusätzlich `SRC` | eine Behauptung mit ihrer Marke |
| `DENIAL` | `TRIED` | ein "geht nicht" mit benannten Versuchen |
| `ABSENT` | `SEARCHED` | eine Abwesenheits-Behauptung mit Suchraum |
| `HANDOFF` | `TRIED` | ein weitergereichter Schritt mit eigenen Versuchen |
| `DEPLOYED` | `VERIFIED` | ein Ausrollen mit Klickweg-Nachweis |

Relative Dateipfade in `SRC` müssen im Arbeitsverzeichnis auflösen. Ein
vorhandener, gültiger Block erfüllt die Ziffernregel der ganzen Antwort; ein
vorhandener, aber lückenhafter Block wird abgelehnt. In deutscher Prosa
genügen weiterhin die klassischen Marken -- der Block ist der Weg für alle
anderen Sprachen.

## Die gefährlichste Form

Nicht die falsche Zahl. Die **richtige Zahl mit erfundener Herkunft** -- sie
hält jeder Nachfrage stand, bis jemand die Herkunft prüft, und dann ist alles
andere auch verdächtig. Deshalb ist die Marke Pflicht, auch wenn der Wert
stimmt.

## Was dieser Skill nicht kann

Er ist eine Anweisung. Er prüft nicht, ob der Wert richtig gerechnet ist --
nur, ob eine Quelle dasteht und ob sie auflöst. Das Rechnen bleibt prüfbar
durch den Owner und durch eine zweite Stimme.

Und wie bei `nothing-missed` gilt: eine Anweisung allein ist die vorletzte
Stelle. Deshalb liefert dieses Plugin den letzten Zentimeter gleich mit: einen
Stop-Hook (`hooks/`), der eine Antwort mit nackter Zahl ablehnt, bevor sie den
Owner erreicht, und der bei gemessen-Marken mit relativem Dateipfad prüft, ob
die Quelle überhaupt existiert. Dazu eine automatische Erinnerung vor jeder
Eingabe. Ob der Wert aus der Quelle richtig abgelesen wurde, prüft der Hook
nicht -- das bleibt beim Owner und der zweiten Stimme. Der Befehl `/source-required:report` erzeugt jederzeit den Tätigkeitsbericht: alle
Behauptungen mit Marke, dazu die protokollierten Blockaden aus
`blockprotokoll.jsonl`.
