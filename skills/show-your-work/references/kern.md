# show-your-work: der Werkstattbericht für KI

Diese Regeln gelten für jede Übergabe: ein veröffentlichtes Artefakt, eine
geschickte Datei, ein Push, ein Pull Request, eine Seite, ein Bericht.

1. Jede Übergabe nennt den GEGENSTAND, der übergeben wird: Pfad, Adresse,
   Commit, Zweig. Nicht "die Seite", sondern welche Datei in welchem Stand.
2. Jede Prüfung, die als Nachweis dient, lief an GENAU DIESEM Gegenstand.
   Eine Prüfung an einer Schwesterdatei, an einer früheren Fassung oder an
   der Quelle statt am Ergebnis ist kein Nachweis für das Gelieferte.
3. Jedes Prüfergebnis nennt die VOLLE SKALA der Prüfung: alle Stufen, die die
   Prüfung kennt, mit ihrem Stand. "Keine Fehler" ist die halbe Skala, wenn
   die Prüfung auch Warnungen kennt. "Bestanden" ist die halbe Skala, wenn es
   auch Hinweise gab.
4. In jeder Sprache gilt der Lieferblock aus festen Token:

   ```
   [SHIPPED]
   OBJECT: <Pfad, Adresse oder Commit des übergebenen Gegenstands>
   CHECK: <Prüfung> | ON: SAME | RESULT: <Ergebnis> | SCALE: <Stufe, Stufe, ...>
   CHECK: <weitere Prüfung> | ON: SAME | RESULT: <Ergebnis> | SCALE: <Stufe, Stufe>
   [/SHIPPED]
   ```

   `ON: SAME` heißt: die Prüfung lief am Gegenstand aus OBJECT. Lief sie an
   etwas anderem, steht das dort -- und dann ist es kein Nachweis, sondern
   eine Nebeninformation. `SCALE` nennt mindestens zwei Stufen.
5. Die gefährlichste Form ist der wahre Satz über den falschen Gegenstand:
   "die Tore sind gelaufen" stimmt, nur nicht über das, was auf dem Tisch
   liegt. Deshalb steht der Gegenstand in jedem Nachweis, auch wenn er
   offensichtlich scheint.
