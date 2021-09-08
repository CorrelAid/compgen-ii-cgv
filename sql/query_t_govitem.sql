---- gov_item
with recursive new_table as 
(
    select o.child, o.parent, o.time_begin, o.time_end
    from relation o 
    /*190315=Deutches Reich, 191050=Schweiz, 306245=Österreich-Ungarn, 220100=Liechtenstein, 218129=Luxemburg*/
    where o.parent in ("190315", "191050", "306245", "2201000", "218129") 
    union 
    select o.child, o.parent , o.time_begin, o.time_end
    from relation o, new_table c 
    where o.parent = c.child
    and (c.time_begin < 24219092 or c.time_begin is NULL) /* 2421909 = 11. November 1918*/
    and (c.time_end   > 24044292 or c.time_end   is NUll) /* 2404429 = 1. Januar 1871, 2420342 = 28. Juli 1914*/
) 
select g1.id, g1.textual_id, g1.deleted
from gov_item g1 
where g1.id in
(
    select n.child
    from new_table n
);
