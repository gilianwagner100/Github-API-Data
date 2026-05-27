# Project Description

## Research Question

- Since ChatGPT dropped in 2022 and especially with the rise of tools like Claude Code or OpenClaw by Peter Steinberger, Github repositories focused on LLMs and Agentic AI are accumulating stars that took foundational ML libraries years to reach. This is partly because coding and building applications became accessible to a much wider audience, meaning more people are actively searching for repositories that can make their own AI/agentic workflows faster and better. But does that actually mean these repositories are being used more or is the star growth mainly short-term hype, while legacy ML repositories grow slower but more sustainably, with people genuinely using them rather than just bookmarking them until the next cool thing emerges? I wanted to find out, and build a portfolio project along the way that lets me apply data engineering and statistical analysis skills on something I'm genuinely passionate about.

- Research Questions:
  - **1. Star Trajectory:**
    -> Research Question: "How does star growth velocity evolve over the first 12 to 24 months of a repository's lifespan, and does this trajectory differ systematically between LLM/Agentic AI repositories and legacy ML repositories?
    -> H₀: There is no significant difference in star growth velocity or trajectory shape between LLM/Agentic AI repositories and legacy ML repositories across the first 12 to 24 months of their lifespan.
    -> H₁: LLM/Agentic AI repositories exhibit significantly higher initial star growth velocity followed by faster post-peak decay, compared to the more sustained growth pattern of legacy ML repositories.
  - **2. Star-to-Commit-Ratio:**
    -> RQ2: Do LLM/Agentic AI repositories exhibit a significantly higher cumulative commit-to-star ratio compared to legacy ML repositories over the first 12 to 24 months of their lifespan, and does this divergence increase over time?
    -> H₀: There is no significant difference in the commit-to-star ratio between LLM/Agentic AI repositories and legacy ML repositories at any point within the first 12-24 months.
    -> H₁: Legacy ML repositories exhibit a significantly higher commit-to-star ratio than LLM/Agentic AI repositories, with this gap widening as repository age increases.

## Analysis Approach

- Repo-age alignment: We will anchor each repo at its creation date (day 0) and compare trajectories over the first N months of life. PyTorch's first 24 months vs. LangChain's first 24 months.
  - In the data tables, we will include the actual date (e.g. week) as well as the date index relative to the repo creation (Week 0, 1, 2, ...)
- Requirement: at least 12 months of data for each repo since the creation of the repo (18 or 24 months is better, but most Agentic AI repositories were probably created in 2025 / 2026)
- Statistical Tests:
  - for Research Question 1:
    -> Mann-Whitney U on average weekly star delta, computed separately for early (months 1–6), mid (7–12), and late (13–24) windows. Non-parametric, handles the skewed star distributions. Running it at three windows also lets you say something about whether differences emerge early or late.
    -> Change-point detection (PELT or CUSUM) on each repo's weekly star velocity to locate the peak. You then compare the timing of the peak and the slope of decay after it between cohorts. The decay slope comparison itself is another Mann-Whitney U or a simple linear regression slope test.
    -> Effect size: rank-biserial correlation (r) — always report this alongside Mann-Whitney. A p-value alone tells you the difference is real; effect size tells you how big it is, which matters much more for a portfolio narrative.
  - for Research Question 2:
    -> Mann-Whitney U on the cumulative star-to-commit ratio at months 12 and 24 — two separate tests, which lets you say whether the gap exists at 12 months and whether it widens by 24.
    -> Log-transform the ratio first before any visualization or descriptive stats — it'll make your distributions interpretable and your charts readable.
    -> Effect size: rank-biserial correlation (r) again.
    -> Optionally, a Spearman correlation between repo age (in weeks) and star-to-commit ratio within each cohort separately — a rising Spearman r in the LLM cohort and a flat one in the legacy cohort would be clean evidence that the gap widens over time.

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
