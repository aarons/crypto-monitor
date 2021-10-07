-- This query can be used to create a queryable table in athena
-- TODO: currently it's loading the first line of each json file, instead of all 9000 lines
--       probably has to do with SERDE properties.
CREATE EXTERNAL TABLE IF NOT EXISTS
    `market_summaries` (
        `price_last` double,
        `price_high` double,
        `price_low` double,
        `price_change_percentage` double,
        `price_change_absolute` double,
        `volume` double,
        `volumequote` double,
        `market` string,
        `asset` string,
        `created_at` timestamp
    )
    ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
    WITH SERDEPROPERTIES (
        'serialization.format' = '1'
        )
    LOCATION 's3://crypto-monitor-data/raw'
    TBLPROPERTIES ('has_encrypted_data'='false')
;