- Chose the Star schema with fact and dimension tables
  - The final data model should look like this:

    Raw tables (loaded by your ingestion scripts)
    ├── raw_repositories ← one row per repo, metadata snapshot (including "topics")
    ├── raw_star_history ← star activity (raw, no aggregates)
    ├── raw_commit_activity ← commit activity (raw, no aggregates)

    Staging (dbt, one-to-one with raw)
    ├── stg_repositories
    ├── stg_star_history
    ├── stg_commit_activity

    Marts (dbt, built for analysis)
    ├── dim_repositories ← one row per repo with category derived from topics
    ├── fct_weekly_activity ← one row per repo per week, stars & commits together
    (└── mart_correlation_analysis ← pre-aggregated for the statistical analysis)

  - Why not other approaches?
    - **One Big Table (ONF):** would remove the data modelling part which I wanted to include for this portfolio project.
    - **Third Normal Form (3NF):** used in transactional systems like a bank, a hospital or an e-commerce system.
    - **Data Vault:** used for large enterprises where data volumes are massive and data comes from a variety of different data sources which does not apply here.