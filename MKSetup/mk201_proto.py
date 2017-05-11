# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'

import wx
import time
from threading import Thread
from wx.lib.pubsub import Publisher
from serialWork import SerialPort
from MK200Transaction import MK200BootTransaction

"""
@brief класс описывающий обработку hex-файла в бинарный и обработку ответа
@Author Yanikeev-as
"""
EVT_RESULT_ID = wx.NewId()
import copy

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class mk201_proto(SerialPort):
    def __init__(self):
        SerialPort.__init__(self)
        self.HexLineTypes = {"04": "Extended Linear Address", "00": "Data", "01": "End of file", "05": "Start linear Address"}
        self.DefauleLineType = {"Type":"Data", "Len": 0, "Address": 0, "Data": ""}

        # hex-file format is :LLAAAATTDD...CC, where LL - lenght in bytes of DD, AAAA - low 2 bytes of address,
        # TT - type (could be 00 - binary data, 01 - EOF, 02 - segment address, 03 - start segment adress record,
        # 04 - write extended address, 05 -  Start Linear Address Record
        # first - parse first line it must be exact format

    def load_hex_mk201(self, hexFilePath, lol=0):
        data_list = self.handleHex_mk201(hexFilePath)
        # print('type hex mk201', type(bin_file))
        # data_list = self.splitString(bin_file)
        loaded_part = 0
        try:
            # cmd = MK200BootTransaction()
            # cmd.SendCommand()
            self.write('Boot\r\n')
            self.read()
            self.read()
            time.sleep(0.5)
            # self.write('Download\n')
            for data_part in data_list:
                self.write(data_part)
                loaded_part = loaded_part + 1
                wx.CallAfter(Publisher().sendMessage, "update", loaded_part)
        finally:
            time.sleep(0.5)
            self.serialAnswer = self.read()
            self.serialAnswer = self.read()
            print(self.serialAnswer)
            self.write('BootEnd\r\n')
            wx.CallAfter(Publisher().sendMessage, 'update', self.serialAnswer)

    def checkHexFile(self, hexFilePath):
        # try:
            dataLenPath = len(self.handleHex_mk500(hexFilePath))
            if dataLenPath >= 204800:
                return False
            else:
                return True
        # except:
        #     return False

    def load_hex_mk500(self, hexFilePath, lol = 0):
        dataLenPath = len(self.handleHex_mk500(hexFilePath))
        if not(self.checkHexFile):
            answer = 'Wrong hex-file!'
            wx.CallAfter(Publisher().sendMessage, "update", 100)
            wx.CallAfter(Publisher().sendMessage, "update", answer)
            return 0
        data_list = self.splitHexInto256bytes(hexFilePath)
        part_increment = (float(100) / float(len(data_list)))
        loaded_part = 0
        try:
            self.write('Boot\r\n')
            answer = self.read(12)
            if not('Done' in str(answer)):
                error_msg = 'Error! No answer from module!'
                raise NameError(error_msg)

            self.write('StartDownloading\r\n')
            answer = self.read(26)
            if not('Done' in answer):
                error_msg = 'Error! No answer from module!'
                raise NameError(error_msg)

            for data_part in data_list:
                self.write('Download\r\n' + (data_part))
                answer = self.read()
                if not('Done' in answer):
                    error_msg = 'Error! No answer from module!'
                    raise NameError(error_msg)
                loaded_part = loaded_part + part_increment
                wx.CallAfter(Publisher().sendMessage, "update", loaded_part)
            self.write('Boot\n')
        finally:
            serialAnswer = self.read()
            time.sleep(0.5)
            # self.write('App\r\n')
            # serialAnswer = self.read()
            self.write('Boot\n')
            serialAnswer = self.read()
            self.write('Boot\n')
            serialAnswer = self.read()

            wx.CallAfter(Publisher().sendMessage, "update", 100.0)
            wx.CallAfter(Publisher().sendMessage, 'update', serialAnswer)

    def writeSerilaMk500(self, serialText):
        self.write('setsn: ' + str(serialText) + '\r\n')
        ansewr = self.read()
        # wx.CallAfter(Publisher().sendMessage, 'serial', ansewr)
        return ansewr

    def readSerilaMk500(self):
        self.write('getsn\r\n')
        ansewr = self.read()
        if 'sn' in ansewr:
            return ansewr[4:]
        else:
            return ansewr


    def splitHexInto256bytes(self, dataPath):
        data = self.handleHex_mk500(dataPath)
        data_list = []
        section_len = 256
        startMsgAdr = 0
        finishMsgAdr = section_len
        section = data[startMsgAdr:finishMsgAdr]
        emprtySection = '\xff' * section_len
        data_list.append(section)
        while (len(section) == section_len):
            startMsgAdr += section_len
            finishMsgAdr += section_len
            section = data[startMsgAdr:finishMsgAdr]
            if len(section) == section_len:
                data_list.append(section)
        # section = data[startMsgAdr:]
        lastSection = section + emprtySection[len(section) - 1:]
        data_list.append(lastSection)
        # print data_list
        return data_list

    def splitString(self, string):
        data_len = len(string)
        step_len = data_len / 10
        data_list = []
        for i in range(0, data_len, step_len):
            data_list.append(string[i:i+step_len])
        return data_list


    def get_hex(self, hexFilePath):
        hexfile = open(hexFilePath, 'r')
        data = hexfile.read()
        lines = data.splitlines()
        firstline = lines[0]
        parsed = self.ParseLineFromHex(firstline)
        if (parsed["Type"] != "Extended Linear Address") or (parsed["Len"] != 2):
            print "Invalid hex-file"
            return
        bindata = []
        lastParsed = None
        for line in lines[1:]:
            parsed = self.ParseLineFromHex(line)
            if parsed["Type"] == "Extended Linear Address":
                if parsed["Data"][0] != 8:
                    break
                continue
            if lastParsed != None:
                emptySpaceLen = parsed["Address"] - lastParsed["Address"] - lastParsed["Len"]
            else:
                emptySpaceLen = 0
            if emptySpaceLen > 0:
                for i in range(0, emptySpaceLen):
                    bindata.append(0xFF)
            if parsed["Len"] > 0:
                bindata.extend(parsed["Data"])
            lastParsed = parsed
        bindatastring = 'Download\r\n' + ''.join([chr(item) for item in bindata])
        return bindatastring

    def handleHex_mk201(self, hexFilePath):
        hexfile = open(hexFilePath, 'r')
        data = hexfile.read()
        lines = data.splitlines()
        firstline = lines[0]
        parsed = self.ParseLineFromHex(firstline)
        if (parsed["Type"] != "Extended Linear Address") or (parsed["Len"] != 2):
            print "Invalid hex-file"
            return
        bindata = []
        lastParsed = None
        for line in lines[1:]:
            parsed = self.ParseLineFromHex(line)
            if parsed["Type"] == "Extended Linear Address":
                if parsed["Data"][0] != 8:
                    break
                continue
            if lastParsed != None:
                emptySpaceLen = parsed["Address"] - lastParsed["Address"] - lastParsed["Len"]
            else:
                emptySpaceLen = 0
            if emptySpaceLen > 0:
                for i in range(0, emptySpaceLen):
                    bindata.append(0xFF)
            if parsed["Len"] > 0:
                bindata.extend(parsed["Data"])
            lastParsed = parsed
        bindatastring = 'Download\r\n' + ''.join([chr(item) for item in bindata])
        bindatastring = self.splitString(bindatastring)
        return bindatastring

    def handleHex_mk500(self, hexFilePath):
            hexfile = open(hexFilePath, 'r')
            data = hexfile.read()
            lines = data.splitlines()
            firstline = lines[0]
            parsed = self.ParseLineFromHex(firstline)
            if (parsed["Type"] != "Extended Linear Address") or (parsed["Len"] != 2):
                print "Invalid hex-file"
                return
            bindata = []
            lastParsed = None
            for line in lines[1:]:
                parsed = self.ParseLineFromHex(line)
                if parsed["Type"] == "Extended Linear Address":
                    if parsed["Data"][0] != 8:
                        break
                    continue
                if lastParsed != None:
                    emptySpaceLen = parsed["Address"] - lastParsed["Address"] - lastParsed["Len"]
                else:
                    emptySpaceLen = 0
                if emptySpaceLen > 0:
                    for i in range(0, emptySpaceLen):
                        bindata.append(0xFF)
                if parsed["Len"] > 0:
                    bindata.extend(parsed["Data"])
                lastParsed = parsed
            bindatastring = '' + ''.join([chr(item) for item in bindata])
            return bindatastring

    def ParseLineFromHex(self, line):
        parsed = copy.deepcopy(self.DefauleLineType)
        recordtype = line[7:9]
        if recordtype in self.HexLineTypes.keys():
            bindata = []
            parsed["Type"] = self.HexLineTypes[recordtype]
            parsed["Len"] = int(line[1:3], 16)
            if parsed["Type"] == "Data":
                parsed["Address"] = int(line[3:7], 16)
            else:
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

if __name__ == '__main__':
    testObj = mk201_proto()