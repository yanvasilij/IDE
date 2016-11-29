#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Базовый класс панели с настройками для IO на MK201
@Author Vasilij
"""
import wx

class MK201IOEditor (wx.Panel):

    def __init__(self, parent, window, controler):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.ParentWindow = window
        self.Controler = controler
        self.firstCall = 1
        self.Bind(wx.EVT_SHOW, self.OnShow)


    def OnShow(self, event):
        if self.firstCall:
            self.RefreshView()
            self.firstCall = 0
        event.Skip()
    
    def RefreshView(self):
        pass

    def RefreshBuffer(self):
        self.Controler.BufferCodeFile()
        self.ParentWindow.RefreshTitle()
        self.ParentWindow.RefreshFileMenu()
        self.ParentWindow.RefreshEditMenu()
        self.ParentWindow.RefreshPageTitles()

    def RefreshModel(self):
        pass

    def GetVariableTypeFunction(self, base_type):
        def VariableTypeFunction(event):
            self.RefreshModel()
            self.RefreshView()
            event.Skip()
        return VariableTypeFunction

