select prd_id, prd_key, prd_start_dt, prd_end_dt
from {{ ref('crm_prd_info') }}
where prd_end_dt < prd_start_dt