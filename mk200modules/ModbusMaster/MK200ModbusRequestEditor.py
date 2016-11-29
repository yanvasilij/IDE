#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Редактор запросов modbus master
@Author Vasilij
"""
import wx
from CodeFileTreeNode import CodeFile
from editors.CodeFileEditor import CodeEditor
from editors.CodeFileEditor import CodeFileEditor
from editors.ConfTreeNodeEditor import ConfTreeNodeEditor
from MBRequestDataPanel import MBRequestDataPanel
from MBPortConfigPanel import MBPortConfigPanel

class ModbusRequestEditor(CodeEditor):

    def __init__(self, parent, window, controler):
        pass

    def SetCodeLexer(self):
        pass

    def RefreshBuffer(self):
        pass

    def ResetBuffer(self):
        pass

    def GetCodeText(self):
        pass

    def RefreshView(self, scroll_to_highlight=False):
        pass

class MK200ModbusRequestEditor (CodeFileEditor):
    CONFNODEEDITOR_TABS = [
        (_("C code"), "_create_CodePanel")]
    CODE_EDITOR = ModbusRequestEditor

    def __init__(self, parent, controler, window):
        ConfTreeNodeEditor.__init__(self, parent, controler, window)

    def _create_CodePanel(self, prnt):
        """Main panel with notebook"""
        self.CodeEditorPanel = wx.Panel(prnt)
        sizer = wx.BoxSizer()
        notebook = wx.Notebook(self.CodeEditorPanel)
        """ request edit panel """
        self.DataEditor = MBRequestDataPanel(notebook, self.ParentWindow, self.Controler)
        self.PortEditor = MBPortConfigPanel(notebook, self.ParentWindow, self.Controler)
        self.VariablesPanel = self.DataEditor

        notebook.AddPage(self.DataEditor, "Request data edit")
        notebook.AddPage(self.PortEditor, "Port configuration")

        sizer.Add(notebook, 1, wx.EXPAND)

        self.CodeEditorPanel.SetSizer(sizer)
        self.CodeEditor = self.CODE_EDITOR(self.CodeEditorPanel, self.ParentWindow, self.Controler)
        return self.CodeEditorPanel

    def RefreshView(self):
        CodeFileEditor.RefreshView(self)
        self.DataEditor.RefreshView()
        pass

