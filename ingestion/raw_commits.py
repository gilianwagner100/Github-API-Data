from ingestion.config import GITHUB_BASE_URL, HEADERS, LEGACY_REPOS, LLM_REPOS
from ingestion.github_client import make_request
from ingestion.models import CommitRecord
from ingestion.bigquery_client import get_client, ensure_table_exists, write_records, get_latest_timestamp
from google.cloud import bigquery
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

COMMIT_ACTIVITY_SCHEMA = [
    bigquery.SchemaField("sha", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("commit_date", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("author_id", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("author_login", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("committer_id", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("committer_login", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("repo_id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("load_timestamp", "TIMESTAMP", mode="REQUIRED"),
]


def get_next_url(link_header: str) -> str | None:
    if not link_header:
        return None
    for part in link_header.split(","):
        url, rel = part.strip().split(";")
        if rel.strip() == 'rel="next"':
            return url.strip()[1:-1]
    return None


def get_commit_data(
    repo_full_name: str,
    repo_id: int,
    since: datetime | None = None,
    max_retries: int = 5
) -> list:
    url = f"{GITHUB_BASE_URL}/repos/{repo_full_name}/commits"
    params = {"per_page": 100}

    if since:
        params["since"] = since.isoformat()

    records = []

    while url:
        response = make_request(url, HEADERS, params=params, max_retries=max_retries)

        if response is None:
            logger.error(f"Failed to fetch commits for {repo_full_name}, stopping.")
            break

        page_records = response.json()

        for item in page_records:
            records.append(CommitRecord.from_api_response(item, repo_id))

        logger.info(f"{repo_full_name}: {len(records)} commits fetched so far...")

        url = get_next_url(response.headers.get("Link"))
        params = {}

    logger.info(f"Finished {repo_full_name}: {len(records)} total new commits.")
    return records


def run(repo_ids: dict):
    client = get_client()
    ensure_table_exists(client, "raw_commit_activity", COMMIT_ACTIVITY_SCHEMA)

    all_records = []

    for category, repos in [("legacy", LEGACY_REPOS), ("llm", LLM_REPOS)]:
        for repo_full_name in repos:
            repo_id = repo_ids.get(repo_full_name)

            if not repo_id:
                logger.warning(f"No repo_id found for {repo_full_name}, skipping.")
                continue

            since = get_latest_timestamp(
                client, "raw_commit_activity", repo_id, "commit_date"
            )

            records = get_commit_data(repo_full_name, repo_id, since=since)
            all_records.extend(records)
            logger.info(f"Collected {len(records)} new commits for {repo_full_name}.")

    if all_records:
        write_records(client, "raw_commit_activity", all_records)
        logger.info(f"Wrote {len(all_records)} total commit records.")
    else:
        logger.info("No new commit records to write.")