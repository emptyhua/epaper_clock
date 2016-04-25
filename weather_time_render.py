#!/usr/bin/env python
#coding: utf-8

import sys, os
import time, datetime
from Waveshare_43inch_ePaper import *
import json

screen_width    = 800
screen_height   = 600
screen = Screen('/dev/ttyAMA0')
screen.connect()
screen.handshake()

#screen.load_pic()
#time.sleep(5)

screen.clear()
screen.set_memory(MEM_FLASH)
screen.set_rotation(ROTATION_180)

clock_x = 40
clock_y = 40
temp_x  = 0
time_now = datetime.datetime.now()
time_string = time_now.strftime('%H:%M')
date_string = time_now.strftime('%Y-%m-%d')
week_string = [u'星期一',u'星期二',u'星期三',u'星期四',u'星期五',u'星期六',u'星期日'][time_now.isoweekday() - 1]
if time_string[0] == '0':
    time_string = time_string[1:]
    temp_x += 40

for c in time_string:
    if c == ':':
        bmp_name = 'NUMS.BMP'
    else:
        bmp_name = 'NUM%s.BMP' % c
    screen.bitmap(clock_x + temp_x, clock_y, bmp_name)
    if c == ':':
        temp_x += 70
    else:
        temp_x += 100

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

weather_data_file = os.path.dirname(os.path.abspath(__file__)) + '/weather.json'
try:
    wdata = json.load(file(weather_data_file, 'r'))
except:
    weather_fail(u'ERROR:无法加载天气数据!')

if wdata.get('error') is not None:
    weather_fail(wdata.get('error'))

if int(time.time()) - wdata['update'] > 2 * 3600:
    weather_fail(u'ERROR:天气数据已过期!')


bmp_name = None
cw = wdata['current_weather']
if cw == u'晴':
    bmp_name = 'WQING.BMP'
elif cw == u'阴':
    bmp_name = 'WYIN.BMP'
elif cw == u'多云':
    bmp_name = 'WDYZQ.BMP'
elif cw == u'雷阵雨':
    bmp_name = 'WLZYU.BMP'
elif cw == u'小雨' or cw == u'中雨':
    bmp_name = 'WXYU.BMP'
elif cw.find(u'雨') != -1:
    bmp_name = 'WYU.BMP'
elif cw.find(u'雪') != -1:
    bmp_name = 'WXUE.BMP'
elif cw.find(u'雹') != -1:
    bmp_name = 'WBBAO.BMP'
elif cw.find(u'雾') != -1 or cw.find(u'霾') != -1:
    bmp_name = 'WWU.BMP'

if bmp_name is not None:
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

tmp0 = u'%s℃ %s %%' % (wdata['current_temp'], wdata['current_humidity'])
tmp0 = tmp0.replace('1', '1 ')
screen.text(weather_text_x + 64, weather_y + margin_top \
            + weather_line1_height \
            + weather_line_spacing \
            + weather_line2_height \
            + weather_line_spacing
            , tmp0)

try:
    home_data_file = os.path.dirname(os.path.abspath(__file__)) + '/home_air.json'
    hdata = json.load(file(home_data_file, 'r'))
    if int(time.time()) - hdata['update'] < 120:
        tmp0 = '%d℃ %d %%' % (int(hdata['temp']), int(hdata['humidity']))
        tmp0 = tmp0.replace('1', '1 ')
        screen.text(weather_text_x + 64, weather_y + margin_top \
                    + weather_line1_height \
                    + weather_line_spacing \
                    + weather_line2_height \
                    + weather_line_spacing \
                    + weather_line3_height \
                    + weather_line_spacing
                    , tmp0)
except Exception, e:
    pass

screen.text(weather_line5_x, weather_y + margin_top \
            + weather_line1_height \
            + weather_line_spacing \
            + weather_line2_height \
            + weather_line_spacing \
            + weather_line3_height \
            + weather_line_spacing \
            + weather_line4_height \
            + weather_line_spacing
            , u'%s %s' % (wdata['current_aq'], wdata['current_aq_desc']))

screen.set_ch_font_size(FONT_SIZE_32)
screen.set_en_font_size(FONT_SIZE_32)

screen.text(weather_text_x  + 64 - 20 - screen.get_text_width(wdata['city_name'], FONT_SIZE_32), weather_y + margin_top + 10, wdata['city_name'])

screen.text(weather_text_x - 20, weather_y + margin_top \
            + weather_line1_height \
            + weather_line_spacing \
            + weather_line2_height \
            + weather_line_spacing + 10
            , '室外')

screen.text(weather_text_x - 20, weather_y + margin_top \
            + weather_line1_height \
            + weather_line_spacing \
            + weather_line2_height \
            + weather_line_spacing \
            + weather_line3_height \
            + weather_line_spacing + 10
            , '室内')

screen.text(weather_line5_x - 64 * 2 - 20, weather_y + margin_top \
            + weather_line1_height \
            + weather_line_spacing \
            + weather_line2_height \
            + weather_line_spacing \
            + weather_line3_height \
            + weather_line_spacing \
            + weather_line4_height \
            + weather_line_spacing + 10
            , u'空气指数')

if wdata.get('today_temp_hig') is None:
    screen.text(weather_text_x + 64, weather_y + margin_top \
                + weather_line1_height \
                + weather_line_spacing + 5
                , u'%s℃ %s' % \
                (
                wdata['today_temp_low'] \
                ,wdata['current_wind']))
else:
    screen.text(weather_text_x + 64, weather_y + margin_top \
                + weather_line1_height \
                + weather_line_spacing + 5
                , u'%s~%s℃ %s' % ( \
                wdata['today_temp_hig'] \
                ,wdata['today_temp_low'] \
                ,wdata['current_wind']))

weather2_x = 550
weather2_y = weather_y + margin_top \
            + weather_line1_height \
            + weather_line_spacing \
            + weather_line2_height \
            + weather_line_spacing

box_height = 210
box_width  = screen_width - 20 - weather2_x
screen.line(weather2_x, weather2_y, screen_width - 20, weather2_y)
screen.line(weather2_x, weather2_y + 48 + 10, screen_width - 20, weather2_y + 48 + 10)
screen.line(weather2_x, weather2_y, weather2_x, weather2_y + box_height)
screen.line(screen_width - 20, weather2_y, screen_width - 20, weather2_y + box_height )
screen.line(weather2_x, weather2_y + box_height, screen_width - 20, weather2_y + box_height)

screen.set_ch_font_size(FONT_SIZE_32)
screen.set_en_font_size(FONT_SIZE_32)
screen.text(weather2_x + 50, weather2_y + 12, '明日预告')

if wdata.get('tomorrow_aq') is None:
    screen.wrap_text(weather2_x + 8, weather2_y + 48 + 20, \
        box_width, u'%s,%s~%s℃,%s' % \
        (wdata['tomorrow_weather'] \
        , wdata['tomorrow_temp_hig'] \
        , wdata['tomorrow_temp_low'] \
        , wdata['tomorrow_wind']))
else:
    screen.wrap_text(weather2_x + 8, weather2_y + 48 + 20, \
        box_width, u'%s,%s~%s℃,%s, AQI %s%s' % \
        (wdata['tomorrow_weather'] \
        , wdata['tomorrow_temp_hig'] \
        , wdata['tomorrow_temp_low'] \
        , wdata['tomorrow_wind'] \
        , wdata['tomorrow_aq'] \
        , wdata['tomorrow_aq_desc']))


screen.update()
screen.disconnect()
