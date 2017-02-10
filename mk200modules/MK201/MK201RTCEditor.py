__author__ = 'Yanikeev-as'


import os

from PLCControler import LOCATION_CONFNODE, LOCATION_GROUP, LOCATION_VAR_MEMORY
from MK201RTCCodeGenerator import RTCCodeGenerator
from CodeFileTreeNode import CodeFile

from MK201RTCCodeGenerator import *

import CodeFileTreeNode
CodeFile = CodeFileTreeNode.CodeFile

class MK201RTCModuleFile(CodeFile):

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

    def CodeFileName(self):
        return os.path.join(self.CTNPath(), "mk201Config.xml")

    def CTNGenerate_C(self, buildpath, locations):

        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))
        text = ""
        text += "//Publish and retrive \n\n"

        # создаю пересенные для связи с программой
        self.timeValue = RTCCodeGenerator(self)

        # myTestVar = self.GetVariables()

        text += "int __init_%s(int argc,char **argv)\n{\n"%location_str
        # text += "\t{}\n".format(myTestVar[1]["testparam"])
        text += "\n}\n\n"

        text += "void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "void __retrieve_%s(void)\n{\n"%location_str
        text += "   ;\n"
        text += "\n}\n\n"

        text += "void __publish_%s(void)\n{\n"%location_str
        text += "\n"
        text += "\n}\n\n"


        Gen_Cfile_path = os.path.join(buildpath, "hhhh%s.c"%location_str)
        cfile = open(Gen_Cfile_path,'w')
        cfile.write(text)
        cfile.close()
        matiec_flags = '"-I%s"'%os.path.abspath(self.GetCTRoot().GetIECLibPath())
        return [(Gen_Cfile_path, str(matiec_flags))],str(""),True