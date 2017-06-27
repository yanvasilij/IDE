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
TEAXLABEL_SIZE = (120, 21)

class NodeId(wx.Panel):
    def __init__(self, parent, window, controler):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)

        self.ParentWindow = window
        self.parent = parent
        self.Controler = controler

        self.DefaultConfig = []
        self.cobeID = self.Controler.GetFullIEC_Channel()
        self.cobeID = self.cobeID[:-2].replace('.', '_')
        self.DefaultConfig.append({
            "Name" : "Node_ID_{}".format(self.cobeID),
            "Address" : "127",
            "Len" : "",
            "Type" : u"INT",
            "Initial": "",
            "Description": DESCRIPTION,
            "OnChange":"",
            "Value":"",
            "Options":""})

        self.nodeIDsizer = wx.BoxSizer(wx.HORIZONTAL)
        nodeIDLbl = wx.StaticText(self, label='Node ID', size=TEAXLABEL_SIZE)
        self.nodeIDsizer.Add(nodeIDLbl, wx.ALIGN_CENTER_VERTICAL)
        self.nodeID = wx.lib.intctrl.IntCtrl(self, value=127, min=0, max=127, limited=True)
        wx.EVT_TEXT(self, self.nodeID.GetId(), self.OnChange)
        self.nodeIDsizer.Add(self.nodeID)
        self.SetSizer(self.nodeIDsizer)

    def GetData(self):
        config = self.DefaultConfig[:]
        nodeID = self.nodeID.GetValue()
        config[0]['Address'] = str(nodeID)
        return config

    def SetData(self, nodeConfig):
        self.RefreshModel()
        if len(nodeConfig) == 0:
            self.nodeID.SetValue(127)
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