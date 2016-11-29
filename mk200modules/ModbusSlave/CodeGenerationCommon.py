#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Общие определения для кодогенерации
@Author Vasilij
"""
CDIV = """
/**********************************************************************************
*				text
**********************************************************************************/
"""

TYPE_LEN = {"SINT":4, "INT":4, "DINT":4, "LINT":4, "USINT":4, "UINT":4, "UDINT":4,
            "ULINT":4, "REAL":4, "LREAL":8, "WORD":2, "DWORD":4, "LWORD":8}

INCLUDES = """

#include "accessor.h"
#include "iec_std_lib.h"
#include "mbport.h"

#define DEBUG

#ifdef DEBUG
#include "stdio.h"
#define DEBUG_LOG(x) printf x
#else
#define DEBUG_LOG(x)
#endif

"""

EXTERNS = """
extern void com1MbSlaveInit ( void * eMBRegInputCB, void * eMBRegHoldingCB,
		void * eMBRegCoilsCB, void * eMBRegDiscreteCB,
		USHORT adr, ULONG baudrate, UCHAR dataBits, eMBParity parity, UCHAR stopBits);

extern void com2MbSlaveInit ( void * eMBRegInputCB, void * eMBRegHoldingCB,
		void * eMBRegCoilsCB, void * eMBRegDiscreteCB,
		USHORT adr, ULONG baudrate, UCHAR dataBits, eMBParity parity, UCHAR stopBits);

extern void com3MbSlaveInit ( void * eMBRegInputCB, void * eMBRegHoldingCB,
		void * eMBRegCoilsCB, void * eMBRegDiscreteCB,
		USHORT adr, ULONG baudrate, UCHAR dataBits, eMBParity parity, UCHAR stopBits);

extern void initModbusTcpTask (void * eMBRegInputCB, void * eMBRegHoldingCB,
		void * eMBRegCoilsCB, void * eMBRegDiscreteCB);

extern void initTcpProcess (uint8_t * ucIPAddress, uint8_t * ucNetMask,
	  uint8_t * ucGatewayAddress, uint8_t * ucDNSServerAddress);

"""


TYPES = """
/**
 * @brief Type for modbus data
 */
typedef struct
{
    USHORT adr; /**< @brief Data begin address */
    ULONG typeLen; /**< @brief Len of data type */
    UCHAR isArray; /**< @brief Is data is array */
    ULONG arrayLen; /**< @brief Len of array if isArray == 1 */
    void * data; /**< @brief pointer data */
}ModbusRegisterType;

/**
 * @brief Type for modbus data
 */
typedef struct
{
    USHORT adr; /**< @brief Data begin address */
    UCHAR isArray; /**< @brief Is data is array */
    ULONG arrayLen; /**< @brief Array len if isArray == 1 */
    void * data; /**< @brief pointer data */
}ModbusDiscreteType;
"""

GET_REGISTER_FUNCTION_NAME = "getRegister"
GET_REGISTER_FUNCTION = """
/**
 * @brief Get register (holding or input) value by address in register map (working with holdingMap[])
 * @param adr register address
 * @param pointer for data
 * @return 1 if register is exist, 0 - register doesn't exist
 */
static UCHAR """+GET_REGISTER_FUNCTION_NAME+"""(USHORT adr, USHORT * regValue, ModbusRegisterType * map, ULONG numOfRegisters)
{
    USHORT adrBegin, adrEnd;
    ULONG len, i;
    DEBUG_LOG(("->getRegister: adr - %d ", (int)adr));
    for (i = 0; i < numOfRegisters; i++)
    {
        adrBegin = map[i].adr;
        if (map[i].isArray)
        {
            len = map[i].arrayLen * map[i].typeLen / 2;
            if (len%2) len++;
        }
        else
        {
            len = map[i].typeLen / 2;
            if (len%2) len++;
        }
        adrEnd = adrBegin + len;
        if ( (adr>=adrBegin) && (adr<adrEnd) )
        {
            DEBUG_LOG(("src - %d <-", (int)*(int*)map[i].data));
            *regValue = (int)*(int*)map[i].data & 0xFFFF;
            DEBUG_LOG(("value - %d <-", (int)*regValue));
            return 1;
        }
    }
    DEBUG_LOG(("not found <-"));
    return 0;
}
"""

SET_REGISTER_FUNCTION_NAME = "setRegister"
SET_REGISTER_FUNCTION = """
/**
 * @brief Set register (holding) value by address in register map (working with holdingMap[])
 * @param adr register address
 * @param pointer for data
 * @return 1 if register is exist, 0 - register doesn't exist
 */
