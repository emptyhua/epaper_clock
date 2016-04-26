###所用的硬件
* 树莓派3
* 微雪4.3寸串口电子墨水屏
* DHT22温湿度传感模块

####硬件连接
屏幕  | 树莓派
------------- | -------------
DIN  | TX(GPIO14)
DOUT  | RX(GPIO15)
GND  | GND
VCC  | 3V

DHT22|树莓派
------------- | -------------
DOUT  | 1-Wire(BCM4)
GND  | GND
VCC  | 3V
DHT22 DOUT引脚也可以接到其他gpio脚上，不过要相应的修改home_air_sensor.py中read_retry第二个参数
###软件依赖
* python-requests
* python-lxml
* python-serial
* https://github.com/adafruit/Adafruit_Python_DHT.git

###成品
![the clock](https://raw.github.com/emptyhua/epaper_clock/master/the_clock_0.jpg)
