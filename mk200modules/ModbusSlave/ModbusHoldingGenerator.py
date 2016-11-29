#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Генератор кода для holding'ов
@Author Vasilij
"""
from ModbusHoldingRegisterEditor import DESCRIPTION
from CodeGenerationCommon import *

INIT_FUNCTION_NAME = "initHoldingsMap"
HOLDING_MAP = "holdingsMap"

HOLDING_REGISTER_CALL_BACK = """
static eMBErrorCode """+HOLDING_REGISTER_CALL_BACK_NAME+"""( UCHAR * pucRegBuffer, USHORT usAddress,
		USHORT usNRegs, eMBRegisterMode eMode )
{
	USHORT value;
	ULONG i;
    DEBUG_LOG(("->get holdings: adr - %%d, len %%d, mode %%d", (int)usAddress, (int)usNRegs, (int)eMode));
	if (eMode == MB_REG_READ)
	{
		for (i = usAddress; i < usAddress + usNRegs; i++)
		{
            DEBUG_LOG((" get usAdress %%d", (int)i));
			if ( getRegister(i, &value, """+HOLDING_MAP+""",%d) == 1 )

			{
				*(pucRegBuffer++) = (value>>8) & 0xFF;
				*(pucRegBuffer++) = value & 0xFF;
			}
			else
			{
                DEBUG_LOG(("no reg \\r\\n"));
				return MB_ENOREG;
			}
		}
        DEBUG_LOG(("\\r\\n"));
		return MB_ENOERR;
	}
	else
	{
		for (i = usAddress; i < usAddress + usNRegs; i++)
		{
			value = 0;
			value = (*pucRegBuffer++)<<8;
			value |= *pucRegBuffer++;
			if ( setRegister(i, &value, """+HOLDING_MAP+""", %d) != 1 )
			{
				return MB_ENOREG;
			}
		}
		return MB_ENOERR;
	}
}
"""

class ModbusHoldingGenerator:
    def __init__(self, Controler):
        self.Controler = Controler
        self.Description = DESCRIPTION

    def GenerateMap(self):
        variables = [var for var in self.Controler.GetVariables() if var["Description"] == self.Description]
        numOfVars = len(variables)
        text = ""
        text += "#define HOLDING_ENTRY_NUMS {} /**< @brief num of entries in holding register map */\n".format(numOfVars)
        text += "static ModbusRegisterType holdingsMap[HOLDING_ENTRY_NUMS];\n\n"
        text += "/**\n * @brief initialization modbus holding register map\n */\n"
        text += "static void {} (void)\n".format(INIT_FUNCTION_NAME)
        text += "{\n"
        for var, i in zip(variables, range(0, numOfVars)):
            text += "\t"+HOLDING_MAP+"[{0}].adr = {1};\n".format(i, var["Address"])
            typeLen = TYPE_LEN[var["Type"]]
            text += "\t"+HOLDING_MAP+"[{0}].typeLen = {1};\n".format(i, typeLen)
            arrayLen = int (var["Len"])
            varName = var["Name"]
            varName = varName.upper()
            if arrayLen > 1:
                text += "\t"+HOLDING_MAP+"[{0}].isArray = 1;\n".format(i)
                text += "\t"+HOLDING_MAP+"[{0}].arrayLen = {1};\n".format(i, arrayLen)
                text += "\t"+HOLDING_MAP+"[{0}].data = __GET_GLOBAL_{1}()->table;\n".format(i, varName)
            else:
                text += "\t"+HOLDING_MAP+"[{0}].isArray = 0;\n".format(i)
                text += "\t"+HOLDING_MAP+"[{0}].arrayLen = 0;\n".format(i)
                text += "\t"+HOLDING_MAP+"[{0}].data = __GET_GLOBAL_{1}();\n".format(i, varName)
        text += "}\n\n"
        return text

    def GenerateInit(self):
        text = "{}();\n".format(INIT_FUNCTION_NAME)
        return text

    def GenerateHandler(self):
        variables = [var for var in self.Controler.GetVariables() if var["Description"] == self.Description]
        numOfVars = len(variables)
        text = ""
        text += "/**\n * @brief Holding registers processing callback\n */\n"
        text += HOLDING_REGISTER_CALL_BACK % (numOfVars, numOfVars)
        return text

