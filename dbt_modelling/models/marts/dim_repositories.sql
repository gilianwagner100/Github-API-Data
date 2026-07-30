{{ config(materialized='table') }}

SELECT
    repo_id,
    repo_name,
    owner_id,
    owner_login,
    description,
    forks_count,
    stargazers_count,
    topics,
    repo_category,
    created_at,
    pushed_at,
    load_timestamp  
FROM {{ ref('stg_repositories') }}