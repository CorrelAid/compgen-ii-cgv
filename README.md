# compgen-ii-cgv
Ziel des Projektes ist es, historische Ortsnamen in den Verlustlisten des 1. Weltkrieges zu vereinheitlichen.

Das Python package `compgen2` bietet ein Interface, um Namen und Listen von Namen gegen das GOV abzugleichen und mögliche Matches zu identifizieren. Hierbei wird versucht, häufig vorkommende Fehler wie falsche Schreibweisen oder häufige Verhörer zu korrigieren und so ein Match zu ermöglichen. 

## Setup
Das Python package kann mit dem folgenden Befehl installiert werden:
```
$ pip install -r requirements.txt
```

Danach steht das `compgen2` package bereit zur Nutzung.

### Daten

Die notwendigen Daten können über den folgenden [Link](https://correlcloud.org/index.php/s/iRXKCqQpxwreaMG) aus der Nextcloud geladen werden.

Der Ordner `final_data` enthält die entsprechenden Datenbankauszüge sowie die Verlustliste und die Abkürzungslisten. Den gesamten Ordner als Archiv herunterladen und lokal entpacken. Der Pfad zu diesem Ordner wird als `data_root` für die verschiedenen Anwendungen gebraucht.

## Quickstart
`compgen2` bietet für Anwender ein Kommandozeilen-Interface sowie Klassen, die im Code importiert werden können. Wir zeigen nachfolgend beide Anwendungsfälle.

### `compgen2` über die Kommandozeile

`compgen2` stellt den gleichnamigen Befehl `compgen2` für die Kommandozeile bereit.

Der Aufruf 
```
$ compgen2 -h
```

zeigt das Interface. 

Grundsätzlich werden zwei Modi unterstützt:
- `-i`: interaktiv. In diesem Modus wird das `Gov` nur am Anfang geladen und der Benutzer kann über die Kommandozeile jeweils einen Ortsnamen eingeben und bekommt dann mögliche Treffer angezeigt.
- `-f`: Dateiliste. In diesem Modus liest das Programm alle Namen aus einer TXT Datei ein und speichert das Ergebnis als JSON in eine Datei Namens `compgen2.json`.

Für beide Modi ist die Angabe eines Ordners mit der Gov-Datenbank notwendig. Dies geschieht als Pfadangabe über den Parameter `-d`.

### `compgen2` package

Das Python package `compgen2` kann mittels `import compgen2` Anweisung geladen werden.

Es stehen im Wesentlichen die Klassen `Gov`, `Matcher` und `Preprocessing` bereit, sowie einige Hilfsmethoden.

Die genaue Verwendung dieser Klassen zeigen die **showcase** notebooks.

## Matching Algorithmus
Unser Algorithmus

**TODO** Mural Bild hinzufügen

## Erkenntnisse aus dem Projekt

Alle während des Projektes gesammelten Erkenntnisse wurden im [GitHub Wiki](https://github.com/CorrelAid/compgen-ii-cgv/wiki) gesammelt.

## Notebooks
...

## Für Entwickler
...

**TODO**: SQL
