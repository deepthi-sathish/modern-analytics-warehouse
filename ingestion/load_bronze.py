"""Bronze ingestion: load CSV files into Postgres with validation and an audit log."""
import csv
import logging
import os
import sys
import time
import uuid
from pathlib import Path

import psycopg2

DATA_DIR = Path(os.getenv("DATA_DIR", "datasets"))
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))

TABLES = [
    ("bronze.crm_cust_info", "source_crm/cust_info.csv"),
    ("bronze.crm_prd_info", "source_crm/prd_info.csv"),
    ("bronze.crm_sales_details", "source_crm/sales_details.csv"),
    ("bronze.erp_cust_az12", "source_erp/CUST_AZ12.csv"),
    ("bronze.erp_loc_a101", "source_erp/LOC_A101.csv"),
    ("bronze.erp_px_cat_g1v2", "source_erp/PX_CAT_G1V2.csv"),
]

log = logging.getLogger("load_bronze")

# Logging configuration
def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)  # create log dir if it doesn't exist
    logging.basicConfig(
        level=logging.INFO,  # records informational messages and errors
        format="%(asctime)s %(levelname)s %(message)s", # timestamp, severity level, message
        handlers=[
            logging.StreamHandler(), # display logs to console
            logging.FileHandler(LOG_DIR / "ingestion.log"), #saves messages in logs/ingestion.log
        ],
    )

#PostgreSQL connection
def connect():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        user=os.getenv("POSTGRES_USER", "warehouse"),
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.getenv("POSTGRES_DB", "warehouse"),
    )

# Read CSV headers and count rows
def read_header(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [col.strip().lower() for col in next(csv.reader(f))]


def count_csv_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return sum(1 for _ in csv.reader(f)) - 1  # minus the header row

# Retrieve PostgreSQL table columns
def get_table_columns(cur, table):
    schema, name = table.split(".") # split the table name into schema and table name
    cur.execute(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """,
        (schema, name),
    )
    return [row[0].lower() for row in cur.fetchall()] # return a list of column names in lowercase

# Validate CSV files before loading!
def validate_file(path, table_columns):
    """Check the file before loading. Returns the number of data rows."""
    if not path.exists():
        raise FileNotFoundError(f"missing file: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"empty file: {path.name}")
    header = read_header(path) # read the header of the CSV file
    if header != table_columns:
        raise ValueError(
            f"header mismatch in {path.name}: file has {header}, table expects {table_columns}"
        )
    return count_csv_rows(path)

# Load CSV data into PostgreSQL
def load_table(cur, table, path):
    cur.execute(f"TRUNCATE TABLE {table}") # clear the table before loading new data
    with open(path, "r", encoding="utf-8") as f:
        cur.copy_expert(f"COPY {table} FROM STDIN WITH (FORMAT csv, HEADER true)", f) # load the CSV data into the table
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    return cur.fetchone()[0]

# Create an ingestion result record
def new_result(table, path, status="success"):
    return {
        "table": table,
        "file": Path(path).name,
        "file_rows": None,
        "loaded_rows": None,
        "status": status,
        "duration_s": 0,
        "error": None,
    }

# Write ingestion results to the audit table
def write_audit(run_id, results):
    try:
        conn = connect() # establish a connection to the PostgreSQL database
        try:
            with conn, conn.cursor() as cur:
                for r in results:
                    cur.execute(
                        """
                        INSERT INTO bronze.load_audit
                            (run_id, table_name, file_name, file_rows, loaded_rows,
                             status, duration_s, error_message)    
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, # insert the ingestion result into the audit table
                        (run_id, r["table"], r["file"], r["file_rows"], r["loaded_rows"],
                         r["status"], r["duration_s"], r["error"]),
                    )
        finally:
            conn.close()
    except Exception as exc:
        log.warning("Could not write audit log: %s", exc)

#the main ingestion function
def main():
    setup_logging()
    run_id = str(uuid.uuid4()) # generate a unique ID for this ingestion run
    log.info("Run %s started (data dir: %s)", run_id, DATA_DIR)
    results = []
    ok = True

    conn = connect()
    try:
        with conn.cursor() as cur:
            for i, (table, rel_path) in enumerate(TABLES): # processes all six tables in order
                path = DATA_DIR / rel_path
                result = new_result(table, path)
                start = time.time()
                try:
                    columns = get_table_columns(cur, table)
                    result["file_rows"] = validate_file(path, columns)
                    result["loaded_rows"] = load_table(cur, table, path)
                    if result["loaded_rows"] != result["file_rows"]:
                        raise ValueError(
                            f"row count mismatch: file has {result['file_rows']}, "
                            f"table has {result['loaded_rows']}"
                        )
                    log.info("%s: loaded %d rows (matches file)", table, result["loaded_rows"])
                except Exception as exc:
                    result["status"] = "failed"
                    result["error"] = str(exc)
                    log.error("%s failed: %s", table, exc)
                result["duration_s"] = round(time.time() - start, 2)
                results.append(result)

                if result["status"] == "failed":
                    ok = False
                    for skipped_table, skipped_path in TABLES[i + 1:]:
                        results.append(new_result(skipped_table, DATA_DIR / skipped_path, "skipped"))
                    break

        if ok:
            conn.commit() # commit all changes if all tables loaded successfully
            log.info("Run %s finished: all %d tables loaded", run_id, len(TABLES))
        else:
            conn.rollback() # rollback all changes if any table failed to load
            for r in results:
                if r["status"] == "success":
                    r["status"] = "rolled_back"
            log.error("Run %s failed: all changes rolled back", run_id)
    finally:
        conn.close()

    write_audit(run_id, results)
    sys.exit(0 if ok else 1)


if __name__ == "__main__": # if this script is run directly, execute the main function
    main()