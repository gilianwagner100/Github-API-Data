from google.cloud import bigquery
from ingestion.config import GCP_PROJECT_ID, BQ_DATASET
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_client() -> bigquery.Client:
    """Initialise BigQuery client using ADC."""
    return bigquery.Client(project=GCP_PROJECT_ID)


def ensure_table_exists(
    client: bigquery.Client,
    table_id: str,
    schema: list[bigquery.SchemaField]
) -> None:
    """Create table if it doesn't already exist."""
    full_table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{table_id}"
    table = bigquery.Table(full_table_id, schema=schema)
    client.create_table(table, exists_ok=True)
    logger.info(f"Table {full_table_id} is ready.")


def write_records(
    client: bigquery.Client,
    table_id: str,
    records: list
) -> None:
    """Write a list of Pydantic model objects to BigQuery using batch load."""
    full_table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{table_id}"

    rows = [
        {k: v.isoformat() if hasattr(v, "isoformat") else v
         for k, v in record.model_dump().items()}
        for record in records
    ]

    job_config = bigquery.LoadJobConfig(
        schema=None,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    job = client.load_table_from_json(rows, full_table_id, job_config=job_config)
    job.result()  # waits for the job to complete

    logger.info(f"Inserted {len(rows)} rows into {full_table_id}")

def get_latest_timestamp(client: bigquery.Client, table_id: str, repo_id: int, timestamp_column: str) -> datetime | None:
    """Get the latest timestamp for a given repo from a raw table."""
    full_table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{table_id}"
    query = f"""
        SELECT MAX({timestamp_column}) as latest
        FROM `{full_table_id}`
        WHERE repo_id = {repo_id}
    """
    result = client.query(query).result()
    row = next(iter(result))
    return row.latest  # returns None if table is empty