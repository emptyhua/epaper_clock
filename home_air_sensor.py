#!/usr/bin/env python
# coding: utf-8

import json
import os
import time

import Adafruit_DHT

h, t = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
result = {'temp': int(t), 'humidity': int(h), 'update': int(time.time())}
data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home_air.json')
with open(data_file, 'w') as out_file:
    json.dump(result, out_file)
