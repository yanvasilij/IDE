#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Serial port class based on YaPySerial.py

from yaplcconnectors.YAPLC.YaPySerial import *


class MK200Serial (YaPySerial):

    def Read(self, nbytes):
        try:
            buf = ctypes.create_string_buffer( int(nbytes) )
        except:
            raise YaPySerialError("Runrtime error on serial read!")
        return buf.raw

