# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'
# в файле описываются классы транзакций, предназначенные для работы с модлем MK201

import time
MAX_CMD_LEN = 200

"""
@brief базовы класс всех трназакций
@Author Yanikeev-as
"""
class MK200TransactionBase(object):
    def __init__(self, serialPort):
        self.serialPort = serialPort
        self.Command = None

    def SendCommand(self):
        self.serialPort.write(self.Command)

    def GetCommandAck(self):
        time.sleep(0.05)
        res = self.serialPort.read()
        return res

class MK200BootTransaction(MK200TransactionBase):
    def __init__(self, serialProt):
        MK200TransactionBase.__init__(self, serialProt)
        self.serialPort.write('Boot\r\n')
        time.sleep(0.5)
        self.serialPort.read()

class MK200BootEndTransaction(MK200TransactionBase):
    def __init__(self, serialProt):
        MK200TransactionBase.__init__(self, serialProt)
        self.Command = "BootEnd\r\n"

class GET_PLCStatusTransaction(MK200TransactionBase):
    def __init__(self, serialProt):
        MK200TransactionBase.__init__(self, serialProt)
        self.serialPort = serialProt
        self.Command = "GetPlcStatus\r\n"
        self.serialPort.serial.reset_input_buffer()
        self.serialPort.write(self.Command)
        self.Status = None

    def GetCommandAck(self):
        res = self.serialPort.read()
        res = self.serialPort.read()
        if type(res) is list:
            self.Status = None
            return self.Status, res[0]
        initital = res.replace("\r", "\\r")
        initital = initital.replace("\n", "\\n")
        # res = res.split("\\n")
        if len(res) > 2:
            res = res[1]
        if initital == "Stopped\\r\\n":
            self.Status = "Stopped"
            return self.Status, 0x55
        elif initital == "Running\\r\\n":
            self.Status = "Started"
            return self.Status, 0xaa
        else:
            self.Status = None
            return self.Status, "MK200 transaction error - controller did not ack order!"
            return("MK200 transaction error - controller did not ack order!")

    def ExchangeData(self):
        return self.Status
