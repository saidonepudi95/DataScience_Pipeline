FROM apache/airflow:latest

USER airflow

RUN pip install confluent-kafka
