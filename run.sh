#!/bin/bash
python3 ./Kafka_producer/producer.py &
python3 ./Kafka_consumer/main.py &
python3 ./Kafka_consumer/FlaskAPI.py &
gunicorn --workers=5 --threads=1 -b 0.0.0.0:5000 --chdir ./Kafka_consumer  FlaskAPI:app