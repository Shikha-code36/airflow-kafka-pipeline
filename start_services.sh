#!/bin/bash

# Start Airflow webserver in the background
airflow webserver -p 8080 &

# Run your application
python main.py
