#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Панель настроек порта modbusTCP
@Author Vasilij
"""
import wx

DESCRIPTION="TCP parameters"


class TextAndLabel (wx.Panel):

    def __init__(self, parent, labeltext):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.LabelTxt = wx.StaticText(self, label=labeltext)
        newId = wx.NewId()
        self.TextCtrl = wx.TextCtrl(self, id=newId)


class ModbusTCPEditor (wx.Panel):

    def __init__(self, parent, window, controler):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.ParentWindow = window
        self.Controler = controler
        self.DefaultConfig = {
            "Name": DESCRIPTION,
            "Type": u"WORD",
            "Description": DESCRIPTION,
            "Options": "Enabled",
            "Ipaddr": "10.155.26.140",
            "Submask": "255.255.255.0",
            "Gateway": "10.155.26.1",
            "Dns": "10.155.100.7",
        }
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.title = wx.StaticText(self, label="TCP port")
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title.SetFont(font)
        main_sizer.Add(self.title, flag=wx.ALIGN_CENTER_VERTICAL)

        controlSizer = wx.GridSizer(5, 2)
        main_sizer.Add(controlSizer, flag=wx.ALIGN_CENTER_VERTICAL)

        self.EnableChkBx = wx.CheckBox(self, label="Enable", id=wx.NewId())
        wx.EVT_CHECKBOX(self, self.EnableChkBx.GetId(), self.OnChange)
        controlSizer.Add(self.EnableChkBx, flag=wx.ALIGN_CENTER_VERTICAL)
        emptytxt = wx.StaticText(self, label="")
        controlSizer.Add(emptytxt, flag=wx.ALIGN_CENTER_VERTICAL)

        self.IpAddr = self.AddTextAndLabel("IP address", controlSizer)
        self.Subnetmask = self.AddTextAndLabel("Subnet mask", controlSizer)
        self.Gateway = self.AddTextAndLabel("Gateway", controlSizer)
        self.Dns = self.AddTextAndLabel("DNS", controlSizer)

        self.SetSizer(main_sizer)
        self.firstCall = 0

    def AddTextAndLabel(self, labelText, sizer):
        staticText = wx.StaticText(self, label=labelText)
        sizer.Add(staticText)
        newId = wx.NewId()
        textCtrl = wx.TextCtrl(self, id=newId)
        wx.EVT_TEXT(self, textCtrl.GetId(), self.OnChange)
        sizer.Add(textCtrl)
        return {"Label": staticText, "TextCtrl": textCtrl}

    def SetTextCtrl(self, dest, value):
        dest["TextCtrl"].Clear()
        dest["TextCtrl"].AppendText(value)

    def OnChange(self, event):
        valuesOnFrame = self.GetData()
        valuesInController = [i for i in self.Controler.GetVariables()
                              if i["Description"] == DESCRIPTION]
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
        data = self.DefaultConfig.copy()
        if self.EnableChkBx.GetValue():
            data["Options"] = "Enabled"
        else:
            data["Options"] = "Disabled"
        data["Ipaddr"] = self.IpAddr["TextCtrl"].GetValue()
        data["Submask"] = self.Subnetmask["TextCtrl"].GetValue()
        data["Gateway"] = self.Gateway["TextCtrl"].GetValue()
        data["Dns"] = self.Dns["TextCtrl"].GetValue()
        return [data]

    def SetData(self, value):
        """
        Выводит конфигурацию на GUI
        :param aiParams: спиоск с конфигурацией по каждому каналу
        :return: none
        """
        """ Если устанавливаемых параметров меньше чем надо, то уставливаются значения
         по умолчанию """
        if len(value) == 0:
            data = self.DefaultConfig.copy()
        else:
            data = value[0]
        if data["Options"] == "Enable":
            self.EnableChkBx.SetValue(True)
        else:
            self.EnableChkBx.SetValue(False)
        self.SetTextCtrl(self.IpAddr, data["Ipaddr"])
        self.SetTextCtrl(self.Subnetmask, data["Submask"])
        self.SetTextCtrl(self.Gateway, data["Gateway"])
        self.SetTextCtrl(self.Dns, data["Dns"])

    def RefreshModel(self):
        controllerVariables = self.Controler.GetVariables()
        controllerVariables = [i for i in controllerVariables if i["Description"] != DESCRIPTION]
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
        varForTable = [i for i in varForTable if i["Description"] == DESCRIPTION]
        self.SetData(varForTable)
        self.Layout()

    def GetVariableTypeFunction(self, base_type):
        def VariableTypeFunction(event):
            self.RefreshModel()
            self.RefreshView()
            event.Skip()
        return VariableTypeFunction

