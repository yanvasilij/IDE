# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'
import wx
import wx.lib.masked
import copy
import os.path
import sys
import time
from threading import Thread
from wx.lib.pubsub import pub
from wx.lib.masked.ipaddrctrl import IpAddrCtrl
from wx.lib.masked import TimeCtrl
import wx.lib.intctrl

# импорт моих модулей
from serialWork import SerialPort
from mk201_proto import mk201_proto

VERISON = '0.0.1'

# wx ID
ID_MAINWXFRAME = wx.NewId()
ID_MAINWXDIALOGFRAME = wx.NewId()


class addLabelWidget(wx.Panel):
    def __init__(self, parent, labelList = ['Empty_list'], *args, **kwds):
        wx.Panel.__init__(self, parent, *args, **kwds)
        gridBoreder = 10
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        for el in labelList:
            mainSizer.Add(wx.StaticText(self, label = el['label'], size = el['size']), 0.5, wx.ALL, gridBoreder)
        self.SetSizer(mainSizer)
        self.Layout()

class initComWidget(wx.Panel):
    def __init__(self, parent, comNum, *args, **kwds):
        wx.Panel.__init__(self, parent, *args, **kwds)

        self.comNum = comNum
        gridBoreder = 10
        parity_list = ["none", "even","odd"]
        baudrate_list = "300 600 900 1200 2400 4800 9600 14400 19200 38400 56000 57600 115200 128000 256000".split()
        modbusSetting_list = [u"Режим Modbus Master 0", u"Режим Modbus Master 1", u"Режим Modbus Master 2",
                              u"Режим Modbus slave", u"Выключен"]
        stopbytes_list = ["1", "1.5", "2"]

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.portLabel = wx.StaticText(self, label = u"COM" + str(comNum))
        self.parityCombobox = wx.ComboBox(self, choices = parity_list)
        self.baudrateCombobox = wx.ComboBox(self, choices = baudrate_list)
        self.databytesCombobox = wx.ComboBox(self, choices = stopbytes_list)
        self.modbusCombobox = wx.ComboBox(self, choices = modbusSetting_list)
        self.modbusAddress = wx.lib.intctrl.IntCtrl(self, min = 0, max = 255, limited = True)
        self.writePortSettingBtn = wx.Button(self, wx.ID_ANY, u"Записать", name = 'writeBtnCOM1')

        self.parityCombobox.SetSelection(1)
        self.baudrateCombobox.SetSelection(12)
        self.databytesCombobox.SetSelection(0)
        self.modbusCombobox.SetSelection(0)

        mainSizer.Add(self.portLabel, 0.5, wx.ALL, gridBoreder)
        mainSizer.Add(self.parityCombobox, 0.5, wx.ALL, gridBoreder)
        mainSizer.Add(self.baudrateCombobox, 0.5, wx.ALL, gridBoreder)
        mainSizer.Add(self.databytesCombobox, 0.5, wx.ALL, gridBoreder)
        mainSizer.Add(self.modbusCombobox, 1, wx.ALL, gridBoreder)
        mainSizer.Add(self.modbusAddress, 0.3, wx.ALL, gridBoreder)
        mainSizer.Add(self.writePortSettingBtn, 0.5, wx.ALL, gridBoreder)

        self.SetSizer(mainSizer)
        self.Layout()


class initNetworkWidget(wx.Panel):
    def __init__(self, parent, strName, defValue = '100.100.100.100',*args, **kwds):
        self.addressType = strName
        wx.Panel.__init__(self, parent, *args, **kwds)
        gridBoreder = 10
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.ipLabel = wx.StaticText(self, label =strName)
        self.addressTextCtl = IpAddrCtrl(self)
        self.addressTextCtl.SetValue(defValue)
        self.writeAddressBtn = wx.Button(self, label = u"Записать")

        # print 'ipLabel ', self.ipLabel.GetSize()
        # print 'addressTextCtl ', self.addressTextCtl.GetSize()
        # print 'writeAddressBtn ', self.writeAddressBtn.GetSize()
        # print 'readAddressBtn ', self.readAddressBtn.GetSize()

        mainSizer.Add(self.ipLabel, 1, wx.ALL, gridBoreder)
        mainSizer.Add(self.addressTextCtl, 1, wx.ALL, gridBoreder)
        mainSizer.Add(self.writeAddressBtn, 1, wx.ALL, gridBoreder)

        self.SetSizer(mainSizer)
        self.Layout()

