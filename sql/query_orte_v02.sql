with recursive new_table as 
(
    select o.child, o.parent, o.time_begin, o.time_end
    from relation o 
    /*190315=Deutches Reich, 191050=Schweiz, 306245=Österreich-Ungarn, 220100=Liechtenstein, 218129=Luxemburg*/
    where o.parent in ("190315", "191050", "306245", "220100", "218129") 
    union
    select o.child, o.parent , o.time_begin, o.time_end
    from relation o, new_table c 
    where o.parent = c.child
    and (c.time_begin < 24215942 or c.time_begin is NULL) /* 2421594 = 31. Dezember 1917*/
    and (c.time_end   > 24047942 or c.time_end   is NUll) /* 2404794 = 1. Januar 1872, 2415021 = 1. Januar 1900*/
) 
select g1.textual_id, p1.content 
from gov_item g1 
inner join property p1
on g1.id = p1.gov_object 
where g1.deleted = 0 
and p1.property_class = "n" 
and p1.language = 'deu' 
and (p1.time_begin < 24215942 or c.time_begin is NULL) /* 2421594 = 31. Dezember 1917*/
and (p1.time_end   > 24047942 or c.time_end   is NUll) /* 2404794 = 1. Januar 1872, 2415021 = 1. Januar 1900*/
and g1.id in
(
    select n.child
    from new_table n
)
and g1.id in
(
    select p2.gov_object 
    from property p2 
    where p2.property_class = "t" 
    and (p2.time_begin < 24215942 or c.time_begin is NULL) /* 2421594 = 31. Dezember 1917*/
    and (p2.time_end   > 24047942 or c.time_end   is NUll) /* 2404794 = 1. Januar 1872, 2415021 = 1. Januar 1900*/
    and 
    (
        p2.type_object in ('5', '32', '36', '37', '110', '99', '149', '212', '78', '95', '134') /* Kreisähnliche Gebilde */
        or
        p2.type_object in ('270', '146', '25', '134') /* Kreisähnlich Österreich-Ungarn, Schweiz*/
        /*or*/
        /*p2.type_object in ('275', '136') /* Unterste Verwaltungsseinheit Österreich-Ungarn, Schweiz */
        /*or
        /*p2.type_object in ('1', '53', '95', '18', '85', '144', '150', '218') /* unterste Verwaltungseinheiten */
        /*or 
        /*p2.type_object in ('51', '55', '120', '230', '54', '39', '69', '129', '40', '54') /* unterste Wohnplätze */
    )
);

/* ------ Deutsches Reich
Bundesstaat 130
*/

/* ------ Bundesstaaten
----- basierend auf https://upload.wikimedia.org/wikipedia/commons/1/17/Karte_Deutsches_Reich%2C_Verwaltungsgliederung_1900-01-01.png
Königreich  31
Großherzogtum   61
Herzogtum   23
Fürstentum 60
Land 34   (Lübeck)
Freistaat 16  (Bremen)
Bundesland  7 (Hamburg)
Provinz 45 (Elsaß-Lothringen)
*/

/* ------- Verwaltungsebene I
----- basierend auf https://upload.wikimedia.org/wikipedia/commons/1/17/Karte_Deutsches_Reich%2C_Verwaltungsgliederung_1900-01-01.png
Landeskommissarbezirk (Untereinheiten von Baden) 201
Provinz 45 (Untereinheiten von Preußen.)
*/

/* ---- Verwaltungsebene II
----- basierend auf https://upload.wikimedia.org/wikipedia/commons/1/17/Karte_Deutsches_Reich%2C_Verwaltungsgliederung_1900-01-01.png
Regierungsbezirk    46 (Untereinheiten von Bayern, im GOV anscheinend eher als Kreis bezeichnet. Außerdem Untereinheiten von Elsaß-Lothringen.)
Kreishauptmannschaft    100 (Untereinheiten von Saschsen)
Provinz 45 (Verwaltungsebene II in Großherzogtum Hessen)
Kreis   32 (Verwaltungsebene II in Großherzogtum Baden und Königreich Württemberg)
*/

/* ---- Kreisähnliche Gebilde
----- basierend auf https://upload.wikimedia.org/wikipedia/commons/1/17/Karte_Deutsches_Reich%2C_Verwaltungsgliederung_1900-01-01.png
Bezirk  5
Kreis   32
Landkreis 36
Oberamt 37
Bezirksamt  110
Amtshauptmannschaft 99
Aushebungsbezirk    nicht im GOV als Typ vorhanden
Amt (kreisähnlich)  78 (Fehler im GOV)
Landratsamt 149
#Landgebiet  wird im GOV nicht benutzt. Sollte eigentlich die Unterebene von Lübeck sein.
Landherrschaft  212
Kreisfreie Stadt    95
Stadtteil (Verwaltung)  262 (Fehler im GOV)
Arrondissement 134 (Elsaß-Lothringen)
*/

/* Österreich-Ungarn
Staatenbund     71
*/

/* ----- Reichshälfte Österreich-Ungarn
Reichshälfte    215 {Cisleithanien, Transleithanien}
*/

/* ---- Verwaltungsebene I Ungarn
Landschaft (Verwaltung) 80 Unterebenen von Ungarn
*/

/* ---- Verwaltungsebene I Österreich
Herzogtum   23  
Königreich  31 {Böhmen, Dalmatien, Galizien und Lodomerien}
Ritterorden 188 {Deutscher Orden}
Region  137 {Litorale/Küstenland}
Markgrafschaft 62 {Mähren}
Landschaft (Verwaltung) 80 {Slowenien}
*/

/* --- Verwaltungsebene II Österreich-Ungarn
Komitat 113 In Ungarn unter den Landschaften
Bezirkshauptmannschaft 146
Gespanschaft    112 (Vukovar Srijem)
*/

/* -----Kreisähnlich Österreich-Ungarn
Bezirk (Österreich) 270
Ballei 190  {Bozen}
*/

/* Luxemburg
Großherzogtum   61
*/
/* Luxemburg kreisähnlich
# Ebene I
Distrikt    170 {Grevenmacher, Diekirch, Luxembourg}
# Ebene II
Kanton  25
*/


/* Schweiz
Staat   50
*/
/* Schweiz kreisähnlich
Kanton (Schweiz)    25
Arrondissement 134 (Schweiz)
*/

/* Liechtenstein 
Fürstentum 60
kreisähnlich: Entfällt. Nur Orte unterhalb von Liechtenstein
*/






/* ------ Unterste Verwaltungseinheiten
Amt 1 (Verwaltung)
Amtsbezirk  2
Stadtkreis  53
Kreisfreie Stadt    95
Gemeinde    18
Landgemeinde    85
Ortschaft   144
Stadt (Gebietskörperschaft) 150
Stadt (Einheitsgemeinde) 218
Stadtgemeinde (Österreich) 275
commune (Schweiz)   136
Stadtrat (UDSSR)
Stadt- und Landgemeinde (Polen)
*/

/* ---- Unterste Wohnplätze
Stadt   51
Dorf    55
Siedlung    120
Streusiedlung   230
Stadtteil 54
Ort 39
Weiler  69
Wohnplatz   129
Ortsteil    40
Stadtteil   54
Siedlung städtischen Typs (GUS)
*/
