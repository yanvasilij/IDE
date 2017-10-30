#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Работа с модулями расширения через протокол CANOpen
@Author Yanikeev-AS
"""
import wx
import os
import CodeFileTreeNode
from editors.CodeFileEditor import CodeFileEditor
from editors.ConfTreeNodeEditor import ConfTreeNodeEditor
from editors.CodeFileEditor import CodeEditor
from PLCControler import LOCATION_CONFNODE, LOCATION_GROUP, LOCATION_VAR_MEMORY
from ModbusTcpMaster_XSD import CODEFILE_XSD
from SocketFile import SocketFile

CodeFile = CodeFileTreeNode.CodeFile

class ModbusTcpEditor (CodeEditor):

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


class ModbusTcpMasterFileEditor(CodeFileEditor):

    CONFNODEEDITOR_TABS = [
        (_("C code"), "_create_CodePanel")]
    EditorType = ModbusTcpEditor

    def __init__(self, parent, controler, window):
        ConfTreeNodeEditor.__init__(self, parent, controler, window)

    def _create_CodePanel(self, prnt):
        self.CodeEditorPanel = wx.Panel(prnt)
        return self.CodeEditorPanel

    def RefreshView(self):
        pass


class RootClass(CodeFile):

    CODEFILE_NAME = "CANOpenConfig"
    SECTIONS_NAMES = [ "includes", "globals", "initFunction", "cleanUpFunction", "retrieveFunction", "publishFunction"]

    EditorType = ModbusTcpMasterFileEditor

    CTNChildrenTypes = [("Socket", SocketFile, "Modbus tcp socket")]

    def __init__(self):
        old_xsd = CodeFileTreeNode.CODEFILE_XSD
        CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
        CodeFile.__init__(self)
        CodeFileTreeNode.CODEFILE_XSD = old_xsd

    def GetIoVariableLocationTree(self, name, type, location, size, numOfChannles):
        variableTree = {"name": name, "type": LOCATION_GROUP, "location": "0", "children": []}
        for i in range(0, numOfChannles):
            variableTree["children"].append({
                'children':[],
                'var_name': 'Channel #{}'.format(i),
                'IEC_type': type,
                'name': 'Channel #{}'.format(i),
                'description': '',
                'type': LOCATION_VAR_MEMORY,
                'location': location+'.{}'.format(i),
                'size':  size})
        return variableTree

    def GetConfNodeGlobalInstances(self):
        return []

    def GetVariables(self):
        datas = []
        return datas

    def SetVariables(self, variables):
        pass

    def GetIconName(self):
        return "Cfile"

    def _CloseView(self, view):
        app_frame = self.GetCTRoot().AppFrame
        if app_frame is not None:
            app_frame.DeletePage(view)

    def CodeFileName(self):
        return os.path.join(self.CTNPath(), "ModbusTcpMaster.xml")

    def CTNGenerate_C(self, buildpath, locations):

        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))
        text = ""
        text += "int __init_%s(int argc,char **argv)\n{\n"%location_str
        text += "\treturn 0;\n}\n\n"

        text += "void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "void __retrieve_%s(void)\n{\n"%location_str
        text += "   ;\n"
        text += "\n}\n\n"

        text += "void __publish_%s(void)\n{\n"%location_str
        text += "\n"
        text += "\n}\n\n"

        Gen_Cfile_path = os.path.join(buildpath, "modbusTcpMaster_%s.c"%location_str)
        cfile = open(Gen_Cfile_path,'w')
        cfile.write(text)
        cfile.close()
        matiec_flags = '"-I%s"'%os.path.abspath(self.GetCTRoot().GetIECLibPath())
        return [(Gen_Cfile_path, str(matiec_flags))],str(""), True
