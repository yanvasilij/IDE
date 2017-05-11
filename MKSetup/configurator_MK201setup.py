# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'

import wx
import copy
import os.path
import sys
import time

import time
import wx

from threading import Thread
from wx.lib.pubsub import Publisher


from configurator_serialWorker import serialWorker
from configurator_GUI import ConfiguratorGUI
from mk201_proto import mk201_proto

class Configurator_MK201(ConfiguratorGUI):
    def __init__(self, parent = None, modulObject = None, hexFilePath = None):
        ConfiguratorGUI.__init__(self, parent, modulObject, hexFilePath)
        self.moduleObject = self.modulObj
        if parent is None:
            res = self.moduleObject.connect('COM6')
            print(res)
        self.comWidget_1.writePortSettingBtn.Bind(wx.EVT_BUTTON, self.setComSettings)
        self.comWidget_2.writePortSettingBtn.Bind(wx.EVT_BUTTON, self.setComSettings)
        self.comWidget_3.writePortSettingBtn.Bind(wx.EVT_BUTTON, self.setComSettings)
        self.ipWidget.writeAddressBtn.Bind(wx.EVT_BUTTON, self.setAddress)
        self.maskWidget.writeAddressBtn.Bind(wx.EVT_BUTTON, self.setAddress)
        self.gatewayWidget.writeAddressBtn.Bind(wx.EVT_BUTTON, self.setAddress)
        self.dateWidget.dateWriteBtn.Bind(wx.EVT_BUTTON, self.setDate)
        self.timeSettigsWidget.timeWriteBtn.Bind(wx.EVT_BUTTON, self.setTime)

        self.serialTread = serialWorker(self.moduleObject)
        # добавляю стандартные команды, которые должны выполняться каждый цикл опроса
        self.serialTread.standartComandsList.append({'str': 'gettime\r\n',
                                                     'responseFormat': 'Done\r\n'})


        self.serialTread.start()
        self.msgQueue = self.serialTread.ConsoleCommandsQueue
        self.firstRequest()
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        Publisher().subscribe(self.updateDisplay, "result")

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


    def setComSettings(self, event):
        # настройки порта
        stopBitsDict = {'1': '1', '1.5': '2', '2': '3'} # чтобы не писать флоаты буду использоваться такие значения ждя
                                                        # stopBits
        eventObject = event.GetEventObject()
        atrComNum = eventObject.Name[-1]
        commandComNum = int(eventObject.Name[-1]) - 1
        curWidget = eventObject.Parent
        comNum = eventObject.Parent.comNum - 1
        # print('dir ', dir(curWidget), eventObject.__class__)
        baud = curWidget.baudrateCombobox.GetStringSelection()
        parity = curWidget.parityCombobox.GetStringSelection()
        stopbits = curWidget.databytesCombobox.GetStringSelection()
        # сообщение для настроек скорости, паритета, стобитов
        cmd_portSetting = {'str': 'setuartcfg: {0} {1} {2} {3}\r\n'.format(comNum, baud, parity, stopBitsDict[stopbits]),
                           'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_portSetting)

        # настройка модбаса
        modbusSelection = curWidget.modbusCombobox.GetStringSelection()
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

    def setAddress(self, event):
        eventObject = event.GetEventObject()
        addressType = eventObject.Parent.addressType
        print('addressType ', addressType)
        address = eventObject.Parent.addressTextCtl.GetAddress()
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
        print(cmd_networkSetting)

    def getAddress(self, event):
        eventObject = event.GetEventObject()
        addressType = eventObject.Parent.addressType
        print('addressType ', addressType)
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
        print(cmd_networkSetting)

    def getDate(self, event):
        cmd_getdate = {'str': 'getdate\r\n',
               'responseFormat': 'Done\r\n'}
        self.msgQueue.put(cmd_getdate)


    def setDate(self, event):
        eventObject = event.GetEventObject()
        parentWidget = eventObject.Parent
        day = parentWidget.dayTextCtl.GetLineText(0)
        month = parentWidget.monthTextCtl.GetLineText(0)
        year = parentWidget.yearTextCtl.GetLineText(0)
        cmd_setdate = {'str': 'setdate: {0} {1} {2}\r\n'.format(day, month, year),
               'responseFormat': 'Done\r\n'}
        print('write date ', cmd_setdate)
        self.msgQueue.put(cmd_setdate)

    def getTime(self, event):
        cmd_getdate = {'str': 'gettime\r\n',
               'responseFormat': 'Done\r\n'}

        self.msgQueue.put(cmd_getdate)
    def setTime(self, event):
        eventObject = event.GetEventObject()
        parentWidget = eventObject.Parent
        hour = parentWidget.hourTextCtl.GetLineText(0)
        min = parentWidget.minuteTextCtl.GetLineText(0)
        sec = parentWidget.secondTextCtl.GetLineText(0)
        cmd_setdate = {'str': 'settime: {0} {1} {2}\r\n'.format(hour, min, sec),
               'responseFormat': 'Done\r\n'}
        print('write date ', cmd_setdate)
        self.msgQueue.put(cmd_setdate)

    def updateDisplay(self, msg):
        modbusSetting_list = {"mbmaster0": u"Режим Modbus Master 0", "mbmaster1": u"Режим Modbus Master 1",
                              "mbmaster2": u"Режим Modbus Master 2", "mbslave": u"Режим Modbus slave",
                              "off": u"Выключен"}
        stopBitsDict = {'1': '1', '2': '1.5', '3': '2'}
        data = msg.data
        comNum = str(int(data[u'portNum']) + 1)
        result = data[u'result']
        result_list = data[u'result'].split()
        # print('data', data)
        # print('result answer', data[u'result'])
        if u"cfg" in result:
            if (len(result_list) == 4):
                baud = result_list[1]
                parity = result_list[2]
                stopBits = result_list[3]
                widgetGroup = getattr(self, "comWidget_" + comNum)
                widgetGroup.baudrateCombobox.SetStringSelection(baud)
                widgetGroup.parityCombobox.SetStringSelection(parity)
                widgetGroup.databytesCombobox.SetStringSelection(stopBitsDict[stopBits])
        if u"mode" in result:
            if (len(result_list) == 2):
                modbus = result_list[1]
                print(modbus)
                widgetGroup = getattr(self, "comWidget_" + comNum)
                widgetGroup.modbusCombobox.SetStringSelection(modbusSetting_list[modbus])
        if u'adr' in result:
            if (len(result_list) == 2):
                widgetGroup = getattr(self, "comWidget_" + comNum)
                modbusAddress = result_list[1]
                widgetGroup.modbusAddress.Clear()
                widgetGroup.modbusAddress.write(modbusAddress)
        if u'ip' in result:
            if (len(result_list) == 5):
                widgetGroup = getattr(self, "ipWidget")
                resAddres = result[4:].replace(' ', '.')
                resAddres = resAddres.replace('\r\n', '')
                print('resAddres', str(resAddres))
                widgetGroup.addressTextCtl.Clear()
                widgetGroup.addressTextCtl.SetValue(resAddres)
        if u'mask' in result:
            if (len(result_list) == 5):
                print('result_list', result_list)
                widgetGroup = getattr(self, "maskWidget")
                resAddres = result[6:].replace(' ', '.')
                resAddres = resAddres.replace('\r\n', '')
                print('mask ', resAddres )
                widgetGroup.addressTextCtl.Clear()
                widgetGroup.addressTextCtl.SetValue(resAddres)
        if u'gateway' in result:
            if (len(result_list) == 5):
                widgetGroup = getattr(self, "gatewayWidget")
                resAddres = result[9:].replace(' ', '.')
                resAddres = resAddres.replace('\r\n', '')
                print('gateway ', resAddres )
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
                print(result)
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

    def OnClose(self, event):
        self.serialTread.stopThread()
        # self.modulObj.serial.close()
        print('Stoped')
        self.Destroy()

if __name__ == '__main__':
    app = wx.App(False)
    top = Configurator_MK201()
    top.Show()
    app.MainLoop()