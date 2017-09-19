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
from RequestTablePanel import RequestTablePanel

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


class SocketRequestEditor (CodeFileEditor):
    CONFNODEEDITOR_TABS = [
        (_("C code"), "_create_CodePanel")]
    CODE_EDITOR = ModbusRequestEditor

    def __init__(self, parent, controler, window):
        ConfTreeNodeEditor.__init__(self, parent, controler, window)

    def _create_CodePanel(self, prnt):
        """Main panel with notebook"""
        """ request edit panel """
        self.CodeEditorPanel = RequestTablePanel(prnt, self.ParentWindow, self.Controler)
        self.VariablesPanel = self.CodeEditorPanel
        self.CodeEditor = self.CODE_EDITOR(self.CodeEditorPanel, self.ParentWindow, self.Controler)
        return self.CodeEditorPanel

    def RefreshView(self):
        CodeFileEditor.RefreshView(self)
        self.CodeEditorPanel.RefreshView()
        pass

