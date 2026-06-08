from ingestion.config import GITHUB_BASE_URL, HEADERS, LEGACY_REPOS, LLM_REPOS
from ingestion.github_client import make_request
from ingestion.bigquery_client import get_client, ensure_table_exists, write_records, get_latest_timestamp
from google.cloud import bigquery
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

COMMIT_HISTORY_SCHEMA = [
    bigquery.SchemaField("repo_id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("repo_full_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("user_id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("user_login", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("starred_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("load_timestamp", "TIMESTAMP", mode="REQUIRED"),
]

def get_commit_data():
    ""

def run():
    ""