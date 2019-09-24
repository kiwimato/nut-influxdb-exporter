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
verbose = os.getenv('VERBOSE', 'false').lower()
remove_these_keys = ['driver.version.internal', 'driver.version.usb', 'ups.beeper.status', 'driver.name', 'battery.mfr.date']
tag_keys = ['battery.type', 'device.model', 'device.serial', 'driver.version', 'driver.version.data', 'device.mfr', 'device.type', 'ups.mfr', 'ups.model', 'ups.productid', 'ups.serial', 'ups.vendorid']

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
    print("VERBOSE: ", verbose)


def convert_to_type(s):
    """ A function to convert a str to either integer or float. If neither, it will return the str. """
    try:
        int_var = int(s)
        return int_var
    except ValueError:
        try:
            float_var = float(s)
            return float_var
        except ValueError:
            return s


def construct_object(data, remove_these_keys, tag_keys):
    """
    Constructs NUT data into  an object that can be sent directly to InfluxDB

    :param data: data received from
    :param remove_these_keys:
    :param tag_keys:
    :return:
    """
    fields = {}
    tags = {'host': os.getenv('HOSTNAME', 'localhost')}

    for k, v in data.items():
        if k not in remove_these_keys:
            if k in tag_keys:
                tags[k] = v
            else:
                fields[k] = convert_to_type(v)

    result = [
        {
            'measurement': 'ups_status',
            'fields': fields,
            'tags': tags
        }
    ]
    return result


while True:
    try:
        ups_data = ups_client.list_vars(ups_alias)
    except:
        tb = traceback.format_exc()
        if verbose == 'true':
            print(tb)
        print("Error getting data from NUT")

    json_body = construct_object(ups_data, remove_these_keys, tag_keys)

    try:
        if verbose == 'true':
            print(json_body)
            print(client.write_points(json_body))
        else:
            client.write_points(json_body)
    except:
        tb = traceback.format_exc()
        if verbose == 'true':
            print(tb)
        print("Error connecting to InfluxDB.")
    time.sleep(interval)
