#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Вкладка DI для классов модулйей проткола CANOpen
@Author Yanikeev-AS
"""
__author__ = 'Yanikeev-as'


from mk200modules.MK200CANOpen.CANOpenIOEditors.CANOpenIOEditor import *
NUM_OF_ON_BOARD_DI = 32

# CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
CodeFile = CodeFileTreeNode.CodeFile

DIV_BEGIN = "/" + ("*"*82) + "\n\t\t\t"
DIV_END = "\n" + ("*"*82) + "/\n"
DESCRIPTION = "On board digital input"

class CANOpenDiChannelEditor(wx.Panel):

    def __init__(self, parent, channel):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        chkBxId = wx.NewId()
        self.isOnChkbx = wx.CheckBox(self, label="Enable channel #{}".format(channel), id=chkBxId)
        main_sizer.Add(self.isOnChkbx, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(main_sizer)

class CANOpenDiEditor(CANOpenIOEditor):
    def __init__(self, parent, window, controler, channelNum=32):
        CANOpenIOEditor.__init__ (self, parent, window, controler)
        gridBoeder = 5
        self.channelNum = channelNum
        """ Настройки по умолчанию для частоных/счетных входов """
        self.DefaultConfig = []
        for i in range(0, channelNum):
            self.DefaultConfig.append({
                "Name" : "MK200_DI_{}".format(i),
                "Address" : "",
                "Len" : "",
                "Type" : u"BOOL",
                "Initial": "",
                "Description": DESCRIPTION,
                "OnChange":"",
                "Options":"On"})

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label="Discrete input configuration")
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title.SetFont(font)
        main_sizer.Add(self.title, flag=wx.ALIGN_CENTER_VERTICAL)

        secondary_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.inputs = []
        cloumn_range = 12
        colum_sizer_1 = wx.BoxSizer(wx.VERTICAL)
        for i in range(0, cloumn_range):
            channel = CANOpenDiChannelEditor(self, i)
            wx.EVT_CHECKBOX(self, channel.isOnChkbx.GetId(), self.OnChange)
            self.inputs.append(channel)
            colum_sizer_1.Add(channel, 1, wx.ALIGN_CENTER_VERTICAL, gridBoeder)
        secondary_sizer.Add(colum_sizer_1, flag=wx.ALIGN_CENTER_VERTICAL)

        colum_sizer_2 = wx.BoxSizer(wx.VERTICAL)
        for i in range(cloumn_range, cloumn_range * 2):
            channel = CANOpenDiChannelEditor(self, i)
            wx.EVT_CHECKBOX(self, channel.isOnChkbx.GetId(), self.OnChange)
            self.inputs.append(channel)
            colum_sizer_2.Add(channel, 1, wx.ALIGN_CENTER_VERTICAL, gridBoeder)
        secondary_sizer.Add(colum_sizer_2, flag=wx.ALIGN_CENTER_VERTICAL)

        colum_sizer_3 = wx.BoxSizer(wx.VERTICAL)
        for i in range(cloumn_range * 2, channelNum):
            channel = CANOpenDiChannelEditor(self, i)
            wx.EVT_CHECKBOX(self, channel.isOnChkbx.GetId(), self.OnChange)
            self.inputs.append(channel)
            colum_sizer_3.Add(channel, 1, wx.ALIGN_CENTER_VERTICAL, gridBoeder)
        secondary_sizer.Add(colum_sizer_3, flag=wx.ALIGN_TOP)

        main_sizer.Add(secondary_sizer, flag=wx.ALIGN_CENTER_VERTICAL)
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
        for channel, chConfig  in zip(self.inputs, config):
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
        if len(config) < self.channelNum:
            config = self.DefaultConfig[:]
            self.RefreshModel()
        for chPanel, chCfg in zip(self.inputs, config):
            if chCfg["Options"] == "On":
                chPanel.isOnChkbx.SetValue(True)
            else:
                chPanel.isOnChkbx.SetValue(False)

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