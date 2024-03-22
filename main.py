import json
from flask import Flask, request, jsonify
from time import sleep
from json import dumps
import yfinance as yf
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable

app = Flask(__name__)

# Kafka producer configuration
producer = KafkaProducer(
    bootstrap_servers=['kafka:9093'],
    value_serializer=lambda x: dumps(x).encode('utf-8'),
    api_version=(0, 10, 0)
)

# Kafka consumer configuration
consumer = KafkaConsumer(
    bootstrap_servers=['kafka:9093'],
    group_id='my_consumer_group',
    auto_offset_reset='earliest'
)

@app.route('/')
def index():
    return "Hello Kafka"

@app.route('/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    # Get the data for the stock
    stock = yf.Ticker(symbol)

    # Get historical market data
    hist = stock.history(period="7d")

    # Convert the DataFrame to a dictionary and return as JSON
    return jsonify(hist.reset_index().to_dict(orient='records'))

@app.route('/publish/<topic>', methods=['POST'])
def publish_to_kafka(topic):
    try:
        # Get data from the request payload
        data = request.get_json()

        # Publish data to Kafka topic
        producer.send(topic, value=data)

        return jsonify({'message': f'Data published to Kafka topic: {topic}'})
    except NoBrokersAvailable as e:
        return jsonify({'status': 'error', 'message': f'No brokers available: {str(e)}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/subscribeall/<topic>', methods=['GET'])
def subscribe_to_kafka(topic):
    try:
        # Subscribe to Kafka topic
        consumer.subscribe([topic])

        # Poll for messages
        messages = consumer.poll(1000)

        if not messages:
            return jsonify({'message': f'No new data in Kafka topic: {topic}', 'kafka': None})

        # Extract and return received data
        received_data = []
        for partition, msg_list in messages.items():
            for msg in msg_list:
                received_data.append(json.loads(msg.value.decode('utf-8')))

        return jsonify({'kafka': received_data})
    except NoBrokersAvailable as e:
        return jsonify({'status': 'error', 'message': f'No brokers available: {str(e)}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        consumer.unsubscribe()

@app.route('/subscribelast/<topic>', methods=['GET'])
def subscribe_last(topic):
    try:
        # Subscribe to Kafka topic
        consumer.subscribe([topic])

        # Poll for messages
        messages = consumer.poll(1000)

        if not messages:
            return jsonify({'message': f'No new data in Kafka topic: {topic}', 'data': None})

        # Extract and return the last received data
        last_message = None
        for partition, msg_list in messages.items():
            for msg in msg_list:
                last_message = json.loads(msg.value.decode('utf-8'))

        return jsonify({'kafka': last_message})
    except NoBrokersAvailable as e:
        return jsonify({'status': 'error', 'message': f'No brokers available: {str(e)}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        consumer.unsubscribe()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)