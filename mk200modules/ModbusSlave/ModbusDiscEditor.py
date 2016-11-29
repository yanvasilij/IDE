#!/usr/bin/env python
# -*- coding: UTF-8 -*-

##
# @file ModbusDiscEditor.py
# @brief Классы обслуживающие настройку параметров Discrete Inputs
# @author Vasilij
# @version 1.00
# @date 2016-01-26

from ModbusSlaveEditorBase import ModbusSlaveRegEditor

DESCRIPTION = "Modus slave disc"
HEADER_TEXT = "    Discrets"
COLUMNS = ["#", "Name", "Address", "Len"]


class ModbusDiscEditor(ModbusSlaveRegEditor):

    def __init__(self, parent, window, controler):
        ModbusSlaveRegEditor.__init__(self, parent, window, controler, HEADER_TEXT, DESCRIPTION, COLUMNS)
        self.VariablesDefaultValue = {
            "Name": "Disc0",
            "Address": "1",
            "Len": "1",
            "Type": "BOOL",
            "Description": DESCRIPTION}
