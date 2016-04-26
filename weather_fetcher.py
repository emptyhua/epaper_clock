#!/usr/bin/env python
# coding: utf-8

import json
import os
import re
import sys
import time

import requests
from lxml import etree

output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather.json')

def fail_exit(msg):
    with open(output_file, 'w') as out_file:
        json.dump({'error': msg}, out_file)
    sys.exit(1)

html = ''
try:
    r = requests.get('http://weather.sina.com.cn/', timeout=10)
    r.encoding = 'utf-8'
    html = r.text
except Exception, e:
    fail_exit(unicode(e))

result = {field: None for field in '''city_name current_temp current_weather
          current_wind current_humidity current_aq current_aq_desc
          today_weather today_temp_low today_temp_hig tomorrow_weather
          tomorrow_temp_low tomorrow_temp_hig tomorrow_wind tomorrow_aq
          tomorrow_aq_desc'''.split()}

tree = etree.HTML(html)
rt = tree.xpath('//*[@id="slider_ct_name"]')
if rt:
    result['city_name'] = rt[0].text
rt = tree.xpath('//*[@id="slider_w"]//div[@class="slider_degree"]')
if rt:
    result['current_temp'] = rt[0].text.replace(u'℃', '')
rt = tree.xpath('//*[@id="slider_w"]//p[@class="slider_detail"]')
if rt:
    tmp0 = re.sub(r'\s', '', rt[0].text)
    tmp0 = tmp0.split('|')
    if len(tmp0) >= 3:
        result['current_weather'] = tmp0[0].strip()
        result['current_wind'] = tmp0[1].strip()
        tmp1 = re.search(r'([\-\d]+)%', tmp0[2])
        if tmp1 is not None:
            result['current_humidity'] = tmp1.group(1)
    tmp0 = None
    tmp1 = None

rt = tree.xpath('//*[@id="slider_w"]/div[1]/div/div[4]/div/div[1]/p')
if rt:
    result['current_aq'] = rt[0].text

rt = tree.xpath('//*[@id="slider_w"]/div[1]/div/div[4]/div/div[2]/p[1]')
if rt:
    result['current_aq_desc'] = rt[0].text

rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[1]/p[3]/img')
if len(rt) == 1:
    result['today_weather'] = rt[0].get('alt')
elif len(rt) == 2:
    tmp0 = rt[0].get('alt')
    tmp1 = rt[1].get('alt')
    result['today_weather'] = tmp0
    if tmp0 != tmp1:
        result['today_weather'] += u'转' + tmp1
    tmp0 = None
    tmp1 = None

rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[1]/p[5]')
if rt:
    tmp0 = rt[0].text.split('/')
    if len(tmp0) > 1:
        result['today_temp_hig'] = tmp0[0].replace(u'°C', '').strip()
        result['today_temp_low'] = tmp0[1].replace(u'°C', '').strip()
    else:
        result['today_temp_low'] = tmp0[0].replace(u'°C', '').strip()
    tmp0 = None

rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[2]/p[3]/img')
if rt:
    tmp0 = rt[0].get('alt')
    tmp1 = rt[1].get('alt')
    result['tomorrow_weather'] = tmp0
    if tmp0 != tmp1:
        result['tomorrow_weather'] += u'转' + tmp1
    tmp0 = None
    tmp1 = None

rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[2]/p[5]')
if rt:
    tmp0 = rt[0].text.split('/')
    result['tomorrow_temp_hig'] = tmp0[0].replace(u'°C', '').strip()
    result['tomorrow_temp_low'] = tmp0[1].replace(u'°C', '').strip()
    tmp0 = None

rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[2]/p[6]')
if rt:
    result['tomorrow_wind'] = rt[0].text.strip()

rt = tree.xpath('//*[@id="blk_fc_c0_scroll"]/div[2]/ul/li')
if rt:
    result['tomorrow_aq'] = rt[0].text
    result['tomorrow_aq_desc'] = rt[1].text

keys_require = '''city_name current_temp current_weather current_wind
    current_humidity current_aq current_aq_desc today_weather
    today_temp_low tomorrow_weather tomorrow_temp_low tomorrow_temp_hig
    tomorrow_wind'''.split()

for key in keys_require:
    if not result.get(key):
        fail_exit('can not get key %s' % key)

result['update'] = int(time.time())
with open(output_file, 'w') as out_file:
    json.dump(result, out_file)
