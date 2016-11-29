#!/usr/bin/env python
# -*- coding: UTF-8 -*-

##
# @file ModbusInputRegisterEditor.py
# @brief Классы обслуживающие настройку параметров Input Registr'ов
# @author Vasilij
# @version 1.01
# @date 2016-01-26

from ModbusSlaveEditorBase import ModbusSlaveRegEditor

DESCRIPTION = "Modbus slave input"
HEADER_TEXT = "    Input Registers"
COLUMNS = ["#", "Name", "Type", "Address", "Len"]


class ModbusInputRegisterEditor(ModbusSlaveRegEditor):

    def __init__(self, parent, window, controler):
        ModbusSlaveRegEditor.__init__(self, parent, window, controler, HEADER_TEXT, DESCRIPTION, COLUMNS)
        self.VariablesDefaultValue = {
            "Name": "Reg0",
            "Address": "1",
            "Len": "1",
            "Type": "WORD",
            "Description": DESCRIPTION}

