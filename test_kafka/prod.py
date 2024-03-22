from flask import Flask
from time import sleep
from json import dumps
from kafka import KafkaProducer

app = Flask(__name__)

producer = KafkaProducer(
    bootstrap_servers=['kafka:9093'],
    value_serializer=lambda x: dumps(x).encode('utf-8'),
    api_version = (0,10,0)
)

@app.route('/')
def index():
    return "Hello Kafka"

#@app.route('/produce')
def produce_data(n):
    for j in range(n):
        data = {'counter': j}
        producer.send('topic_test', value=data)
        print(data)
        sleep(0.5)
    return "Data produced to Kafka!"

if __name__ == '__main__':
    produce_data(10)
    app.run(host='0.0.0.0', port=5000)
