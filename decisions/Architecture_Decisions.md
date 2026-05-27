# Tech Stack

- Python for ingestion scripts — learning production-level Python, not notebooks
- BigQuery as the warehouse — widely used in industry, appears constantly in job descriptions, worth learning the credential management and IAM patterns even at small scale
- dbt Core for transformation — industry standard for analytics engineering, enforces good practices
- GitHub Actions for CI and scheduled pipeline runs — simple orchestration without Airflow complexity
- Docker to containerize the pipeline — demonstrates reproducibility, credentials passed as environment variables not baked into the image
- Jupyter plus pandas, scipy, and seaborn for analysis
- Streamlit for a lightweight frontend
- Pydantic for data validation in the ingestion layer

# Data Modelling Design Decisions

## Final Data Model

- Chose the Star schema with fact and dimension tables
  - The final data model should look like this:

    Raw tables (loaded by your ingestion scripts)
    ├── raw_repositories ← one row per repo, metadata snapshot
    ├── raw_star_history ← star activity (raw, no aggregates)
    ├── raw_commit_activity ← commit activity (raw, no aggregates)
    ├── raw_page_views
    ├── raw_repository_clones
    └── raw_repo_topics ← topics tags per repo

    Staging (dbt, one-to-one with raw)
    ├── stg_repositories
    ├── stg_star_history
    ├── stg_commit_activity
    ├── stg_page_views
    ├── stg_repository_clones
    └── stg_repo_topics

    Marts (dbt, built for analysis)
    ├── dim_repositories ← one row per repo with category derived from topics
    ├── fct_weekly_activity ← one row per repo per week, stars, commits, page views & repo clones together
    (└── mart_correlation_analysis ← pre-aggregated for the statistical analysis)

## Why not other approaches?

- **One Big Table (ONF):** would remove the data modelling part which I wanted to include for this portfolio project.
- **Third Normal Form (3NF):** used in transactional systems like a bank, a hospital or an e-commerce system.
- **Data Vault:** used for large enterprises where data volumes are massive and data comes from a variety of different data sources which does not apply here.

## Why raw event data and not pre-aggregated data?

Wanted to create real-world dataset where data is not just suited for this usecase, but where I can apply real transformations

# API Endpoints

## Why Github API?

## Github API Endpoints

- raw_repositories ← one row per repo, metadata snapshot
  -> https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#get-a-repository
- raw_star_history ← star activity (raw, no aggregates)
  -> https://docs.github.com/en/rest/activity/starring?apiVersion=2026-03-10
- raw_commit_activity ← commit activity (raw, no aggregates)
  -> Single Commits: https://docs.github.com/en/rest/commits/commits?apiVersion=2026-03-10
  [DROP] (-> Weekly Commit Counts (aggregated): https://docs.github.com/en/rest/metrics/statistics?apiVersion=2026-03-10#get-the-weekly-commit-activity)
- raw_repo_topics ← topics tags per repo
  [DROP] -> https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#get-all-repository-topics
  -> https://docs.github.com/en/rest/repos/repos?apiVersion=2026-03-10#get-a-repository (under "Topics" key in the response)

# Data

## Why those specific columns and not others?

# Analysis Approach

## Why commits as proxy for development activity?

Page Views and Repo Clones are only available to repo admins and were therefore disregarded.
