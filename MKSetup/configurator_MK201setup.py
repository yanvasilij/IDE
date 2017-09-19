# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'

import wx
import copy
import os.path
import sys
import time
import xml.etree.ElementTree as ET

import time
import wx

from threading import Thread
# from wx.lib.pubsub import Publisher # importing Publisher for old wx version
from wx.lib.pubsub import pub as Publisher
from threading import Lock

from configurator_serialWorker import serialWorker
from configurator_GUI import ConfiguratorGUI
from mk201_proto import mk201_proto

CONFIG_FILE_NAME = "MK201_config.xml"

DEFAULT_CONFFILE = \
"""
<root>
    <COM1>
        <parity>even</parity>
        <baudrate>115200</baudrate>
        <databytes>1</databytes>
        <modbusAddress>0</modbusAddress>
        <modbusType>&#1056;&#1077;&#1078;&#1080;&#1084; Modbus Master 0</modbusType>
    </COM1>
    <COM2>
        <parity>even</parity>
        <baudrate>115200</baudrate>
        <databytes>1</databytes>
        <modbusAddress>0</modbusAddress>
        <modbusType>&#1056;&#1077;&#1078;&#1080;&#1084; Modbus Master 0</modbusType>
    </COM2>
    <COM3>
        <parity>even</parity>
        <baudrate>115200</baudrate>
        <databytes>1</databytes>
        <modbusAddress>0</modbusAddress>
        <modbusType>&#1056;&#1077;&#1078;&#1080;&#1084; Modbus Master 0</modbusType>
    </COM3>
    <common>
        <IP>100.100.100.100</IP>
        <gateway>100.100.100.100</gateway>
        <mask>100.100.100.100</mask>
        <day>0</day>
        <month>0</month>
        <year>0</year>
    </common>
</root>
"""


