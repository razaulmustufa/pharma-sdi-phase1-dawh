"""Phase 1 demonstrator: generate one deterministic additive CSV batch.

Not an Airflow DAG. Run manually from the Airflow worker with batch 1 or 2.
New ids are deterministic and a per-batch marker prevents ordinary accidental reruns.
For the full project, orchestrate generation as a separate Airflow task and extend to all seven sources.
"""

import csv
import random
import sys
from datetime import date
from pathlib import Path

DATA = Path('/opt/airflow/dags/data')

if len(sys.argv) != 2 or sys.argv[1] not in ('1', '2'):
    raise SystemExit('Usage: python sdi_generate_refresh.py 1 OR 2')

batch = int(sys.argv[1])
month = batch
rng = random.Random(202600 + batch)
sales_path = DATA / '05_pharmacy_sales_data.csv'
demand_path = DATA / '06_hospital_demand_data.csv'
marker = DATA / f'.refresh_{batch}_generated'

if marker.exists():
    raise SystemExit(f'Refresh {batch} already generated. No duplicates added.')


def sample_sales(count):
    sample = []
    eligible = 0
    with sales_path.open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for row in reader:
            try:
                expiry = date.fromisoformat(row['BatchExpiryDate'][:10])
            except (ValueError, TypeError):
                continue
            if expiry <= date(2026, 2, 28):
                continue
            if row['SaleStatus'] != 'Completed':
                continue
            eligible += 1
            if len(sample) < count:
                sample.append(row)
            else:
                j = rng.randrange(eligible)
                if j < count:
                    sample[j] = row
    if len(sample) < count:
        raise RuntimeError('Not enough unexpired sales records')
    return fields, sample


def sample_demand(count):
    latest = {}
    with demand_path.open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        for row in reader:
            key = (row['HospitalID'], row['MedicineID'])
            if key not in latest or row['DemandMonth'] > latest[key]['DemandMonth']:
                latest[key] = row
    rows = list(latest.values())
    if len(rows) < count:
        raise RuntimeError('Not enough unique hospital-medicine pairs')
    return fields, rng.sample(rows, count)


sales_fields, sales_rows = sample_sales(2000)
demand_fields, demand_rows = sample_demand(300)

for i, row in enumerate(sales_rows, 1):
    sale_day = date(2026, month, 1 + ((i - 1) % 28))
    row['SalesTransactionID'] = f'SALE-{900000000 + (batch-1)*100000 + i:09d}'
    row['SalesDate'] = sale_day.isoformat()
    row['SalesTimestampUTC'] = sale_day.isoformat() + 'T12:00:00Z'
    expiry = date.fromisoformat(row['BatchExpiryDate'][:10])
    row['DaysToExpiryAtSale'] = str((expiry - sale_day).days)
    if row.get('PrescriptionID', '').startswith('RX-'):
        row['PrescriptionID'] = f'RX-{900000000 + (batch-1)*100000 + i:09d}'

for i, row in enumerate(demand_rows, 1):
    row['HospitalDemandRecordID'] = f'HDEM-{90000000 + (batch-1)*100000 + i:08d}'
    row['DemandMonth'] = f'2026-{month:02d}-01'


def append_rows(path, fields, rows):
    with path.open('rb+') as f:
        f.seek(-1, 2)
        if f.read(1) not in (b'\n', b'\r'):
            f.write(b'\n')
    with path.open('a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writerows(rows)


append_rows(sales_path, sales_fields, sales_rows)
append_rows(demand_path, demand_fields, demand_rows)
marker.write_text(f'Refresh {batch}: 2000 sales, 300 demand, month=2026-{month:02d}\n')

print(f'REFRESH {batch} GENERATED SUCCESSFULLY')
print('New sales records: 2000')
print('New demand records: 300')
print(f'Month: 2026-{month:02d}')
