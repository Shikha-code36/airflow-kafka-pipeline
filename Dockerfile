# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Upgrade pip to the latest version
RUN python -m pip install --upgrade pip

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get -y install libc6-dev build-essential
RUN pip install -U pip

# Copy and install Python dependencies first (to leverage Docker cache)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install Apache Airflow
RUN pip install apache-airflow

# Set AIRFLOW_HOME environment variable
ENV AIRFLOW_HOME=/app/airflow

# Initialize Airflow database
RUN airflow db init

# Copy the rest of your application files
COPY . /app/

EXPOSE 5000
# Expose port for Airflow webserver
EXPOSE 8080  

# Add a script to run your application and the Airflow webserver
COPY start_services.sh /app/
RUN chmod +x /app/start_services.sh

# Command to run your script
CMD ["/app/start_services.sh"]
