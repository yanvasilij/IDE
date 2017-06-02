#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Панель для редактирования свойств аналоговых выходов
@Author Vasilij
"""

from mk200modules.MK200CANOpen.CANOpenIOEditors.CANOpenIOEditor import *

AO_MODES = ("Off", "4-20mA", "0-20mA")
NUM_OF_AO = 2

class CANOpenAoChannelEditor(wx.Panel):

    def __init__(self, parent, channel):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.channelTxt = wx.StaticText(self, label="Output #{}".format(channel))
        newId = wx.NewId()
        self.modeCmbbx = wx.ComboBox(self, id=newId, value="SelectRange", choices=AO_MODES)
        main_sizer.Add(self.channelTxt, flag=wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(self.modeCmbbx, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(main_sizer)

class CANOpenAoutputEditor(wx.Panel):
    def __init__(self, parent, window, controler):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)

        self.ParentWindow = window
        self.Controler = controler

        self.DefaultConfig = []
        for i in range(0, NUM_OF_AO):
            self.DefaultConfig.append({
                "Name" : "MK200_AO_{}".format(i),
                "Address" : "",
                "Len" : "",
                "Type" : u"REAL",
                "Initial": "",
                "Description": "On board AO",
                "OnChange":"",
                "Options":"4-20mA"})

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label="Analog input configuration")
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title.SetFont(font)
        main_sizer.Add(self.title, flag=wx.ALIGN_CENTER_VERTICAL)

        self.outputs = []
        for i in range(0, 2):
            channel = CANOpenAoChannelEditor(self, i)
            self.outputs.append(channel)
            wx.EVT_COMBOBOX(self, channel.modeCmbbx.GetId(), self.OnChange)
            main_sizer.Add(channel, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(main_sizer)

        self.firstCall = 1
        # self.Bind(wx.EVT_SHOW, self.OnShow)

    def OnChange(self, event):
        valuesOnFrame = self.GetData()
        valuesInController = [i for i in self.Controler.GetVariables()
                              if i["Description"] == "On board AO"]
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
        aoConfig = self.DefaultConfig[:]
        for i in range (0, NUM_OF_AO):
            channelState = self.outputs[i].modeCmbbx.GetStringSelection()
            if channelState == "4-20mA":
                aoConfig[i]["Options"] = channelState
            elif channelState == "0-20mA":
                aoConfig[i]["Options"] = channelState
            else:
                aoConfig[i]["Options"] = "Off"
        return aoConfig

    def SetData(self, aoConfig):
        """
        Выводит конфигурацию на GUI
        :param aoConfig: спиоск с конфигурацией по каждому каналу
        :return: none
        """
        """ Если устанавливаемых параметров меньше чем надо, то уставливаются значения
         по умолчанию """
        if len(aoConfig) < NUM_OF_AO:
            aoConfig = self.DefaultConfig[:]
            self.RefreshModel()
        for ao, params in zip(self.outputs, aoConfig):
            ao.modeCmbbx.SetStringSelection(params["Options"])

    def RefreshModel(self):
        controllerVariables = self.Controler.GetVariables()
        controllerVariables = [i for i in controllerVariables if i["Description"] != "On board AO"]
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
        varForTable = [i for i in varForTable if i["Description"] == "On board AO"]
        self.SetData(varForTable)
        self.Layout()

    def GetVariableTypeFunction(self, base_type):
        def VariableTypeFunction(event):
            self.RefreshModel()
            self.RefreshView()
            event.Skip()
        return VariableTypeFunction

