#!/usr/bin/env python
# coding: utf-8

"""
部分函数取自https://github.com/yy502/ePaperDisplay.git
由于不太习惯原作的行文风格，故重造一遍。。。
"""

import struct

import serial

FONT_SIZE_32 = 0x01
FONT_SIZE_48 = 0x02
FONT_SIZE_64 = 0x03

MEM_FLASH   = 0x00
MEM_SD      = 0x01

ROTATION_NORMAL = 0x00
ROTATION_180    = 0x01

# commands
CMD_HANDSHAKE       = 0x00  # handshake
CMD_SET_MEMORY      = 0x07  # get memory mode
CMD_SET_ROTATION    = 0x0d
CMD_UPDATE          = 0x0A  # update
CMD_LOAD_FONT       = 0x0E  # copy font files from SD card to NandFlash.
                            # Font files include GBK32/48/64.FON
                            # 48MB allocated in NandFlash for fonts
                            # LED will flicker 3 times when starts and ends.
CMD_LOAD_PIC        = 0x0F  # Import the image files from SD card to the NandFlash.
                            # LED will flicker 3 times when starts and ends.
                            # 80MB allocated in NandFlash for images
CMD_SET_COLOR       = 0x10  # set colour
CMD_SET_EN_FONT     = 0x1E  # set English font
CMD_SET_CH_FONT     = 0x1F  # set Chinese font

CMD_DRAW_LINE       = 0x22  # draw line
CMD_CLEAR           = 0x2E  # clear screen use back colour
CMD_DRAW_STRING     = 0x30  # draw string
CMD_DRAW_BITMAP     = 0x70  # draw bitmap

COLOR_BLACK         = 0x00
COLOR_DARK_GRAY     = 0x01
COLOR_GRAY          = 0x02
COLOR_WHITE         = 0x03


class Screen(object):
    def __init__(self, tty):
        self.tty = tty
        self.socket = None

    @staticmethod
    def _build_frame(cmd, args=None):
        length = 9
        if args:
            length += len(args)
        frame = '\xA5' + struct.pack('>h', length) + chr(cmd)
        if args:
            frame += args
        frame += '\xCC\x33\xC3\x3C'
        parity = 0x00
        for i in xrange(0, len(frame)):
            parity ^= ord(frame[i])
        frame += chr(parity)
        return frame

    def _send(self, frame):
        self.socket.write(frame)
        return self.socket.read(10)

    def connect(self):
        self.socket = serial.Serial(port=self.tty,
                                    baudrate=115200,
                                    stopbits=serial.STOPBITS_ONE,
                                    bytesize=serial.EIGHTBITS,
                                    timeout=0.03)

    def disconnect(self):
        self.socket.close()

    def handshake(self):
        self._send(self._build_frame(CMD_HANDSHAKE))

    def set_memory(self, mem):
        self._send(self._build_frame(CMD_SET_MEMORY, chr(mem)))

    def set_rotation(self, r):
        self._send(self._build_frame(CMD_SET_ROTATION, chr(r)))

    def clear(self):
        self._send(self._build_frame(CMD_CLEAR))

    def update(self):
        self._send(self._build_frame(CMD_UPDATE))

    def line(self, x0, y0, x1, y1):
        args = struct.pack('>hhhh', x0, y0, x1, y1)
        self._send(self._build_frame(CMD_DRAW_LINE, args))

    def set_color(self, front, background):
        self._send(self._build_frame(CMD_SET_COLOR, chr(front) + chr(background)))

    def set_en_font_size(self, size):
        self._send(self._build_frame(CMD_SET_EN_FONT, chr(size)))

    def set_ch_font_size(self, size):
        self._send(self._build_frame(CMD_SET_CH_FONT, chr(size)))

    @staticmethod
    def _get_real_font_size(font_size):
        return [0, 32, 48, 64][font_size]

    def get_text_width(self, txt, size=FONT_SIZE_32):
        size = self._get_real_font_size(size)
        width = 0
        for c in txt:
            if c in "'":
                width += 5
            elif c in "ijl|":
                width += 6
            elif c in "f":
                width += 7
            elif c in " It![].,;:/\\":
                width += 8
            elif c in "r-`(){}":
                width += 9
            elif c in '"':
                width += 10
            elif c in "*":
                width += 11
            elif c in "x^":
                width += 12
            elif c in "Jvz":
                width += 13
            elif c in "cksy":
                width += 14
            elif c in "Labdeghnopqu$#?_1234567890":
                width += 15
            elif c in "T+<>=~":
                width += 16
            elif c in "FPVXZ":
                width += 17
            elif c in "ABEKSY&":
                width += 18
            elif c in "HNUw":
                width += 19
            elif c in "CDR":
                width += 20
            elif c in "GOQ":
                width += 21
            elif c in "m":
                width += 22
            elif c in "M":
                width += 23
            elif c in "%":
                width += 24
            elif c in "@":
                width += 27
            elif c in "W":
                width += 28
            else:  # non-ascii or Chinese character
                width += 32
        return int(width * (size / 32.0))

    def text(self, x0, y0, text):
        args = struct.pack('>hh', x0, y0)
        if isinstance(text, str):
            text = text.decode('utf-8')
        args += text.encode('gb2312') + '\x00'
        self._send(self._build_frame(CMD_DRAW_STRING, args))

    def wrap_text(self, x0, y0, limit, text, font_size=FONT_SIZE_32, line_space=10):

        line_height = self._get_real_font_size(font_size)
        line = ''
        width = 0
        cy = y0

        if not isinstance(text, unicode):
            text = text.decode('utf-8')

        for c in text:
            line += c
            width += self.get_text_width(c, font_size)
            if width + font_size * 32 > limit:
                self.text(x0, cy, line)
                cy += line_height + line_space
                line = ''
                width = 0

        if line:
            self.text(x0, cy, line)

    def load_pic(self):
        self._send(self._build_frame(CMD_LOAD_PIC))

    def bitmap(self, x0, y0, image):
        if isinstance(image, str):
            image = image.decode('utf-8')
        args = struct.pack('>hh', x0, y0)
        args = args + image.encode('ascii') + '\x00'
        self._send(self._build_frame(CMD_DRAW_BITMAP, args))
