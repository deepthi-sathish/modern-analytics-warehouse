select cst_id, cst_firstname, cst_lastname
from {{ ref('crm_cust_info') }}
where cst_firstname != trim(cst_firstname)
   or cst_lastname != trim(cst_lastname)