# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'

"""
@brief методы работы с последовательным портом
@Author Yanikeev-as
"""

import serial
import serial.tools.list_ports
import sys
import Queue

from threading import Thread

class SerialPort(object):
    def __init__(self):
        self.baud = 115200
        self.parity = serial.PARITY_NONE
        self.timeout = 0.01
        self.serial = serial.Serial()
        self.setSerialOptions()
        self.ConsoleCommandsQueue = Queue
        self.error_msg = []

    def setSerialOptions(self,  port=None, baudrate=115200, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None,
                         dsrdtr=False, inter_byte_timeout=None,exclusive=None):
        self.serial.port = port
        self.serial.baudrate = baudrate
        self.serial.bytesize = bytesize
        self.serial.parity = parity
        self.serial.stopbits = stopbits
        self.serial.timeout = self.timeout
        self.serial.xonxoff = xonxoff
        self.serial.rtscts = rtscts
        self.serial.write_timeout = write_timeout
        self.serial.dsrdtr = dsrdtr
        self.serial.inter_byte_timeout = inter_byte_timeout
        self.serial.exclusive = exclusive

    def read(self, count=0):
        try:
            if count == 0:
                data = self.serial.readline()
            else:
                data = self.serial.read(count)
            return data
        except serial.serialutil.SerialException:
            self.error_msg.append('Error in process loading: ' + str(sys.exc_info()[0]))
            return self.getErrorLog()
            # return None

    def connect(self, port):
        try:
            self.serial.port = port
            self.serial.open()
            return 'Connected'
        except serial.serialutil.SerialException:
            self.error_msg.append('Cant_connect! Error: ' + str(sys.exc_info()[0]) )
            return self.getErrorLog()
            # return None

    def checkConnection(self):
        try:
            self.serial.readline()
            status = True
        except:
            status = False
        return status

    def getPorts(self):
        portsFullName = []
        comPorts = []
        for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
            portsFullName.append('%s - %s' % (portname, desc))
            comPorts.append(portname)
        return comPorts, portsFullName

    def write(self, data):
        try:
            bytes = self.serial.write(data)
            return bytes
        except serial.serialutil.SerialException:
            self.error_msg.append('Error in process loading: ' + str(sys.exc_info()[0]) )
            return self.getErrorLog()


    def getErrorLog(self):
        error_out = self.error_msg
        if len(self.error_msg) == 0:
            return 1
        else:
            self.error_msg = []
            return error_out

    def stringSpliter(self, string):
        data_len = len(string)
        step_len = data_len / 10
        data_list = []
        for i in range(0, data_len, step_len):
            data_list.append(string[i:i+step_len])
        return data_list

