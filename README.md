# Modern Analytics Warehouse
<p align="center">
  <strong>Building a modern analytical data warehouse using CRM and ERP data</strong>
</p>

An End-to-End Data Engineering Project with **PostgreSQL, Docker, and dbt**. The project transforms raw CRM and ERP data into structured, analytics-ready datasets through a layered warehouse architecture, with data quality tests and documented model lineage.

## Project Overview

The project implements a Medallion Architecture (Bronze, Silver and Gold) using PostgreSQL and dbt. It demonstrates relational data modelling, SQL-based transformations, data quality engineering, dimensional modelling and reproducible development using Docker.

The objective is to build a modular and maintainable warehouse that turns raw operational data into reliable datasets for downstream analytics and reporting.

The three layers:

- **Bronze:** Stores the raw CRM and ERP source data in PostgreSQL.
- **Silver:** Cleans and transforms the raw data using dbt models.
- **Gold:** Creates analytical fact and dimension views using a star-schema approach.

## Architecture

```text
          CRM Source CSVs       ERP Source CSVs
                 │                     │
                 └──────────┬──────────┘
                            ▼
                    PostgreSQL
                    Bronze Layer
                    (Raw Tables)
                            │
                            ▼
                         dbt
                            │
                            ▼
                    Silver Layer
                 (Cleaned & Transformed)
                            │
                            ▼
                      Gold Layer
                (Analytical Data Models)
                            │
                            ▼
                  Analytics-Ready Data
```

## Technology Stack

| Category | Technologies |
|---|---|
| Database | PostgreSQL 16 |
| Data Transformation | dbt Core, dbt-postgres |
| Containerization | Docker, Docker Compose |
| Query Language | SQL |
| Programming | Python |
| Version Control | Git, GitHub |
| Development Environment | Visual Studio Code |

## Data Sources

The project uses six CSV files from two source systems.

**CRM**
- `cust_info.csv`
- `prd_info.csv`
- `sales_details.csv`

**ERP**
- `CUST_AZ12.csv`
- `LOC_A101.csv`
- `PX_CAT_G1V2.csv`

The source data is stored in six corresponding Bronze tables in PostgreSQL.

## Data Transformation

### 1. Bronze Layer - Raw Data Storage

- Stores the six raw CRM and ERP datasets in PostgreSQL.
- Preserves the source data for downstream transformations.

### 2. Silver Layer - Data Cleaning & Transformation

Built six dbt models to clean and standardize the source data.

Implemented transformations include:
- Removing duplicate customer records.
- Handling null and invalid values.
- Standardizing customer names and categorical fields.
- Converting and cleaning date fields.
- Applying business rules to product and sales data.
- Preparing consistent datasets for analytical modelling.

Each model is independently maintained and materialized as a PostgreSQL table.

### 3. Gold Layer - Dimensional Modelling

The Gold layer provides business-oriented datasets designed for analytical queries and reporting.

Created three analytical models:

| Model | Description |
|---|---|
| `dim_customers` | Customer dimension combining CRM and ERP customer information. |
| `dim_products` | Product dimension enriched with ERP product category information. |
| `fact_sales` | Sales fact model connecting sales records to customer and product dimensions. |

The Gold layer uses a **star-schema design**, using one fact model and two dimension models.

Gold models are materialized as PostgreSQL views.

## Data Quality & Testing

Implemented dbt generic tests and custom SQL tests to validate the transformed data.

**Generic tests include:**
- `not_null: `Checking mandatory identifiers and attributes.
- `unique: `Ensuring key identifiers are not duplicated.
- `accepted_values: `Validating standardized categorical values. 
- `relationships: `Checking relationships between customer, product and sales records.

**Custom SQL tests validate:**
- Untrimmed customer names.
- Untrimmed product categories.
- Invalid product date ranges.
- Sales date consistency.
- Sales amount calculations.
- Customer birth-date ranges.
- Fact-to-dimension connectivity.

### Test Results

| Layer | Tests | Passed | Warnings | Errors |
|---|---:|---:|---:|---:|
| Silver | 24 | 23 | 1 | 0 |
| Gold | 13 | 13 | 0 | 0 |
| **Total** | **37** | **36** | **1** | **0** |

### Data Quality Observation

During validation, 15 customer records were identified with birth dates earlier than 1924. The oldest recorded date is 1916-02-10.

These records are flagged by a dbt warning and deliberately left unchanged because there is insufficient evidence to classify them as incorrect.

This preserves the original customer records while making the data quality issue visible for further investigation.

## Validation Results

The following row counts were verified against the PostgreSQL Gold models:

| Gold Model | Validated Records |
|---|---:|
| dim_customers | 18,484 |
| dim_products | 295 |
| fact_sales | 60,398 |

The product dimension contains only products without an end date, as defined by the model's active-product filter.

The customer and sales row counts match their corresponding Silver models. The product dimension contains only active products, as defined by the model's end-date filter.

## Project Structure

```text
modern_warehouse/
│
├── datasets/
│   ├── source_crm/
│   └── source_erp/
│
├── dbt_warehouse/
│   ├── models/
│   │   ├── silver/
│   │   │   ├── crm_cust_info.sql
│   │   │   ├── crm_prd_info.sql
│   │   │   ├── crm_sales_details.sql
│   │   │   ├── erp_cust_az12.sql
│   │   │   ├── erp_loc_a101.sql
│   │   │   ├── erp_px_cat_g1v2.sql
│   │   │   ├── sources.yml
│   │   │   └── schema.yml
│   │   │
│   │   └── gold/
│   │       ├── dim_customers.sql
│   │       ├── dim_products.sql
│   │       ├── fact_sales.sql
│   │       └── schema.yml
│   │
│   ├── macros/
│   │   └── generate_schema_name.sql
│   │
│   ├── tests/
│   │   └── [custom SQL data tests]
│   │
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── docs/
│   └── dbt-lineage.png
|
├── sql/bronze
|   ├── check_counts.sql
|   ├── ddl_bronze.sql
|   └── load_bronze.sql
|
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Docker Desktop
- Python
- dbt Core with the PostgreSQL adapter
- Git

### 1. Start PostgreSQL using Docker Compose

From the project root:

```bash
docker compose up -d
```

### 2. Activate the Python virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Navigate to the dbt project

```powershell
cd dbt_warehouse
```

Configure your local dbt `profiles.yml` with the PostgreSQL connection details.

Note: The six Bronze source tables must be created and populated in PostgreSQL before running the dbt models. The current repository uses an already-populated local warehouse; automated source ingestion is not yet implemented.

### 4. Check the connection

```bash
dbt debug
```

### 5. Run the dbt models and Execute data quality tests

```bash
dbt run
```

```bash
dbt test
```

### 6. Generate and view documentation

```bash
dbt docs generate
dbt docs serve
```

Open [`http://localhost:8080`](http://localhost:8080) to explore the dbt documentation and model lineage.

## Documentation

The project includes a dbt lineage screenshot showing the relationships between the Bronze sources, Silver transformations, Gold analytical models and associated tests.

See [`docs/dbt-lineage.png`](docs/dbt-lineage.png).

---

## Author

**Deepthi Sathish Kumar**

M.Sc. Computer Science | RPTU Kaiserslautern-Landau

[LinkedIn](https://www.linkedin.com/in/deepthi-cs/) · [GitHub](https://github.com/deepthi-sathish)
