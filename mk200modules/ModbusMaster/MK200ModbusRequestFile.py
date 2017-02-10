#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Плагин для работы Modbus мастером
@Author Vasilij
"""
import wx
import os
import CodeFileTreeNode
from MK200ModbusMaster_XSD import CODEFILE_XSD
from PLCControler import LOCATION_CONFNODE, LOCATION_GROUP, LOCATION_VAR_MEMORY
from MK200ModbusRequestEditor import MK200ModbusRequestEditor
from MBPortConfigPanel import DEFAULT_CONFIG
import copy

CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
CodeFile = CodeFileTreeNode.CodeFile

DATALEN_DIC = {"8": "USART_WordLength_8b", "9": "USART_WordLength_9b"}
PARITY_DIC = {"none": "USART_Parity_No", "even": "USART_Parity_Even", "odd":"USART_Parity_Odd"}
STOPBITS_DIC = {"1": "USART_StopBits_1", "0.5":"USART_StopBits_0_5", "1.5":"USART_StopBits_1_5", "2":"USART_StopBits_2"}

class MK200ModbusRequestFile (CodeFile):
    CODEFILE_NAME = "mk201Config"
    SECTIONS_NAMES = [ "includes", "globals", "initFunction", "cleanUpFunction",
            "retrieveFunction", "publishFunction"]

    EditorType = MK200ModbusRequestEditor

    def GetVariableLocationHoldings(self):
        """Получить дерево переменных для холдингов"""
        variableTree = {"name": "Holdings", "type": LOCATION_GROUP,
                "location": "0", "children": []}
        iecChannel = self.GetFullIEC_Channel()[:1]
        variables = self.GetVariables()
        for i, j in zip(variables, range(0, len(variables))):
            if i["Modbus type"] != "Holding" or int(i["Len"]) > 1:
                continue
            if i["Data type"] in ("REAL", "INT"):
                locationType = "D"
                size = "D"
            else:
                locationType = "W"
                size = "W"
            variableTree["children"].append({
                'children':[],
                'var_name': i["Name"],
                'IEC_type': i["Data type"],
                'name': i["Name"],
                'description': '',
                'type': LOCATION_VAR_MEMORY,
                'location': "%Q"+locationType+iecChannel+".0.{}".format(j),
                'size':  size})
        return variableTree

    def GetVariableLocationTree(self):
        children = []
        iecChannel = self.GetFullIEC_Channel()[:1]
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
                          "Modbus type"     : var.getopts(),
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
        return "CFile"

    def CodeFileName(self):
        return os.path.join(self.CTNPath(), "mk201Config.xml")

    def GetPortConfig(self):
        configVariables = [i for i in self.GetVariables() if i["Description"] == "Port configuration"]
        config = {}
        if len(configVariables) != 5:
            config = copy.copy(DEFAULT_CONFIG)
            config["COM PORT"] = int(config["COM PORT"][-1])
            config["PARITY"] = PARITY_DIC[config["PARITY"]]
            return config
        for variable in configVariables:
            optValue = variable["Modbus type"]
            if variable["Name"] == "Port selection":
                config["COM PORT"] = int(optValue[-1])
            elif variable["Name"] == "Baudrate":
                config["BAUD"] = variable["Modbus type"]
            elif variable["Name"] == "Data bits":
                config["DATA BITS"] = DATALEN_DIC[variable["Modbus type"]]
            elif variable["Name"] == "Parity":
                config["PARITY"] = PARITY_DIC[variable["Modbus type"]]
            elif variable["Name"] == "Stopbits":
                config["STOPBITS"] = STOPBITS_DIC[variable["Modbus type"]]
        return config

    def GenerateVariblePrototypes(self):
        text = ""
        alreadyCreatedTypes = []
        requests = [i for i in self.GetVariables() if i["Description"] == "Modus master request data"]
        for request in requests:
            varName = request["Name"]
            varName = varName.upper()
            len = int(request["Len"])
            varType = request["Data type"]
            if len > 1:
                newType = "__DECLARE_ARRAY_TYPE(__ARRAY_OF_{0}_{1},{2},[{3}]);\n".format(varType, len, varType, len)
                if newType not in alreadyCreatedTypes:
                    text += newType
                    alreadyCreatedTypes.append(newType)
                text += "__DECLARE_GLOBAL_PROTOTYPE(__ARRAY_OF_{0}_{1},{2});\n\n".format(varType, len, varName)
            else:
                text += "__DECLARE_GLOBAL_PROTOTYPE({0},{1});\n".format(varType, varName)
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
        iecChannel = self.GetFullIEC_Channel()[:1]
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
        return requestStruct

    def CTNGenerate_C(self, buildpath, locations):
        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))
        text = "#include \"MbMasterTypes.h\"\n\n"
        text += "#include \"accessor.h\"\n"
        text += "#include \"iec_std_lib.h\"\n"
        text += "\n"

        text += "#define USART_WordLength_8b ((u16)0x0000)\n"
        text += "#define USART_WordLength_9b ((u16)0x1000)\n"
        text += "#define USART_StopBits_1 ((u16)0x0000)\n"
        text += "#define USART_StopBits_0_5 ((u16)0x1000)\n"
        text += "#define USART_StopBits_2 ((u16)0x2000)\n"
        text += "#define USART_StopBits_1_5 ((u16)0x3000)\n"
        text += "#define USART_Parity_No ((u16)0x0000)\n"
        text += "#define USART_Parity_Even ((u16)0x0400)\n"
        text += "#define USART_Parity_Odd ((u16)0x0600)\n\n"

        config = self.GetPortConfig()
        comMbMasterInit = "com{}MbMasterInit".format(config["COM PORT"])
        text += "extern void " + comMbMasterInit + "(u32 baud, u16 stopBits, u16 parity, u16 dataBits);\n\n"
        comMbAddRequest = "comPort{}AddRequest".format(config["COM PORT"])
        text += "extern void " + comMbAddRequest + "(RequestType * request);\n\n"

        text += self.GenerateVariblePrototypes()
        #text += "#include \"config.h\"\n\n"

        text += self.GenerateRequestSturcts()

        text += "int __init_%s(int argc,char **argv)\n{\n"%location_str
        baud = config["BAUD"]
        dataBits = config["DATA BITS"]
        parity = config["PARITY"]
        stopBits = config["STOPBITS"]
        text += "\t" + comMbMasterInit + "({0},{1},{2},{3});\n".format(baud,stopBits,parity,dataBits)

        requests = [i for i in self.GetVariables() if i["Description"] == "Modus master request data"]
        for request in requests:
            text += "\tcomPort{0}AddRequest(&req_{1});\n".format(config["COM PORT"], request["Name"])

        text += "\treturn 0;\n}\n\n"

        text += "void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "void __retrieve_%s(void)\n{\n"%location_str
        text += "   ;\n"
        text += "\n}\n\n"

        text += "void __publish_%s(void)\n{\n"%location_str
        text += "\n"
        text += "\n}\n\n"

        Gen_Cfile_path = os.path.join(buildpath, "mk200mbReq%s.c"%location_str)
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

