TRUNCATE TABLE bronze.crm_cust_info;
COPY bronze.crm_cust_info FROM '/data/source_crm/cust_info.csv' WITH (FORMAT csv, HEADER true);

TRUNCATE TABLE bronze.crm_prd_info;
COPY bronze.crm_prd_info FROM '/data/source_crm/prd_info.csv' WITH (FORMAT csv, HEADER true);

TRUNCATE TABLE bronze.crm_sales_details;
COPY bronze.crm_sales_details FROM '/data/source_crm/sales_details.csv' WITH (FORMAT csv, HEADER true);

TRUNCATE TABLE bronze.erp_cust_az12;
COPY bronze.erp_cust_az12 FROM '/data/source_erp/CUST_AZ12.csv' WITH (FORMAT csv, HEADER true);

TRUNCATE TABLE bronze.erp_loc_a101;
COPY bronze.erp_loc_a101 FROM '/data/source_erp/LOC_A101.csv' WITH (FORMAT csv, HEADER true);

TRUNCATE TABLE bronze.erp_px_cat_g1v2;
COPY bronze.erp_px_cat_g1v2 FROM '/data/source_erp/PX_CAT_G1V2.csv' WITH (FORMAT csv, HEADER true);