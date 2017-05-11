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
        self.serialPort.Write(self.Command)

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
        self.serialPort.write(self.Command)
        self.Status = None

    def GetCommandAck(self):
        res = self.serialPort.read()
        print 'res', res, type(res)
        # initital = res.replace("\r", "\\r")
        # initital = initital.replace("\n", "\\n")
        # res = res.split("\\n")
        if len(res) > 2:
            res = res[1]
        if res == "Stopped\r":
            self.Status = "Stopped"
            return self.Status, 0x55
        elif res == "Running\r":
            self.Status = "Started"
            return self.Status, 0xaa
        else:
            self.Status = None
            return self.Status, 0xaa
            return("MK200 transaction error - controller did not ack order!")

    def ExchangeData(self):
        return self.Status
