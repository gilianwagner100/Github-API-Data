{{ config(materialized='table') }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_star_history') }}
)

SELECT
    repo_id,
    repo_full_name,
    user_id,
    user_login,
    CAST(starred_at AS TIMESTAMP) AS starred_at,
    CAST(load_timestamp AS TIMESTAMP) AS load_timestamp
FROM source