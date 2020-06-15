#!/bin/sh
while :
do 
	sleep 10s
	python -u /src/nut-influxdb-exporter.py
done
