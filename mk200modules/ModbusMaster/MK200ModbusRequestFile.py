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
from MBRequestDataPanel import MASTER_OPTION
import copy

CodeFile = CodeFileTreeNode.CodeFile

DATALEN_DIC = {"8": "USART_WordLength_8b", "9": "USART_WordLength_9b"}
PARITY_DIC = {"none": "USART_Parity_No", "even": "USART_Parity_Even", "odd":"USART_Parity_Odd"}
STOPBITS_DIC = {"1": "USART_StopBits_1", "0.5":"USART_StopBits_0_5", "1.5":"USART_StopBits_1_5", "2":"USART_StopBits_2"}

class MK200ModbusRequestFile (CodeFile):
    CODEFILE_NAME = "mk201Config"
    SECTIONS_NAMES = [ "includes", "globals", "initFunction", "cleanUpFunction",
            "retrieveFunction", "publishFunction"]

    EditorType = MK200ModbusRequestEditor

    def __init__(self):
        old_xsd = CodeFileTreeNode.CODEFILE_XSD
        CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
        CodeFile.__init__(self)
        CodeFileTreeNode.CODEFILE_XSD = old_xsd

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
            if var.gettimeout() == "":
                timeOut = var.getperiod()
            else:
                timeOut = var.gettimeout()
            datas.append({"Name" : var.getname(),
                          "Data type" : var.gettype(),
                          "Device ID" : var.getdevid(),
                          "Description" : var.getdesc(),
                          "OnChange"    : var.getonchange(),
                          "Modbus type"     : var.getopts(),
                          "Address" : var.getaddress(),
                          "Len" : var.getlen(),
                          "Transfer method" : var.gettxtype(),
                          "Period (ms)" : var.getperiod(),
                          "Timeout (ms)" : timeOut,
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
            variable.setperiod(var["Period (ms)"])
            variable.settimeout(var["Timeout (ms)"])
            self.CodeFile.variables.appendvariable(variable)

    def GetIconName(self):
        return "Cfile"

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

    def GenerateVariblePrototypes(self, requests):
        text = ""
        alreadyCreatedTypes = []
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

    def GenerateRequestSturcts(self, requests):
        """
        Generates structures with modbus request information
        that should be to pass to modbus master object
        :return: tuple with two elements. First string with sturctes that should be generate,
        second prototypes of this structures for header file
        """
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
        iecChannel = self.GetFullIEC_Channel()[:1]
        for request, i in zip(requests, range(0, len(requests))):
            varName = request["Name"]
            varName = varName.upper()

            """ Buffers for protected read befor and after user cycle """
            publish_buffer_name = "{0}_publishBuf".format(request["Name"])
            retrive_buffer_name = "{0}_retriveBuf".format(request["Name"])
            requestStruct += "static u16 {0}[{1}] __attribute__((section(\"._sdram\")));\n".format(publish_buffer_name, request["Len"])
            requestStruct += "static u16 {0}[{1}] __attribute__((section(\"._sdram\")));\n".format(retrive_buffer_name, request["Len"])

            """ Callbask for accessing data """
            requestStruct += "void "+request["Name"]+"_reqGetHandler (u16 * data)\n{\n"
            requestStruct += "\tu32 i,j;\n"
            if request["Data type"] == "BOOL":
                if int(request["Len"]) == 1:
                    requestStruct + "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                    requestStruct += "\tdata[0] = 0;\n"
                    requestStruct += "\tif ({0}[0])\n".format(publish_buffer_name)
                    requestStruct += "\t\tdata[0] |= (1<<0);\n"
                    requestStruct += "\txSemaphoreGive(dataAccessMutex);\n"
                else:
                    requestStruct + "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                    requestStruct += "\tfor(i=0, j=0; i<{}; i++, j=i/16)\n".format(request["Len"])
                    requestStruct += "\t\tdata[j] = 0;\n"
                    requestStruct += "\tfor(i=0, j=0; i<{}; i++, j=i/16)\n".format(request["Len"])
                    requestStruct += "\t{\n"
                    requestStruct += "\t\tu8 offset = i%16;\n"
                    requestStruct += "\t\tif ( {}[i] )\n".format(publish_buffer_name)
                    requestStruct += "\t\t\tdata[j] |= (1<<offset);\n"
                    requestStruct += "\t}\n"
                    requestStruct += "\txSemaphoreGive(dataAccessMutex);\n"
            else:
                if int(request["Len"]) == 1:
                    requestStruct += "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                    requestStruct += "\tdata[0] = {}[0];\n".format(publish_buffer_name)
                    requestStruct += "\txSemaphoreGive(dataAccessMutex);\n"
                else:
                    requestStruct += "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                    requestStruct += "\tfor (i=0; i<{}; i++)\n".format(request["Len"])
                    requestStruct += "\t{\n"
                    requestStruct += "\t\tdata[i] = {}[i];\n".format(publish_buffer_name)
                    requestStruct += "\t}\n"
                    requestStruct += "\txSemaphoreGive(dataAccessMutex);\n"
            requestStruct += "};\n\n"

            requestStruct += "void "+request["Name"]+"_reqSetHandler (u16 * data) \n{\n\n"
            requestStruct += "\tu32 i,j;\n"
            if request["Data type"] == "BOOL":
                if int(request["Len"]) == 1:
                    requestStruct += "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                    requestStruct += "\tif (data[0] & 1)\n".format(varName)
                    requestStruct += "\t\t{}[0] = 1;\n".format(retrive_buffer_name)
                    requestStruct += "\telse\n"
                    requestStruct += "\t\t{}[0] = 0;\n".format(retrive_buffer_name)
                    requestStruct += "\txSemaphoreGive(dataAccessMutex);\n"
                else:
                    requestStruct += "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                    requestStruct += "\tfor(i=0, j=0; i<{}; i++, j=i/16)\n".format(request["Len"])
                    requestStruct += "\t{\n"
                    requestStruct += "\t\tu8 offset = i%16;\n"
                    requestStruct += "\t\tif ( data[j] & (1<<offset) )\n"
                    requestStruct += "\t\t\t{}[i] = 1;\n".format(retrive_buffer_name)
                    requestStruct += "\t\telse\n"
                    requestStruct += "\t\t\t{}[i] = 0;\n".format(retrive_buffer_name)
                    requestStruct += "\t}\n"
                    requestStruct += "\txSemaphoreGive(dataAccessMutex);\n"
            else:
                if int(request["Len"]) == 1:
                    requestStruct += "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                    requestStruct += "\t{}[0] = data[0];\n".format(retrive_buffer_name)
                    requestStruct += "\txSemaphoreGive(dataAccessMutex);\n"
                else:
                    requestStruct += "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                    requestStruct += "\tfor (i=0; i<{}; i++)\n".format(request["Len"])
                    requestStruct += "\t{\n"
                    requestStruct += "\t\t{}[i] = data[i];\n".format(retrive_buffer_name)
                    requestStruct += "\t}\n"
                    requestStruct += "\txSemaphoreGive(dataAccessMutex);\n"
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
            requestStruct += "\t{},\n".format(request["Timeout (ms)"])
            requestStruct += "\t{},\n".format(request["Device ID"])
            requestStruct += "\t0,\n"
            requestStruct += "\t{},\n".format(request["Period (ms)"])
            requestStruct += "\t{},\n".format(request["Address"])
            requestStruct += "\t{},\n".format(request["Len"])
            requestStruct += "\t{}_reqGetHandler,\n".format(request["Name"])
            requestStruct += "\t{}_reqSetHandler\n".format(request["Name"])
            requestStruct += "};\n\n"
            requestStruct += "static u16 req_{0}_status;\n".format(request["Name"])
            requestStruct += "static u16 req_{0}_err;\n".format(request["Name"])
            requestStruct += "void *__QX{0}_{1}_{2} = &req_{3}.run;\n".format(iecChannel, i, 0, request["Name"])
            requestStruct += "void *__QW{0}_{1}_{2} = &req_{3}_status;\n".format(iecChannel, i, 1, request["Name"])
            requestStruct += "void *__QW{0}_{1}_{2} = &req_{3}_err;\n".format(iecChannel, i, 2, request["Name"])
            requestStruct += "\n"
        return requestStruct, prototypes

    def GeneratePublishFunction(self, location_str, requests):
        text = "void __publish_%s(void)\n{\n"%location_str
        text += "\tu32 i;\n"
        for request in requests:
            publish_buffer_name = "{0}_publishBuf".format(request["Name"])
            varName = request["Name"]
            varName = varName.upper()
            if int(request["Len"]) == 1:
                text += "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                text += "\t{0}[0] = *__GET_GLOBAL_{1}();\n\n".format(publish_buffer_name, varName)
                text += "\txSemaphoreGive(dataAccessMutex);\n"
            else:
                text += "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                text += "\tfor (i=0; i<{}; i++)\n".format(request["Len"])
                text += "\t{\n"
                text += "\t\t{0}[i] = __GET_GLOBAL_{1}()->table[i];\n".format(publish_buffer_name, varName)
                text += "\t}\n\n"
                text += "\txSemaphoreGive(dataAccessMutex);\n"
            text += "\treq_{0}_status = req_{0}.status;\n\n".format(request["Name"])
            text += "\treq_{0}_err = req_{0}.error;\n\n".format(request["Name"])
        text += "\n}\n\n"
        return text

    def GenerateRetriveFunction(self, location_str, requests):
        text = "void __retrieve_%s(void)\n{\n"%location_str
        text += "\tu32 i;\n"
        for request in requests:
            retrive_buffer_name = "{0}_retriveBuf".format(request["Name"])
            varName = request["Name"]
            varName = varName.upper()
            if int(request["Len"]) == 1:
                text += "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                text += "\t*__GET_GLOBAL_{0}() = {1}[0];\n\n".format(varName, retrive_buffer_name)
                text += "\txSemaphoreGive(dataAccessMutex);\n"
            else:
                text += "\txSemaphoreTake(dataAccessMutex, portMAX_DELAY);\n"
                text += "\tfor (i=0; i<{}; i++)\n".format(request["Len"])
                text += "\t{\n"
                text += "\t\t__GET_GLOBAL_{0}()->table[i] = {1}[i];\n".format(varName, retrive_buffer_name)
                text += "\t}\n\n"
                text += "\txSemaphoreGive(dataAccessMutex);\n"
        text += "\n}\n\n"
        return text

    def CTNGenerate_C(self, buildpath, locations):
        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))

        """ list of requestes created by user """
        requests = [i for i in self.GetVariables() if i["Description"] == "Modus master request data"]

        """Here creats file for C-extension usage"""
        modbusAccesorHeaderText = "#include \"MbMasterTypes.h\"\n\n"
        modbusAccesorHeaderText += "#include \"accessor.h\"\n"
        modbusAccesorHeaderText += "#include \"iec_std_lib.h\"\n"
        modbusAccesorHeaderText += "\n"
        modbusAccesorHeaderText += self.GenerateVariblePrototypes(requests)
        masterNum = [i for i in self.GetVariables() if i["Description"] == MASTER_OPTION]
        if len(masterNum) == 0:
            masterNum = 0
        else:
            masterNum = int(masterNum[0]["Modbus type"][-1])
        modbusAccesorHeaderName = "MK200ModbusRequest_%s.h"%location_str
        modbusAccesorHeader = os.path.join(buildpath, modbusAccesorHeaderName)
        mbsAccHdrFile = open(modbusAccesorHeader,'w')
        mbsAccHdrFile.write(modbusAccesorHeaderText)
        """Include this header to .c file"""
        text = "#include \"%s\"\n\n"%modbusAccesorHeaderName
        text += "#include \"FreeRTOS.h\"\n"
        text += "#include \"task.h\"\n"
        text += "#include \"semphr.h\"\n"

        """ Mutex for protect frome simultanios data acces from user app and form modbus """
        text += "static SemaphoreHandle_t dataAccessMutex;\n"

        structurest, prototypes = self.GenerateRequestSturcts(requests)

        """ Add structrure prototypes to header file """
        mbsAccHdrFile.write(prototypes)
        mbsAccHdrFile.close()

        text += structurest

        text += "int __init_%s(int argc,char **argv)\n{\n"%location_str

        requests = [i for i in self.GetVariables() if i["Description"] == "Modus master request data"]
        text += "\tdataAccessMutex = xSemaphoreCreateMutex();\n"
        for request in requests:
            text += "\tmodbusMasterAddRequest({0}, &req_{1});\n".format(masterNum, request["Name"])
            text += "\tif(req_{0}.ciclic)\n".format(request["Name"])
            text += "\t\treq_{0}.run = 1;\n".format(request["Name"])
            text += "\treq_{0}.status = MBRequestSuccesfulyDone;\n".format(request["Name"])
            text += "\treq_{0}.error = MBNotProcessingYet;\n".format(request["Name"])
            request_data_len = int(request["Len"]) * 2
            text += "\tmemset({0}_publishBuf, 0, {1});\n".format(request["Name"], request_data_len)
            text += "\tmemset({0}_retriveBuf, 0, {1});\n".format(request["Name"], request_data_len)

        text += "\treturn 0;\n}\n\n"

        text += "void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += self.GenerateRetriveFunction(location_str, requests)

        text += self.GeneratePublishFunction(location_str, requests)

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

