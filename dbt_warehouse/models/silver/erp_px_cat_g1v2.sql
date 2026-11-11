select
    id,
    cat,
    subcat,
    maintenance,
    current_timestamp as dwh_create_date
from {{ source('bronze', 'erp_px_cat_g1v2') }}