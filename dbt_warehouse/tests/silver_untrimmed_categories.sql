select id, cat, subcat, maintenance
from {{ ref('erp_px_cat_g1v2') }}
where cat != trim(cat)
   or subcat != trim(subcat)
   or maintenance != trim(maintenance)