#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Holding register editor
@Author Vasilij
"""
from ModbusSlaveEditorBase import ModbusSlaveRegEditor

DESCRIPTION = "Modus slave holdings"
HEADER_TEXT = "    Holding Registers"
COLUMNS = ["#", "Name", "Type", "Address", "Len"]


class ModbusHoldingRegisterEditor(ModbusSlaveRegEditor):

    def __init__(self, parent, window, controler):
        ModbusSlaveRegEditor.__init__(self, parent, window, controler, HEADER_TEXT, DESCRIPTION, COLUMNS)
        self.VariablesDefaultValue = {
            "Name": "Hold0",
            "Address": "1",
            "Len": "1",
            "Type": "WORD",
            "Description": DESCRIPTION}
