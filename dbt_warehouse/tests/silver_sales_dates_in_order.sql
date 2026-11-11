select sls_ord_num, sls_order_dt, sls_ship_dt, sls_due_dt
from {{ ref('crm_sales_details') }}
where sls_order_dt > sls_ship_dt
   or sls_order_dt > sls_due_dt