---- relation
select o.child, o.parent, o.time_begin, o.time_end
from relation o 
where o.child is not NULL and o.parent is not NULL
;


