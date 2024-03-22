from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import yfinance as yf
from datetime import datetime, timedelta
import requests

# Instantiate the DAG
dag = DAG(
    "stock_kafka_dag",
    default_args={"start_date": days_ago(1)},
    schedule_interval="0 23 * * *",
    catchup=False,
)

# Define the Python functions for your APIs
def get_stock_data(symbol):
    response = requests.get(f"http://127.0.0.1:5000/stock/{symbol}")
    data = response.json()
    return data

def publish_to_kafka(topic, data):
    print("data in publisher:", data, "for topic:", topic)
    response = requests.post(f"http://127.0.0.1:5000/publish/{topic}", json=data)
    print("publisher's response:", response.json())
    return response.json()

def subscribe_to_kafka(topic):
    response = requests.get(f"http://127.0.0.1:5000/subscribeall/{topic}")
    print("subscribeall's response:", response.json())
    return response.json()

def subscribe_last(topic):
    response = requests.get(f"http://127.0.0.1:5000/subscribelast/{topic}")
    print("subscribelast's response:", response.json())
    return response.json()

# Create the tasks
stock_data_task = PythonOperator(
    task_id="get_stock_data",
    python_callable=get_stock_data,
    op_kwargs={"symbol": "AAPL"},
    dag=dag,
    provide_context=True,
)

publish_to_kafka_task = PythonOperator(
    task_id="publish_to_kafka",
    python_callable=publish_to_kafka,
    op_kwargs={"topic": "stock_topic"},
    dag=dag,
    provide_context=True,
)


subscribe_to_kafka_task = PythonOperator(
    task_id="subscribe_to_kafka",
    python_callable=subscribe_to_kafka,
    op_kwargs={"topic": "stock_topic"},
    dag=dag,
)

subscribe_last = PythonOperator(
    task_id="subscribe_last",
    python_callable=subscribe_last,
    op_kwargs={"topic": "stock_topic"},
    dag=dag,
)

# Define the task dependencies
stock_data_task >> publish_to_kafka_task >> [subscribe_to_kafka_task, subscribe_last]
