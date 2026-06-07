from ingestion.config import GITHUB_BASE_URL, HEADERS, LEGACY_REPOS, LLM_REPOS
from ingestion.github_client import make_request
from ingestion.models import StarRecord
from ingestion.bigquery_client import get_client, ensure_table_exists, write_records, get_latest_timestamp
from google.cloud import bigquery
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

STAR_HEADERS = {**HEADERS, "Accept": "application/vnd.github.star+json"}

STAR_HISTORY_SCHEMA = [
    bigquery.SchemaField("repo_id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("repo_full_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("user_id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("user_login", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("starred_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("load_timestamp", "TIMESTAMP", mode="REQUIRED"),
]

def get_next_url(link_header: str) -> str | None:
    """Parse Link header and return next page URL if it exists."""
    if not link_header:
        return None
    for part in link_header.split(","):
        url, rel = part.strip().split(";")
        if rel.strip() == 'rel="next"':
            return url.strip()[1:-1]
    return None

def get_star_data(
    repo_full_name: str,
    repo_id: int,
    since: datetime | None = None,
    max_retries: int = 5
) -> list:
    """Fetch star history for a repo, optionally only since a given timestamp."""
    url = f"{GITHUB_BASE_URL}/repos/{repo_full_name}/stargazers"
    params = {"per_page": 100}
    records = []

    while url:
        response = make_request(url, STAR_HEADERS, params=params, max_retries=max_retries)

        if response is None:
            logger.error(f"Failed to fetch stars for {repo_full_name}")
            break

        page_records = response.json()
        stop = False

        for item in page_records:
            starred_at = datetime.fromisoformat(
                item["starred_at"].replace("Z", "+00:00")
            )

            if since and starred_at <= since:
                stop = True
                break

            records.append(StarRecord.from_api_response(item, repo_id, repo_full_name))

        if stop:
            logger.info(f"Reached already-ingested stars for {repo_full_name}, stopping.")
            break

        url = get_next_url(response.headers.get("Link"))
        params = {}  # params are already encoded in the next URL

    logger.info(f"Fetched {len(records)} stars for {repo_full_name}")
    return records

def run(repo_ids: dict):
    client = get_client()
    ensure_table_exists(client, "raw_star_history", STAR_HISTORY_SCHEMA)

    all_records = []

    for category, repos in [("legacy", LEGACY_REPOS), ("llm", LLM_REPOS)]:
        for repo_full_name in repos:
            repo_id = repo_ids.get(repo_full_name)

            if not repo_id:
                logger.warning(f"No repo_id found for {repo_full_name}, skipping.")
                continue

            since = get_latest_timestamp(
                client, "raw_star_history", repo_id, "starred_at"
            )

            records = get_star_data(repo_full_name, repo_id, since=since)
            all_records.extend(records)
            logger.info(f"Collected {len(records)} new stars for {repo_full_name}.")

    if all_records:
        write_records(client, "raw_star_history", all_records)
        logger.info(f"Wrote {len(all_records)} total star records.")
    else:
        logger.info("No new star records to write.")