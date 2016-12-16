#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Serial port class based on YaPySerial.py

from yaplcconnectors.YAPLC.YaPySerial import *


class MK200Serial (YaPySerial):

    def Read(self, nbytes):
        try:
            buf = ctypes.create_string_buffer( int(nbytes) )
            res = int(self._SerialRead( ctypes.byref( self.port ), ctypes.cast( buf, ctypes.c_void_p ), ctypes.c_size_t( nbytes ) ))
        except:
            raise YaPySerialError("Runrtime error on serial read!")
        tmp = str(buf.raw)
        response = tmp.replace("\0", "")
        print response
        return response

