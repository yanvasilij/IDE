#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Serial port class based on YaPySerial.py

from yaplcconnectors.YAPLC.YaPySerial import *
import copy

CONNECTION_ATTEMPS = 50

class MK200Serial (YaPySerial):

    def Read(self, nbytes):
        try:
            buf = ctypes.create_string_buffer( int(nbytes) )
            int(self._SerialRead( ctypes.byref( self.port ), ctypes.cast( buf, ctypes.c_void_p ), ctypes.c_size_t( nbytes ) ))
            tmp = str(buf.raw)
            tmp = tmp.replace("\0", "")
            if len(tmp) == 0:
                self.Write(self.TxBuf)
                time.sleep(0.05)
                int(self._SerialRead( ctypes.byref( self.port ), ctypes.cast( buf, ctypes.c_void_p ), ctypes.c_size_t( nbytes ) ))
        except:
            raise YaPySerialError("Runtime error on serial read!")
        tmp = str(buf.raw)
        response = tmp.replace("\0", "")
        return response

    def Write(self, buf):
        YaPySerial.Write(self, buf)
        self.TxBuf = buf

    def Open(self, device, baud, modestr, timeout):
        self.port = ctypes.c_void_p(0)
        res = None
        for i in range(0, CONNECTION_ATTEMPS):
            try:
                res = int( self._SerialOpen( ctypes.byref( self.port ), ctypes.c_char_p( device ), ctypes.c_int( baud ), ctypes.c_char_p( modestr ), ctypes.c_int( timeout )))
            except:
                if i == CONNECTION_ATTEMPS:
                    raise YaPySerialError("Runrtime error on serial close!")
                else:
                    pass
            if res > 0:
                if i == CONNECTION_ATTEMPS:
                    msg = "Couldn't open serial port, error: " + str( res ) + "!"
                    raise YaPySerialError( msg )
            else:
                break
            time.sleep(0.1)


