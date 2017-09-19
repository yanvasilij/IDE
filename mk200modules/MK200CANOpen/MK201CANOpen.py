#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief вкладка GUI-я настройки CAN'а на модлуле MK201
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
from MK200CANOpenBase import MK200CANOpenBase
from CANOpenIOEditors.CANOpenSettings import CANOpenSettingsEditor


CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
CodeFile = CodeFileTreeNode.CodeFile

DIV_BEGIN = "/" + ("*"*82) + "\n\t\t\t"
DIV_END = "\n" + ("*"*82) + "/\n"

NODE_ID_DESCRIPTION = "Node ID"

NUM_OF_DI = 24
NUM_OF_AI = 7
LOACTION_MODULE_NUM = '.0'

class MK201CANOpenEditor(CodeEditor):

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


class MK201CANOpenFileEditor(MK200CANOpenBase):

    CONFNODEEDITOR_TABS = [
        (_("C code"), "_create_CodePanel")]
    EditorType = MK201CANOpenEditor

    def _create_CodePanel(self, prnt):
        MK200CANOpenBase._create_CodePanel(self, prnt)
        self.DefaultNodID = []

        self.CANSettings = CANOpenSettingsEditor(self.CodeEditorPanel, self.ParentWindow, self.Controler, NUM_OF_DI)

        self.cobeID = self.Controler.GetFullIEC_Channel()
        self.cobeID = self.cobeID[:-2]
        self.nodeIDsizer.DefaultConfig[0]["Name"] = "Node_ID_master_{}".format(self.cobeID)

        self.mainSizer.Add(self.CANSettings, 1, wx.EXPAND)
        self.CodeEditorPanel.SetSizer(self.mainSizer)
        return self.CodeEditorPanel

    def RefreshView(self):
        MK200CANOpenBase.RefreshView(self)
        self.CANSettings.RefreshView()

class MK201CANOpenFile(CodeFile):

    CODEFILE_NAME = "CANOpenConfig"
    SECTIONS_NAMES = [ "includes", "globals", "initFunction", "cleanUpFunction", "retrieveFunction", "publishFunction"]

    EditorType = MK201CANOpenFileEditor

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

    def GenerateDefaultVariables(self):
        defaultConfig = []
        cobeID = self.GetFullIEC_Channel()
        cobeID = cobeID[:-2].replace('.', '_')
        defaultConfig.append({
            "Name" : "Node_ID_{}".format(cobeID),
            "Address" : "127",
            "Len" : "",
            "Type" : u"INT",
            "Initial": "",
            "Description": "Node ID",
            "OnChange":"",
            "Value":"",
            "Options":""})
        defaultConfig.append({
            "Name" : "Node_ID_{}".format(cobeID),
            "Address" : "127",
            "Len" : "",
            "Type" : u"INT",
            "Initial": "",
            "Description": "Node ID",
            "OnChange":"",
            "Value":"",
            "Options":""})
        return defaultConfig

    def GetVariables(self):
        datas = []
        codeFileVariables = self.CodeFileVariables(self.CodeFile)
        if len(codeFileVariables) == 0:
            datas = self.GenerateDefaultVariables()
            return datas
        datas = []
        for var in self.CodeFileVariables(self.CodeFile):
            datas.append({"Name" : var.getname(),
                          "Type" : var.gettype(),
                          "Initial" : var.getinitial(),
                          "Description": var.getdesc(),
                          "OnChange": var.getonchange(),
                          "Options": var.getopts(),
                          "Address" : var.getaddress(),
                          "Value" : var.getvalue(),
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
            variable.setvalue(var["Value"])
            variable.setlen(var["Len"])
            self.CodeFile.variables.appendvariable(variable)

    def GetIconName(self):
        return "CFile"

    def _CloseView(self, view):
        app_frame = self.GetCTRoot().AppFrame
        if app_frame is not None:
            app_frame.DeletePage(view)

    def CodeFileName(self):
        return os.path.join(self.CTNPath(), "CANOpen.xml")

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

        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))
        text = ""
        text += "#include \"MK200CANOpenMasterProcess.h\"\r\n"

        node_id = [i["Address"] for i in self.GetVariables() if i["Description"] == NODE_ID_DESCRIPTION]
        # print node_id
        if len(node_id) > 0:
            node_id = node_id[0]
        else:
            node_id = 1
        text += "CANOpenMK211 mk211_{0}({1});\r\n".format(location_str, node_id)

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

