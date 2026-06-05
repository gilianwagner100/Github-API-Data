from ingestion.config import GITHUB_BASE_URL, HEADERS, LEGACY_REPOS, LLM_REPOS
import requests
import time
from datetime import datetime, timezone
from google.cloud import bigquery
from ingestion.models import RepositoryRecord
from ingestion.bigquery_client import get_client, ensure_table_exists, write_records

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
    """GET request for repository endpoint with rate limit handling."""
    url = f"{GITHUB_BASE_URL}/repos/{repository}"

    wait_time = 60 # required wait time of 60 seconds as per API doc

    for attempt in range(max_retries):
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 403:
            retry_after = response.headers.get("retry-after")

            if retry_after:
                print(f"Rate limited. Waiting for {retry_after}s (retry-after) ...")
                time.sleep(int(retry_after))
            
            elif response.headers.get("x-ratelimit-remaining") == "0":
                time_reset = int(response.headers.get("x-ratelimit-reset"))
                time_now = time.time()
                sleep_for = max(time_reset - time_now, 0)

                print(f"Rate limited & will reset at {time_reset}. Sleeping for {sleep_for}s ...")
                time.sleep(sleep_for)

            else:
                if attempt >= max_retries -1:
                    raise Exception(f"Secondary Rate Limit: max retries {max_retries} exceeded.")
                print(f"Secondary rate limit: waiting for {wait_time}s (attempt {attempt + 1})")
                time.sleep(wait_time)
                wait_time *= 2 # exponential backoff when secondary rate limit is reached as per API doc

        else:
            print(f"HTTP Response Code '{response.status_code} on {url}'")
    
    return {}

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