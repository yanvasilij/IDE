#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Панель для редактирования свойств частотных входов
@Author Vasilij
"""
import wx
from MK201IOEditor import MK201IOEditor

FREQIN_MODES = ("Off", "Counter", "Frequency")
NUM_OF_FRQ_IN = 4
DESCRIPTION = "On board freq in"

class MK201FreqInChannelEditor(wx.Panel):

    def __init__(self, parent, channel):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.channelTxt = wx.StaticText(self, label="Input #{}".format(channel))
        newId = wx.NewId()
        self.modeCmbbx = wx.ComboBox(self, id=newId, value="Select mode", choices=FREQIN_MODES)
        main_sizer.Add(self.channelTxt, flag=wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(self.modeCmbbx, flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(main_sizer)

class MK201FreqInEditor(MK201IOEditor):

    def __init__(self, parent, window, controler):
        MK201IOEditor.__init__ (self, parent, window, controler)

        """ Настройки по умолчанию для частоных/счетных входов """
        self.DefaultConfig = []
        for i in range(0, NUM_OF_FRQ_IN):
            self.DefaultConfig.append({
                "Name" : "OnBoardFrqIn{}".format(i),
                "Address" : "",
                "Len" : "",
                "Type" : u"REAL",
                "Initial": "",
                "Description": DESCRIPTION,
                "OnChange":"",
                "Options":"Couter"})

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label="Frequency input configuration")
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title.SetFont(font)
        main_sizer.Add(self.title, flag=wx.ALIGN_CENTER_VERTICAL)

        self.inputs = []
        for i in range(0,4):
            channel = MK201FreqInChannelEditor(self, i)
            wx.EVT_COMBOBOX(self, channel.modeCmbbx.GetId(), self.OnChange)
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
        for i in range (0, NUM_OF_FRQ_IN):
            channelState = self.inputs[i].modeCmbbx.GetStringSelection()
            if channelState in FREQIN_MODES:
                config[i]["Options"] = channelState
            else:
                config[i]["Options"] = "Off"
        return config

    def SetData(self, config):
        """
        Выводит конфигурацию на GUI
        :param config: спиоск с конфигурацией по каждому каналу
        :return: none
        """
        """ Если устанавливаемых параметров меньше чем надо, то уставливаются значения
         по умолчанию """
        if len(config) < NUM_OF_FRQ_IN:
            config = self.DefaultConfig[:]
            self.RefreshModel()
        for channelConfig, params in zip(self.inputs, config):
            channelConfig.modeCmbbx.SetStringSelection(params["Options"])

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


