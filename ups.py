#!/usr/bin/python
import os
import time
import traceback

from nut2 import PyNUTClient
from influxdb import InfluxDBClient

# InfluxDB details
dbname = os.getenv('INFLUXDB_DATABASE', 'nutupstest')
username = os.getenv('INFLUXDB_USER')
password = os.getenv('INFLUXDB_PASSWORD')
host = os.getenv('INFLUXDB_HOST', '127.0.0.1')
port = os.getenv('INFLUXDB_PORT', 8086)
# NUT related variables
nut_host = os.getenv('NUT_HOST', '127.0.0.1')
nut_port = os.getenv('NUT_PORT', '3493')
nut_username = os.getenv('NUT_PASSWORD', None)
nut_password = os.getenv('NUT_USERNAME', None)
# Other vars
interval = float(os.getenv('INTERVAL', 21))
ups_alias = os.getenv('UPS_ALIAS', 'UPS')

print("Connecting to InfluxDB host:{}, DB:{}".format(host, dbname))

client = InfluxDBClient(host, port, username, password, dbname)
client.create_database(dbname)

ups_client = PyNUTClient(host=nut_host, port=nut_port, login=nut_username, password=nut_password)

if os.getenv('VERBOSE', 'false').lower() == 'true':
    print("INFLUXDB_DATABASE: ", dbname)
    print("INFLUXDB_USER: ", username)
    # print("INFLUXDB_PASSWORD: ", password) # Not really safe to just print it.
    print("INFLUXDB_PORT: ", port)
    print("INFLUXDB_HOST: ", host)
    print("UPS_ALIAS", ups_alias)
    print("INTERVAL: ", interval)
    print("VERBOSE: ", os.getenv('VERBOSE', 'false'))

while True:
    try:
        data = ups_client.list_vars(ups_alias)
    except:
        print("Error getting data from NUT")

    watts = float(os.getenv('WATTS', data.get('ups.realpower.nominal', 0.0))) * 0.01 * float(data.get('ups.load', 0.0))

    json_body = [
        {
            'measurement': 'ups_status',
            'fields': data,
            'tags': {
                'host': os.getenv('HOSTNAME', 'localhost'),
                'ups_alias': ups_alias,
            }
        }
    ]

    try:
        if os.getenv('VERBOSE', 'false').lower() == 'true':
            print(json_body)
            print(client.write_points(json_body))
        else:
            client.write_points(json_body)
    except:
        if os.getenv('VERBOSE', 'false').lower() == 'true':
            print(traceback.format_exc())
        print("Error connecting to InfluxDB.")
    time.sleep(interval)
