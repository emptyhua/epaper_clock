#!/usr/bin/env python
import sys, os
import Adafruit_DHT as dht
import json
import time
h,t = dht.read_retry(dht.DHT22, 4)
result = {}
result['temp']      = t
result['humidity']  = h
result['update']    = int(time.time())
data_file = os.path.dirname(os.path.abspath(__file__)) + '/home_air.json'
json.dump(result, file(data_file, 'w'))
