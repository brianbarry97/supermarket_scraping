-- Data-quality guardrail for the scrapers.
--
-- The staging models drop stale-ID rows (error = 'Not found in any store'), which is benign --
-- the ID feed simply lags the price scrape. This test watches for every OTHER failure mode so a
-- real outage can't hide behind that filter. Concretely: Tesco started returning HTTP 429 on
-- ~56% of requests from 2026-08-09 onwards, which this test would have caught on day one.
--
-- Reads the raw sources directly (four S3 scans -- deliberately not cheap; it is a monitor, run
-- it on the daily build, not on every `dbt test`). Warns rather than errors so a scraper problem
-- is loud without blocking analytics on data that is still partially usable.
--
-- To see the full per-retailer / per-error-string breakdown, run the `agg` CTE below on its own.

{{ config(severity = 'warn') }}

WITH raw AS (
    -- CAST to VARCHAR: `error` is inferred as JSON for some retailers, which makes the string
    -- comparison below try to JSON-parse the literal.
    SELECT 'aldi'      AS retailer, CAST(error AS VARCHAR) AS error FROM {{ source('external_source', 'aldi') }}
    UNION ALL
    SELECT 'tesco'     AS retailer, CAST(error AS VARCHAR) AS error FROM {{ source('external_source', 'tesco') }}
    UNION ALL
    SELECT 'dunnes'    AS retailer, CAST(error AS VARCHAR) AS error FROM {{ source('external_source', 'dunnes') }}
    UNION ALL
    SELECT 'supervalu' AS retailer, CAST(error AS VARCHAR) AS error FROM {{ source('external_source', 'supervalu') }}
),

agg AS (
    SELECT
        retailer,
        count(*) AS total_records,
        count(*) FILTER (
            WHERE error IS NOT NULL AND error <> 'Not found in any store'
        ) AS non_stale_errors,
        round(
            100.0 * count(*) FILTER (
                WHERE error IS NOT NULL AND error <> 'Not found in any store'
            ) / nullif(count(*), 0),
            1
        ) AS non_stale_error_pct
    FROM raw
    GROUP BY retailer
)

SELECT *
FROM agg
WHERE non_stale_error_pct >= 5.0
