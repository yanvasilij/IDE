#!/usr/bin/env python
# -*- coding: utf-8 -*-

#MK200 connector, based on YAPLC connector, LPCProto.py and LPCAppProto.py
#from PLCManager

from yaplcconnectors.YAPLC.YAPLCProto import *

class TestTransaction(YAPLCTransaction):
    def __init__(self):
        YAPLCTransaction.__init__(self, "Try to connect to target\r")

    def SendCommand(self):
        # send command thread
        self.SerialPort.Write(self.Command)

    def GetCommandAck(self):
        return 0x55


class MK200Transaction (YAPLCTransaction):

    def SendCommand(self):
        # send command thread
        self.SerialPort.Write(self.Command)

    def GetCommandAck(self):
        return 0x55

    def GetData(self):
        return None



class STARTTransaction(MK200Transaction):
    def __init__(self):
        MK200Transaction.__init__(self, "Start transaction\r")


class IDLETransaction(MK200Transaction):
    def __init__(self):
        MK200Transaction.__init__(self, "Idle transaction\r")


class STOPTransaction(MK200Transaction):
    def __init__(self):
        MK200Transaction.__init__(self, "Stop trasaction\r")
        #ExchangeData = YAPLCTransaction.GetData


class BOOTTransaction(MK200Transaction):
    def __init__(self):
        MK200Transaction.__init__(self, "Boot trasaction\r")


class SET_TRACE_VARIABLETransaction(MK200Transaction):
    def __init__(self, data):
        YAPLCTransaction.__init__(self, "SET_TRACE_VARIABLETransaction\r")


class GET_TRACE_VARIABLETransaction(MK200Transaction):
    def __init__(self):
        YAPLCTransaction.__init__(self, "GET_TRACE_VARIABLETransaction\r")


class GET_PLCIDTransaction(MK200Transaction):
    def __init__(self):
        YAPLCTransaction.__init__(self, "GET_PLCIDTransaction\r")


class GET_LOGCOUNTSTransaction(MK200Transaction):
    def __init__(self):
        YAPLCTransaction.__init__(self, "GET_LOGCOUNTSTransaction\r")


class GET_LOGMSGTransaction(MK200Transaction):
    def __init__(self,level,msgid):
        YAPLCTransaction.__init__(self, "GET_LOGMSGTransaction\r")


class RESET_LOGCOUNTSTransaction(MK200Transaction):
    def __init__(self):
        YAPLCTransaction.__init__(self, "RESET_LOGCOUNTSTransaction\r")


class SETRTCTransaction(MK200Transaction):
    def __init__(self):
        YAPLCTransaction.__init__(self, "SETRTCTransaction\r")

