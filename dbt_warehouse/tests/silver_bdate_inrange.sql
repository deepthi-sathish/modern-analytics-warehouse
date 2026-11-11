{{ config(severity='warn') }}

select cid, bdate
from {{ ref('erp_cust_az12') }}
where bdate < date '1924-01-01'
   or bdate > current_date