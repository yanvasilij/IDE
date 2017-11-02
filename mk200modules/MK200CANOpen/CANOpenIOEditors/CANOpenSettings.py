#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Вкладка для настройки подключения CAN'a для классов модулйей проткола CANOpen
@Author Yanikeev-AS
"""

__author__ = 'Yanikeev-as'

from mk200modules.MK200CANOpen.CANOpenIOEditors.CANOpenIOEditor import *


# CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
CodeFile = CodeFileTreeNode.CodeFile

DIV_BEGIN = "/" + ("*"*82) + "\n\t\t\t"
DIV_END = "\n" + ("*"*82) + "/\n"

TEAXLABEL_SIZE = (120, 21)
SETTINGSWIDGET_SIZE = (100, 21)
BAUDRATE_LIST = ('1000', '500', '250', '125', '100','50', '20')
DESCRIPTION = ["HeartbeatTime", "Baudrate", "DataUpdateTime"]

# class CANOpenSettingsChannelEditor(wx.Panel):
#
#     def __init__(self, parent, window, controler):
#         wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
#
#         self.ParentWindow = window
#         self.parent = parent
#         self.Controler = controler
#
#         main_sizer = wx.BoxSizer(wx.HORIZONTAL)
#         hardBitTimelbl = wx.StaticText(self, label='Hardbit Time', size=(1000, 21))
#         main_sizer.Add(hardBitTimelbl, wx.ALIGN_CENTER_VERTICAL)
#         self.hardBitTime = wx.lib.intctrl.IntCtrl(self, value=1, min=1, max=127, limited=True)
#         main_sizer.Add(self.hardBitTime)
#
#         # self.modeCmbbx = wx.ComboBox(self, id=newId, value="SelectRange", choices=AI_MODES)
#         # main_sizer.Add(self.channelTxt, flag=wx.ALIGN_CENTER_VERTICAL)
#         # main_sizer.Add(self.modeCmbbx, flag=wx.ALIGN_CENTER_VERTICAL)
#
#         self.SetSizer(main_sizer)

class CANOpenSettingsEditor(wx.Panel):
    def __init__(self, parent, window, controler, chanelNum):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)

        self.ParentWindow = window
        self.Controler = controler
        self.chanelNum = chanelNum

        self.DefaultConfig = []
        self.cobeID = self.Controler.GetFullIEC_Channel()
        self.cobeID = self.cobeID[:-2]

        for i in range(3):
            self.DefaultConfig.append({
                "Name" : "",
                "Address" : "1",
                "Len" : "",
                "Type" : u"INT",
                "Initial": "",
                "Description": DESCRIPTION[i],
                "OnChange":"",
                "Options":"",
                "Value":"500"})

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        ''' виджеты для Heartbeat Time'''
        self.heartbeatTimeSizer = wx.BoxSizer(wx.HORIZONTAL)
        heartbeatTimeLbl = wx.StaticText(self, label=_('Heartbeat Time (ms)'), size=TEAXLABEL_SIZE)
        self.heartbeatTimeSizer.Add(heartbeatTimeLbl)
        self.heartbeatTime = wx.lib.intctrl.IntCtrl(self, value=500, min=0, max=5000, limited=True, size=SETTINGSWIDGET_SIZE)
        wx.EVT_TEXT(self, self.heartbeatTime.GetId(), self.OnChange)
        self.heartbeatTimeSizer.Add(self.heartbeatTime)
        mainSizer.Add(self.heartbeatTimeSizer)

        ''' виджеты для скорости'''
        self.baudRateSizer = wx.BoxSizer(wx.HORIZONTAL)
        baudRateLbl = wx.StaticText(self, label=_('Baud (b/s)'), size=TEAXLABEL_SIZE)
        self.baudRateSizer.Add(baudRateLbl)
        self.baudRate = wx.ComboBox(self, choices = BAUDRATE_LIST, size=SETTINGSWIDGET_SIZE)
        wx.EVT_TEXT(self, self.baudRate.GetId(), self.OnChange)
        self.baudRate.SetStringSelection(BAUDRATE_LIST[0])
        self.baudRateSizer.Add(self.baudRate)
        mainSizer.Add(self.baudRateSizer)


        ''' виджеты для Data update time'''
        self.dataUpdateSizer = wx.BoxSizer(wx.HORIZONTAL)
        dataUpdateLbl = wx.StaticText(self, label=_('Data update time (ms)'), size=TEAXLABEL_SIZE)
        self.dataUpdateSizer.Add(dataUpdateLbl)
        self.dataUpdate = wx.lib.intctrl.IntCtrl(self, value=500, min=0, max=10000, limited=True, size=SETTINGSWIDGET_SIZE)
        wx.EVT_TEXT(self, self.dataUpdate.GetId(), self.OnChange)
        self.dataUpdateSizer.Add(self.dataUpdate)
        mainSizer.Add(self.dataUpdateSizer)

        self.SetSizer(mainSizer)


    def OnChange(self, event):
        valuesOnFrame = self.GetData()
        valuesInController = [i for i in self.Controler.GetVariables()
                              if i["Description"] in DESCRIPTION]
        if valuesOnFrame != valuesInController:
            self.RefreshModel()
        event.Skip()

    def OnShow(self, event):
        if self.firstCall:
            self.RefreshView()
            self.firstCall = 0
        event.Skip()

    def GetData(self):
        """
        Считывает с GUI настроенные пользователем параметры и возвращает их в виде списка
        словарей
        """
        CANParams = self.DefaultConfig[:]
        # CANParams = []
        # CANParams.append(self.DefaultConfig[:])
        heartbeatValue = str(self.heartbeatTime.GetValue())
        CANParams[0]["Name"] = "HeartbeatTime_" + self.cobeID
        CANParams[0]["Value"] = heartbeatValue

        baudValue = self.baudRate.GetStringSelection()
        CANParams[1]["Name"] = "Baudrate_" + self.cobeID
        CANParams[1]["Value"] = baudValue

        dataUpdateValue = str(self.dataUpdate.GetValue())
        CANParams[2]["Name"] = "DataUpdateTime_" + self.cobeID
        CANParams[2]["Value"] = dataUpdateValue

        return CANParams

    def SetData(self, settingParams):
        """
        Выводит конфигурацию на GUI
        :param aiParams: спиоск с конфигурацией по каждому каналу
        :return: none
        """
        """ Если устанавливаемых параметров меньше чем надо, то уставливаются значения
         по умолчанию """
        paramNum = 2

        if len(settingParams) == 0:
            settingParams = self.DefaultConfig[:]
            self.RefreshModel()
        self.RefreshModel()
        self.heartbeatTime.Clear()
        self.heartbeatTime.write((settingParams[0]["Value"]))
        self.baudRate.SetStringSelection(settingParams[1]["Value"])
        self.dataUpdate.Clear()
        self.dataUpdate.write((settingParams[2]["Value"]))

    def RefreshModel(self):
        controllerVariables = self.Controler.GetVariables()
        controllerVariables = [i for i in controllerVariables if not(i["Description"] in DESCRIPTION)]
        controllerVariables += self.GetData()
        self.Controler.SetVariables(controllerVariables)
        self.RefreshBuffer()

    def RefreshBuffer(self):
        self.Controler.BufferCodeFile()
        self.ParentWindow.RefreshTitle()
        self.ParentWindow.RefreshFileMenu()
        self.ParentWindow.RefreshEditMenu()
        self.ParentWindow.RefreshPageTitles()

    def RefreshView(self):
        varForTable = self.Controler.GetVariables()
        varForTable = [i for i in varForTable if i["Description"] in DESCRIPTION]
        self.SetData(varForTable)
        self.Layout()

    def GetVariableTypeFunction(self, base_type):
        def VariableTypeFunction(event):
            self.RefreshModel()
            self.RefreshView()
            event.Skip()
        return VariableTypeFunction

