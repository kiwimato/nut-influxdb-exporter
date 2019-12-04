#!/bin/bash
n=10
while n < 1
do 
sleep 10s
python -u /src/nut-influxdb-exporter.py
done
