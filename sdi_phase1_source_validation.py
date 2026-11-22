"""DAWH Fall 2026 — Phase 1: source file validation (Apache Airflow 3.x).

This is the FIRST runnable step of the SDI pipeline, not the finished ETL.
Place the three input CSV files in DAWH-Phase1/dags/data before triggering.
"""

import csv
from pathlib import Path

import pendulum
from airflow.sdk import dag, task

DATA_DIR = Path('/opt/airflow/dags/data')
SOURCE_FILES = {
    '01_master_data.csv': 'MedicineID',
    '05_pharmacy_sales_data.csv': 'SalesTransactionID',
    '06_hospital_demand_data.csv': 'HospitalDemandRecordID',
}


@dag(
    dag_id='sdi_phase1_source_validation',
    description='Validate the real Sales and Hospital Demand source files before ingestion',
    schedule=None,
    start_date=pendulum.datetime(2026, 11, 1, tz='UTC'),
    catchup=False,
    max_active_runs=1,
    tags=['DAWH', 'Phase-1', 'Sales-Demand'],
)
def sdi_phase1_source_validation():
    @task
    def check_source_files():
        missing = [name for name in SOURCE_FILES if not (DATA_DIR / name).is_file()]
        if missing:
            raise FileNotFoundError(
                f'Missing input CSVs in {DATA_DIR}: {missing}. '
                'Copy the three source CSV files to the Windows dags\\data folder.'
            )
        print('All three required source files are present.')
        return True

    @task
    def profile_csv(filename: str, key_column: str):
        path = DATA_DIR / filename
        rows = 0
        null_keys = 0
        with path.open('r', encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or key_column not in reader.fieldnames:
                raise ValueError(f'{filename} missing required primary key column {key_column}')
            for row in reader:
                rows += 1
                if not (row.get(key_column) or '').strip():
                    null_keys += 1
        if rows == 0:
            raise ValueError(f'{filename} contains no data rows')
        if null_keys:
            raise ValueError(f'{filename} has {null_keys} records with blank {key_column}')
        summary = {'source': filename, 'row_count': rows, 'null_keys': null_keys}
        print(f'SOURCE PROFILE: {summary}')
        return summary

    checked = check_source_files()
    master = profile_csv.override(task_id='profile_medicines')('01_master_data.csv', 'MedicineID')
    sales = profile_csv.override(task_id='profile_sales')('05_pharmacy_sales_data.csv', 'SalesTransactionID')
    demand = profile_csv.override(task_id='profile_demand')('06_hospital_demand_data.csv', 'HospitalDemandRecordID')
    checked >> [master, sales, demand]


sdi_phase1_source_validation()
