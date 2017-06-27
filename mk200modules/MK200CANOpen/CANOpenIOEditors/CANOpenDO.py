#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Панель для редактирования свойств дискретных входов
@Author Vasilij
"""

from mk200modules.MK200CANOpen.CANOpenIOEditors.CANOpenIOEditor import *

NUM_OF_ON_BOARD_DO = 8
DESCRIPTION = "On board digital outputs"

class CANOpenDoChannelEditor(wx.Panel):

    def __init__(self, parent, channel):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        chkBxId = wx.NewId()
        self.isOnChkbx = wx.CheckBox(self, label="Enable channel #{}".format(channel), id=chkBxId)
        self.isOnChkbx.SetValue(True)
        main_sizer.Add(self.isOnChkbx, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(main_sizer)

class CANOpenDoEditor(CANOpenIOEditor):
    def __init__(self, parent, window, controler):
        CANOpenIOEditor.__init__ (self, parent, window, controler)
        """ Настройки по умолчанию для частоных/счетных входов """
        self.DefaultConfig = []
        self.cobeID = self.Controler.GetFullIEC_Channel()
        self.cobeID = self.cobeID[:-2].replace('.', '_')
        for i in range(0, NUM_OF_ON_BOARD_DO):
            self.DefaultConfig.append({
                "Name" : "MK200_DO_{0}_{1}".format(self.cobeID, i),
                "Address" : "",
                "Len" : "",
                "Type" : u"BOOL",
                "Initial": "",
                "Description": DESCRIPTION,
                "OnChange":"",
                "Options":"On"})

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label="Discrete output configuration")
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title.SetFont(font)
        main_sizer.Add(self.title, flag=wx.ALIGN_CENTER_VERTICAL)

        self.inputs = []
        for i in range(0, NUM_OF_ON_BOARD_DO):
            channel = CANOpenDoChannelEditor(self, i)
            wx.EVT_CHECKBOX(self, channel.isOnChkbx.GetId(), self.OnChange)
            self.inputs.append(channel)
            main_sizer.Add(channel, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(main_sizer)

    def OnChange(self, event):
        valuesOnFrame = self.GetData()
        valuesInController = [i for i in self.Controler.GetVariables()
                              if i["Description"] == DESCRIPTION]
        if valuesOnFrame != valuesInController:
            self.RefreshModel()
        event.Skip()

    def GetData(self):
        """
        Считывает с GUI настроенные пользователем параметры и возвращает их 
        в виде списка словарей
        """
        config = self.DefaultConfig[:]
        for channel, chConfig in zip(self.inputs, config):
            if channel.isOnChkbx.GetValue():
                chConfig["Options"] = "On"
            else:
                chConfig["Options"] = "Off"
        return config

    def SetData(self, config):
        """
        Выводит конфигурацию на GUI
        :param config: спиоск с конфигурацией по каждому каналу
        :return: none
        """
        """ Если устанавливаемых параметров меньше чем надо, то уставливаются значения
         по умолчанию """
        if len(config) < NUM_OF_ON_BOARD_DO:
            config = self.DefaultConfig[:]
            self.RefreshModel()
        for chPanel, chCfg in zip(self.inputs, config):
            if chCfg["Options"] == "On":
                chPanel.isOnChkbx.SetValue (True)
            else:
                chPanel.isOnChkbx.SetValue (False)

    def RefreshModel(self):
        controllerVariables = self.Controler.GetVariables()
        controllerVariables = [i for i in controllerVariables if i["Description"] != DESCRIPTION]
        controllerVariables += self.GetData()
        self.Controler.SetVariables(controllerVariables)
        self.RefreshBuffer()

    def RefreshView(self):
        varForTable = self.Controler.GetVariables()
        varForTable = [i for i in varForTable if i["Description"] == DESCRIPTION]
        self.SetData(varForTable)
        self.Layout()

