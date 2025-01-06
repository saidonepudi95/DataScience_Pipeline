# DAG to Orchestrate Spark Job
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# DAG Definition
dag = DAG(
    'spark_job_pipeline',
    default_args=default_args,
    description='Run Spark jobs and move data to Cassandra',
    schedule_interval='@hourly',
    start_date=days_ago(1),
    catchup=False,
)

# Task to Run Spark Job
run_spark_job = BashOperator(
    task_id='run_spark_job',
    bash_command='docker exec -it spark-master spark-submit --master spark://spark-master:7077 --jars /opt/bitnami/spark/jars/postgresql-42.7.3.jar /opt/bitnami/spark/data_processing.py',
    dag=dag,
)

# Python Task to Move Data to Cassandra
def move_to_cassandra():
    # Logic to transfer data from PostgreSQL to Cassandra
    print("Moving processed data from PostgreSQL to Cassandra")

move_data = PythonOperator(
    task_id='move_to_cassandra',
    python_callable=move_to_cassandra,
    dag=dag,
)

# Notification on Completion
def notify_completion():
    print("Spark Job and Data Movement Completed Successfully!")

notify_task = PythonOperator(
    task_id='notify_completion',
    python_callable=notify_completion,
    dag=dag,
)

# Task Dependencies
run_spark_job >> move_data >> notify_task
