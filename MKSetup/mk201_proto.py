# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'

import os
import sys
import wx
import time
from threading import Thread
# from wx.lib.pubsub import Publisher # importing Publisher for old wx version ( must use Publisher. instead of Publisher())
# from wx.lib.pubsub import pub as Publisher
from serialWork import SerialPort
from MK200Transaction import MK200BootTransaction


"""
@brief тип объекьа событие для взаимодейсвтия между потоками \ event type to use for communication between threads
@Author Yanikeev-as
"""
class CountEvent(wx.PyCommandEvent):
    """Event to signal that value is ready"""
    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        return self._value

"""
@brief класс описывающий обработку hex-файла в бинарный и обработку ответа
@Author Yanikeev-as
"""
EVT_RESULT_ID = wx.NewId()
import copy

class CrcException(Exception): pass

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
    CRC_TAB16 = []
    def __init__(self, wxParent):
        SerialPort.__init__(self)
        self.HexLineTypes = {"04": "Extended Linear Address", "00": "Data", "01": "End of file", "05": "Start linear Address"}
        self.DefauleLineType = {"Type":"Data", "Len": 0, "Address": 0, "Data": ""}
        self._wxParent = wxParent
        # hex-file format is :LLAAAATTDD...CC, where LL - lenght in bytes of DD, AAAA - low 2 bytes of address,
        # TT - type (could be 00 - binary data, 01 - EOF, 02 - segment address, 03 - start segment adress record,
        # 04 - write extended address, 05 -  Start Linear Address Record
        # first - parse first line it must be exact format
        # event for send update loading datas
        self.typeEVT_UPDATE = wx.NewEventType()
        self.EVT_UPDATE = wx.PyEventBinder(self.typeEVT_UPDATE, 1)
        # event send CRC len
        self.typeLEN_CRC = wx.NewEventType()
        self.LEN_CRC = wx.PyEventBinder(self.typeLEN_CRC, 2)

    def breakCheck(self):
        for i in range(5):
            try:
                self.write("logenable 0\r\n")
                self.serial.reset_input_buffer()
                self.write("GetPlcStatus\r\n")
                self.read() # чтения эхо
                answer = self.read(64)
                if "Stopped" in answer:
                    return 1
                time.sleep(0.1)
                self.write("GetPlcStatus\r\n")
            except:
                pass
        return 0


    def load_hex_mk201(self, hexFilePath, lol=0):
        data_list = self.handleHex_mk201(hexFilePath)
        # print('type hex mk201', type(bin_file))
        # data_list = self.splitString(bin_file)
        loaded_part = 0
        try:

            # cmd = MK200BootTransaction()
            # cmd.SendCommand()
            self.write('logenable 0\r\n')
            time.sleep(0.5)
            self.serial.reset_input_buffer()
            self.write('Boot\r\n')
            self.read()
            self.read()
            time.sleep(0.5)
            # self.write('Download\n')
            for data_part in data_list:
                answer = self.write(data_part)
                loaded_part = loaded_part + 1
                if type(answer) is list:
                    # wx.CallAfter(Publisher.sendMessage, "update", answer[0])
                    evt = CountEvent(self.typeEVT_RESOULT, -1, answer)
                    wx.PostEvent(self._wxParent, evt)
                    break
                # wx.CallAfter(Publisher.sendMessage, "update", loaded_part)
                evt = CountEvent(self.EVT_UPDATE, -1, loaded_part)
                wx.PostEvent(self._wxParent, evt)
        finally:
            time.sleep(1)
            self.serialAnswer = self.read()
            self.serialAnswer = self.read()
            # print(self.serialAnswer)
            self.write('BootEnd\r\n')
            # wx.CallAfter(Publisher.sendMessage, 'update', self.serialAnswer)
            evt = CountEvent(self.EVT_UPDATE, -1, self.serialAnswer)
            wx.PostEvent(self._wxParent, evt)

    def saveHex(self, hex, path):
        self.hexFileOut = open(path + '\\hexFileOut.hex', 'a')
        self.hexFileOut.write(hex)
        self.hexFileOut.close()

    def init_crc16_tab(self):
        DATA_MAX_LEN = 256
        P16 = 0xA001
        crc, c = 0, 0
        for i in range(0, DATA_MAX_LEN):
            crc = 0
            c = i
            for j in range(0, 8):
                if ( ( crc ^ c ) & 0x0001 ):
                    crc = ( crc >> 1 ) ^ P16
                else:
                    crc =   crc >> 1
                c = c >> 1
            self.CRC_TAB16.append(crc)


    def calcCrc(self, data, msgLen):
        crc_16_modbus  = 0xffff
        self.init_crc16_tab()
        for i in range(0, msgLen):
            crc_16_modbus = self.update_crc_16(crc_16_modbus, ord(data[i]))
        return crc_16_modbus

    def update_crc_16(self, crc, c):
        tmp, short_c = 0, 0
        short_c = 0x00ff & c
        tmp =  crc ^ short_c
        crc = ( crc >> 8 ) ^ self.CRC_TAB16[ tmp & 0xff ]
        return crc

    def sendSegment(self, data):
        max_msg_len = 2100
        data_len = len(data)
        crc = self.calcCrc(data, data_len)
        crcChar = chr(crc % 256) + chr(crc // 256)
        self.write("SendSegment {}\r\n".format(data_len))
        # time.sleep(0.01)
        self.write(data + crcChar)
        # time.sleep(0.01)
        read_status = True
        answer = ""
        start_time = time.time()
        while(1):
            port_msg = self.read(max_msg_len)
            if type(port_msg) is list:
                return False, "Response error: serial connection error"
            answer = answer + port_msg
            # target_response = "SendSegment {}\r\r\nDone!\r\n".format(data_len)
            target_response_correct = "CRC correct!\r\n"
            target_response_incorrect = "CRC incorrect!\r\n"
            if target_response_correct in answer:
                return True, ""
            elif target_response_incorrect in answer:
                error_answer = "SendSegment error : " + answer
                return False, error_answer
            timeout = time.time() - start_time
            if timeout > 2:
                self.write("\r\n".format(data_len))
                # TODO: Есть подозрение, что иногда reset_input_buffer() не работает
                self.serial.reset_input_buffer()
                return False, answer

    def load_hex_mk201_CRC(self, hexFilePath, conn=None):
        read_len = 500
        self.write('logenable 0\r\n')
        time.sleep(0.5)
        a = self.read(read_len)
        self.write("ResetDownload\r\n")
        data_list = self.splitHexInto4096bytes(hexFilePath)
        self.riseEvent(self.typeLEN_CRC, len(data_list)) # instead wx.CallAfter(Publisher.sendMessage, 'partLen', len(data_list))
        all_msg = ""
        for data_part in data_list:
            all_msg = all_msg + data_part
        # total_len = len(all_msg)
        total_crc = self.calcCrc(all_msg, len(all_msg))
        # total_crc_char = chr(total_crc % 256) + chr(total_crc // 256)
        self.write("Boot\r\n")
        time.sleep(1)
        part_counter = 0
        # time_start_asc = time.asctime()
        # time_start_ms = time.time()
        for data_part in data_list:
            error_msg = ""
            result = self.sendSegment(data_part)
            if not(result[0]):
                for i in range(6):
                    result = self.sendSegment(data_part)
                    if result[0]:
                        break
                if i == 5:
                    error_msg = result[1]
            part_counter += 1
            if not(len(error_msg) > 1):
                self.riseEvent(self.typeEVT_UPDATE, part_counter)
            else:
                self.riseEvent(self.typeEVT_UPDATE, error_msg)
                sys.exit(0)
        time.sleep(1)
        self.write("SendTotalCRC {}\r\n".format(total_crc))
        time.sleep(1)
        end_answer = ""
        end_answer += self.read(read_len)
        end_answer += self.read(read_len)
        if "Total CRC correct" in end_answer:
            # print "Youpi! Its work!"
            self.write("RunUserApp\r\n")
            evt = CountEvent(self.typeEVT_UPDATE, -1, "Done!")
            wx.PostEvent(self._wxParent, evt)
        else:
            evt = CountEvent(self.typeEVT_UPDATE, -1, "Error: incorrect total CRC")
            wx.PostEvent(self._wxParent, evt)
        # time_end_asc = time.asctime()
        # time_end_ms = time.time()
        # tottal_time = time_end_ms - time_start_ms
        sys.exit(0)

    def riseEvent(self, eventType, data):
        evt = CountEvent(eventType, -1, data)
        wx.PostEvent(self._wxParent, evt)

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
            wx.CallAfter(Publisher.sendMessage, "update", 100)
            wx.CallAfter(Publisher.sendMessage, "update", answer)
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
                wx.CallAfter(Publisher.sendMessage, "update", loaded_part)
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

            wx.CallAfter(Publisher.sendMessage, "update", 100.0)
            wx.CallAfter(Publisher.sendMessage, 'update', serialAnswer)

    def writeSerilaMk500(self, serialText):
        self.write('setsn: ' + str(serialText) + '\r\n')
        ansewr = self.read()
        # wx.CallAfter(Publisher.sendMessage, 'serial', ansewr)
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

    def splitHexInto4096bytes(self, dataPath):
        data = self.handleHex_mk500(dataPath)
        data_list = []
        section_len = 4096
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
            # print "Invalid hex-file"
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
            # print "Invalid hex-file"
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
                # print "Invalid hex-file"
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
            pass
            # print "Download successful!"
        return 0x55

if __name__ == '__main__':
    testObj = mk201_proto()
    testObj.connect("COM2")
    testObj.load_hex_mk201_CRC("Test_stand_MK200.hex")

