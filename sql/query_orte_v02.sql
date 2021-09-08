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
    and (c.time_begin < 24219092 or c.time_begin is NULL) /* 2421909 = 11. November 1918*/
    and (c.time_end   > 24044292 or c.time_end   is NUll) /* 2404429 = 1. Januar 1871, 2420342 = 28. Juli 1914*/
) 
select g1.textual_id, p1.content 
from gov_item g1 
inner join property p1
on g1.id = p1.gov_object 
where g1.deleted = 0 
and p1.property_class = "n" 
and p1.language = 'deu' 
and (p1.time_begin < 24219092 or p1.time_begin is NULL) /* 2421909 = 11. November 1918*/
and (p1.time_end   > 24044292 or p1.time_end   is NULL) /* 2404429 = 1. Januar 1871, 2420342 = 28. Juli 1914*/
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
    and (p2.time_begin < 24219092 or p2.time_begin is NULL) /* 2421909 = 11. November 1918*/
    and (p2.time_end   > 24044292 or p2.time_end   is NUll) /* 2404429 = 1. Januar 1871, 2420342 = 28. Juli 1914*/
    and 
    (
        /*p2.type_object in ('5', '32', '36', '37', '110', '99', '78', '2', '149', '211', '212', '95') /* Kreisähnliche Gebilde */
        /*or
        /*p2.type_object in ('270', '25', '207', '134') /* Kreisähnlich Österreich-Ungarn, Schweiz*/
        /*or*/
        p2.type_object in ('275', '136') /* Unterste Verwaltungsseinheit Österreich-Ungarn, Schweiz */
        or
        p2.type_object in ('1', '53', '95', '18', '85', '144', '150', '218') /* unterste Verwaltungseinheiten */
        or 
        p2.type_object in ('51', '55', '120', '230', '54', '39', '69', '129', '40', '54') /* unterste Wohnplätze */
    )
);
/* ---- Kreisähnliche Gebilde
----- basierend auf https://upload.wikimedia.org/wikipedia/commons/1/17/Karte_Deutsches_Reich%2C_Verwaltungsgliederung_1900-01-01.png
Bezirk  5
Kreis   32
Landkreis 36
Oberamt 37
Bezirksamt  110
Amtshauptmannschaft 99
Aushebungsbezirk    nicht im GOV als Typ vorhanden
Amt (kreisähnlich)  78
Amtsbezirk  2
Landratsamt 149
Landgebiet  211
Landherrschaft  212
Kreisfreie Stadt    95
Stadtteil (Verwaltung)  262
Bezirk (Österreich) 270
Kanton (Schweiz)    25
Oberamt/Oberamtsbezirk  207
Arrondissement (Schweiz) 134
*/

/* ------ Unterste Verwaltungseinheiten
Amt 1
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
