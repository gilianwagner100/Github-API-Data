{{ config(materialized='table') }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_repositories') }}
)

SELECT
    id AS repo_id,
    name AS repo_name,
    owner_id,
    owner_login,
    description,
    forks_count,
    stargazers_count,
    topics,
    repo_category,
    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(pushed_at AS TIMESTAMP) AS pushed_at,
    CAST(load_timestamp AS TIMESTAMP) AS load_timestamp  
FROM source