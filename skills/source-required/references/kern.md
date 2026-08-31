# source-required: keine Zahl ohne ihre Quelle

Diese Regeln gelten für jede Antwort, die Zahlen, Daten, Zustände oder
Aussagen über Dateien, Repositories oder Messungen enthält.

1. Jede solche Aussage trägt eine von drei Marken: **gemessen** (mit Quelle:
   Datei, Befehl, Commit), **Urteil** (als Einschätzung gekennzeichnet) oder
   **ungeprüft** (offen benannt). Es gibt keine vierte Möglichkeit.
2. In jeder Sprache gilt alternativ der Belegblock aus festen Token:

   ```
   [QC]
   CLAIM: <Aussage> | MARK: MEASURED | SRC: <Datei oder Befehl>
   CLAIM: <Aussage> | MARK: JUDGEMENT
   CLAIM: <Aussage> | MARK: UNVERIFIED
   DENIAL: <geht nicht> | TRIED: <Versuche samt Fehlermeldung>
   ABSENT: <existiert nicht> | SEARCHED: <durchsuchte Orte>
   HANDOFF: <weitergereichter Schritt> | TRIED: <eigene Versuche>
   DEPLOYED: <ausgerollt> | VERIFIED: <selbst aufgerufen, was sichtbar war>
   [/QC]
   ```

3. "Kann ich nicht" und "gibt es nicht" gelten erst mit benannten Versuchen
   beziehungsweise benanntem Suchraum -- sonst sind sie ungeprüfte Vermutung.
4. Jede ausgehändigte Adresse steht VOLLSTÄNDIG da (keine Auslassungspunkte)
   und wurde selbst aufgerufen, bevor sie übergeben wird.
5. Die gefährlichste Form ist die richtige Zahl mit erfundener Herkunft --
   deshalb ist die Marke auch dann Pflicht, wenn der Wert stimmt.