class modbusWidget(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self,  *args, **kwds)
        gridBoreder = 10
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.modbusSettingsLabel = wx.StaticText(self, label = u"Порт")
        self.modbusSettingsTextCtl = wx.lib.intctrl.IntCtrl(self, pos = (5,65), size = (50, 20),
                                                            min = 0, max = 65535, limited = True)
        self.modbusSettingsWriteBtn = wx.Button(self, label = u"Записать")

        mainSizer.Add(self.modbusSettingsLabel, 1, wx.ALL, gridBoreder)
        mainSizer.Add(self.modbusSettingsTextCtl, 1, wx.ALL, gridBoreder)
        mainSizer.Add(self.modbusSettingsWriteBtn, 1, wx.ALL, gridBoreder)

        self.SetSizer(mainSizer)
        self.Layout()

class dateWidget(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self,  *args, **kwds)
        gridBoreder = 10
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.modbusSettingsLabel = wx.StaticText(self, label = u"Дата")
        self.dayTextCtl = wx.lib.intctrl.IntCtrl(self, size = (21,21) ,min = 0, max = 31, limited = True)
        self.monthTextCtl = wx.lib.intctrl.IntCtrl(self, size = (21,21), min = 0, max = 12, limited = True)
        self.yearTextCtl = wx.lib.intctrl.IntCtrl(self, size = (21,21), min = 0, max = 64, limited = True)
        self.dateWriteBtn = wx.Button(self, label = u"Записать")

        mainSizer.Add(self.modbusSettingsLabel, 1, wx.ALL, gridBoreder)
        mainSizer.Add(self.dayTextCtl, 0.1, wx.ALL, gridBoreder)
        mainSizer.Add(self.monthTextCtl, 0.1, wx.ALL, gridBoreder)
        mainSizer.Add(self.yearTextCtl, 0.1, wx.ALL, gridBoreder)
        mainSizer.Add(self.dateWriteBtn, 0.7, wx.ALL, gridBoreder)


        self.SetSizer(mainSizer)
        self.Layout()

class timeWidget(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self,  *args, **kwds)
        gridBoreder = 10
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.modbusSettingsLabel = wx.StaticText(self, label = u"Время")
        self.hourTextCtl = wx.lib.intctrl.IntCtrl(self, size = (21,21), min = 0, max = 23, limited = True)
        self.minuteTextCtl = wx.lib.intctrl.IntCtrl(self, size = (21,21), min = 0, max = 59, limited = True)
        self.secondTextCtl = wx.lib.intctrl.IntCtrl(self, size = (21,21) ,min = 0, max = 59, limited = True)

        self.timeWriteBtn = wx.Button(self, label = u"Записать")

        mainSizer.Add(self.modbusSettingsLabel, 1, wx.ALL, gridBoreder)
        mainSizer.Add(self.hourTextCtl, 0.1, wx.ALL, gridBoreder)
        mainSizer.Add(self.minuteTextCtl, 0.1, wx.ALL, gridBoreder)
        mainSizer.Add(self.secondTextCtl, 0.1, wx.ALL, gridBoreder)
        mainSizer.Add(self.timeWriteBtn, 0.7, wx.ALL, gridBoreder)


        self.SetSizer(mainSizer)
        self.Layout()

class connectWidget(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self,  *args, **kwds)
        gridBoreder = 10
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.portsListCombobox = wx.ComboBox(self)
        self.connectnBtn = wx.Button(self, label = u"Подключить")

        mainSizer.Add(self.portsListCombobox, 1, wx.ALL, gridBoreder)
        mainSizer.Add(self.connectnBtn, 0.3, wx.ALL, gridBoreder)

        self.SetSizer(mainSizer)
        self.Layout()


