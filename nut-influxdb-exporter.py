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
nut_port = os.getenv('NUT_PORT') if os.getenv('NUT_PORT') != '' else '3493'
nut_password = os.getenv('NUT_PASSWORD') if os.getenv('NUT_PASSWORD') != '' else None
nut_username = os.getenv('NUT_USERNAME') if os.getenv('NUT_USERNAME') != '' else None
nut_watts = os.getenv('WATTS') if os.getenv('WATTS') != '' else None
# Other vars
interval = float(os.getenv('INTERVAL', 21))
ups_name = os.getenv('UPS_NAME', 'UPS')
verbose = os.getenv('VERBOSE', 'false').lower()
remove_keys = ['driver.version.internal', 'driver.version.usb', 'ups.beeper.status', 'driver.name', 'battery.mfr.date']
tag_keys = ['battery.type', 'device.model', 'device.serial', 'driver.version', 'driver.version.data', 'device.mfr', 'device.type', 'ups.mfr', 'ups.model', 'ups.productid', 'ups.serial', 'ups.vendorid']

print("Connecting to InfluxDB host:{}, DB:{}".format(host, dbname))
client = InfluxDBClient(host, port, username, password, dbname)
client.create_database(dbname)
if client:
    print("Connected successfully to InfluxDB")

if os.getenv('VERBOSE', 'false').lower() == 'true':
    print("INFLUXDB_DATABASE: ", dbname)
    print("INFLUXDB_USER: ", username)
    # print("INFLUXDB_PASSWORD: ", password)    # Not really safe to just print it. Feel free to uncomment this if you really need it
    print("INFLUXDB_PORT: ", port)
    print("INFLUXDB_HOST: ", host)
    print("NUT_USER: ", nut_username)
    # print("NUT_PASS: ", nut_password)
    print("UPS_NAME", ups_name)
    print("INTERVAL: ", interval)
    print("VERBOSE: ", verbose)

print("Connecting to NUT host {}:{}".format(nut_host, nut_port))
ups_client = PyNUTClient(host=nut_host, port=nut_port, login=nut_username, password=nut_password, debug=(verbose == 'true'))
if ups_client:
    print("Connected successfully to NUT")


def convert_to_type(s):
    """ A function to convert a str to either integer or float. If neither, it will return the str. """
    try:
        float_var = float(s)
        return float_var
    except ValueError:
        return s


def construct_object(data, remove_keys, tag_keys):
    """
    Constructs NUT data into  an object that can be sent directly to InfluxDB

    :param data: data received from NUT
    :param remove_keys: some keys which are considered superfluous
    :param tag_keys: some keys that are actually considered tags and not measurements
    :return:
    """
    fields = {}
    tags = {'host': os.getenv('HOSTNAME', 'localhost')}

    for k, v in data.items():
        if k not in remove_keys:
            if k in tag_keys:
                tags[k] = v
            else:
                fields[k] = convert_to_type(v)

    watts = float(nut_watts) if nut_watts else float(fields['ups.realpower.nominal'])
    fields['watts'] = watts * 0.01 * fields['ups.load']

    result = [
        {
            'measurement': 'ups_status',
            'fields': fields,
            'tags': tags
        }
    ]
    return result


# Main infinite loop: Get the data from NUT every interval and send it to InfluxDB.
while True:
    try:
        ups_data = ups_client.list_vars(ups_name)
    except:
        tb = traceback.format_exc()
        if verbose == 'true':
            print(tb)
        print("Error getting data from NUT")
        exit(1)

    json_body = construct_object(ups_data, remove_keys, tag_keys)

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
        exit(2)
    time.sleep(interval)
