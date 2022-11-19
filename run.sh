#!/bin/bash
python3 producer.py &
python3 consumer.py &
python3 test_conn.py