static UCHAR """+SET_REGISTER_FUNCTION_NAME+"""(USHORT adr, USHORT * regValue, ModbusRegisterType * map, ULONG numOfRegisters)
{
    USHORT adrBegin, adrEnd;
    ULONG len, i;
    for (i = 0; i < numOfRegisters; i++)
    {
        adrBegin = map[i].adr;
        if (map[i].isArray)
        {
            len = map[i].arrayLen * map[i].typeLen / 2;
            if (len%2) len++;
        }
        else
        {
            len = map[i].typeLen / 2;
            if (len%2) len++;
        }
        adrEnd = adrBegin + len;
        if ( (adr>=adrBegin) && (adr<adrEnd) )
        {
            USHORT * data;
            data = map[i].data;
            data[adr-adrBegin] = *regValue;
            return 1;
        }
    }
    return 0;
}
"""

GET_DISCRETE_FUNCTION_NAME = "getDiscrete"
GET_DISCRETE_FUNCTION = """
static UCHAR """+GET_DISCRETE_FUNCTION_NAME+"""(USHORT adr, UCHAR *value, ModbusDiscreteType *map, ULONG mapLen)
{
    USHORT adrBegin, adrEnd;
    ULONG i, len;
    for (i=0; i<mapLen; i++)
    {
        adrBegin = map[i].adr;
        if (map[i].isArray)
            adrEnd = adrBegin + map[i].arrayLen;
        else
            adrEnd = adrBegin + 1;
        if ( (adr >= adrBegin) && (adr < adrEnd) )
        {
            *value = ((UCHAR*)map[i].data)[adrBegin-adr];
            return 1;
        }
    }
    return 0;
}
"""

SET_DISCRETE_FUNCTION_NAME = "setDiscrete"
SET_DISCRETE_FUNCTION = """
static UCHAR """+SET_DISCRETE_FUNCTION_NAME+"""(USHORT adr, UCHAR *value, ModbusDiscreteType *map, ULONG mapLen)
{
    USHORT adrBegin, adrEnd;
    ULONG i, len;
    for (i=0; i<mapLen; i++)
    {
        adrBegin = map[i].adr;
        if (map[i].isArray)
            adrEnd = adrBegin + map[i].arrayLen;
        else
            adrEnd = adrBegin + 1;
        if ( (adr >= adrBegin) && (adr < adrEnd) )
        {
            ((UCHAR*)map[i].data)[adrBegin-adr] = *value;
            return 1;
        }
    }
    return 0;
}
"""

PARITY_INIT_VALUE = {"None": "MB_PAR_NONE", "Even": "MB_PAR_EVEN", "Odd": "MB_PAR_ODD"}
INIT_COM_PORT = {"COM1": "com1MbSlaveInit", "COM2": "com2MbSlaveInit", "COM3": "com3MbSlaveInit"}
INIT_MBTCP_PORT = "initModbusTcpTask"
INIT_TCP_PORT = "initTcpProcess"
DISC_CALL_BACK_NAME = "eMBDiscCB"
INPUT_REGISTER_CALL_BACK_NAME = "eMBRegInputCB"
HOLDING_REGISTER_CALL_BACK_NAME = "eMBRegHoldingCB"
COIL_CALL_BACK_NAME = "eMBCoilCB"



