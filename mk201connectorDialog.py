#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yanikeev-as'

import wx
import serial
import serial.tools.list_ports

GRID_BORDER = 10

class ConnectDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent=parent, id=wx.NewId(), title=u'Настройки покдлючения', size=(300, 120))
        self.ports = []
        self.choice_port = []
        self.getPorts()

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        cmbBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.portCmbBox = wx.ComboBox(self, choices=self.choice_port)
        self.portCmbBox.SetSelection(0)
        cmbBoxSizer.Add(self.portCmbBox, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(cmbBoxSizer, 1, wx.ALIGN_CENTER, GRID_BORDER)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.confirmBtn = wx.Button(self, id=wx.ID_OK, label = u"Ок")
        self.cancelBtn = wx.Button(self, id=wx.ID_CANCEL, label = u"Cancel")
        btnSizer.Add(self.confirmBtn, 1, wx.ALL, 1)
        btnSizer.Add(self.cancelBtn, 1, wx.ALL, 1)
        mainSizer.Add(btnSizer, 1, wx.ALIGN_CENTER, GRID_BORDER)

        self.SetSizer(mainSizer)
        self.Layout()

    def getPort(self):
        if not( self.portCmbBox.GetCurrentSelection() == -1):
            return self.ports[self.portCmbBox.GetCurrentSelection()]

    def comfirm(self, event):
        self.resoult = self.cmbBoxSizer.GetStringSelection()

    def onClose(self, event):
        self.Destroy()

    def GetURI(self):
        return self.getPort()

    def getPorts(self):
        newchoice_port = []
        newports = []
        for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
            newchoice_port.append('%s - %s' % (portname, desc))
            newports.append(portname)
        if newports != self.ports:
            self.ports = newports
            self.choice_port = newchoice_port

