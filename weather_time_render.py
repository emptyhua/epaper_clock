#!/usr/bin/env python
# coding: utf-8

import datetime
import json
import os
import sys
import time

from Waveshare_43inch_ePaper import *

screen_width = 800
screen_height = 600
screen = Screen('/dev/ttyAMA0')
screen.connect()
screen.handshake()

# screen.load_pic()
# time.sleep(5)

screen.clear()
screen.set_memory(MEM_FLASH)
screen.set_rotation(ROTATION_180)

clock_x = 40
clock_y = 40
temp_x = 0
time_now = datetime.datetime.now()
time_string = time_now.strftime('%H:%M')
date_string = time_now.strftime('%Y-%m-%d')
week_string = [u'星期一',u'星期二',u'星期三',u'星期四',u'星期五',u'星期六',u'星期日'][time_now.isoweekday() - 1]
if time_string[0] == '0':
    time_string = time_string[1:]
    temp_x += 40

for c in time_string:
    bmp_name = 'NUM{}.BMP'.format('S' if c == ':' else c)
    screen.bitmap(clock_x + temp_x, clock_y, bmp_name)
    temp_x += 70 if c == ':' else 100

screen.set_ch_font_size(FONT_SIZE_48)
screen.set_en_font_size(FONT_SIZE_48)
screen.text(clock_x + 350 + 140, clock_y + 10, date_string)
screen.text(clock_x + 350 + 170, clock_y + 70, week_string)

screen.line(0, clock_y + 160, 800, clock_y + 160)
screen.line(0, clock_y + 161, 800, clock_y + 161)

def weather_fail(msg):
    screen.text(10, clock_y + 170, msg)
    screen.update()
    screen.disconnect()
    sys.exit(1)

weather_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather.json')
wdata = {}
try:
    with open(weather_data_file, 'r') as in_file:
        wdata = json.load(in_file)
except IOError:
    weather_fail(u'ERROR:无法加载天气数据!')

if wdata.get('error'):
    weather_fail(wdata.get('error'))

if int(time.time()) - wdata['update'] > 2 * 3600:
    weather_fail(u'ERROR:天气数据已过期!')

cw = wdata['current_weather']
bmp_name = {u'晴': 'WQING.BMP', u'阴': 'WYIN.BMP', u'多云': 'WDYZQ.BMP',
            u'雷阵雨': 'WLZYU.BMP', u'小雨': 'WXYU.BMP', u'中雨': 'WXYU.BMP'}.get(cw, None)
if not bmp_name:
    if u'雨' in cw:
        bmp_name = 'WYU.BMP'
    elif u'雪' in cw:
        bmp_name = 'WXUE.BMP'
    elif u'雹' in cw:
        bmp_name = 'WBBAO.BMP'
    elif u'雾' in cw or u'霾' in cw:
        bmp_name = 'WWU.BMP'

if bmp_name:
    screen.bitmap(20, clock_y + 240, bmp_name)

screen.set_ch_font_size(FONT_SIZE_64)
screen.set_en_font_size(FONT_SIZE_64)

margin_top = 20
weather_y = clock_y + 170
weather_line_spacing = 10
weather_line1_height = 64
weather_line2_height = 42
weather_line3_height = 64
weather_line4_height = 64
weather_text_x = 256 - 30
weather_line5_x = weather_text_x + 64
if len(wdata['current_aq_desc']) > 2:
    weather_line5_x -= 80

screen.text(weather_text_x + 64, weather_y + margin_top, wdata['today_weather'])

tmp0 = u'{current_temp}℃ {current_humidity} %'.format(**wdata)
tmp0 = tmp0.replace('1', '1 ')
screen.text(weather_text_x + 64, weather_y + margin_top +
            weather_line1_height +
            weather_line_spacing +
            weather_line2_height +
            weather_line_spacing, tmp0)

try:
    home_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home_air.json')
    hdata = json.load(file(home_data_file, 'r'))
    if int(time.time()) - hdata['update'] < 120:
        tmp0 = u'{temp}℃ {humidity} %'.format(**hdata)
        tmp0 = tmp0.replace('1', '1 ')
        screen.text(weather_text_x + 64, weather_y + margin_top +
                    weather_line1_height +
                    weather_line_spacing +
                    weather_line2_height +
                    weather_line_spacing +
                    weather_line3_height +
                    weather_line_spacing, tmp0)
except Exception, e:
    pass

screen.text(weather_line5_x, weather_y + margin_top +
            weather_line1_height +
            weather_line_spacing +
            weather_line2_height +
            weather_line_spacing +
            weather_line3_height +
            weather_line_spacing +
            weather_line4_height +
            weather_line_spacing,
            u'{current_aq} {current_aq_desc}'.format(**wdata))

screen.set_ch_font_size(FONT_SIZE_32)
screen.set_en_font_size(FONT_SIZE_32)

screen.text(weather_text_x + 64 - 20 - screen.get_text_width(wdata['city_name'], FONT_SIZE_32),
            weather_y + margin_top + 10, wdata['city_name'])

screen.text(weather_text_x - 20, weather_y + margin_top +
            weather_line1_height +
            weather_line_spacing +
            weather_line2_height +
            weather_line_spacing + 10, u'室外')

screen.text(weather_text_x - 20, weather_y + margin_top +
            weather_line1_height +
            weather_line_spacing +
            weather_line2_height +
            weather_line_spacing +
            weather_line3_height +
            weather_line_spacing + 10, u'室内')

screen.text(weather_line5_x - 64 * 2 - 20, weather_y + margin_top +
            weather_line1_height +
            weather_line_spacing +
            weather_line2_height +
            weather_line_spacing +
            weather_line3_height +
            weather_line_spacing +
            weather_line4_height +
            weather_line_spacing + 10, u'空气指数')

if wdata.get('today_temp_hig'):
    fmt = u'{today_temp_hig}~{today_temp_low}℃ {current_wind}'
else:
    fmt = u'{today_temp_low}℃ {current_wind}'
msg = fmt.format(**wdata)
screen.text(weather_text_x + 64, weather_y + margin_top
            + weather_line1_height + weather_line_spacing + 5, msg)
weather2_x = 550
weather2_y = (weather_y + margin_top +
              weather_line1_height +
              weather_line_spacing +
              weather_line2_height +
              weather_line_spacing)

box_height = 210
box_width = screen_width - 20 - weather2_x
screen.line(weather2_x, weather2_y, screen_width - 20, weather2_y)
screen.line(weather2_x, weather2_y + 48 + 10, screen_width - 20, weather2_y + 48 + 10)
screen.line(weather2_x, weather2_y, weather2_x, weather2_y + box_height)
screen.line(screen_width - 20, weather2_y, screen_width - 20, weather2_y + box_height)
screen.line(weather2_x, weather2_y + box_height, screen_width - 20, weather2_y + box_height)

screen.set_ch_font_size(FONT_SIZE_32)
screen.set_en_font_size(FONT_SIZE_32)
screen.text(weather2_x + 50, weather2_y + 12, u'明日预告')

fmt = u'{tomorrow_weather},{tomorrow_temp_hig}~{tomorrow_temp_low}℃,{tomorrow_wind}'
msg = fmt.format(**wdata)
if wdata.get('tomorrow_aq'):
    msg += u', AQI {tomorrow_aq}{tomorrow_aq_desc}'.format(**wdata)
screen.wrap_text(weather2_x + 8, weather2_y + 48 + 20, box_width, msg)

screen.update()
screen.disconnect()
