import os
import glob
from datetime import datetime

import requests
# import json

# either run as root and uncomment these lines, or ensure the modules are loaded before running the 
# tool
# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')

# sensor map
# 28-000004dd5ac6 - ambient

sensor_base_dir = '/sys/bus/w1/devices'
sensor_name_start_characters = '28'
sensors = {
    'ambient': '-000004dd5ac6'
}

logging_url = 'http://127.0.0.1:8000/api/record'

def get_sensor(sensor_name):
    p = os.path.join(sensor_base_dir, sensor_name_start_characters + sensors[sensor_name], 'w1_slave')
    return p

def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def parse_temp(raw):
    equals_pos = raw[1].find('t=')
    if equals_pos != -1:
        temp_string = raw[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

# for each sensor in the map, grab it's temperature
# send the value back up to the server

def read_temp():
    results = dict()
    for k in sensors.iterkeys():
        raw = read_temp_raw(get_sensor(k))
        degrees_c = parse_temp(raw)
        results[k] = degrees_c

    return results

# fire back to the service for storage
measurements = read_temp()
print measurements
payload = {
    'instant': datetime.now(),
    'measurements': measurements
}

req = requests.post(logging_url, data=payload)
