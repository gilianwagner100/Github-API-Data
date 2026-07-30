{{ config(materialized='table') }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_commit_activity') }}
)

SELECT
    sha AS commit_sha,
    repo_id,
    CAST(commit_date AS TIMESTAMP) AS committed_at,
    author_id,
    author_login,
    committer_id,
    committer_login,
    CAST(load_timestamp AS TIMESTAMP) AS load_timestamp
FROM source