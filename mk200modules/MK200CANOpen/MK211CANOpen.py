#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief вкладка GUI-я настройки CAN'а для MK211
@Author Vasilij
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
from MK201CANOpen_XSD import CODEFILE_XSD
from CANOpenIOEditors.CANOpenDI import CANOpenDiEditor
from CANOpenIOEditors.CANOpenAI import CANOpenAinputEditor
from MK200CANOpenBase import MK200CANOpenBase

CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
CodeFile = CodeFileTreeNode.CodeFile

DIV_BEGIN = "/" + ("*"*82) + "\n\t\t\t"
DIV_END = "\n" + ("*"*82) + "/\n"

DI_DESCRIPTION = "On board digital input"
AI_DESCRIPTION = "On board AI"
NODE_ID_DESCRIPTION = "Node ID"

NUM_OF_DI = 24
NUM_OF_AI = 8
LOACTION_MODULE_NUM = '.0'

class MK211CANOpenEditor(CodeEditor):

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


class MK211CANOpenFileEditor(MK200CANOpenBase):

    CONFNODEEDITOR_TABS = [
        (_("C code"), "_create_CodePanel")]
    EditorType = MK211CANOpenEditor

    def _create_CodePanel(self, prnt):
        MK200CANOpenBase._create_CodePanel(self, prnt)
        self.DefaultNodID = []
        # self.nodeIDsizer = NodeId(self.CodeEditorPanel, self.ParentWindow, self.Controler)
        # self.mainSizer.Add(self.nodeIDsizer)
        notebook = wx.Notebook(self.CodeEditorPanel)
        """DI tab"""
        self.diEditor = CANOpenDiEditor(notebook, self.ParentWindow, self.Controler, NUM_OF_DI)
        notebook.AddPage(self.diEditor, "DI Config")
        """AI tab"""
        self.aiEditor = CANOpenAinputEditor(notebook, self.ParentWindow, self.Controler, NUM_OF_AI)
        notebook.AddPage(self.aiEditor, "AI Config")

        self.mainSizer.Add(notebook, 1, wx.EXPAND)
        self.CodeEditorPanel.SetSizer(self.mainSizer)
        return self.CodeEditorPanel

    def RefreshView(self):
        MK200CANOpenBase.RefreshView(self)
        self.diEditor.RefreshView()
        self.aiEditor.RefreshView()

