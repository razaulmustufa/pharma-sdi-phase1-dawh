-- SDI Phase 1: analytical SQL queries for report / demo
-- Run against DATABASE sdi_phase1 (not the Airflow metadata database).

-- 1. Fact tables: verify complete load
SELECT 'FactSales' AS table_name, COUNT(*) AS row_count FROM mart.fact_sales
UNION ALL
SELECT 'FactDemand', COUNT(*) FROM mart.fact_demand;

-- 2. Conformed dimensions / Fact Constellation
SELECT 'DimDate' AS table_name, COUNT(*) FROM mart.dim_date
UNION ALL SELECT 'DimMedicine', COUNT(*) FROM mart.dim_medicine
UNION ALL SELECT 'DimLocation', COUNT(*) FROM mart.dim_location
UNION ALL SELECT 'DimPharmacy', COUNT(*) FROM mart.dim_pharmacy
UNION ALL SELECT 'DimHospital', COUNT(*) FROM mart.dim_hospital
UNION ALL SELECT 'DimChannel', COUNT(*) FROM mart.dim_channel;

-- 3. Sales channel revenue / margin
SELECT c.sales_channel, COUNT(*) AS transactions,
       ROUND(SUM(f.net_sales_usd), 2) AS net_revenue_usd,
       ROUND(SUM(f.gross_margin_usd), 2) AS gross_margin_usd,
       ROUND(100 * SUM(f.gross_margin_usd) / NULLIF(SUM(f.net_sales_usd),0),2) AS gross_margin_pct
FROM mart.fact_sales f JOIN mart.dim_channel c USING(channel_key)
GROUP BY c.sales_channel ORDER BY net_revenue_usd DESC;

-- 4. Monthly hospital demand vs consumption
SELECT d.year_number, d.month_number,
       SUM(f.forecast_demand_packs) AS forecast_packs,
       SUM(f.consumed_quantity_packs) AS consumed_packs,
       SUM(f.unfulfilled_demand_packs) AS unfulfilled_packs,
       SUM(f.stockout_days) AS stockout_days
FROM mart.fact_demand f JOIN mart.dim_date d USING(date_key)
GROUP BY d.year_number, d.month_number ORDER BY d.year_number, d.month_number;

-- 5. Cold-chain fast-moving medicines
SELECT m.generic_name, m.therapeutic_class,
       SUM(f.quantity_sold_packs) AS quantity_packs,
       SUM(f.net_sales_usd) AS revenue_usd
FROM mart.fact_sales f JOIN mart.dim_medicine m USING(medicine_key)
WHERE m.cold_chain_flag='Y'
GROUP BY m.generic_name, m.therapeutic_class
ORDER BY quantity_packs DESC LIMIT 10;

-- 6. Sales vs demand by shared location (preaggregated to avoid fact-to-fact row multiplication)
WITH sales AS (
    SELECT location_key, SUM(quantity_sold_packs) AS sold_packs FROM mart.fact_sales GROUP BY location_key
), demand AS (
    SELECT location_key, SUM(consumed_quantity_packs) AS consumed_packs,
           SUM(unfulfilled_demand_packs) AS unfulfilled_packs
    FROM mart.fact_demand GROUP BY location_key
)
SELECT l.city,l.state,COALESCE(s.sold_packs,0) AS sold_packs,
       COALESCE(d.consumed_packs,0) AS consumed_packs,
       COALESCE(d.unfulfilled_packs,0) AS unfulfilled_packs
FROM mart.dim_location l
LEFT JOIN sales s USING(location_key)
LEFT JOIN demand d USING(location_key)
ORDER BY l.state,l.city;

-- 7. Batch ingestion observability
SELECT source_name, MAX(attempted_at) AS last_load,
       SUM(scanned_rows) AS cumulative_processed, SUM(newly_inserted_rows) AS cumulative_new_rows,
       ROUND(AVG(elapsed_seconds)::numeric,2) AS avg_load_seconds
FROM ops.batch_load_log GROUP BY source_name ORDER BY source_name;

-- 8. Query observability
SELECT query_name, COUNT(*) AS execution_count,
       ROUND(AVG(duration_ms)::numeric,2) AS avg_exec_ms
FROM ops.query_log GROUP BY query_name ORDER BY query_name;
