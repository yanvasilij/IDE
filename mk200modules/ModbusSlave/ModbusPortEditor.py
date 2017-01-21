#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##
# @file ModbusPortEditor.py
# @brief Панель для настройки порта modbus
# @author Vasilij
# @version 1.00
# @date 2016-01-26

import wx
from copy import deepcopy
from ModbusSlaveEditorBase import ModbusSlaveRegEditor, ModbusSalveTable
from controls.VariablePanel import VARIABLE_NAME_SUFFIX_MODEL

DESCRIPTION = "Modbus slave RTU port"
HEADER_TEXT = "    RTU ports"
COLUMNS = ["Name", "Port", "Address", "Baudrate", "Data bits", "Parity", "Stop bits"]

RS485_PORTS = ["COM1", "COM2", "COM3"]
RS485_PORTS_STR = ','.join(RS485_PORTS)

BAUDRATES = ["9600", "9600", "14400", "19200", "38400", "57600", "115200"]
BAUDRATES_STR = ','.join(BAUDRATES[1:])

PARITYS = ["None", "Odd", "Even"]
PARITY_STR = ','.join(PARITYS)

STOPBITS = ["0.5", "1", "1.5", "2"]
STOPBITS_STR = ",".join(STOPBITS)

DATA_BITS = ["8", "9"]
DATA_BITS_STR = ','.join(DATA_BITS)



class PortEditorTable (ModbusSalveTable):

    def _updateColAttrs(self, grid):
        for row in range(self.GetNumberRows()):
            for col in range(self.GetNumberCols()):
                editor = None
                renderer = None
                colname = self.GetColLabelValue(col, False)
                if colname == "Port":
                    editor = wx.grid.GridCellChoiceEditor()
                    editor.SetParameters(RS485_PORTS_STR)
                elif colname == "Baudrate":
                    editor = wx.grid.GridCellChoiceEditor()
                    editor.SetParameters(BAUDRATES_STR)
                elif colname == "Data bits":
                    editor = wx.grid.GridCellChoiceEditor()
                    editor.SetParameters(DATA_BITS_STR)
                elif colname == "Parity":
                    editor = wx.grid.GridCellChoiceEditor()
                    editor.SetParameters(PARITY_STR)
                elif colname == "Stop bits":
                    editor = wx.grid.GridCellChoiceEditor()
                    editor.SetParameters(STOPBITS_STR)
                elif colname == "Address":
                    editor = wx.grid.GridCellNumberEditor()
                else:
                    grid.SetReadOnly(row, col, True)

                grid.SetCellEditor(row, col, editor)
                grid.SetCellRenderer(row, col, renderer)

                grid.SetCellBackgroundColour(row, col, wx.WHITE)
            self.ResizeRow(grid, row)
        self.CheckPort()
        # self.CheckPort()

    def CheckPort(self):
        curPorts = self.data
        errorStatus = 0
        erroCheck = False
        for variables1 in curPorts:
            errorStatus = 0
            for variables2 in curPorts:
                if variables1["Port"] == variables2["Port"]:
                    errorStatus += 1
                if errorStatus >= 2:
                    erroCheck = True
        if erroCheck:
            print("COM ERROR!" * 10)
            message = _("lol")
            dialog = wx.MessageDialog(self.Parent, message, _("Error"))
            dialog.ShowModal()
            dialog.Destroy()





class ModbusPortEditor (ModbusSlaveRegEditor):

    def __init__(self, parent, window, controler):
        ModbusSlaveRegEditor.__init__(self, parent, window, controler, HEADER_TEXT, DESCRIPTION, COLUMNS)
        self.VariablesDefaultValue = {
            "Name": "Port0",
            "Address": "1",
            "Baudrate": "115200",
            "Data bits": "8",
            "Type": "BOOL",
            "Description": DESCRIPTION,
            "Port": "COM1",
            "Parity": "None",
            "Stop bits": "1"}
        """ handlers for adding variable """

        self.Table = PortEditorTable(self, COLUMNS)
        self.ColSizes = [20, 150] + [100]*(len(self.VariablesDefaultValue)-1)
        self.VariablesGrid.SetTable(self.Table)
        newParamsRS485 = deepcopy(RS485_PORTS)

        def _AddVariable(new_row):
            row_all = self.Table.data
            if new_row > 0:
                row_content = self.Table.data[new_row - 1].copy()
                result = VARIABLE_NAME_SUFFIX_MODEL.search(row_content["Name"])
                if result is not None:
                    name = row_content["Name"][:result.start(1)]
                    suffix = result.group(1)
                    if suffix != "":
                        start_idx = int(suffix)
                    else:
                        start_idx = 0
                else:
                    name = row_content["Name"]
                    start_idx = 0
                row_content["Name"] = self.Controler.GenerateNewName(
                    name + "%d", start_idx)

                # newParams = deepcopy(RS485_PORTS)
                comNum = 1
                comName = "COM" + str(comNum)
                curPorts = []
                for variable in row_all:
                    curPorts.append(variable["Port"])
                for port in sorted(curPorts):
                    if comName == port:
                        comNum += 1
                        comName = "COM" + str(comNum)
                    # newParamsRS485 = deepcopy(RS485_PORTS)
                    # for widget in row_all:
                    #     newParamsRS485.remove(widget["Port"])
                    # editor = wx.grid.GridCellChoiceEditor()
                    # newParamsRS485 = ','.join(newParamsRS485)
                row_content["Port"] = comName
            else:
                row_content = self.VariablesDefaultValue.copy()
            if len(row_all) < 3:
                self.Table.InsertRow(new_row, row_content)
                self.RefreshModel()
                self.RefreshView()
                return new_row
        setattr(self.VariablesGrid, "_AddRow", _AddVariable)


    def RefreshView(self):
        controlerVars = self.Controler.GetVariables()
        controlerVars = [i for i in controlerVars if i["Description"] == self.description]
        tableVars = []
        for var in controlerVars:
            tableVar = {}
            tableVar["Name"] = var["Name"]
            tableVar["Port"] = var["Options"]
            tableVar["Address"] = var["Address"]
            tableVar["Baudrate"] = var["Baudrate"]
            tableVar["Data bits"] = var["Len"]
            tableVar["Parity"] = var["Parity"]
            tableVar["Stop bits"] = var["Id"]
            tableVar["Type"] = var["Type"]
            tableVar["Description"] = var["Description"]
            tableVars.append(tableVar)
        self.Table.SetData(tableVars)
        self.Table.ResetView(self.VariablesGrid)
        self.VariablesGrid.RefreshButtons()


    def RefreshModel(self):
        controllerVariables = self.Controler.GetVariables()
        controllerVariables = [i for i in controllerVariables if i["Description"] != self.description]
        tableVars = self.Table.GetData()
        for var in tableVars:
            controlerVar = {}
            controlerVar["Name"] = var["Name"]
            controlerVar["Options"] = var["Port"]
            controlerVar["Address"] = var["Address"]
            controlerVar["Baudrate"] = var["Baudrate"]
            controlerVar["Len"] = var["Data bits"]
            controlerVar["Parity"] = var["Parity"]
            controlerVar["Id"] = var["Stop bits"]
            controlerVar["Type"] = var["Type"]
            controlerVar["Description"] = var["Description"]
            controllerVariables.append(controlerVar)
        self.Controler.SetVariables(controllerVariables)
        self.RefreshBuffer()
