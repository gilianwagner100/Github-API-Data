from ingestion.config import GITHUB_BASE_URL, HEADERS, LEGACY_REPOS, LLM_REPOS
from ingestion.github_client import make_request
from ingestion.models import RepositoryRecord
from ingestion.bigquery_client import get_client, ensure_table_exists, write_records
from google.cloud import bigquery

REPOSITORY_SCHEMA = [
    bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("owner_id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("owner_login", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("forks_count", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("stargazers_count", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("watchers_count", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("topics", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("pushed_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("repo_category", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("load_timestamp", "TIMESTAMP", mode="REQUIRED"),
]

def get_repository_data(repository:str, max_retries:int = 5) -> dict:
    """GET request for repository endpoint."""
    url = f"{GITHUB_BASE_URL}/repos/{repository}"
    response = make_request(url=url, headers=HEADERS, max_retries=max_retries)
    return response.json() if response else {}

def run():
    """Fetch all repositories and write to BigQuery."""
    client = get_client()
    ensure_table_exists(client, "raw_repositories", REPOSITORY_SCHEMA)

    records = []

    for repo in LEGACY_REPOS:
        raw = get_repository_data(repo)
        if raw:
            record = RepositoryRecord.from_api_response(raw, category="legacy")
            records.append(record)

    for repo in LLM_REPOS:
        raw = get_repository_data(repo)
        if raw:
            record = RepositoryRecord.from_api_response(raw, category="llm")
            records.append(record)

    write_records(client, "raw_repositories", records)
    print(f"Done. Wrote {len(records)} records to raw_repositories.")