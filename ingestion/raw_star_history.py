from ingestion.config import GITHUB_BASE_URL, HEADERS, LEGACY_REPOS, LLM_REPOS
import requests
import time
from datetime import datetime, timezone
from google.cloud import bigquery

STAR_HISTORY_SCHEMA = [
    bigquery.SchemaField("user_id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("user_login_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("starred_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("load_timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("repository_id", "INTEGER", mode="REQUIRED"),
]

def get_star_data(xxx) -> dict:
    ""

def run():
    ""
