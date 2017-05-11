# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'

# импорт сторонних библиотек
import wx
import wx.lib.masked
import copy
import os.path
import sys
import time
from threading import Thread
from wx.lib.pubsub import pub
from wx.lib.pubsub import Publisher
import wx.lib.intctrl

# импорт моих модулей
from serialWork import SerialPort
from mk201_proto import mk201_proto

VERSION = 'v0.1.1'

import os

def hook(mod):
    pth = str(mod.__path__[0])
    if os.path.isdir(pth):
        mod.__path__.append(os.path.normpath(os.path.join(pth, 'kwargs')))
    return mod

class MKSetup_GUI(wx.Frame):
    def __init__(self):
        self.connectStatus = None # отображет сообщение от действий объекта SerialWork
        self.connection = False # отображает состояние соединения
        self.moduleTypesList = ['AI', 'AO', 'DI', 'DO', 'PSU']
        self.modulObj = mk201_proto()
        self.comPorts = self.modulObj.getPorts()[1]
        self.buildMainFrame()

        # привязки к кнопкам
        self.setModuleType.Bind(wx.EVT_BUTTON, self.setModule)
        self.loadInSerialBtn.Bind(wx.EVT_BUTTON, self.loadHex)
        self.connectBtn.Bind(wx.EVT_BUTTON, self.connectPort)
        self.writeSerialBtn.Bind(wx.EVT_BUTTON, self.serialWrite)
        self.readSerialBtn.Bind(wx.EVT_BUTTON, self.serialRead)
        # self.error_dialig()

        Publisher().subscribe(self.loadStatus, "update")
        Publisher().subscribe(self.serialWrite, "serial")

    def buildMainFrame(self):
        self.heigth = 400
        self.width = 280
        wx.Frame.__init__(self, None, id = wx.NewId(), title = "MKSetup " + VERSION, name = 'mainFrame',
                          pos=(150,150), size = (self.heigth, self.width), )
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # меню
        self.menuBar = wx.MenuBar()
        self.menu = wx.Menu()
        self.m_exit = self.menu.Append(wx.ID_EXIT, "&Connection settings\tAlt-P", "Settings for serial port")
        self.m_exit = self.menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, self.m_exit)
        # self.menuBar.Append(self.menu, "&File")
        self.SetMenuBar(self.menuBar)

        # кнопки
        self.loadInSerialBtn = wx.Button(self, id = wx.ID_ANY, label="Load", pos = (300, 170))
        self.loadInSerialBtn.Disable()
        self.setModuleType = wx.Button(self, id = wx.ID_ANY, label="Select", pos = (300, 5))
        self.connectBtn = wx.Button(self, id = wx.ID_ANY, label="Connect", pos = (300, 35))
        self.writeSerialBtn = wx.Button(self, id = wx.ID_ANY, label="Write Serial", pos = (300, 65))
        self.writeSerialBtn.Disable()
        self.readSerialBtn = wx.Button(self, id = wx.ID_ANY, label="Read Serial", pos = (300, 96))
        self.readSerialBtn.Disable()


        # другие виджеты
        self.statusBar = wx.StatusBar(self, id = wx.ID_ANY)
        self.ports_combobox = wx.ComboBox(self, pos = (5,35), size = (280, 20), choices=(self.comPorts))
        self.moduleTypeCombobox = wx.ComboBox(self, pos = (5,5), size = (280, 20), choices=(self.moduleTypesList))

        self.serialWriteTextCtl = wx.lib.intctrl.IntCtrl(self, pos = (5,65), size = (280, 20), min = 0, max = 4294967295, limited = True)
        # self.serialWriteTextCtl.SetValidator(valid)
        self.serialReadTextCtl = wx.TextCtrl(self, pos = (5,95), size = (280, 20), style=wx.TE_READONLY)
        self.progressBar = wx.Gauge(self, id = wx.ID_ANY, range = 100, pos = (5, 200), size = (370, 20))


    def OnClose(self, event):
        # dlg = wx.MessageDialog(top,
        #     "Do you really want to close this application?",
        #     "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        # result = dlg.ShowModal()
        # dlg.Destroy()
        # if result == wx.ID_OK:
            self.Destroy()

    def setEnableButtons(self, value):
        if value == True:
            self.loadInSerialBtn.Enable()
            self.writeSerialBtn.Enable()
            self.readSerialBtn.Enable()
            self.connectBtn.Enable()
        if value == False:
            self.loadInSerialBtn.Disable()
            self.writeSerialBtn.Disable()
            self.readSerialBtn.Disable()


    def setModule(self, event):
        moduleType = self.moduleTypeCombobox.GetStringSelection()
        hexFilePath = moduleType + '.hex'
        resExist = os.path.exists(hexFilePath)
        if not(resExist):
            statusMsg = 'Hex-file does not exist!'
            self.setStatusText(statusMsg)
            return 1
        resRightHex = self.modulObj.checkHexFile(hexFilePath)
        if not(resRightHex):
            statusMsg = 'Wrong hex-file! File length greater than 204800 bytes'
            self.setStatusText(statusMsg)
            return 1
        statusMsg = 'Module selected: ' + moduleType
        self.setStatusText(statusMsg)

    def connectPort(self, event = None):
        if not self.connection:
            serialPort = self.ports_combobox.GetStringSelection()
            self.connectStatus = self.modulObj.connect(serialPort[:5])
            if 'Connected' in self.connectStatus:
                self.connectStatus = self.modulObj.getErrorLog()
                # self.statusBar.SetStatusText(str(self.connectStatus)
                self.setEnableButtons(True)
                self.connectBtn.SetLabel('Disconnect')
                self.connection = True
            self.statusBar.SetStatusText(str(self.connectStatus))
        else:
            try:
                self.modulObj.serial.close()
            finally:
                self.setEnableButtons(False)
                self.connectBtn.SetLabel('Connect')
                self.connection = False
                self.statusBar.SetStatusText('Disconnected')

    def loadHex(self, event):
        moduleType = self.moduleTypeCombobox.GetStringSelection()
        hexFilePath = moduleType + '.hex'
        t = Thread(target=self.modulObj.load_hex_mk500, args = (hexFilePath, 0))
        t.start()
        self.loadInSerialBtn.Disable()
        self.connectBtn.Disable()
        self.writeSerialBtn.Disable()
        self.readSerialBtn.Disable()

    def serialWrite(self, event):
        serialNum = self.serialWriteTextCtl.GetLineText(0)
        if len(serialNum) == 0:
            self.setStatusText('Wrong serial number!')
            return
        answer = self.modulObj.writeSerilaMk500(serialNum)
        self.setStatusText(answer)

    def serialRead(self, event):
        answer = self.modulObj.readSerilaMk500()
        self.serialReadTextCtl.Clear()
        self.serialReadTextCtl.write(str(answer))
        self.statusBar.SetStatusText('Done!')


    def setStatusText(self, Text):
        self.statusBar.SetStatusText(str(Text))

    def loadStatus(self, msg):
        total_load = 0
        answer = msg.data
        if (type(answer) is float):
            # self.progressBar.SetValue((answer - 1) * 10)
            self.progressBar.SetValue(answer)
            total_load += answer
            # self.statusBar.SetStatusText(str( (total_load - 1)*10) + '% loaded')
            self.statusBar.SetStatusText(str( (int(total_load))) + '% loaded')
        if (type(answer) is str):
            # self.modulObj.serial.close()
            # self.connectPort()
            # self.connection = False
            # self.loadInSerialBtn.Enable()
            if 'Download' in str(answer):
                self.statusBar.SetStatusText('Download success')
            if 'Done' in answer:
                self.statusBar.SetStatusText('Download success')
            else:
                self.statusBar.SetStatusText('Download canceled. Error: %s. ' % str(answer))
            self.connectBtn.Enable()
            self.setEnableButtons(True)

    def error_dialig(self):
        try:
            erroDialog = wx.Dialog(self, title = 'Error', name = 'Error lol')
            dlg = erroDialog.ShowModal()

        finally:
            erroDialog.Destroy()

if __name__ == '__main__':
    app = wx.App(False)
    top = MKSetup_GUI()
    top.Show()
    app.MainLoop()
    # sys.exit(app.exec_())