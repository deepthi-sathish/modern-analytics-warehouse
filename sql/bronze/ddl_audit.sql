CREATE TABLE IF NOT EXISTS bronze.load_audit (
    audit_id SERIAL PRIMARY KEY,
    run_id VARCHAR(36),
    table_name VARCHAR(100),
    file_name VARCHAR(200),
    file_rows INT,
    loaded_rows INT,
    status VARCHAR(20),
    duration_s NUMERIC(8,2),
    error_message TEXT,
    loaded_at TIMESTAMP DEFAULT now()
);