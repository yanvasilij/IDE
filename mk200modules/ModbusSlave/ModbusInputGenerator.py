#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Генератор кода для input'ов
@Author Vasilij
"""
from ModbusInputRegisterEditor import DESCRIPTION
from CodeGenerationCommon import *

INIT_FUNCTION_NAME = "initInputMap"
INPUT_REGISTER_MAP = "inputsMap"

INPUT_REGISTER_CALL_BACK = """
static eMBErrorCode """+INPUT_REGISTER_CALL_BACK_NAME+"""( UCHAR * pucRegBuffer, USHORT usAddress, USHORT usNRegs)
{
    USHORT value;
    ULONG i;
    for (i = usAddress; i < usAddress + usNRegs; i++)
    {
        if ( getRegister(i, &value, """ + INPUT_REGISTER_MAP + """,%d) == 1 )

        {
            *(pucRegBuffer++) = (value>>8) & 0xFF;
            *(pucRegBuffer++) = value & 0xFF;
        }
        else
            return MB_ENOREG;
    }
    return MB_ENOERR;
}
"""


class ModbusInputGenerator:
    def __init__(self, Controler):
        self.Controler = Controler
        self.Description = DESCRIPTION

    def GenerateMap(self):
        variables = [var for var in self.Controler.GetVariables() if var["Description"] == self.Description]
        numOfVars = len(variables)
        text = ""
        text += "#define INPUTS_ENTRY_NUMS {} /**< @brief num of entries in input register map */\n".format(numOfVars)
        text += "static ModbusRegisterType {}[INPUTS_ENTRY_NUMS];\n\n".format(INPUT_REGISTER_MAP)
        text += "/**\n * @brief initialization modbus input register map\n */\n"
        text += "static void {} (void)\n".format(INIT_FUNCTION_NAME)
        text += "{\n"
        for var, i in zip(variables, range(0, numOfVars)):
            text += "\t" + INPUT_REGISTER_MAP + "[{0}].adr = {1};\n".format(i, var["Address"])
            typeLen = TYPE_LEN[var["Type"]]
            text += "\t" + INPUT_REGISTER_MAP + "[{0}].typeLen = {1};\n".format(i, typeLen)
            arrayLen = int(var["Len"])
            varName = var["Name"]
            varName = varName.upper()
            if arrayLen > 1:
                text += "\t" + INPUT_REGISTER_MAP + "[{0}].isArray = 1;\n".format(i)
                text += "\t" + INPUT_REGISTER_MAP + "[{0}].arrayLen = {1};\n".format(i, arrayLen)
                text += "\t" + INPUT_REGISTER_MAP + "[{0}].data = __GET_GLOBAL_{1}()->table;\n".format(i, varName)
            else:
                text += "\t" + INPUT_REGISTER_MAP + "[{0}].isArray = 0;\n".format(i)
                text += "\t" + INPUT_REGISTER_MAP + "[{0}].arrayLen = 0;\n".format(i)
                text += "\t" + INPUT_REGISTER_MAP + "[{0}].data = __GET_GLOBAL_{1}();\n".format(i, varName)
        text += "}\n\n"
        return text

    def GenerateInit(self):
        text = "\t{}();\n".format(INIT_FUNCTION_NAME)
        return text

    def GenerateHandler(self):
        variables = [var for var in self.Controler.GetVariables() if var["Description"] == self.Description]
        numOfVars = len(variables)
        text = ""
        text += "/**\n * @brief Input registers processing callback\n */\n"
        text += INPUT_REGISTER_CALL_BACK % (numOfVars)
        return text

