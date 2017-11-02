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
                          "Period (ms)" : var.getperiod(),
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
            self.CodeFile.variables.appendvariable(variable)

    def GetIconName(self):
        return "CFile"

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
                    requestStruct += "\t\tif ( data[j] & (1<<offset) )\n".format(varName)
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
            requestStruct += "\t100,\n"
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
        text = "extern \"C\" void __publish_%s(void)\n{\n"%location_str
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
        text = "extern \"C\" void __retrieve_%s(void)\n{\n"%location_str
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
        text += "#include \"FreeRTOS.h\"\n"
        text += "#include \"task.h\"\n"
        text += "#include \"semphr.h\"\n\n"

        """ Mutex for protect frome simultanios data acces from user app and form modbus """
        text += "static SemaphoreHandle_t dataAccessMutex;\n"

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

        text += "\tdataAccessMutex = xSemaphoreCreateMutex();\n"
        requests = [i for i in self.GetVariables() if i["Description"] == "Modus master request data"]
        for request in requests:
            text += "\tmbSocket.addRequest(&req_{0});\n".format(request["Name"])
            text += "\tif(req_{0}.ciclic)\n".format(request["Name"])
            text += "\t\treq_{0}.run = 1;\n".format(request["Name"])
            text += "\treq_{0}.status = MBRequestSuccesfulyDone;\n".format(request["Name"])
            text += "\treq_{0}.error = MBNotProcessingYet;\n".format(request["Name"])
            request_data_len = int(request["Len"]) * 2
            text += "\tmemset({0}_publishBuf, 0, {1});\n".format(request["Name"], request_data_len)
            text += "\tmemset({0}_retriveBuf, 0, {1});\n".format(request["Name"], request_data_len)

        text += "\n\txTaskCreate(mbTcpMasterSocketTask, \"mbTcpMasterSocketTask\", " \
                "configMINIMAL_STACK_SIZE*5, NULL, 2, NULL);\n"

        text += "\treturn 0;\n}\n\n"

        text += "extern \"C\" void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += self.GenerateRetriveFunction(location_str, requests)

        text += self.GeneratePublishFunction(location_str, requests)

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

