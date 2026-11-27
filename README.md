# Pharmaceutical Cold Supply Chain — Phase 1: Sales & Demand Intelligence (SDI)

**IBA Karachi | Data Analytics & Warehousing | Fall 2026**  
**Phase:** 1 — Sales & Demand Intelligence (SDI)

## Project overview

This Phase 1 implementation provides a sales and hospital-demand data mart for the pharmaceutical cold supply chain. The implemented stack includes PostgreSQL 16, Apache Airflow 3.4, Docker/WSL2, Grafana (Data Engineering monitoring) and Power BI (Business Intelligence).

## Verified Phase 1 implementation

| Component | Recorded result |
|---|---:|
| Source validation DAG | 4/4 tasks successful |
| ETL DAG | 7/7 tasks successful |
| Initial fact records | 500,000 sales / 27,216 hospital-demand records |
| Incremental refresh 1 (Jan 2026) | 502,000 sales / 27,516 demand records |
| Incremental refresh 2 (Feb 2026) | 504,000 sales / 27,816 demand records |
| Dimensional model | 6 dimensions / 2 fact tables |
| PostgreSQL mart indexes | 22 |
| Analytical SQL query types | 4 |
| Grafana ingestion monitoring | 10 logged batch loads; 100% logged success rate |
| Grafana storage monitoring | 356.51 MB database footprint; 1,155 date rows |
| Grafana query monitoring | 12 logged executions; 100% logged success; 375.56 ms average in query log |
| Power BI | 8 visuals; 6.01M sales revenue; 504K transactions; 6.38M requested demand packs |

The separately recorded `EXPLAIN ANALYZE` execution time was 1,410.275 ms. This is a distinct test and should not be confused with the 375.56 ms query-log average.

## Dimensional model

**Dimensions:** `dim_date`, `dim_medicine`, `dim_location`, `dim_pharmacy`, `dim_hospital`, `dim_channel`.

**Facts:**
- `fact_sales` — pharmacy sales transaction grain.
- `fact_demand` — hospital medicine-demand record grain.

Date, Medicine and Location are shared conformed dimensions. The `staging` schema holds the Phase 1 source data used by this implementation; the `ops` schema holds ingestion and query audit logs.

## Phase 1 source scope and refreshes

The Phase 1 Sales & Demand Intelligence implementation uses these three source CSVs:
- `01_master_data.csv`
- `05_pharmacy_sales_data.csv`
- `06_hospital_demand_data.csv`

Two additive synthetic refresh batches were generated for January and February 2026 and loaded into the existing warehouse. The same generator batch IDs must not be rerun against an already populated environment, or records may be duplicated.

The remaining source domains and broader requirements—seven-source oversampling, automated file-watcher/API ingestion, and streaming IoT—belong to the wider project scope and are not represented as completed by this Phase 1 snapshot.

## Repository files (current uploaded layout)

The current GitHub upload stores the files at the repository root:

- `docker-compose.yaml` — sanitized Docker Compose template; local secrets are supplied through `.env`.
- `.env.example` — placeholder template only; copy to `.env` locally and set private values.
- `sdi_phase1_etl.py` — Phase 1 ETL DAG source.
- `sdi_phase1_source_validation.py` — source validation DAG source.
- `sdi_generate_refresh.py` — additive refresh generator.
- `sdi_phase1_queries.sql` — analytical SQL queries.
- `01_Ingestion_Monitoring.json`, `02_Storage_Monitoring.json`, `03_Query_Monitoring.json` — Grafana dashboard exports.
- `01_Airflow_ETL.png`, `02_Grafana_Ingestion.png`, `03_Grafana_Storage.png`, `04_Grafana_Query.png`, `05_PowerBI_Final_Dashboard.png` — evidence screenshots.
- `Phase.1.Report.pdf` — Phase 1 report.
- `SDI.Excel.xlsx` — instructor SDI template.
- `SDI_Phase1_Business_Intelligence_Final.pbix` — Power BI report file.
- `Group_Info.txt` — group details; verify that all placeholders have been replaced.
- `README_SECURITY.txt` — instructions for keeping secrets out of public version control.

## Local setup notes

1. Install Docker Desktop with WSL2 and use the sanitized `docker-compose.yaml` with a private local `.env` file. Copy `.env.example` to `.env` and replace every placeholder with valid private values. **Never upload `.env`.**
2. The Compose file mounts `./dags` into `/opt/airflow/dags`. Because the DAG Python files are currently stored at the repository root, create a local `dags` folder and copy the three Python files into it before starting Airflow. For example, in PowerShell from the repository directory:

   ```powershell
   New-Item -ItemType Directory -Force .\dags | Out-Null
   Copy-Item .\sdi_phase1_etl.py, .\sdi_phase1_source_validation.py, .\sdi_generate_refresh.py .\dags\
   ```

3. Create `dags/data` locally and place the three supplied Phase 1 CSV source files there. Raw source data is not included in this public repository.
4. Start the local Docker Compose environment and run the source-validation DAG before the ETL DAG.
5. Verify fact counts in the `mart` schema and review `ops` ingestion/query logs.
6. In Grafana, configure a PostgreSQL data source pointing to the local database and import the three dashboard JSON files. A different Grafana instance may require selecting/remapping its data source.
7. Open the PBIX in Power BI Desktop. Refreshing it requires a working local PostgreSQL connection; the saved report and screenshots are included here as project evidence.

This is a classroom/local-development implementation, not a production deployment. The public repository intentionally excludes raw CSV data and private secrets.

## Submission and remaining items

The demo video has **not yet been recorded** and is not claimed as complete; it is planned as a later addition. Add its link to this README after recording, if the instructor permits a later update.

Phase 2 focuses on inventory, expiry and replenishment. Phase 3 focuses on end-to-end traceability and IoT cold-chain performance.
