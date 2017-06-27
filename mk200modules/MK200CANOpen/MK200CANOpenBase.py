#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief базовый класс для модулей MK200
@Author YanikeevAndrey
"""

import wx
import CodeFileTreeNode

from MK201CANOpen_XSD import CODEFILE_XSD
from editors.CodeFileEditor import CodeFileEditor
from editors.ConfTreeNodeEditor import ConfTreeNodeEditor
from CANOpenIOEditors.CANOpenNodeID import NodeId

CodeFile = CodeFileTreeNode.CodeFile


class MK200CANOpenFile(CodeFile):
    def __init__(self):
        old_xsd = CodeFileTreeNode.CODEFILE_XSD
        CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
        CodeFile.__init__(self)
        CodeFileTreeNode.CODEFILE_XSD = old_xsd


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


