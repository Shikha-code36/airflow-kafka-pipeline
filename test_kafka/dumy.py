from fastapi import FastAPI, BackgroundTasks
from time import sleep
from json import dumps, loads
from kafka import KafkaProducer, KafkaConsumer
from typing import Optional

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers=['kafka:9093'],
    value_serializer=lambda x: dumps(x).encode('utf-8'),
    api_version = (0,10,0)
)

@app.get("/")
def index():
    return "Hello Kafka"

@app.get("/produce/{n}")
def produce_data(n: int):
    for j in range(n):
        data = {'counter': j}
        producer.send('topic_test', value=data)
        print(data)
        sleep(0.5)
    return "Data produced to Kafka!"

def consume_data():
    consumer = KafkaConsumer(
        'topic_test',
        bootstrap_servers=['kafka:9093'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-group',
        value_deserializer=lambda x: loads(x.decode('utf-8'))
    )

    for message in consumer:
        message = message.value
        print(f"Received: {message}")

@app.get("/consume")
def consume(background_tasks: BackgroundTasks):
    background_tasks.add_task(consume_data)
    return "Started consuming data!"

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8003)
