---
name: nothing-missed
description: Use when writing any document, roadmap, plan, report or specification whose content comes from a conversation with the owner. Extracts the input list from the conversation first, writes against it, then hands over with a point-by-point coverage check. Prevents the failure where a document is written from memory and silently drops what the owner said.
license: MIT
metadata:
  author: betteryields GmbH
  version: "1.7.0"
  homepage: https://www.myaisen.com
  source: https://github.com/betteryieldsgmbh/betteryields-ai-check
---

# Nothing missed: kein Dokument aus dem Gedächtnis

## Warum es diesen Skill gibt

Zweimal in derselben Stunde ist etwas verloren gegangen, das im Gespräch
ausdrücklich gesagt worden war -- eine vereinbarte Stufenliste samt ihrer
Tests, und die Ausarbeitung der Schritte. Beide Male hat es der Leser bemerkt,
nicht der Assistent. Die Ursache war jedes Mal dieselbe:

**Das Dokument wurde aus dem geschrieben, was im Moment des Schreibens vorlag,
und nichts hat geprüft, ob alles Besprochene darin steht.**

Das Gedächtnis einer Sitzung ist ein Messmittel mit unbekannter
Wiederholbarkeit. Es wie einen kalibrierten Maßstab zu behandeln, ist der
Fehler. In einer Fertigung würde niemand ein Bauteil gegen den Kopf des
Werkers prüfen, sondern gegen die Zeichnung.

## Die vier Schritte

### 1. Eingangsliste ziehen, BEVOR eine Zeile geschrieben wird

Aus dem Gespräch eine nummerierte Liste ziehen: jede Entscheidung, jede
Tabelle, jede Forderung, jede Frage, die beantwortet werden soll. Nicht
zusammenfassen -- auflisten. Eine Forderung, die in der Liste fehlt, kann im
Dokument nicht auftauchen.

Nicht aus der Erinnerung. Das Gespräch liegt vollständig vor; die Liste wird
daraus gezogen. Wenn ein Teil des Gesprächs nicht mehr im Kontext ist, wird das
Protokoll gelesen, nicht geraten.

Die Liste führt BEIDE Sprecher: jede Forderung des Owners UND jede Zusage,
die die Sitzung selbst gemacht hat ("ich baue noch X", angekündigte
Folgearbeiten). Eine verlorene eigene Zusage ist genauso verlorene Arbeit
wie eine verlorene Owner-Forderung.

Jeder Eintrag der Liste bekommt: Kennung, die Art (Owner-Forderung oder
Sitzungs-Zusage), den Wortlaut, und was daraus im Dokument stehen muss.

### 2. Gegen die Liste schreiben, nicht gegen das Gefühl

Während des Schreibens wird jeder Eintrag abgehakt. Die Liste ist der Auftrag;
das Dokument ist ihr Ergebnis. Was in der Liste steht und im Dokument fehlt, ist
nicht "noch nicht dran", sondern unfertig.

### 3. Abnahme Punkt für Punkt, mit Fundstelle

Vor der Übergabe wird die Liste durchgegangen: zu jedem Eintrag die Stelle im
Dokument nennen, an der er steht. Nicht "ist alles drin" -- die Liste mit
Fundstellen. Ein Eintrag ohne Fundstelle ist ein roter Befund, kein Versehen.

Diese Abnahme wird dem Owner gezeigt, nicht nur selbst durchgeführt. Er soll
eine Lücke an der Liste sehen, bevor er sie beim Lesen entdecken muss.

### 4. Ins Register, sofort

Jede Owner-Entscheidung wird in dem Moment ins Entscheidungsregister
geschrieben, in dem sie fällt -- mit Datum, Wortlaut und Zustand. Nicht am
Ende der Sitzung, nicht wenn Zeit ist.

Eine neue Sitzung hat kein Gedächtnis dieses Gesprächs. Sie hat nur, was im
Repository steht. Alles, was nur gesagt wurde, ist für sie nie passiert.

## Die zwei Richtungen

Beide Richtungen sind Fehler, und die zweite wird leicht vergessen:

Und dazwischen liegt das Verworfene: ein Thema, das bewusst fallengelassen
wurde, bleibt mit dem Vermerk "verworfen" samt Grund in der Liste stehen.
Nur so bleibt unterscheidbar, was entschieden wegfiel und was verloren ging.

- **Eine Anforderung, die niemand gestellt hat**, ist rot. Sie ist ungefragte
  Arbeit.
- **Eine Anforderung, die der Owner gestellt hat und die nirgends steht**, ist
  genauso rot. Sie ist verlorene Arbeit. Dasselbe gilt für eine Zusage, die
  die Sitzung selbst gemacht und dann fallengelassen hat.

Die zweite Richtung ist die, die am 29.08. zweimal zugeschlagen hat.

## Woran man merkt, dass dieser Skill gebraucht wird

- Ein Dokument entsteht aus einem längeren Gespräch.
- Der Owner hat mehrere Entscheidungen getroffen, über mehrere Nachrichten
  verteilt.
- Es wurden Tabellen oder Listen erarbeitet, die im Ergebnis auftauchen sollen.
- Das Gespräch ist lang genug, dass nicht alles gleichzeitig im Blick ist.

In allen vier Fällen: erst die Eingangsliste, dann schreiben.

## Die Abnahme in jeder Sprache

Die Wörter "Eingangsliste" und "Fundstelle" sind deutsch. Damit die Abnahme
auch in englischen, französischen oder anderssprachigen Dokumenten prüfbar
bleibt, gibt es den sprachfreien Weg (dieselbe Bauidee wie der QC-Belegblock
von source-required): feste Token statt Vokabeln. Jede Position der
Eingangsliste trägt die Zeilenmarke `INTAKE:`, ihre Fundstelle die Marke
`REF:` -- mit Doppelpunkt, die Groß- oder Kleinschreibung ist frei:

```
INTAKE: 1. rename both skills to plain English names
REF: chapter "Naming", second paragraph
INTAKE: 2. every claim carries its source
REF: table in chapter "Rules", rows one to three
```

Der Stop-Hook akzeptiert eine Übergabe, wenn ENTWEDER beide deutschen
Begriffe ODER beide Token im Zug vorkommen. Die Prosa drumherum darf jede
Sprache sein; geprüft wird nur, dass die Marken dastehen.

## Was dieser Skill NICHT ersetzt

Er ist eine Anweisung, und Anweisungen sind genau das, was am 29.08. versagt
hat -- die Hausregeln standen die ganze Zeit da. Deshalb liefert dieses Plugin
den letzten Zentimeter gleich mit: einen Stop-Hook (`hooks/`), der eine
Dokumentübergabe ohne Eingangsliste und Fundstellen ablehnt, bevor sie den
Owner erreicht, und eine automatische Erinnerung vor jeder Eingabe. Der Hook
erzwingt die Form der Abnahme; ob die Liste vollständig ist, bleibt Urteil des
Lesers. Der Befehl `/nothing-missed:report` erzeugt jederzeit den
Tätigkeitsbericht: Eingangsliste mit Fundstellen und Erledigungsstand, dazu
die protokollierten Blockaden aus `blockprotokoll.jsonl`.
