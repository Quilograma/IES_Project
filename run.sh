#!/bin/bash
python3 ./Kafka_producer/producer.py &
python3 ./Kafka_consumer/main.py &
python3 ./Kafka_consumer/FlaskAPI.py 