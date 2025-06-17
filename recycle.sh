#!/bin/bash

trap 'echo "Stopping gracefully..."; exit 0' SIGINT SIGTERM

while true; do
    echo "$(date): Starting sdrangel-ais-mqtt.py..."
    timeout 15m python3 sdrangel-ais-mqtt.py
    echo "$(date): Restarting..."
    sleep 5
done 
