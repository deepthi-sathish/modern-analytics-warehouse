select
    prd_id,
    replace(substring(prd_key from 1 for 5), '-', '_') as cat_id,
    substring(prd_key from 7) as prd_key,
    prd_nm,
    coalesce(prd_cost, 0) as prd_cost,
    case upper(trim(prd_line))
        when 'M' then 'Mountain'
        when 'R' then 'Road'
        when 'S' then 'Sales'
        when 'T' then 'Touring'
        else 'N/A'
    end as prd_line,
    cast(prd_start_dt as date) as prd_start_dt,
    cast(
        lead(prd_start_dt) over (partition by prd_key order by prd_start_dt)
        - interval '1 day' as date
    ) as prd_end_dt,
    current_timestamp as dwh_create_date
from {{ source('bronze', 'crm_prd_info') }}