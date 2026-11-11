select
    replace(cid, '-', '') as cid,
    case
        when trim(cntry) = 'DE' then 'Germany'
        when trim(cntry) in ('US', 'USA', 'United States') then 'United States'
        when trim(cntry) = '' or cntry is null then 'N/A'
        else trim(cntry)
    end as cntry,
    current_timestamp as dwh_create_date
from {{ source('bronze', 'erp_loc_a101') }}