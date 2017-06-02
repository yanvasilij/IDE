#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief базовый класс для модулей MK200
@Author YanikeevAndrey
"""

import wx
import os
import wx.lib.agw.customtreectrl as CT
import CodeFileTreeNode
from editors.CodeFileEditor import CodeEditor
from editors.CodeFileEditor import CodeFileEditor
from editors.ConfTreeNodeEditor import ConfTreeNodeEditor
from ConfigTreeNode import ConfigTreeNode
from PLCControler import LOCATION_CONFNODE, LOCATION_GROUP, LOCATION_VAR_MEMORY
from CANOpenIOEditors.CANOpenNodeID import NodeId


class MK200CANOpenBase(CodeFileEditor):

    def __init__(self, parent, controler, window):
        ConfTreeNodeEditor.__init__(self, parent, controler, window)

    def _create_CodePanel(self, prnt):
        self.CodeEditorPanel = wx.Panel(prnt)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.DefaultNodID = []

        self.nodeIDsizer = NodeId(self.CodeEditorPanel, self.ParentWindow, self.Controler)
        self.mainSizer.Add(self.nodeIDsizer)

    def RefreshView(self):
        self.nodeIDsizer.RefreshView()


