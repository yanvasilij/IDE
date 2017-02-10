#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Панель настройки параметров порта
@Author Vasilij
"""
import copy
import wx
from plcopen.structures import TestIdentifier, IEC_KEYWORDS, DefaultType
from util.BitmapLibrary import GetBitmap
from controls.VariablePanel import VARIABLE_NAME_SUFFIX_MODEL

DESCRIPTION = "Port configuration"
CONFIG_LEN = 5
PORTS = ("COM1", "COM2", "COM3")
DATA_BITS = ("8", "9")
PARITY = ("none", "even", "odd")
STOP_BITS = ("1", "2")
BAUDRATES = ("115200", "57600", "56000", "38400", "28800", "19200", "14400", "9600", "4800", "2400")
DEFAULT_CONFIG = {"COM PORT": "COM1", "BAUD": "115200", "DATA BITS": "8", "PARITY": "none", "STOPBITS": "1"}

HEIGHT = 20

class ComboBoxWithLabel(wx.Panel):
    def __init__(self, parent, labelText, cmbBxchoices):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lable = wx.StaticText(self, label=labelText, size=wx.Size(100, HEIGHT))
        newId = wx.NewId()
        self.cmbbox = wx.ComboBox(self, id=newId, value="SelectRange",
                choices=cmbBxchoices, size=wx.Size(100, HEIGHT))
        main_sizer.Add(self.lable, flag=wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(self.cmbbox, flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(main_sizer)

class MBPortConfigPanel(wx.Panel):

    def __init__ (self, parent, window, controler):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.ParentWindow = window
        self.Controler = controler
        self.Bind(wx.EVT_SHOW, self.OnShow)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.DefaultConfig = []
        self.DefaultConfig.append ({
                "Name" : "Port selection",
                "Address" : "",
                "Len" : "",
                "Device ID" : "",
                "Data type" : u"WORD",
                "Transfer method" : "",
                "Period" : "",
                "Description": DESCRIPTION,
                "Modbus type": DEFAULT_CONFIG["COM PORT"]})
        self.DefaultConfig.append ({
                "Name" : "Baudrate",
                "Address" : "",
                "Len" : "",
                "Device ID" : "",
                "Data type" : u"WORD",
                "Transfer method" : "",
                "Period" : "",
                "Description": DESCRIPTION,
                "Modbus type": DEFAULT_CONFIG["BAUD"]})
        self.DefaultConfig.append ({
                "Name" : "Data bits",
                "Address" : "",
                "Len" : "",
                "Device ID" : "",
                "Data type" : u"WORD",
                "Transfer method" : "",
                "Period" : "",
                "Description": DESCRIPTION,
                "Modbus type": DEFAULT_CONFIG["DATA BITS"]})
        self.DefaultConfig.append ({
                "Name" : "Parity",
                "Address" : "",
                "Len" : "",
                "Device ID" : "",
                "Data type" : u"WORD",
                "Transfer method" : "",
                "Period" : "",
                "Description": DESCRIPTION,
                "Modbus type": DEFAULT_CONFIG["PARITY"]})
        self.DefaultConfig.append ({
                "Name" : "Stopbits",
                "Address" : "",
                "Len" : "",
                "Device ID" : "",
                "Data type" : u"WORD",
                "Transfer method" : "",
                "Period" : "",
                "Description": DESCRIPTION,
                "Modbus type": DEFAULT_CONFIG["STOPBITS"]})

        self.title = wx.StaticText(self, label="Port configuration")
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title.SetFont(font)
        main_sizer.Add(self.title, flag=wx.ALIGN_CENTER_VERTICAL)

        self.AllComboboxes = []

        self.portSelectionCmbx = ComboBoxWithLabel(self, "Port selction", PORTS)
        wx.EVT_COMBOBOX(self, self.portSelectionCmbx.cmbbox.GetId(), self.OnChange)
        main_sizer.Add(self.portSelectionCmbx, flag=wx.ALIGN_CENTER_VERTICAL)
        self.AllComboboxes.append(self.portSelectionCmbx)

        self.baudSelectionCmbx = ComboBoxWithLabel(self, "Baudrate", BAUDRATES)
        wx.EVT_COMBOBOX(self, self.baudSelectionCmbx.cmbbox.GetId(), self.OnChange)
        main_sizer.Add(self.baudSelectionCmbx, flag=wx.ALIGN_CENTER_VERTICAL)
        self.AllComboboxes.append(self.baudSelectionCmbx)

        self.dataBitsSelectionCmbx = ComboBoxWithLabel(self, "Data bits", DATA_BITS)
        wx.EVT_COMBOBOX(self, self.dataBitsSelectionCmbx.cmbbox.GetId(), self.OnChange)
        main_sizer.Add(self.dataBitsSelectionCmbx, flag=wx.ALIGN_CENTER_VERTICAL)
        self.AllComboboxes.append(self.dataBitsSelectionCmbx)

        self.paritySelectionCmbx = ComboBoxWithLabel(self, "Parity", PARITY)
        wx.EVT_COMBOBOX(self, self.paritySelectionCmbx.cmbbox.GetId(), self.OnChange)
        main_sizer.Add(self.paritySelectionCmbx, flag=wx.ALIGN_CENTER_VERTICAL)
        self.AllComboboxes.append(self.paritySelectionCmbx)

        self.stopbitsSelectionCmbx = ComboBoxWithLabel(self, "Stopbits", STOP_BITS)
        wx.EVT_COMBOBOX(self, self.stopbitsSelectionCmbx.cmbbox.GetId(), self.OnChange)
        main_sizer.Add(self.stopbitsSelectionCmbx, flag=wx.ALIGN_CENTER_VERTICAL)
        self.AllComboboxes.append(self.stopbitsSelectionCmbx)

        self.SetData(self.DefaultConfig)

        self.SetSizer(main_sizer)

    def OnShow(self, event):
        try:
            if self.alreadyShown:
                event.Skip()
        except:
            self.alreadyShown = 1
            self.RefreshView()

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
        config = copy.deepcopy(self.DefaultConfig[:])
        for param, cmbx in zip(config, self.AllComboboxes):
            param["Modbus type"] = cmbx.cmbbox.GetStringSelection()
        return config

    def SetData(self, config):
        """
        Выводит конфигурацию на GUI
        """
        """ Если устанавливаемых параметров меньше чем надо, то уставливаются значения
         по умолчанию """
        if len(config) < CONFIG_LEN:
            config = copy.deepcopy (self.DefaultConfig[:])
            self.RefreshModel()
        for param, cmbx in zip(config, self.AllComboboxes):
            cmbx.cmbbox.SetStringSelection(param["Modbus type"])

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

    def RefreshBuffer(self):
        self.Controler.BufferCodeFile()
        self.ParentWindow.RefreshTitle()
        self.ParentWindow.RefreshFileMenu()
        self.ParentWindow.RefreshEditMenu()
        self.ParentWindow.RefreshPageTitles()

    def GetVariableTypeFunction(self, base_type):
        def VariableTypeFunction(event):
            self.RefreshModel()
            self.RefreshView()
            event.Skip()
        return VariableTypeFunction

