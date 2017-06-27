#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Работа с модулями расширения через протокол CANOpen
@Author Yanikeev-AS
"""
import os
import CodeFileTreeNode
from PLCControler import LOCATION_CONFNODE, LOCATION_GROUP, LOCATION_VAR_MEMORY
from MK200CANOpenBase import MK200CANOpenFile
from MK211CANOpen import MK211CANOpenFile
from MK234CANOpen import MK234CANOpenFile
from MK243CANOpen import MK243CANOpenFile
from MK245CANOpen import MK245CANOpenFile
from MK201CANOpen import MK201CANOpenFileEditor

DIV_BEGIN = "/" + ("*"*82) + "\n\t\t\t"
DIV_END = "\n" + ("*"*82) + "/\n"

class RootClass(MK200CANOpenFile):

    CODEFILE_NAME = "CANOpenConfig"
    SECTIONS_NAMES = [ "includes", "globals", "initFunction", "cleanUpFunction", "retrieveFunction", "publishFunction"]

    EditorType = MK201CANOpenFileEditor

    CTNChildrenTypes = [("MK211", MK211CANOpenFile, "MK211 module"),
                       ("MK234", MK234CANOpenFile, "MK232 module"),
                       ("MK243", MK243CANOpenFile, "MK243 module"),
                       ("MK245", MK245CANOpenFile, "MK245 module")]

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

    def GetOneParameterByDesc(self, desc, parameter_name, default_value):
        """
        Returns one parameter by name, if parameter doesn't exist returns default value
        :param desc: value of Descrition field to find
        :param parameter_name: parameter name to find
        :param default_value: if parametr doesn't exits return this value
        :return: target parameter
        """
        value = [i[parameter_name] for i in self.GetVariables() if i["Description"] == desc]
        if len(value) > 0:
            return value[0]
        else:
            return default_value

    def GenerateInit(self, location_str):
        """
        :param location_str: location of whole module in project three (e.g. 1,2,3...)
        :return: C-Function code
        """
        self_node_id = self.GetOneParameterByDesc("Node ID", "Address", "0x7F")
        heartbeat_time = self.GetOneParameterByDesc("HeartbeatTime", "Value", "500")
        data_update_time = self.GetOneParameterByDesc("DataUpdateTime", "Value", "500")
        text = ""
        text += "extern \"C\" int __init_%s(int argc,char **argv)\n"%location_str
        text += "{\n"
        text += "    mk200CANOpenMaster.selfNodeId = {};\n".format(self_node_id)
        text += "    mk200CANOpenMaster.consumerHeartbeatTime = {};\n".format(heartbeat_time)
        text += "    mk200CANOpenMaster.pdoEventTimer = {};\n".format(data_update_time)
        text += "    return 0;\n"
        text += "}\n"
        return text

    def CTNGenerate_C(self, buildpath, locations):

        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))
        text = ""
        text += "#include \"MK200CANOpenMasterProcess.h\"\r\n"


        text += DIV_BEGIN + "Publish and retrive" + DIV_END
        text += self.GenerateInit(location_str)

        text += "extern \"C\" void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "extern \"C\" void __retrieve_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "extern \"C\" void __publish_%s(void)\n{\n"%location_str
        text += "\n"
        text += "\n}\n\n"

        Gen_Cfile_path = os.path.join(buildpath, "MK200CANOpen_%s.cpp"%location_str)
        cfile = open(Gen_Cfile_path,'w')
        cfile.write(text)
        cfile.close()
        matiec_flags = '"-I%s"'%os.path.abspath(self.GetCTRoot().GetIECLibPath())
        return [(Gen_Cfile_path, str(matiec_flags))],str(""), True