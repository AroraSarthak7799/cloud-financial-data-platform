from datetime import timedelta

import pendulum

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


DBT_PROJECT_DIR = "/opt/airflow/project/cloud_financial_dbt"
SQL_DIR = "/opt/airflow/project/sql"


with DAG(
    dag_id="financial_data_pipeline",
    description="Financial data ingestion and transformation pipeline",
    start_date=pendulum.datetime(2026, 10, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    template_searchpath=[SQL_DIR],
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["financial-data", "snowflake", "dbt"],
) as dag:

    verify_ingest_connection = SQLExecuteQueryOperator(
        task_id="verify_ingest_connection",
        conn_id="snowflake_ingest",
        sql="SELECT CURRENT_ROLE() AS ACTIVE_ROLE",
        show_return_value_in_logs=True,
    )
    upload_to_s3 = BashOperator(
        task_id="upload_to_s3",
        bash_command=(
            "cd /opt/airflow/project && "
            "python src/upload_to_s3_once.py"
        ),
    )

    load_snowflake_raw = SQLExecuteQueryOperator(
        task_id="load_snowflake_raw",
        conn_id="snowflake_ingest",
        sql="airflow_load_raw.sql",
        split_statements=True,
        do_xcom_push=False,
    )

    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run",
    )

    run_dbt_tests = BashOperator(
        task_id="run_dbt_tests",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test",
    )

    run_customer_snapshot = BashOperator(
        task_id="run_customer_snapshot",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            "dbt snapshot --select customer_history"
        ),
    )

    (
      verify_ingest_connection
      >> upload_to_s3
      >> load_snowflake_raw
      >> run_dbt_models
      >> run_dbt_tests
      >> run_customer_snapshot
    )