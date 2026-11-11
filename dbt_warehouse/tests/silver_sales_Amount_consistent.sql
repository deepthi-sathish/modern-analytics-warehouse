select sls_ord_num, sls_sales, sls_quantity, sls_price
from {{ ref('crm_sales_details') }}
where sls_sales is null or sls_quantity is null or sls_price is null
   or sls_sales <= 0 or sls_quantity <= 0 or sls_price <= 0
   or sls_sales != sls_quantity * sls_price