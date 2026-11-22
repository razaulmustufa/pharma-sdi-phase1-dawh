# Pharmaceutical Cold Supply Chain — Phase 1: Sales & Demand Intelligence (SDI)

**IBA Karachi | Data Analytics & Warehousing | Fall 2026**  
**Submission date:** 22 November 2026  
**Group information:** Complete `Group_Info.txt` before submitting the GitHub link.

## Project overview
A functional dimensional data warehouse and Business Intelligence solution for pharmacy sales and hospital-demand analysis. The implementation uses PostgreSQL 16, Apache Airflow 3.4, Docker/WSL2, Grafana and Power BI Desktop.

### Verified implementation
| Milestone | Result |
|---|---:|
| Validation DAG | 4/4 tasks successful |
| ETL DAG | 7/7 tasks successful |
| Initial sales / demand fact records | 500,000 / 27,216 |
| Refresh 1, Jan 2026 | 502,000 / 27,516 |
| Refresh 2, Feb 2026 | **504,000 / 27,816** |
| Warehouse design | 6 dimensions / 2 facts |
| PostgreSQL mart indexes | 22 |
| Analytical SQL types | 4 |
| Ingestion Grafana dashboard | 10 batch loads, 100% logged success |
| Storage Grafana dashboard | 356.51 MB database, 1,155 date rows |
| Query Grafana dashboard | 12 executions, 100% success, 375.56 ms average |
| Business Power BI | 8 visuals, 6.01M sales revenue, 504K transactions, 6.38M demand packs |

The SQL EXPLAIN execution time of **1,410.275 ms** is a separate measured test; it is not the query-log mean.

## Dimensional model
- `mart.dim_date`, `dim_medicine`, `dim_location`, `dim_pharmacy`, `dim_hospital`, `dim_channel`.
- `mart.fact_sales`: pharmacy transaction grain.
- `mart.fact_demand`: hospital demand record grain.
- Shared conformed dimensions: Date, Medicine, Location.
- `staging` stores imported master / sales / demand files; `ops` stores ingestion and query audit logs.

## Data pipeline
Three Phase 1 CSV sources — `01_master_data.csv`, `05_pharmacy_sales_data.csv`, `06_hospital_demand_data.csv` — flow through the source validation and Airflow ETL pipelines into staging, dimensional mart, analytical SQL and monitoring/BI.

The two synthetic additive refreshes were **manually generated** with `dags/sdi_generate_refresh.py` and loaded by the ETL DAG. Do not rerun the same generator batch IDs on an existing populated environment.

## Repository contents
```
Phase.1.Report.pdf               5-page evidence-backed report
SDI.Excel.xlsx                   Instructor SDI template
dags/                            Airflow ETL, validation and refresh generator
sql/                             Four analytical SQL queries
grafana/                         3 importable Grafana dashboard JSON exports
evidence/                        Airflow, Grafana, Power BI and SQL evidence
docs/                            Methodology and optional future demo guide
Group_Info.txt                   Team details (fill before submission)
.gitignore                       Excludes private/large runtime data
```

**Additional local file:** `SDI_Phase1_Business_Intelligence_Final.pbix` is on the student's Windows PC and must be uploaded alongside these package contents. Likewise, the existing local `docker-compose.yaml` should be included **only after removing inline passwords, secrets and private environment-specific values**.

## Grafana (data engineering dashboards)
1. **SDI | 01 Ingestion Monitoring** — batch volume, load duration, success rate and audit rows.
2. **SDI | 02 Storage Monitoring** — row counts, database size, table footprints and schema breakdown.
3. **SDI | 03 Query Monitoring** — query count, success/error rates, runtime trend and query audit.

Import `grafana/*.json` into Grafana and point their data source to the deployed PostgreSQL database `sdi_phase1` (`ops` and `mart` schemas). The original data-source UID may need remapping when importing into a different Grafana instance.

## Power BI (business intelligence dashboard)
Single-page report **SDI | Sales & Demand Intelligence**, displaying:
- Sales revenue ($6.01M), sales transactions (504K), hospital demand (6.38M packs)
- Monthly sales revenue trend and channel comparison
- Hospital demand by city
- Top 10 medicines by revenue and by hospital demand

Power BI is imported from PostgreSQL via the student environment (`127.0.0.1:5433` local bridge); it is not a public data source. A viewer needs a working data source to refresh the `.pbix`, but the saved report and evidence screenshots are available in this repository.

## How to run locally
1. On Windows, enable Docker Desktop with WSL2 and use the course Airflow Docker Compose environment.
2. Use the student's reviewed `docker-compose.yaml` and local environment variables. Never commit live secrets.
3. Initialize database `sdi_phase1` in PostgreSQL and place the three actual CSVs under the mounted `dags/data/` folder.
4. Run `sdi_phase1_source_validation`, then `sdi_phase1_etl` in Airflow.
5. Review `ops.batch_load_log`, `ops.query_log` and `mart` fact counts.
6. Start Grafana on the Docker network, connect PostgreSQL as a read-only data source and import the three JSON dashboards.
7. Open the `.pbix` in Power BI Desktop and update the database connection when necessary.

The zipped repository intentionally omits raw large CSV files and any passwords. This is a classroom implementation, not a production-deployment guarantee.

## Important delivery notes
**Demo video:** Not recorded at the time of this initial repository preparation; to be added later. It is **not** claimed as completed. The instructor's requirement still needs attention.
**Phase 2:** Inventory/expiry integration. **Phase 3:** IoT cold-chain traceability.
Other full-course objectives (seven-source oversampling, file watcher, ingestion API and automated streaming) remain beyond the implemented Phase 1 snapshot.
