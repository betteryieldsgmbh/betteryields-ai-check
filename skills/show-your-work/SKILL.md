---
name: show-your-work
description: Use before handing anything over -- publishing an artifact, sending a file, pushing a branch, opening or merging a pull request, reporting a check result. The hand-over names the exact object delivered, the check that ran on that same object, and the full scale of what the check reported. Prevents the failure where a true check result is stated about a different object, or only the worst level of a result is reported.
license: MIT
metadata:
  author: betteryields GmbH
  version: "1.0.0"
  homepage: https://www.myaisen.com
  source: https://github.com/betteryieldsgmbh/betteryields-ai-check
---

# Show your work: der Werkstattbericht für KI

## Warum es diesen Skill gibt

In jeder Werkstatt bekommen Sie bei der Abholung einen Bericht, was genau
gemacht wurde: welches Fahrzeug, welche Punkte geprüft, welcher Befund je
Punkt. Ein KI-Assistent liefert Ihnen einen Satz ("geprüft, alles in
Ordnung") und behält den Bericht für sich.

Der Satz kann wahr sein und trotzdem nichts über Ihre Lieferung aussagen:
die Prüfung lief an einer älteren Fassung, an der Vorlage statt am Ergebnis,
an einer Schwesterdatei. Oder "in Ordnung" meint nur die schlimmste Stufe,
und drei Warnungen bleiben unerwähnt. Sie sehen dem Satz nicht an, welches
von beidem gilt.

**Die Lücke ist im Aufbau:** ein Prüfbericht ohne Kennzeichen und ohne
Prüfpunkte ist kein Prüfbericht, egal wie viele Werte darin stehen. Genau
diese zwei Angaben verlangt dieser Skill bei jeder Lieferung.

## Die Regel

Jede Übergabe -- Artefakt, Datei, Push, Pull Request, Seite, Bericht -- trägt
drei Angaben:

| Angabe | Frage | Was dabeisteht |
|---|---|---|
| **Gegenstand** | Was genau lege ich hin? | Pfad, Adresse, Commit, Zweig -- der Stand, den der Leser bekommt |
| **Prüfung am Gegenstand** | Lief die Prüfung an genau diesem? | die Prüfung und die Bestätigung, dass ihr Eingang der Gegenstand war |
| **Volle Skala** | Was hat die Prüfung auf jeder Stufe gemeldet? | alle Stufen, die die Prüfung kennt: Fehler UND Warnungen, blockierend UND beobachtend |

Eine Prüfung an der Schwesterdatei, an der Quelle statt am Ergebnis oder an
einer früheren Fassung ist kein Nachweis. Eine Skala mit einer Stufe ist die
halbe Skala.

## Die drei Fragen vor jeder Übergabe

1. **Ist das, was ich geprüft habe, das, was ich hinlege?** Wird die Seite
   aus dem geprüften Text erzeugt, ja. Wurde sie daneben geschrieben, nein:
   dann ist der Text geprüft und die Seite nicht.
2. **Welche Stufen kennt die Prüfung?** Vor dem Satz "sauber" die Skala der
   Prüfung ansehen: Fehler, Warnungen, Hinweise, Beobachtungen. Jede Stufe
   bekommt ihren Stand, auch die Nullen.
3. **Steht der Gegenstand dabei?** Nicht "die Seite", sondern
   `seite.html @ 4914da3`. Ein Gegenstand, der offensichtlich scheint, ist
   genau der, bei dem der Fehler unbemerkt bleibt.

## Der Lieferblock: dieselbe Regel in jeder Sprache

Wie der QC-Block von `source-required` ist der Lieferblock sprachfrei: feste
Token, die der Hook strukturell prüft, egal in welcher Sprache die Prosa
drumherum steht.

```
[SHIPPED]
OBJECT: seite.html @ 4914da3 | branch main
CHECK: house style gates, 47 gates | ON: SAME | RESULT: 0 blocking red, 9 watching with findings | SCALE: blocking, watching
CHECK: pytest tools/ | ON: SAME | RESULT: 1381 passed, 0 failed | SCALE: passed, failed
[/SHIPPED]
```

| Feld | Pflicht | Bedeutung |
|---|---|---|
| `OBJECT` | genau einmal | der übergebene Gegenstand: Pfad, Adresse, Commit |
| `CHECK` | mindestens einmal | die Prüfung, die als Nachweis dient |
| `ON` | je CHECK | `SAME` oder wörtlich der OBJECT-Text; alles andere ist kein Nachweis |
| `RESULT` | je CHECK | das Ergebnis |
| `SCALE` | je CHECK, mindestens zwei Stufen | jede Stufe, die die Prüfung kennt |

## Die gefährlichste Form

Der wahre Satz über den falschen Gegenstand. Er hält jeder Nachfrage stand,
weil er stimmt -- bis jemand fragt, worüber. Deshalb steht der Gegenstand in
jedem Nachweis, und deshalb ist der beste Bau der, bei dem das Gelieferte aus
dem Geprüften ERZEUGT wird statt daneben geschrieben.

## Was dieser Skill nicht kann

Er prüft Form, nicht Wahrheit. Ob die Prüfung wirklich an diesem Gegenstand
lief, kann nur ein Leser mit Zugriff nachvollziehen. Aber die Form zwingt die
Sitzung, Gegenstand und Skala hinzuschreiben; ein hingeschriebener falscher
Gegenstand ist eine sichtbare Lüge, kein Versehen mehr.

Und wie bei den Geschwister-Skills gilt: eine Anweisung allein ist die
vorletzte Stelle. Deshalb liefert dieses Plugin den letzten Zentimeter mit:
einen Stop-Hook (`hooks/`), der nach einer Übergabe im Zug (Artefakt
veröffentlicht, Datei geschickt, `git push`, Pull Request eröffnet oder
gemergt) eine Antwort ohne vollständigen Lieferblock ablehnt, und eine
Erinnerung vor jeder Eingabe.
