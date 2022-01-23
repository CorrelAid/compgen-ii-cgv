README SQL
=====================
## SQL Dateien
| Datei | Beschreibung |
| - | - |
| query_orte_v02.sql | (veraltet) Experimentelle sql query, mit der in einer frühen Phase des Projekts ein gefilterter Auszug des GOV angelegt worden ist. Die Query wurde im weiteren Verlauf des Projekts aufgegeben. Stattdessen werden aus der GOV Datenbank nur Rohdaten gezogen per `query_raw_{}.sql` und die Filterung wird komplett in Python in der Klasse Gov realisiert.
| query_raw_govitem.sql | Rohdaten query. Siehe [unten](#aktueller-auszug-gov) |
| query_raw_propertynames.sql | Rohdaten query. Siehe [unten](#aktueller-auszug-gov) | 
| query_raw_propertytypes.sql | Rohdaten query. Siehe [unten](#aktueller-auszug-gov) |
| query_raw_relation.sql  | Rohdaten query. Siehe [unten](#aktueller-auszug-gov) |
| query_raw_typenames.sql | Rohdaten query. Siehe [unten](#aktueller-auszug-gov) |
| query_orte_v02_kreise_long_lat.sql | Experimentelle query, um Geodaten aus der GOV-Datenbank zu laden. Der Geo-Daten-Ansatz ist (Stand 29. November 2021) noch nicht implementiert. |
| query_orte_v02_orte_long_lat.sql  | Experimentelle query, um Geodaten aus der GOV-Datenbank zu laden. Der Geo-Daten-Ansatz ist (Stand 29. November 2021) noch nicht implementiert. |


## Aktueller Auszug GOV
Für einen aktuellen Abzug aus dem GOV verwendet man die [5 sql Dateien](https://github.com/CorrelAid/compgen-ii-cgv/tree/main/sql) `query_raw_{...}.sql`. Mit ihrer Hilfe werden die 5 csv Dateien `gov_a_{...}.csv` erstellt, die für die Initialisierung des Gov Objekts im data Ordner erwartet werden. Mit folgendem Befehl lässt sich das von der Kommando-Zeile aus erreichen:
```
mysql -N -h IP-ADDRESS -u gov -PASSWORD gov < query_raw_xyz.sql > gov_a_xyz.csv
```
PASSWORD muss durch das entsprechende Passwort ersetzt werden. Der Parameter `-N` ist notwendig, um die Spaltenüberschriften zu unterdrücken.
