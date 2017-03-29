### 所用的硬件
* 树莓派3
* 微雪4.3寸串口电子墨水屏
* DHT22温湿度传感模块

#### 硬件连接
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

### 准备软件环境
#### 禽兽，放开那个串口。。
树莓派的串口默认是用于linux串口终端登录用的，如果要通过串口控制屏幕，就需要把它解放出来～
#### 树莓派3的串口BUG
在释放串口之前，我们要先解决一下树莓派3的BUG（如果用1,2代请忽略这一步）树莓派3的硬件串口被分配分配给了蓝牙模块，而GPIO14和GPIO15的串口是由内核模拟的，不稳定（可以说基本不能用)，所以首先要把GPIO14和GPIO15改成硬件驱动

第一步 确保SD卡刷了最新的raspbian jessie镜像

第二步 系统启动，并连接了网络

第三步 执行
```bash
sudo apt-get update
sudo apt-get upgrade
```
第四步 编辑 /boot/config.txt 添加一行
```
dtoverlay=pi3-miniuart-bt
```
最后 禁用自带蓝牙
```bash
sudo systemctl disable hciuart
```

#### 释放串口
编辑 /boot/cmdline.txt，默认是下面这样
```
dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait
```
或者这样
```
dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=/dev/mmcblk0p2 kgdboc=serial0,115200 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait
```
把`console=ttyAMA0`,`console=serial0`,`kgdboc=***`这两个参数删掉
变成下面这样
```
dwc_otg.lpm_enable=0 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait
```
之后`sudo reboot`重启系统 串口就可以正常使用了

#### 安装软件依赖
```bash
sudo apt-get install python-requests python-lxml python-serial git build-essential python-dev
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python ./setup.py install
```
#### 准备串口屏幕的图片和字体资源
这个串口屏是通过TF卡加载字体和图片资源的（好坑爹的设计。。），所以你需要准备一张TF卡，格式化为 FAT32 文件系统，分配单元大小选择
4096 字节，然后把tf_card文件夹中的文件全部copy到TF卡根目录，并把TF卡查到屏幕的卡槽里。串口屏的更多资料见：http://www.waveshare.net/w/upload/archive/4/4a/20150408073133!4.3inch-e-Paper-UserManual-CN.pdf

#### 终于可以运行了～～
在运行之前先编辑一下weather_time_render.py，找到下面2行，把注释取消掉，运行时会把屏幕TF卡中的文件加载到屏幕自带的NandFlash中，之后就不需要插TF卡了～～ 
```
# screen.load_pic()
# time.sleep(5)
```
运行脚本
```
sudo ./home_air_sensor.py
./weather_fetcher.py
./weather_time_render.py
```
没有特殊情况，屏幕将和成品显示同样的画面，第一次运行之后就可以把加载图片的2句代码再次注释掉了～

### 成品
![the clock](https://raw.github.com/emptyhua/epaper_clock/master/the_clock_0.jpg)
