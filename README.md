# compgen-ii-cgv
Historische Ortsnamen in Verlustlisten des 1. Weltkrieges vereinheitlichen

## Pipeline

Die Pipeline in `pipeline.py` ist eine Klasse, die Veränderungen an sich selbst trackt. Dazu wird jede Version der Pipeline im Order `log/pipeline` abgespeichert. Das Attribut `self.hash` speichert den Sourcecode der Klasse als Hash. Sobald man etwas an der Klasse verändert, verändert sich auch dieser Hash. Beim nächsten Aufruf der Klasse wird dann die Versionsnummer im Attribut `self.version` inkrementiert. Auf diese Weise können wir Änderungen an der Klasse automatisch nachverfolgen.

Die Ergebnisse eines jeden Durchlaufs werden in `log` abgelegt unter der Versionsnummer der aktuell gültigen Pipeline. Das Ergebnis sieht so aus:
``` 
Pipeline version 1 | vl: 1,204,819 lines | gov cities: 211,606 lines | gov districts: 5,395 lines | matches: 524,575 (0.4353973501413905)
```

