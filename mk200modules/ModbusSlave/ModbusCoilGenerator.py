#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Кодогенерация Coil'ов
@Author Vasilij
"""

from ModbusCoilEditor import DESCRIPTION
from CodeGenerationCommon import *

INIT_FUNCTION_NAME = "initCoilMap"
COIL_MAP = "coilMap"

COIL_CALL_BACK = """
static eMBErrorCode """+COIL_CALL_BACK_NAME+"""( UCHAR * pucRegBuffer, USHORT usAddress, USHORT usNRegs, eMBRegisterMode eMode)
{
    UCHAR value;
    ULONG i, j=0;
    if (eMode==MB_REG_READ)
    {
        for (i = usAddress; i < usAddress + usNRegs; i++)
        {
            if ( getDiscrete(i, &value, """ + COIL_MAP + """,%d) == 1 )

            {
                if (value) value = 1;
                *(pucRegBuffer) &= ~(1<<j);
                *(pucRegBuffer) |= (value<<j);
                j++;
                if (j==8)
                {
                    pucRegBuffer++;
                    j=0;
                }
            }
            else
                return MB_ENOREG;
        }
    }
    else
    {
        for (i = usAddress; i < usAddress + usNRegs; i++)
        {
            if ( *(pucRegBuffer) & (1<<j) ) value = 1;
            else value = 0;
            if (setDiscrete(usAddress, &value, """+COIL_MAP+""", %d) != 1)
                return MB_ENOREG;
            j++;
            if (j==8)
            {
                pucRegBuffer++;
                j=0;
            }
        }
    }
    return MB_ENOERR;
}
"""

class ModbusCoilGenerator:
    def __init__(self, Controler):
        self.Controler = Controler
        self.Description = DESCRIPTION

    def GenerateMap(self):
        variables = [var for var in self.Controler.GetVariables() if var["Description"] == self.Description]
        numOfVars = len(variables)
        text = ""
        text += "#define COIL_ENTRY_NUMS {} /**< @brief num of entries in coil map */\n".format(numOfVars)
        text += "static ModbusDiscreteType {}[COIL_ENTRY_NUMS];\n\n".format(COIL_MAP)
        text += "/**\n * @brief initialization modbus coil map\n */"
        text += "static void {} (void)\n".format(INIT_FUNCTION_NAME)
        text += "{\n"
        for var, i in zip(variables, range(0, numOfVars)):
            text += "\t" + COIL_MAP + "[{0}].adr = {1};\n".format(i, var["Address"])
            arrayLen = int(var["Len"])
            varName = var["Name"]
            varName = varName.upper()
            if arrayLen > 1:
                text += "\t" + COIL_MAP + "[{0}].isArray = 1;\n".format(i)
                text += "\t" + COIL_MAP + "[{0}].arrayLen = {1};\n".format(i, arrayLen)
                text += "\t" + COIL_MAP + "[{0}].data = __GET_GLOBAL_{1}()->table;\n".format(i, varName)
            else:
                text += "\t" + COIL_MAP + "[{0}].isArray = 0;\n".format(i)
                text += "\t" + COIL_MAP + "[{0}].arrayLen = 0;\n".format(i)
                text += "\t" + COIL_MAP + "[{0}].data = __GET_GLOBAL_{1}();\n".format(i, varName)
        text += "}\n\n"
        return text

    def GenerateInit(self):
        text = "\t{}();\n".format(INIT_FUNCTION_NAME)
        return text

    def GenerateHandler(self):
        variables = [var for var in self.Controler.GetVariables() if var["Description"] == self.Description]
        numOfVars = len(variables)
        text = ""
        text += "/**\n * @brief Coils processing callback\n */\n"
        text += COIL_CALL_BACK % (numOfVars, numOfVars)
        return text