class ConfiguratorGUI(wx.Frame, wx.Dialog):
    heigthFrame = 690
    widthFrame = 540
    def __init__(self, parent = None, modulObject = None, hexFilePath = None):
        self.connectStatus = None # отображет сообщение от действий объекта SerialWork
        self.connection = False # отображает состояние соединения
        if parent is None:
            self.modulObj = mk201_proto()
            self.comPorts = self.modulObj.getPorts()[1]
            self.initWxFrame()
        else:
            self.parent = parent
            self.modulObj = modulObject
            self.hexFilePath = hexFilePath
            self.comPorts = self.modulObj.getPorts()[1]
            self.initWxDialogFrame()
        self.initWidgets()

    def initWxFrame(self):
        wx.Frame.__init__(self, None, id = ID_MAINWXFRAME, title = "MKSetup " + VERISON, name = 'mainWxFrame',
                          pos=(150,150), size = (self.heigthFrame, self.widthFrame))
        self.frameParent = wx.Panel(self)

        self.mainsizer = wx.BoxSizer(wx.VERTICAL)

        self.connectWidget = connectWidget(self)
        connectSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Подключение'))

        connectSettingsBox.Add(self.connectWidget, 1, wx.EXPAND)
        self.mainsizer.Add(connectSettingsBox)


    def initWxDialogFrame(self):
        wx.Dialog.__init__(self, parent = self.parent, id = ID_MAINWXDIALOGFRAME, title = "MKSetup " + VERISON, name = 'mainWxFrame',
                          pos=(150,150), size = (self.heigthFrame, self.widthFrame))
        self.frameParent = self
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)


    def initWidgets(self):
        # self.panel = wx.Panel(self)

        '''Настройка TCP'''
        netwrokSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Настройка TCP'),
                                                    wx.VERTICAL)
        label_list = [{'label' : u'', 'size': (50, 13)},
                      {'label' : u'Адрес', 'size': (113, 22)},
                       {'label' : u'', 'size': (75, 23)},
                        {'label' : u'', 'size': (75, 23)}
                      ]
        # label_widget = addLabelWidget(self, label_list)
        # netwrokSettingsBox.Add(label_widget, 1, wx.EXPAND)
        self.ipWidget = initNetworkWidget(self, u'IP-адресс')
        netwrokSettingsBox.Add(self.ipWidget, 1, wx.EXPAND)
        self.gatewayWidget = initNetworkWidget(self, u'Шлюз')
        netwrokSettingsBox.Add(self.gatewayWidget, 1, wx.EXPAND)
        self.maskWidget = initNetworkWidget(self, u'Маска')
        netwrokSettingsBox.Add(self.maskWidget, 1, wx.EXPAND)

        self.mainsizer.Add(netwrokSettingsBox)

        '''Настройка COM-портов'''
        portSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Настройка COM-портов'),
                                                    wx.VERTICAL)
        self.comWidget_1 = initComWidget(self, comNum = 1)
        portSettingsBox.Add(self.comWidget_1, 1, wx.EXPAND)
        self.comWidget_2 = initComWidget(self, comNum = 2)
        portSettingsBox.Add(self.comWidget_2, 1, wx.EXPAND)
        self.comWidget_3 = initComWidget(self, comNum = 3)
        portSettingsBox.Add(self.comWidget_3, 1, wx.EXPAND)

        self.mainsizer.Add(portSettingsBox)

        '''Настройка времени и даты'''
        dateSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Настройка времени и даты'),
                                                    wx.VERTICAL)
        self.dateWidget = dateWidget(self)
        dateSettingsBox.Add(self.dateWidget, 1, wx.EXPAND)
        self.timeSettigsWidget = timeWidget(self)
        dateSettingsBox.Add(self.timeSettigsWidget, 1, wx.EXPAND)

        self.mainsizer.Add(dateSettingsBox)

        '''Вывод времени '''
        curTimeSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Текущее время'),
                                                    wx.VERTICAL)
        # self.curTimeWidget = timeWidget(self)
        self.curTimeWidget = timeWidget(self)
        curTimeSettingsBox.Add(self.curTimeWidget, 1, wx.EXPAND)

        self.mainsizer.Add(curTimeSettingsBox)

        '''Настройка MODBUS'''
        modbusSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Настройка Modbus'),
                                                    wx.VERTICAL)
        self.modbusWidget = modbusWidget(self)
        modbusSettingsBox.Add(self.modbusWidget, 1, wx.EXPAND)

        self.mainsizer.Add(modbusSettingsBox)

        self.SetSizer(self.mainsizer)
        self.mainsizer.Fit(self)
        self.Layout()
        # self.statusBar = wx.StatusBar(self, id = wx.ID_ANY)

if __name__ == '__main__':
    app = wx.App(False)
    top = ConfiguratorGUI()
    top.Show()
    app.MainLoop()