class MK211CANOpenFile (CodeFile):

    CODEFILE_NAME = "CANOpenConfig"
    SECTIONS_NAMES = [ "includes", "globals", "initFunction", "cleanUpFunction", "retrieveFunction", "publishFunction"]

    EditorType = MK211CANOpenFileEditor

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

    def GetVariableLocationTree(self):
        iecChannel = self.GetFullIEC_Channel()[:1]
        analogInputsFloat = self.GetIoVariableLocationTree("Analog inputs (Float)", u'REAL', '%QD'+iecChannel+LOACTION_MODULE_NUM+'.0', 'D', NUM_OF_AI)
        analogInputsU16 = self.GetIoVariableLocationTree("Analog inputs (U16)", u'DINT', '%QD'+iecChannel+LOACTION_MODULE_NUM+'.1', 'D', NUM_OF_AI)
        digitalOutputs = self.GetIoVariableLocationTree("Digital inputs", u'BOOL', '%QX'+iecChannel+LOACTION_MODULE_NUM+'.2', 'X', NUM_OF_DI)
        children = [analogInputsFloat, analogInputsU16, digitalOutputs]
        return {"name": self.BaseParams.getName(),
                "type": LOCATION_CONFNODE,
                "location": self.GetFullIEC_Channel(),
                "children": children}

    def GetConfNodeGlobalInstances(self):
        return []

    def GetVariables(self):
        datas = []
        for var in self.CodeFileVariables(self.CodeFile):
            datas.append({"Name" : var.getname(),
                          "Type" : var.gettype(),
                          "Initial" : var.getinitial(),
                          "Description": var.getdesc(),
                          "OnChange": var.getonchange(),
                          "Options": var.getopts(),
                          "Address" : var.getaddress(),
                          "Len" : var.getlen(),
                          })
        return datas


    def SetVariables(self, variables):
        self.CodeFile.variables.setvariable([])
        for var in variables:
            variable = self.CodeFileParser.CreateElement("variable", "variables")
            variable.setname(var["Name"])
            variable.settype(var["Type"])
            variable.setinitial(var["Initial"])
            variable.setdesc(var["Description"])
            variable.setonchange(var["OnChange"])
            variable.setopts(var["Options"])
            variable.setaddress(var["Address"])
            variable.setlen(var["Len"])
            self.CodeFile.variables.appendvariable(variable)

    def GetIconName(self):
        return "CFile"

    def _CloseView(self, view):
        app_frame = self.GetCTRoot().AppFrame
        if app_frame is not None:
            app_frame.DeletePage(view)

    def CodeFileName(self):
        return os.path.join(self.CTNPath(), "MK211CANOpen.xml")

    def GenerateLocationVariables(self, location_str):
        """
        Generates Locations vairables that binds user app variables and runtime
        :param location_str: location of whole module in project three (e.g. 1,2,3...)
        :return: C-code of declaring binding variables
        """
        text = ""
        for i in range(NUM_OF_AI):
            text += "void *__QD{0}_0_{1} = &mk211_{2}.ai[{3}].fValue;\n".format(location_str,
                                                                                  i, location_str, i)
            text += "void *__QD{0}_1_{1} = &mk211_{2}.ai[{3}].u16Value;\n".format(location_str,
                                                                              i, location_str, i)
        for i in range(NUM_OF_DI):
            text += "void * __QX{0}_2_{1} = &mk211_{2}.di[{3}].value;\n".format(location_str,
                                                                         i, location_str, i)
        return text

    def GenerateInit(self, location_str):
        """
        :param location_str: location of whole module in project three (e.g. 1,2,3...)
        :return: C-Function code
        """
        # di init
        di_config = [i for i in self.GetVariables() if i["Description"] == DI_DESCRIPTION]
        text = ""
        text += "extern \"C\" int __init_%s(int argc,char **argv)\n"%location_str
        text += "{\n"
        for config in di_config:
            # the last symbol should channel num
            channel = config["Name"][-1]
            if config["Options"] == "Off":
                text += "    mk211_{0}.di[{1}].enabled = 0;\n".format(location_str, channel)
            else:
                text += "    mk211_{0}.di[{1}].enabled = 1;\n".format(location_str, channel)

        ai_config = [i for i in self.GetVariables() if i["Description"] == DI_DESCRIPTION]
        for config in ai_config:
            channel = config["Name"][-1]
            if config["Options"] == "Off":
                text += "    mk211_{0}.ai[{1}].enabled = 0;\n".format(location_str, channel)
            else:
                text += "    mk211_{0}.ai[{1}].enabled = 1;\n".format(location_str, channel)
        text += "    mk200CANOpenMaster.addNode(&mk211_{0});\n".format(location_str)
        text += "}\n"
        return text

    def CTNGenerate_C(self, buildpath, locations):
        """
        Generates cpp-file that binds user app with runtime
        :param buildpath: path where cpp-file should be generated
        :param locations:
        :return:
        """
        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))
        text = ""
        text += "#include \"MK200CANOpenMasterProcess.h\"\r\n"

        node_id = [i["Address"] for i in self.GetVariables() if i["Description"] == NODE_ID_DESCRIPTION]
        print node_id
        if len(node_id) > 0:
            node_id = node_id[0]
        else:
            node_id = 1
        text += "CANOpenMK211 mk211_{0}({1});\r\n".format(location_str, node_id)

        text += self.GenerateLocationVariables(location_str)

        text += DIV_BEGIN + "Publish and retrive" + DIV_END
        text += self.GenerateInit(location_str)

        text += "extern \"C\" void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "extern \"C\" void __retrieve_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "extern \"C\" void __publish_%s(void)\n{\n"%location_str
        text += "\n"
        text += "\n}\n\n"

        Gen_Cfile_path = os.path.join(buildpath, "MK211CANOpen_%s.cpp"%location_str)
        cfile = open(Gen_Cfile_path,'w')
        cfile.write(text)
        cfile.close()
        matiec_flags = '"-I%s"'%os.path.abspath(self.GetCTRoot().GetIECLibPath())
        return [(Gen_Cfile_path, str(matiec_flags))],str(""), True
