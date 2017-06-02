__author__ = 'Yanikeev-as'

import wx
import os
import wx.lib.agw.customtreectrl as CT
import CodeFileTreeNode
import wx.lib.intctrl
from editors.CodeFileEditor import CodeEditor
from editors.CodeFileEditor import CodeFileEditor
from editors.ConfTreeNodeEditor import ConfTreeNodeEditor
from ConfigTreeNode import ConfigTreeNode
from PLCControler import LOCATION_CONFNODE, LOCATION_GROUP, LOCATION_VAR_MEMORY

DESCRIPTION = "Node ID"

class NodeId(wx.Panel):
    def __init__(self, parent, window, controler):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)

        self.ParentWindow = window
        self.parent = parent
        self.Controler = controler

        self.DefaultConfig = []
        self.DefaultConfig.append({
            "Name" : "Node_ID",
            "Address" : "1",
            "Len" : "",
            "Type" : u"INT",
            "Initial": "",
            "Description": DESCRIPTION,
            "OnChange":"",
            "Options":""})

        nodeIDsizer = wx.BoxSizer(wx.HORIZONTAL)
        nodeIDText = wx.StaticText(self, label = 'Node ID')
        nodeIDsizer.Add(nodeIDText, wx.ALIGN_CENTER_VERTICAL)
        self.nodeID = wx.lib.intctrl.IntCtrl(self, value=1, min=1, max=127, limited=True)
        wx.EVT_TEXT(self, self.nodeID.GetId(), self.OnChange)
        nodeIDsizer.Add(self.nodeID)
        self.SetSizer(nodeIDsizer)

    def GetData(self):
        config = self.DefaultConfig[:]
        nodeID = self.nodeID.GetValue()
        config[0]['Address'] = str(nodeID)
        return config

    def SetData(self, nodeConfig):
        self.RefreshModel()
        if len(nodeConfig) == 0:
            self.nodeID.SetValue(1)
        else:
            self.nodeID.SetValue(int(nodeConfig[0]["Address"]))


    def OnChange(self, event):
        valuesOnFrame = self.GetData()
        valuesInController = [i for i in self.Controler.GetVariables()
                              if i["Description"] == DESCRIPTION]
        # print valuesOnFrame != valuesInController
        if valuesOnFrame != valuesInController:
            self.RefreshModel()
        event.Skip()

    def RefreshView(self):
        varForTable = self.Controler.GetVariables()
        varForTable = [i for i in varForTable if i["Description"] == DESCRIPTION]
        self.SetData(varForTable)
        self.Layout()

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

    def GetVariableTypeFunction(self, base_type):
        def VariableTypeFunction(event):
            self.RefreshModel()
            self.RefreshView()
            event.Skip()
        return VariableTypeFunction