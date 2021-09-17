---- property: names
select g1.id, p1.content, p1.language, p1.time_begin, p1.time_end
from property p1
inner join gov_item g1
on g1.id = p1.gov_object 
where p1.property_class = "n"
;
