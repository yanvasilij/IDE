#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Генератор кода modbus slave, общие моменты
@Author Vasilij
"""


from ModbusHoldingRegisterEditor import DESCRIPTION as MODDBUS_HOLDING_DESC
from ModbusDiscEditor import DESCRIPTION as MODBUS_DISC_DESC
from ModbusCoilEditor import DESCRIPTION as MODBUS_COIL_DESC
from ModbusInputRegisterEditor import DESCRIPTION as MODBUS_INPUT_DESC
from ModbusPortEditor import DESCRIPTION as MODBUS_PORT_DESC
from ModbusHoldingGenerator import ModbusHoldingGenerator
from ModbusInputGenerator import ModbusInputGenerator
from ModbusCoilGenerator import ModbusCoilGenerator
from ModbusDiscGenerator import ModbusDiscGenerator
from ModbusTcpGenerator import ModbusTcpGenerator
from CodeGenerationCommon import *


class CodeGenerator:

    def __init__(self, controler):
        self.Controler = controler
        self.HoldingGenerator = ModbusHoldingGenerator(controler)
        self.InputGenerator = ModbusInputGenerator(controler)
        self.CoilGenerator = ModbusCoilGenerator(controler)
        self.DiscGenerator = ModbusDiscGenerator(controler)
        self.MbTcpGenerator = ModbusTcpGenerator(controler)

    def GenerateVariblePrototypes(self):
        text = ""
        alreadyCreatedTypes = []
        variables = [i for i in self.Controler.GetVariables() if i["Description"]
                     in (MODDBUS_HOLDING_DESC, MODBUS_COIL_DESC, MODBUS_DISC_DESC, MODBUS_INPUT_DESC)]
        for var in variables:
            varName = var["Name"]
            varName = varName.upper()
            len = int(var["Len"])
            varType = var["Type"]
            if len > 1:
                newType = "__DECLARE_ARRAY_TYPE(__ARRAY_OF_{0}_{1},{2},[{3}]);\n" \
                    .format(varType, len, varType, len)
                if newType not in alreadyCreatedTypes:
                    text += newType
                    alreadyCreatedTypes.append(newType)
                text += "__DECLARE_GLOBAL_PROTOTYPE(__ARRAY_OF_{0}_{1},{2});\n\n" \
                    .format(varType, len, varName)
            else:
                text += "__DECLARE_GLOBAL_PROTOTYPE({0},{1});\n".format(varType, varName)
        return text

    def GenerateCode(self):
        text = ""
        text += INCLUDES
        text += EXTERNS
        text += CDIV.replace("text", "Types")
        text += TYPES
        text += CDIV.replace("text", "Vars")
        text += self.GenerateVariblePrototypes()
        text += CDIV.replace("text", "static functions")
        text += GET_REGISTER_FUNCTION
        text += SET_REGISTER_FUNCTION
        text += GET_DISCRETE_FUNCTION
        text += SET_DISCRETE_FUNCTION
        text += self.HoldingGenerator.GenerateMap()
        text += self.HoldingGenerator.GenerateHandler()
        text += self.InputGenerator.GenerateMap()
        text += self.InputGenerator.GenerateHandler()
        text += self.CoilGenerator.GenerateMap()
        text += self.CoilGenerator.GenerateHandler()
        text += self.DiscGenerator.GenerateMap()
        text += self.DiscGenerator.GenerateHandler()
        return text

    def GeneratePortInit(self):
        ports = self.Controler.GetVariables()
        ports = [i for i in ports if i["Description"] == MODBUS_PORT_DESC]
        text = ""
        for port in ports:
            adr = port["Address"]
            comPort = port["Options"]
            dataBits = port["Len"]
            parity = PARITY_INIT_VALUE[port["Parity"]]
            stopBits = port["Id"]
            baudrate = port["Baudrate"]
            text += "\t" + INIT_COM_PORT[comPort] + "("
            text += INPUT_REGISTER_CALL_BACK_NAME + ","
            text += HOLDING_REGISTER_CALL_BACK_NAME + ","
            text += COIL_CALL_BACK_NAME + ","
            text += DISC_CALL_BACK_NAME + ","
            text += adr + ","
            text += baudrate + ","
            text += dataBits + ","
            text += parity + ","
            text += stopBits + ");\n"
        return text

    def GeneretaInit(self):
        text = ""
        #text += self.HoldingGenerator.GenerateInit()
        #text += self.InputGenerator.GenerateInit()
        #text += self.CoilGenerator.GenerateInit()
        #text += self.DiscGenerator.GenerateInit()
        #text += self.MbTcpGenerator.GenerateInit()
        #text += self.GeneratePortInit()
        text +=  "\treturn 0;\n"
        return text

