
from datetime import datetime, timedelta

from airflow.decorators import dag, task

from src.init_db import main as initialize_mysql_database
from src.pipeline import TABLES, read_rows, run_pipeline, counts
from src.logging_config import get_logger

logger = get_logger("airflow.banking")


@dag(
    dag_id="banking_analytics_mysql_pipeline",
    description="Banking analytics ETL pipeline using MySQL",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "banking-data-team",
        "retries": 3,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=15),
    },
    tags=["banking", "mysql", "medallion", "analytics"],
)
def banking_analytics_mysql_pipeline():

    @task
    def initialize_database():
        """Create the database and verify its tables."""
        initialize_mysql_database()
        logger.info("Database initialization completed")
        return True

    @task
    def validate_source_files():
        """Verify that all required CSV files exist and contain data."""
        source_summary = {}

        for table, (filename, columns, primary_keys) in TABLES.items():
            rows = read_rows(filename)

            if not rows:
                raise ValueError(
                    f"Source file {filename} contains no records"
                )

            source_summary[table] = len(rows)
            logger.info(
                "Validated source=%s rows=%s",
                filename,
                len(rows),
            )

        logger.info("All source files validated")
        return source_summary

    @task
    def load_and_transform():
        """Load CSV data, generate fraud alerts and build Gold KPIs."""
        result = run_pipeline()
        logger.info(
            "Pipeline completed batch_id=%s rows=%s",
            result["batch_id"],
            result["rows_loaded"],
        )
        return result

    @task
    def validate_database(pipeline_result, source_summary):
        """Check that essential data reached MySQL."""
        actual_counts = counts()

        required_tables = [
            "customers",
            "accounts",
            "transactions",
            "loans",
            "loan_payments",
        ]

        for table in required_tables:
            if actual_counts.get(table, 0) <= 0:
                raise ValueError(
                    f"Data validation failed for table: {table}"
                )

        expected_rows = sum(source_summary.values())
        loaded_rows = pipeline_result["rows_loaded"]

        if loaded_rows != expected_rows:
            raise ValueError(
                f"Row-count mismatch: expected {expected_rows}, "
                f"pipeline reported {loaded_rows}"
            )

        logger.info("Database validation passed: %s", actual_counts)

        return {
            "batch_id": pipeline_result["batch_id"],
            "rows_loaded": loaded_rows,
            "database_counts": actual_counts,
        }

    database_ready = initialize_database()
    sources_ready = validate_source_files()
    load_result = load_and_transform()
    validation_result = validate_database(load_result, sources_ready)

    database_ready >> sources_ready >> load_result >> validation_result


banking_analytics_mysql_pipeline()