#!/usr/bin/env python
# -*- coding: utf-8 -*-

#MK200 connector, based on YAPLC connector, LPCProto.py and LPCAppProto.py
#from PLCManager

from yaplcconnectors.YAPLC.YAPLCProto import *
from MK200Serial import *
import copy
import wx

MAX_CMD_LEN = 200


class MK200Proto(YAPLCProto):

    def __init__(self, libfile, port, baud, timeout):
        # serialize access lock
        self.port = port
        self.baud = baud
        self.timeout = timeout
        # open serial port
        self.SerialPort = MK200Serial(libfile)
        self.Open()

    def HandleTransaction(self, transaction):
        try:
            transaction.SetSerialPort(self.SerialPort)
            # send command, wait ack (timeout)
            transaction.SendCommand()
            current_plc_status = transaction.GetCommandAck()
            if current_plc_status is not None:
                res = transaction.ExchangeData()
        except Exception, e:
            msg = "PLC protocol transaction error : "+str(e)
            raise YAPLCProtoError( msg )
        return YAPLC_STATUS.get(current_plc_status,"Broken"), res


class MK200Transaction (YAPLCTransaction):

    def SendCommand(self):
        # send command thread
        self.SerialPort.Write(self.Command)

    def GetCommandAck(self):
        res = self.SerialPort.Read(MAX_CMD_LEN)
        print res
        return 0x55

    def GetData(self):
        return None


class MK200BinaryTransaction (MK200Transaction):

    def SendCommand(self):
        for ch in self.Command:
            self.SerialPort.Write(ch)



class STARTTransaction(MK200Transaction):
    def __init__(self):
        MK200Transaction.__init__(self, "Start transaction\r")


class IDLETransaction(MK200Transaction):
    def __init__(self):
        MK200Transaction.__init__(self, "Idle transaction\r\n")


class STOPTransaction(MK200Transaction):
    def __init__(self):
        MK200Transaction.__init__(self, "BootEnd\r\n")
        #ExchangeData = YAPLCTransaction.GetData


class BOOTTransaction(MK200Transaction):
    def __init__(self):
        MK200Transaction.__init__(self, "Boot\r\n")

    def GetCommandAck(self):
        res = self.SerialPort.Read(50)
        if res == "Done\r\n":
            return 0x55
        else:
            return None


class DownloadTransaction(MK200Transaction):

    def __init__(self, data, controller):
        self.Controller = controller
        lines = data.splitlines()
        firstline = lines[0]
        self.HexLineTypes = {"04": "Extended Linear Address", "00": "Data", "01": "End of file", "05": "Start linear Address"}
        self.DefauleLineType = {"Type":"Data", "Len": 0, "Address": 0, "Data": ""}
        # hex-file format is :LLAAAATTDD...CC, where LL - lenght in bytes of DD, AAAA - low 2 bytes of address,
        # TT - type (could be 00 - binary data, 01 - EOF, 02 - segment address, 03 - start segment adress record,
        # 04 - write extended address, 05 -  Start Linear Address Record
        parsed = self.ParseLineFromHex(firstline)
        if (parsed["Type"] != "Extended Linear Address") or (parsed["Len"] != 2):
            print "Invalid hex-file"
            return
        bindata = []
        for line in lines[1:]:
            parsed = self.ParseLineFromHex(line)
            if parsed["Type"] == "Extended Linear Address":
                if parsed["Data"][0] != 8:
                    break
                continue
            if parsed["Len"] > 0:
                bindata.extend(parsed["Data"])
        bindatastring = 'Download\r\n' + ''.join([chr(item) for item in bindata])
        MK200Transaction.__init__(self, bindatastring)

    def ParseLineFromHex(self, line):
        parsed = copy.deepcopy(self.DefauleLineType)
        recordtype = line[7:9]
        if recordtype in self.HexLineTypes.keys():
            bindata = []
            parsed["Type"] = self.HexLineTypes[recordtype]
            parsed["Len"] = int(line[1:3], 16)
            parsed["Address"] = int(line[9:13], 16)
            for i in range(0, parsed["Len"]):
                bindata.append(int(line[9+i*2:9+i*2+2], 16))
            parsed["Data"] = copy.copy(bindata)
        return parsed

    def GetCommandAck(self):
        res = self.SerialPort.Read(50)
        if res == "Done\r\n":
            print "Download successful!"
        return 0x55

    def SendCommand(self):
        self.SerialPort.Write(self.Command)
        time.sleep(0.5)


class SET_TRACE_VARIABLETransaction(MK200Transaction):
    def __init__(self, data):
        YAPLCTransaction.__init__(self, "SET_TRACE_VARIABLETransaction\r\n")


class GET_TRACE_VARIABLETransaction(MK200Transaction):
    def __init__(self):
        YAPLCTransaction.__init__(self, "GET_TRACE_VARIABLETransaction\r\n")


class GET_PLCIDTransaction(MK200Transaction):
    def __init__(self):
        YAPLCTransaction.__init__(self, "GET_PLCIDTransaction\r\n")


class GET_LOGCOUNTSTransaction(MK200Transaction):
    def __init__(self):
        YAPLCTransaction.__init__(self, "GetPlcStatus\r\n")


class GET_LOGMSGTransaction(MK200Transaction):
    def __init__(self,level,msgid):
        YAPLCTransaction.__init__(self, "GET_LOGMSGTransaction\r\n")


class RESET_LOGCOUNTSTransaction(MK200Transaction):
    def __init__(self):
        YAPLCTransaction.__init__(self, "RESET_LOGCOUNTSTransaction\r\n")


class SETRTCTransaction(MK200Transaction):
    def __init__(self):
        YAPLCTransaction.__init__(self, "SETRTCTransaction\r\n")

