#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Плагин для работы Modbus мастером
@Author Vasilij
"""
import wx
import os
import copy
import CodeFileTreeNode
from PLCControler import LOCATION_CONFNODE, LOCATION_GROUP, LOCATION_VAR_MEMORY
from ModbusTcpMaster_XSD import CODEFILE_XSD
from SocketRequestEditor import SocketRequestEditor

CodeFile = CodeFileTreeNode.CodeFile

SOCKET_TASK = """

static MbTcpMasterSocketType mbSocket;

static void mbTcpMasterSocketTask (void *p)
{
    for(;;)
    {
        mbSocket.poll();
        taskYIELD();
    }
}
"""

DATALEN_DIC = {"8": "USART_WordLength_8b", "9": "USART_WordLength_9b"}
PARITY_DIC = {"none": "USART_Parity_No", "even": "USART_Parity_Even", "odd":"USART_Parity_Odd"}
STOPBITS_DIC = {"1": "USART_StopBits_1", "0.5":"USART_StopBits_0_5", "1.5":"USART_StopBits_1_5", "2":"USART_StopBits_2"}

class SocketFile (CodeFile):
    CODEFILE_NAME = "modbusTcpSocket"
    SECTIONS_NAMES = [ "includes", "globals", "initFunction", "cleanUpFunction",
            "retrieveFunction", "publishFunction"]

    EditorType = SocketRequestEditor

    def __init__(self):
        old_xsd = CodeFileTreeNode.CODEFILE_XSD
        CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
        CodeFile.__init__(self)
        CodeFileTreeNode.CODEFILE_XSD = old_xsd

    def GetVariableLocationTree(self):
        children = []
        tmp = self.GetFullIEC_Channel()
        iecChannel = tmp[:-2]
        variables = [i for i in self.GetVariables() 
                if i["Modbus type"] in ("Holding read", "Holding write", "Input", "Coil read", "Coil write", "Disc")]
        for variable, i in zip (variables, range(0, len(variables))):
            run = {
                    'children':[],
                    'var_name': 'run',
                    'IEC_type': 'BOOL',
                    'name': 'run',
                    'description': '',
                    'type': LOCATION_VAR_MEMORY,
                    'location': "%QX"+iecChannel+".{}.0".format(i),
                    'size': 'X'
                    }
            status = {
                    'children':[],
                    'var_name': 'status',
                    'IEC_type': 'WORD',
                    'name': 'status',
                    'description': '',
                    'type': LOCATION_VAR_MEMORY,
                    'location': "%QW"+iecChannel+".{}.1".format(i),
                    'size': 'W'
                    }
            error = {
                    'children':[],
                    'var_name': 'error',
                    'IEC_type': 'WORD',
                    'name': 'error',
                    'description': '',
                    'type': LOCATION_VAR_MEMORY,
                    'location': "%QW"+iecChannel+".{}.2".format(i),
                    'size': 'W'
                    }
            requeset = {
                    "name": variable["Name"],
                    "type": LOCATION_CONFNODE, 
                    "location": '%QD'+iecChannel+".{}".format(i),
                    "children": [run,status,error]
                    }
            children.append(requeset)
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
                          "Data type" : var.gettype(),
                          "Device ID" : var.getdevid(),
                          "Description" : var.getdesc(),
                          "OnChange"    : var.getonchange(),
                          "Modbus type" : var.getopts(),
                          "Address" : var.getaddress(),
                          "Len" : var.getlen(),
                          "Transfer method" : var.gettxtype(),
                          "Period" : var.getperiod(),
                          })
        return datas

    def SetVariables(self, variables):
        self.CodeFile.variables.setvariable([])
        for var in variables:
            variable = self.CodeFileParser.CreateElement("variable", "variables")
            variable.setname(var["Name"])
            variable.setdevid(var["Device ID"])
            variable.settype(var["Data type"])
            variable.setopts(var["Modbus type"])
            variable.setaddress(var["Address"])
            variable.setlen(var["Len"])
            variable.setdesc(var["Description"])
            variable.settxtype(var["Transfer method"])
            variable.setperiod(var["Period"])
            self.CodeFile.variables.appendvariable(variable)

    def GetIconName(self):
        return "Cfile"

    def CodeFileName(self):
        return os.path.join(self.CTNPath(), "modbusTcpSocket.xml")

    def GenerateVariblePrototypes(self):
        text = ""
        alreadyCreatedTypes = []
        requests = [i for i in self.GetVariables() if i["Description"] == "Modus master request data"]
        for request in requests:
            varName = request["Name"]
            varName = varName.upper()
            len = int(request["Len"])
            text += "extern \"C\"\n{\n"
            varType = request["Data type"]
            if len > 1:
                newType = "__DECLARE_ARRAY_TYPE(__ARRAY_OF_{0}_{1},{2},[{3}]);\n".format(varType, len, varType, len)
                if newType not in alreadyCreatedTypes:
                    text += newType
                    alreadyCreatedTypes.append(newType)
                text += "__DECLARE_GLOBAL_PROTOTYPE(__ARRAY_OF_{0}_{1},{2});\n\n".format(varType, len, varName)
            else:
                text += "__DECLARE_GLOBAL_PROTOTYPE({0},{1});\n".format(varType, varName)
            text += "}\n"
        return text

    def GenerateRequestSturcts(self):
        requests = [i for i in self.GetVariables() if i["Description"] == "Modus master request data"]
        REQUEST_TYPES = \
            {
                "Holding read": "MBHoldingRegisterRead",
                "Holding write": "MBHoldingRegisterWrite",
                "Input": "MBInputRegisterRead",
                "Coil read": "MBCoilRead",
                "Coil write": "MBCoilWrite",
                "Disc": "MBDiscRead"
            }
        requestStruct = ""
        prototypes = ""
        iecChannel = self.GetFullIEC_Channel()[:-2].replace(".", "_")
        for request, i in zip(requests, range(0, len(requests))):
            varName = request["Name"]
            varName = varName.upper()
            requestStruct += "void "+request["Name"]+"_reqGetHandler (u16 * data)\n{\n"
            requestStruct += "\tu32 i,j;\n"
            if request["Data type"] == "BOOL":
                if int(request["Len"]) == 1:
                    requestStruct += "\tdata[0] = 0;\n"
                    requestStruct += "\tif (*__GET_GLOBAL_{}())\n".format(varName)
                    requestStruct += "\t\tdata[0] |= (1<<0);\n"
                else:
                    requestStruct += "\tfor(i=0, j=0; i<{}; i++, j=i/16)\n".format(request["Len"])
                    requestStruct += "\t\tdata[j] = 0;\n"
                    requestStruct += "\tfor(i=0, j=0; i<{}; i++, j=i/16)\n".format(request["Len"])
                    requestStruct += "\t{\n"
                    requestStruct += "\t\tu8 offset = i%16;\n"
                    requestStruct += "\t\tif ( __GET_GLOBAL_{}()->table[i] )\n".format(varName)
                    requestStruct += "\t\t\tdata[j] |= (1<<offset);\n"
                    requestStruct += "\t}\n"
            else:
                if int(request["Len"]) == 1:
                    requestStruct += "\tdata[0] = *__GET_GLOBAL_{}();\n".format(varName)
                else:
                    requestStruct += "\tfor (i=0; i<{}; i++)\n".format(request["Len"])
                    requestStruct += "\t{\n"
                    requestStruct += "\t\tdata[i] = __GET_GLOBAL_{}()->table[i];\n".format(varName)
                    requestStruct += "\t}\n"
            requestStruct += "};\n\n"

            requestStruct += "void "+request["Name"]+"_reqSetHandler (u16 * data) \n{\n\n"
            requestStruct += "\tu32 i,j;\n"
            if request["Data type"] == "BOOL":
                if int(request["Len"]) == 1:
                    requestStruct += "\tif (data[0] & 1)\n".format(varName)
                    requestStruct += "\t\t*__GET_GLOBAL_{}() = 1;\n".format(varName)
                    requestStruct += "\telse\n"
                    requestStruct += "\t\t*__GET_GLOBAL_{}() = 0;\n".format(varName)
                else:
                    requestStruct += "\tfor(i=0, j=0; i<{}; i++, j=i/16)\n".format(request["Len"])
                    requestStruct += "\t{\n"
                    requestStruct += "\t\tu8 offset = i%16;\n"
                    requestStruct += "\t\tif ( data[j] & (1<<offset) )\n".format(varName)
                    requestStruct += "\t\t\t__GET_GLOBAL_{}()->table[i] = 1;\n".format(varName)
                    requestStruct += "\t\telse\n"
                    requestStruct += "\t\t\t__GET_GLOBAL_{}()->table[i] = 0;\n".format(varName)
                    requestStruct += "\t}\n"
            else:
                if int(request["Len"]) == 1:
                    requestStruct += "\t*__GET_GLOBAL_{}() = data[0];\n".format(varName)
                else:
                    requestStruct += "\tfor (i=0; i<{}; i++)\n".format(request["Len"])
                    requestStruct += "\t{\n"
                    requestStruct += "\t\t__GET_GLOBAL_{}()->table[i] = data[i];\n".format(varName)
                    requestStruct += "\t}\n"
            requestStruct += "};\n\n"

            prototypes += "extern RequestType req_" + request["Name"] + ";\r\n"
            requestStruct += "RequestType req_" + request["Name"] + " =\n{\n"
            requestStruct += "\t" + REQUEST_TYPES[request["Modbus type"]] + ",\n"
            requestStruct += "\tMBRequestSuccesfulyDone,\n"
            requestStruct += "\tMBNoError,\n"
            if request["Transfer method"] == "Periodic":
                requestStruct += "\t1,\n"
                requestStruct += "\t1,\n"
            else:
                requestStruct += "\t0,\n"
                requestStruct += "\t0,\n"
            requestStruct += "\t100,\n"
            requestStruct += "\t{},\n".format(request["Device ID"])
            requestStruct += "\t0,\n"
            requestStruct += "\t{},\n".format(request["Period"])
            requestStruct += "\t{},\n".format(request["Address"])
            requestStruct += "\t{},\n".format(request["Len"])
            requestStruct += "\t{}_reqGetHandler,\n".format(request["Name"])
            requestStruct += "\t{}_reqSetHandler\n".format(request["Name"])
            requestStruct += "};\n\n"
            requestStruct += "void *__QX{0}_{1}_{2} = &req_{3}.run;\n".format(iecChannel, i, 0, request["Name"])
            requestStruct += "void *__QW{0}_{1}_{2} = &req_{3}.status;\n".format(iecChannel, i, 1, request["Name"])
            requestStruct += "void *__QW{0}_{1}_{2} = &req_{3}.error;\n".format(iecChannel, i, 2, request["Name"])
            requestStruct += "\n"
        return requestStruct, prototypes

    def CTNGenerate_C(self, buildpath, locations):
        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))

        """Here creats file for C-extension usage"""
        modbusAccesorHeaderText = "\n#include \"MbMasterConfig.h\"\n"
        modbusAccesorHeaderText += "\n#include \"MbMasterTypes.h\"\n"
        modbusAccesorHeaderText += "\n#include \"MbMasterTcpHal.h\"\n"
        modbusAccesorHeaderText += "\n#include \"MbMasterBase.h\"\n"
        modbusAccesorHeaderText += "\n#include \"MbMasterTCP.h\"\n"
        modbusAccesorHeaderText += "#include \"accessor.h\"\n"
        modbusAccesorHeaderText += "#include \"iec_std_lib.h\"\n"
        modbusAccesorHeaderText += "\n"
        modbusAccesorHeaderText += self.GenerateVariblePrototypes()
        modbusAccesorHeaderName = "MK200ModbusRequest_%s.h"%location_str
        modbusAccesorHeader = os.path.join(buildpath, modbusAccesorHeaderName)
        mbsAccHdrFile = open(modbusAccesorHeader,'w')
        mbsAccHdrFile.write(modbusAccesorHeaderText)
        """Include this header to .c file"""
        text = "#include \"%s\"\n\n"%modbusAccesorHeaderName

        structurest, prototypes = self.GenerateRequestSturcts()

        """ Add structrure prototypes to header file """
        mbsAccHdrFile.write(prototypes)
        mbsAccHdrFile.close()

        text += structurest

        text += SOCKET_TASK

        text += "extern \"C\" int __init_%s(int argc,char **argv)\n{\n"%location_str

        ip_address = [i for i in self.GetVariables() if i["Description"] == "ip address"]
        ip_address = ip_address[0]["Address"].replace(".", ", ")
        text += "\tu8 ip[] = {%s};\n" % (ip_address)
        port = [i for i in self.GetVariables() if i["Description"] == "port"]
        port= port[0]["Address"]
        text += "\tu16 port = {};\n".format(port)
        text += "\tmbSocket.init(ip, port, 1000);\n"

        requests = [i for i in self.GetVariables() if i["Description"] == "Modus master request data"]
        for request in requests:
            text += "\tmbSocket.addRequest(&req_{0});\n".format(request["Name"])

        text += "\n\txTaskCreate(mbTcpMasterSocketTask, \"mbTcpMasterSocketTask\", " \
                "configMINIMAL_STACK_SIZE*5, NULL, 1, NULL);\n"

        text += "\treturn 0;\n}\n\n"

        text += "extern \"C\" void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "extern \"C\" void __retrieve_%s(void)\n{\n"%location_str
        text += "   ;\n"
        text += "\n}\n\n"

        text += "extern \"C\" void __publish_%s(void)\n{\n"%location_str
        text += "\n"
        text += "\n}\n\n"

        Gen_Cfile_path = os.path.join(buildpath, "mbTcpMasterSocket_%s.cpp"%location_str)
        cfile = open(Gen_Cfile_path,'w')
        cfile.write(text)
        cfile.close()
        matiec_flags = '"-I%s"'%os.path.abspath(self.GetCTRoot().GetIECLibPath())
        return [(Gen_Cfile_path, str(matiec_flags))],str(""),True

    def CTNGlobalInstances(self):
        variables = self.CodeFileVariables(self.CodeFile)
        ret = []
        for variable in variables:
            if variable.getdesc() != "Modus master request data":
                continue
            varLen = int(variable.getlen())
            varType = variable.gettype()
            if varLen > 1:
                varType = "ARRAY [0..{0}] OF {1}".format(varLen-1, varType)
            ret.append((variable.getname(), varType, variable.getinitial()))
        ret.extend([("On"+variable.getname()+"Change", "python_poll", "")
                    for variable in variables
                    if variable.getonchange()])
        return ret

