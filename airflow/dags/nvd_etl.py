import sys
from pathlib import Path
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from etl.extract import extract
from etl.transform import transform
from etl.load import load

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'nvd_daily_etl',
    default_args=default_args,
    schedule_interval='0 2 * * *',
    catchup=False
) as dag:

    extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract
    )

    transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform,
        op_args=["{{ ti.xcom_pull(task_ids='extract') }}"]
    )

    load_task = PythonOperator(
        task_id='load',
        python_callable=load,
        op_args=["{{ ti.xcom_pull(task_ids='transform') }}"]
    )

    extract_task >> transform_task >> load_task