class Configurator_MK201(ConfiguratorGUI):
    def __init__(self, parent=None, modulObject=None, projectPath=""):
        ConfiguratorGUI.__init__(self, parent)
        if parent is None:
            self.moduleObject = mk201_proto(self)
            # self.moduleObject.serial.timeout = 0.05
            res = self.moduleObject.connect('COM9')
        else:
            self.moduleObject = modulObject

        self.projectPath = projectPath
        if projectPath == "":
            self.projectPath = os.path.abspath(os.curdir)
        self.configeFilePath = projectPath + CONFIG_FILE_NAME
        self.configeWidget.pathTextCtrl.SetValue(self.configeFilePath)

        self.configeWidget.downloadFromPLCBtn.Bind(wx.EVT_BUTTON, self.readFromPLC)
        self.configeWidget.downloadInPLCBtn.Bind(wx.EVT_BUTTON, self.writeInPLC)
        self.configeWidget.saveBtn.Bind(wx.EVT_BUTTON, self.saveConfige)
        self.configeWidget.openFileBtn.Bind(wx.EVT_BUTTON, self.OnOpen)
        self.loadConfige()

        if not(self.moduleObject is None):
            self.configeWidget.downloadFromPLCBtn.Enable(True)
            self.configeWidget.downloadInPLCBtn.Enable(True)
            self.serialTread = serialWorker(self.moduleObject, self)
            self.serialTread.run()

            # добавляю стандартные команды, которые должны выполняться каждый цикл опроса
            self.serialTread.standartComandsList.append({'str': 'gettime\r\n',
                                                     'responseFormat': 'Done\r\n'})


            self.msgQueue = self.serialTread.ConsoleCommandsQueue
            self.Bind(self.serialTread.EVT_RESOULT, self.updateDisplay)
        # self.firstRequest()
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        # Publisher().subscribe(self.OnClose, "lostConection")
        # Publisher.subscribe(self.updateDisplay, "result")
        # Publisher.subscribe(self.OnClose, "lostConection")

    def dialogMessage(self, message):
        dialog = wx.MessageBox(message, u'Ошибка!', wx.OK | wx.ICON_INFORMATION)

    def readFromPLC(self, event):
        self.firstRequest()
        self.serialTread.run()

    def writeInPLC(self, event):
        self.setComSettings(self.comWidget_1)
        self.setComSettings(self.comWidget_2)
        self.setComSettings(self.comWidget_3)
        self.setAddress(self.ipWidget)
        self.setAddress(self.maskWidget)
        self.setAddress(self.gatewayWidget)
        self.setDate(self.dateWidget)
        self.setTime(self.timeSettigsWidget)
        self.serialTread.run()

    def firstRequest(self):
        for comNuum in range(3):
            self.msgQueue.put({'str': 'getuartcfg: {0}\r\n'.format(comNuum),
                              'responseFormat': 'Done\r\n'})
            self.msgQueue.put({'str': 'getcommode: {0}\n'.format(comNuum),
                               'responseFormat': 'Done\r\n'})
            self.msgQueue.put({'str': 'getmbaddr: {0}\r\n'.format(comNuum),
                               'responseFormat': 'Done\r\n'})
        self.msgQueue.put({'str': 'getnmask\r\n',
           'responseFormat': 'Done\r\n'})
        self.msgQueue.put({'str': 'getgateway\r\n',
           'responseFormat': 'Done\r\n'})
        self.msgQueue.put({'str': 'getip\r\n',
           'responseFormat': 'Done\r\n'})
        self.msgQueue.put( {'str': 'getdate\r\n',
               'responseFormat': 'Done\r\n'})
        self.msgQueue.put( {'str': 'gettime\r\n',
               'responseFormat': 'Done\r\n'})

    def OnOpen(self, event):
        openFileDialog = wx.FileDialog(self, "Open XYZ file", "", "",
                                       "XML files (*.xml)|*.xml", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetDirectory(self.projectPath)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        self.configeFilePath = openFileDialog.GetPath()
        self.configeWidget.pathTextCtrl.SetValue(self.configeFilePath)
        self.loadConfige()

    def setComSettings(self, object):
        # настройки порта
        stopBitsDict = {'1': '1', '1.5': '2', '2': '3'} # чтобы не писать флоаты буду использоваться такие значения ждя
                                                        # stopBits
        curWidget = object
        comNum = curWidget.comNum
        baud = curWidget.baudrateCombobox.GetValue()
        parity = str(curWidget.parityCombobox.GetValue())
        stopbits = str(curWidget.databytesCombobox.GetValue())
        # сообщение для настроек скорости, паритета, стобитов
        cmd_portSetting = {'str': 'setuartcfg: {0} {1} {2} {3}\r\n'.format(comNum, baud, parity, stopBitsDict[stopbits]),
                           'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_portSetting)

        # настройка модбаса
        modbusSelection = curWidget.modbusCombobox.GetValue()
        modbusSetting_list = {u"Режим Modbus Master 0": "mbmaster0", u"Режим Modbus Master 1": "mbmaster1",
                              u"Режим Modbus Master 2": "mbmaster2", u"Режим Modbus slave": "mbslave",
                              u"Выключен": "off"}
        cmd_modbusSetting = {'str': 'setcommode: {0} {1}\r\n'.format(comNum, modbusSetting_list[modbusSelection]),
                            'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_modbusSetting)

        # настройка порта модбаса
        modbusaAddres = curWidget.modbusAddress.GetLineText(0)
        cmd_modbusAddress = {'str': 'setmbaddr: {0} {1}\r\n'.format(comNum, modbusaAddres),
                            'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_modbusAddress)

    def getComSetting(self, event):
        eventObject = event.GetEventObject()
        comNuum = eventObject.Parent.comNum - 1
        cmd_portSettings = {'str': 'getuartcfg: {0}\r\n'.format(comNuum),
               'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_portSettings)
        cmd_modbusSettings = {'str': 'getcommode: {0}\r\n'.format(comNuum),
               'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_modbusSettings)
        cmd_modbusPort = {'str': 'getmbaddr: {0}\r\n'.format(comNuum),
               'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_modbusPort)

    def getModbusPort(self, event):
        eventObject = event.GetEventObject()
        comNuum = eventObject.Parent.comNum - 1
        cmd_readModbusPort = {'str': 'getuartcfg: {0}\r\n'.format(comNuum),
               'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_readModbusPort)

    def setAddress(self, object):
        curObject = object
        addressType = curObject.addressType
        # print('addressType ', addressType)
        address = curObject.addressTextCtl.GetAddress()
        address = address.replace('.', ' ')
        if addressType == u'IP-адресс':
            cmd_networkSetting = {'str': 'setip: {0}\r\n'.format(address),
               'responseFormat': 'Done\r\n'}
        if addressType == u'Шлюз':
            cmd_networkSetting = {'str': 'setgateway: {0}\r\n'.format(address),
               'responseFormat': 'Done\r\n'}
        if addressType == u'Маска':
            cmd_networkSetting = {'str': 'setnmask: {0}\r\n'.format(address),
               'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_networkSetting)
        # print(cmd_networkSetting)

    def getAddress(self, event):
        eventObject = event.GetEventObject()
        addressType = eventObject.Parent.addressType
        # print('addressType ', addressType)
        if addressType == u'IP-адресс':
            cmd_networkSetting = {'str': 'getip\r\n',
               'responseFormat': 'Done\r\n'}
        if addressType == u'Шлюз':
            cmd_networkSetting = {'str': 'getgateway\r\n',
               'responseFormat': 'Done\r\n'}
        if addressType == u'Маска':
            cmd_networkSetting = {'str': 'getnmask\r\n',
               'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_networkSetting)
        # print(cmd_networkSetting)

    def getDate(self, event):
        cmd_getdate = {'str': 'getdate\r\n',
               'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_getdate)

    def creacConfFile(self):
        file = open(self.configeFilePath, 'w')
        file.write(DEFAULT_CONFFILE)
        file.close()

    def saveConfige(self, event):
        if not(os.path.isfile(self.configeFilePath)):
            self.creacConfFile()

        tree = ET.parse(self.configeFilePath)
        root = tree.getroot()
        # try:
        COM1 = root.find('COM1')
        COM2 = root.find('COM2')
        COM3 = root.find('COM3')
        common = root.find('common')
        try:
            COM1.find("parity").text = str(self.comWidget_1.parityCombobox.GetValue())
            COM1.find("baudrate").text = str(self.comWidget_1.baudrateCombobox.GetValue())
            COM1.find("databytes").text = (str(self.comWidget_1.databytesCombobox.GetValue()))
            COM1.find("modbusType").text = (self.comWidget_1.modbusCombobox.GetValue())
            COM1.find("modbusAddress").text = str(self.comWidget_1.modbusAddress.GetLineText(0))

            COM2.find("parity").text = str(self.comWidget_2.parityCombobox.GetValue())
            COM2.find("baudrate").text = str(self.comWidget_2.baudrateCombobox.GetValue())
            COM2.find("databytes").text = str(self.comWidget_2.databytesCombobox.GetValue())
            COM2.find("modbusType").text = (self.comWidget_2.modbusCombobox.GetValue())
            COM2.find("modbusAddress").text = str(self.comWidget_2.modbusAddress.GetLineText(0))

            COM3.find("parity").text = str(self.comWidget_3.parityCombobox.GetValue())
            COM3.find("baudrate").text = str(self.comWidget_3.baudrateCombobox.GetValue())
            COM3.find("databytes").text = str(self.comWidget_3.databytesCombobox.GetValue())
            COM3.find("modbusType").text = (self.comWidget_3.modbusCombobox.GetValue())
            COM3.find("modbusAddress").text = str(self.comWidget_3.modbusAddress.GetLineText(0))

            common.find("IP").text = str(self.ipWidget.addressTextCtl.GetValue())
            common.find("gateway").text = str(self.gatewayWidget.addressTextCtl.GetValue())
            common.find("mask").text = str(self.maskWidget.addressTextCtl.GetValue())
            common.find("day").text = str(self.dateWidget.dayTextCtl.GetLineText(0))
            common.find("month").text = str(self.dateWidget.monthTextCtl.GetLineText(0))
            common.find("year").text = str(self.dateWidget.yearTextCtl.GetLineText(0))
        except:
            self.creacConfFile()
            self.saveConfige(1)
            return 0

        tree.write(self.configeFilePath)


    def loadConfige(self):
        # если не бдует конфиг файла, то в видежтах будет значение по-умолчанию
        if os.path.isfile(self.configeFilePath):
            tree = ET.parse(self.configeFilePath)
            root = tree.getroot()
            data = {}
            for numPort in range(1,4):
                port = "COM" + str(numPort)
                data[port] = {
                    "parity": root.find(port).find("parity").text,
                    "baudrate": root.find(port).find("baudrate").text,
                    "databytes": root.find(port).find("databytes").text,
                    "modbusType": root.find(port).find("modbusType").text,
                    "modbusAddress": root.find(port).find("modbusAddress").text
                }
            data["IP"] = root.find("common").find("IP").text
            data["gateway"] = root.find("common").find("gateway").text
            data["mask"] = root.find("common").find("mask").text
            data["day"] = root.find("common").find("day").text
            data["month"] = root.find("common").find("month").text
            data["year"] = root.find("common").find("year").text
            try:
                self.ipWidget.addressTextCtl.SetValue(data["IP"])
                self.gatewayWidget.addressTextCtl.SetValue(data["gateway"])
                self.maskWidget.addressTextCtl.SetValue(data["mask"])
                # в комментариях метод выставление в комбобокс элемента комбобокса, а то что ниже я просто записываю
                # стринговое значение, а не беру
                # self.comWidget_1.parityCombobox.SetSelection(self.comWidget_1.parityCombobox.FindString(data["COM1"]["parity"]))
                self.comWidget_1.parityCombobox.SetValue(data["COM1"]["parity"])
                self.comWidget_1.baudrateCombobox.SetValue(data["COM1"]["baudrate"])
                self.comWidget_1.databytesCombobox.SetValue(data["COM1"]["databytes"])
                self.comWidget_1.modbusCombobox.SetValue(data["COM1"]["modbusType"])
                self.comWidget_1.modbusAddress.SetValue(int(data["COM1"]["modbusAddress"]))
                self.comWidget_2.parityCombobox.SetValue(data["COM2"]["parity"])
                self.comWidget_2.baudrateCombobox.SetValue(data["COM2"]["baudrate"])
                self.comWidget_2.databytesCombobox.SetValue(data["COM2"]["databytes"])
                self.comWidget_2.modbusCombobox.SetValue(data["COM2"]["modbusType"])
                self.comWidget_2.modbusAddress.SetValue(int(data["COM2"]["modbusAddress"]))
                self.comWidget_3.parityCombobox.SetValue(data["COM3"]["parity"])
                self.comWidget_3.baudrateCombobox.SetValue(data["COM3"]["baudrate"])
                self.comWidget_3.databytesCombobox.SetValue(data["COM3"]["databytes"])
                self.comWidget_3.modbusCombobox.SetValue(data["COM3"]["modbusType"])
                self.comWidget_3.modbusAddress.SetValue(int(data["COM3"]["modbusAddress"]))
                self.dateWidget.dayTextCtl.SetValue(int(data["day"]))
                self.dateWidget.monthTextCtl.SetValue(int(data["month"]))
                self.dateWidget.yearTextCtl.SetValue(int(data["year"]))
            except TypeError:
                # print sys.exc_info()
                message = u"Неверный конфигурационный файл"
                self.dialogMessage(message)

    def setDate(self, obj):
        curtObject = obj
        day = curtObject.dayTextCtl.GetLineText(0)
        month = curtObject.monthTextCtl.GetLineText(0)
        year = curtObject.yearTextCtl.GetLineText(0)
        cmd_setdate = {'str': 'setdate: {0} {1} {2}\r\n'.format(day, month, year),
               'responseFormat': 'Done\r\n'}
        # print('write date ', cmd_setdate)
        self.msgQueue.put(cmd_setdate)

    def getTime(self, event):
        cmd_gettime = {'str': 'gettime\r\n',
               'responseFormat': 'Done\r\n'}

        self.msgQueue.put(cmd_gettime)

    def setTime(self, obj):
        eventObject = obj
        hour = eventObject.hourTextCtl.GetLineText(0)
        min = eventObject.minuteTextCtl.GetLineText(0)
        sec = eventObject.secondTextCtl.GetLineText(0)
        cmd_setdate = {'str': 'settime: {0} {1} {2}\r\n'.format(hour, min, sec),
               'responseFormat': 'Done\r\n'}
        # print('write date ', cmd_setdate)
        self.msgQueue.put(cmd_setdate)

    def updateDisplay(self, msg):
        modbusSetting_list = {"mbmaster0": u"Режим Modbus Master 0", "mbmaster1": u"Режим Modbus Master 1",
                              "mbmaster2": u"Режим Modbus Master 2", "mbslave": u"Режим Modbus slave",
                              "off": u"Выключен"}
        stopBitsDict = {'1': '1', '2': '1.5', '3': '2'}
        data = msg.GetValue()
        comNum = str(int(data[u'portNum']) + 1)
        result = data[u'result']
        result_list = data[u'result'].split()
        # print('data', data)
        # # print('result answer', data[u'result'])
        if u"cfg" in result:
            if (len(result_list) == 4):
                baud = result_list[1]
                parity = result_list[2]
                stopBits = result_list[3]
                widgetGroup = getattr(self, "comWidget_" + comNum)
                widgetGroup.baudrateCombobox.SetStringSelection(baud)
                widgetGroup.parityCombobox.SetStringSelection(parity)
                widgetGroup.databytesCombobox.SetStringSelection(stopBitsDict[stopBits])
        if (u"mode" in result) and not('getcommode' in result):
            if (len(result_list) == 2):
                modbus = result_list[1]
                # print(modbus)
                widgetGroup = getattr(self, "comWidget_" + comNum)
                widgetGroup.modbusCombobox.SetStringSelection(modbusSetting_list[modbus])
        if u'adr' in result:
            if (len(result_list) == 2):
                widgetGroup = getattr(self, "comWidget_" + comNum)
                modbusAddress = result_list[1]
                widgetGroup.modbusAddress.Clear()
                widgetGroup.modbusAddress.write(modbusAddress)
        if (u'ip' in result) and not(u'setip' in result):
            if (len(result_list) == 5):
                widgetGroup = getattr(self, "ipWidget")
                resAddres = result[4:].replace(' ', '.')
                resAddres = resAddres.replace('\r\n', '')
                # print('resAddres', str(resAddres))
                widgetGroup.addressTextCtl.Clear()
                widgetGroup.addressTextCtl.SetValue(resAddres)
        if (u'mask' in result) and not(u'setnmask' in result):
            if (len(result_list) == 5):
                # print('result_list', result_list)
                widgetGroup = getattr(self, "maskWidget")
                resAddres = result[6:].replace(' ', '.')
                resAddres = resAddres.replace('\r\n', '')
                widgetGroup.addressTextCtl.Clear()
                widgetGroup.addressTextCtl.SetValue(resAddres)
        if (u'gateway' in result) and not(u'setgateway' in result):
            if (len(result_list) == 5):
                widgetGroup = getattr(self, "gatewayWidget")
                resAddres = result[9:].replace(' ', '.')
                resAddres = resAddres.replace('\r\n', '')
                # print('gateway ', resAddres )
                widgetGroup.addressTextCtl.Clear()
                widgetGroup.addressTextCtl.SetValue(resAddres)
        if u'date' in result:
            if (len(result_list) == 4):
                day = result_list[1]
                month = result_list[2]
                year = result_list[3]
                widgetGroup = getattr(self, "dateWidget")
                widgetGroup.dayTextCtl.Clear()
                widgetGroup.dayTextCtl.write(day)
                widgetGroup.monthTextCtl.Clear()
                widgetGroup.monthTextCtl.write(month)
                widgetGroup.yearTextCtl.Clear()
                widgetGroup.yearTextCtl.write(month)
        if u'time' in result:
            if (len(result_list) == 4):
                # print(result)
                hour = result_list[1]
                min = result_list[2]
                sec = result_list[3]
                widgetGroup = getattr(self, "curTimeWidget")
                widgetGroup.hourTextCtl.Clear()
                widgetGroup.hourTextCtl.write(hour)
                widgetGroup.minuteTextCtl.Clear()
                widgetGroup.minuteTextCtl.write(min)
                widgetGroup.secondTextCtl.Clear()
                widgetGroup.secondTextCtl.write(sec)
        if u'Error:' in result:
            # print 'Lost connection'
            self.OnClose(1)

    def OnClose(self, event):
        # self.serialTread.stopThread()
        # self.modulObj.serial.close()
        self.Destroy()

if __name__ == '__main__':
    app = wx.App(False)
    top = Configurator_MK201()
    top.Show()
    app.MainLoop()