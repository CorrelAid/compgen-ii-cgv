# compgen-ii-cgv
Historische Ortsnamen in Verlustlisten des 1. Weltkrieges vereinheitlichen

## Notebooks

Die Jupyter Notebooks liegen im Repo als .py Dateien im "Python Percent Script Format" (das ermöglicht sinnvolle Diffs).
Um sie wie gewohnt als Notebooks zu nutzen, öffne sie mit jupyterlab und dem jupytext plugin (wird beides über requirements.txt installiert).

1. Installiere die requirements.txt via 
```
pip install --upgrade pip
pip install -r requirements.txt
```
2. Öffne jupyterlab via `python -m jupyterlab`. (Ich bin mir nicht sicher, welche Konsole ihr in Windows benutzt). Es sollte sich anschließend der Browser öffnen und ihr seht jupyterlab.
4. In jupyterlab: Rechte Maustaste auf die .py Datei und "Open with Notebook" auswählen.
5. In jupyterlab: Drücke CTRL+Shift+C (Windows, Linux) oder Command+Shift+C (Mac). In der Box, die am oberen Bildschirm von Jupyterlab erscheint, suche die Option "Pair Notebook with percent Script". Überprüfe, dass der Haken gesetzt ist.

Wenn du nun ein Notebook speicherst, wird stets die `.py` und die `.ipynb` Datei gespeichert. In das git-Repository pushen wir aber nur die `.py` Datei. Der Sinn dahinter ist, dass die `.py` Datei saubere diffs ermöglicht.

## Pipeline

Die Pipeline in `pipeline.py` ist eine Klasse, die Veränderungen an sich selbst trackt. Dazu wird jede neue Version der Pipeline im Order `log/pipeline` abgespeichert, zudem das Ergebnis als `csv` direkt in `log`. Das Attribut `self.hash` speichert den Sourcecode der Klasse als Hash. Sobald man etwas an der Klasse verändert, verändert sich auch dieser Hash. Beim nächsten Aufruf der Klasse wird dann die Versionsnummer im Attribut `self.version` inkrementiert. Auf diese Weise können wir Änderungen an der Klasse automatisch nachverfolgen.

Die Ergebnisse eines jeden Durchlaufs werden in `log` abgelegt unter der Versionsnummer der aktuell gültigen Pipeline. Das Ergebnis sieht so aus:
``` 
Pipeline version 1 | vl: 1,204,819 lines | gov cities: 211,606 lines | gov districts: 5,395 lines | matches: 524,575 (0.4353973501413905)
```

