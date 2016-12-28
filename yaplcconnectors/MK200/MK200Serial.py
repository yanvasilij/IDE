#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Serial port class based on YaPySerial.py

from yaplcconnectors.YAPLC.YaPySerial import *
import copy


class MK200Serial (YaPySerial):

    def Read(self, nbytes):
        try:
            buf = ctypes.create_string_buffer( int(nbytes) )
            res = int(self._SerialRead( ctypes.byref( self.port ), ctypes.cast( buf, ctypes.c_void_p ), ctypes.c_size_t( nbytes ) ))
            tmp = str(buf.raw)
            tmp = tmp.replace("\0", "")
            if len(tmp) == 0:
                self.Write(self.TxBuf)
                time.sleep(0.05)
                res = int(self._SerialRead( ctypes.byref( self.port ), ctypes.cast( buf, ctypes.c_void_p ), ctypes.c_size_t( nbytes ) ))
        except:
            raise YaPySerialError("Runrtime error on serial read!")
        tmp = str(buf.raw)
        response = tmp.replace("\0", "")
        return response

