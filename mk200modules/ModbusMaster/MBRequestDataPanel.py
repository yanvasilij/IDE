#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Таблица данных для запроса
@Author Vasilij
"""
import wx
from plcopen.structures import TestIdentifier, IEC_KEYWORDS, DefaultType
from controls import CustomGrid, CustomTable
from util.BitmapLibrary import GetBitmap
from controls.VariablePanel import VARIABLE_NAME_SUFFIX_MODEL

DESCRIPTION = "Modus master request data"
MASTER_OPTION = "Master option"

HOLDING_REGISTER_READ = "Holding read"
HOLDING_REGISTER_WRITE = "Holding write"
INPUT_REGISTER_READ = "Input"
COIL_READ = "Coil read"
COIL_WRITE = "Coil write"
DISCRETE_INPUT_READ = "Disc"
MAX_SIMULTANEOUS_REGISTERS_READ = 125
MAX_SIMULTANEOUS_REGISTERS_WRITE = 123
MAX_SIMULTANEOUS_COIL_DISC_READ = 2000
MAX_SIMULTANEOUS_COIL_WRITE = 1968

HOLDING_REGISTERS = (HOLDING_REGISTER_READ, HOLDING_REGISTER_WRITE)
INPUT_REGISTERS = (INPUT_REGISTER_READ,)
HOLDING_AND_INPUTS = HOLDING_REGISTERS + INPUT_REGISTERS
COIL = (COIL_READ, COIL_WRITE)
DISCRETE_INPUT = (DISCRETE_INPUT_READ,)
MODBUS_TYPES = HOLDING_REGISTERS + INPUT_REGISTERS + COIL + DISCRETE_INPUT
MODBUS_TYPES_STR = []
for mbType in MODBUS_TYPES:
    MODBUS_TYPES_STR.append(mbType)

HEIGHT = 20


class ComboBoxWithLabel(wx.Panel):
    def __init__(self, parent, labelText, cmbBxchoices):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lable = wx.StaticText(self, label=labelText, size=wx.Size(100, HEIGHT))
        newId = wx.NewId()
        self.cmbbox = wx.ComboBox(self, id=newId, value="Master option",
                                  choices=cmbBxchoices, size=wx.Size(100, HEIGHT))
        self.cmbbox.SetSelection(1)
        main_sizer.Add(self.lable, flag=wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(self.cmbbox, flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(main_sizer)

class MBRequestDataTable (CustomTable):

    def __init__(self, parent):
        CustomTable.__init__(self, parent,
                [], ["#", "Name", "Device ID", "Address", "Modbus type", "Data type",
                    "Len", "Transfer method", "Period (ms)", "Timeout (ms)"])

    def _updateColAttrs(self, grid):
        content = self.GetData()
        for row in range(self.GetNumberRows()):
            for col in range(self.GetNumberCols()):
                editor = None
                renderer = None
                colname = self.GetColLabelValue(col, False)

                if colname in ["Name", "Address", "Len", "Device ID", "Period (ms)", "Timeout (ms)"]:
                    editor = wx.grid.GridCellTextEditor()
                elif colname == "Transfer method":
                    editor = wx.grid.GridCellChoiceEditor()
                    editor.SetParameters("Periodic,One shot")
                elif colname == "Data type":
                    if content[row]["Modbus type"] in HOLDING_AND_INPUTS:
                        grid.SetCellValue(row, col, "WORD")
                        grid.SetReadOnly(row, col, True)
                        continue
                    else:
                        grid.SetCellValue(row, col, "BOOL")
                        grid.SetReadOnly(row, col, True)
                        continue
                elif colname == "Modbus type":
                    editor = wx.grid.GridCellChoiceEditor(MODBUS_TYPES_STR)
                    #editor.SetParameters(MODBUS_TYPES_STR)
                else:
                    grid.SetReadOnly(row, col, True)

                grid.SetCellEditor(row, col, editor)
                grid.SetCellRenderer(row, col, renderer)

                grid.SetCellBackgroundColour(row, col, wx.WHITE)
            self.ResizeRow(grid, row)


class MBRequestDataPanel (wx.Panel):
    def __init__    (self, parent, window, controler):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        """ main sizer """
        requestPanelSizer = wx.FlexGridSizer(cols=2, hgap=0, rows=1, vgap=4)
        requestPanelSizer.AddGrowableCol(1)
        requestPanelSizer.AddGrowableRow(0)
        """ sizer with control buttons """
        controls_sizer = wx.BoxSizer(wx.VERTICAL)
        requestPanelSizer.AddSizer(controls_sizer, border=5, flag=wx.ALL)
        for name, bitmap, help in [
            ("AddVariableButton", "add_element", _("Add variable")),
            ("DeleteVariableButton", "remove_element", _("Remove variable")),
            ("UpVariableButton", "up", _("Move variable up")),
            ("DownVariableButton", "down", _("Move variable down"))]:
            button = wx.lib.buttons.GenBitmapButton(self, bitmap=GetBitmap(bitmap),
                                                    size=wx.Size(28, 28), 
                                                    style=wx.NO_BORDER)
            button.SetToolTipString(help)
            setattr(self, name, button)
            controls_sizer.AddWindow(button, border=5, flag=wx.BOTTOM)
        """ variable grid """
        self.VariablesGrid = CustomGrid(self, style=wx.VSCROLL)
        self.VariablesGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.OnVariablesGridCellChange)
        self.VariablesGrid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnVariablesGridCellLeftClick)
        self.VariablesGrid.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self.OnVariablesGridEditorShown)
        requestPanelSizer.AddWindow(self.VariablesGrid, flag=wx.GROW)
        """ add header to grid """
        mainSizer = wx.FlexGridSizer(cols=1, hgap=0, rows=2, vgap=4)
        mainSizer.AddGrowableRow(1)
        mainSizer.AddGrowableCol(0)


        headerSizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, label="      Request data")
        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        label.SetFont(font)
        headerSizer.Add(label)

        self.masterSelectCmbx = ComboBoxWithLabel(self, "", ("Master0", "Master1", "Master2"))
        wx.EVT_COMBOBOX(self, self.masterSelectCmbx.cmbbox.GetId(), self.OnChangeMasterOption)
        headerSizer.Add(self.masterSelectCmbx, flag=wx.ALIGN_CENTER_VERTICAL)

        mainSizer.AddSizer(headerSizer, flag=wx.GROW)
        mainSizer.AddSizer(requestPanelSizer, flag=wx.GROW)
        self.SetSizer(mainSizer)
        self.ParentWindow = window
        self.Controler = controler
        """ request defaule data value """
        self.VariablesDefaultValue = {
                "Name" : "",
                "Address" : "1",
                "Len" : "1",
                "Data type" : "WORD",
                "Modbus type": HOLDING_REGISTER_READ,
                "Description": DESCRIPTION,
                "Device ID" : "1",
                "Transfer method" : "Periodic",
                "Period (ms)" : "100",
                "Timeout (ms)" : "100",}
        self.Table = MBRequestDataTable(self)
        self.ColAlignements = [wx.ALIGN_RIGHT] + \
                              [wx.ALIGN_LEFT]*(len(self.VariablesDefaultValue))
        self.ColSizes = [20, 150] + [100]*(len(self.VariablesDefaultValue)-1)
        self.VariablesGrid.SetTable(self.Table)
        self.VariablesGrid.SetButtons({"Add": self.AddVariableButton,
                                       "Delete": self.DeleteVariableButton,
                                       "Up": self.UpVariableButton,
                                       "Down": self.DownVariableButton})

        """ handlers for adding variable """
        def _AddVariable(new_row):
            if new_row > 0:
                row_content = self.Table.data[new_row - 1].copy()
                newAddr = int(row_content["Address"])
                newLen = int(row_content["Len"])
                if row_content["Data type"] in ("REAL", "INT"):
                    newLen = newLen * 2
                newAddr = newAddr + newLen;
                row_content["Address"] = str(newAddr)
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
            else:
                row_content = self.VariablesDefaultValue.copy()
            self.Table.InsertRow(new_row, row_content)
            self.RefreshModel()
            self.RefreshView()
            return new_row
        setattr(self.VariablesGrid, "_AddRow", _AddVariable)

        """ handlers for deleting variable """
        def _DeleteVariable(row):
            self.Table.RemoveRow(row)
            self.RefreshModel()
            self.RefreshView()
        setattr(self.VariablesGrid, "_DeleteRow", _DeleteVariable)

        """ handlers for moving varible """
        def _MoveVariable(row, move):
            new_row = self.Table.MoveRow(row, move)
            if new_row != row:
                self.RefreshModel()
                self.RefreshView()
            return new_row
        setattr(self.VariablesGrid, "_MoveRow", _MoveVariable)

        self.VariablesGrid.SetRowLabelSize(0)
        for col in range(self.Table.GetNumberCols()):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(self.ColAlignements[col], wx.ALIGN_CENTRE)
            self.VariablesGrid.SetColAttr(col, attr)
            self.VariablesGrid.SetColSize(col, self.ColSizes[col])
        self.Table.ResetView(self.VariablesGrid)

    def OnChangeMasterOption(self, event):
        masterOptionOnFrame = self.masterSelectCmbx.cmbbox.GetStringSelection()
        masterOptionInXml = [i for i in self.Controler.GetVariables() if i["Name"] == MASTER_OPTION]
        if len(masterOptionInXml) > 0:
            if masterOptionOnFrame != masterOptionInXml[0]:
                self.RefreshModel()
        else:
            self.RefreshModel()
        event.Skip()

    def GetMasterOption(self):
        return {"Name": "Master option",
                "Address": "",
                "Len": "",
                "Device ID": "",
                "Data type": u"WORD",
                "Transfer method": "",
                "Period (ms)": "100",
                "Timeout (ms)": "100",
                "Description": MASTER_OPTION,
                "Modbus type": self.masterSelectCmbx.cmbbox.GetStringSelection()}

    def RefreshModel(self):
        controllerVariables = self.Controler.GetVariables()
        controllerVariables = [i for i in controllerVariables
                               if i["Description"] not in (DESCRIPTION, MASTER_OPTION)]
        controllerVariables += self.Table.GetData()
        controllerVariables.append(self.GetMasterOption())
        self.Controler.SetVariables(controllerVariables)
        self.RefreshBuffer()

    def RefreshView(self):
        varForTable = self.Controler.GetVariables()
        varForTable = [i for i in varForTable if i["Description"] == DESCRIPTION]
        self.Table.SetData(varForTable)
        self.Table.ResetView(self.VariablesGrid)
        varForTable = self.Controler.GetVariables()
        varForTable = [i for i in varForTable if i["Name"] == MASTER_OPTION]
        if len(varForTable) > 0:
            self.masterSelectCmbx.cmbbox.SetStringSelection(varForTable[0]["Modbus type"])
        self.VariablesGrid.RefreshButtons()

    def OnVariablesGridCellChange(self, event):
        row, col = event.GetRow(), event.GetCol()
        colname = self.Table.GetColLabelValue(col, False)
        value = self.Table.GetValue(row, col)
        message = None

        if colname == "Modbus type":
            self.VariablesGrid.SetCellValue(row, col+1, "WORD")

        if colname == "Len":
            modbusType = self.Table.GetValue(row, 4) # Modubs type value
            if modbusType in (HOLDING_REGISTER_READ, INPUT_REGISTER_READ):
                if int(value) > MAX_SIMULTANEOUS_REGISTERS_READ:
                    value = MAX_SIMULTANEOUS_REGISTERS_READ
                    self.VariablesGrid.SetCellValue(row, col, str(MAX_SIMULTANEOUS_REGISTERS_READ))
            if modbusType == HOLDING_REGISTER_WRITE:
                if int(value) > MAX_SIMULTANEOUS_REGISTERS_WRITE:
                    self.VariablesGrid.SetCellValue(row, col, str(MAX_SIMULTANEOUS_REGISTERS_WRITE))
            if modbusType in (COIL_READ, DISCRETE_INPUT_READ):
                if int(value) > MAX_SIMULTANEOUS_COIL_DISC_READ:
                    self.VariablesGrid.SetCellValue(row, col, str(MAX_SIMULTANEOUS_COIL_DISC_READ))
            if modbusType == COIL_WRITE:
                if int(value) > MAX_SIMULTANEOUS_COIL_WRITE:
                    self.VariablesGrid.SetCellValue(row, col, str(MAX_SIMULTANEOUS_COIL_WRITE))

        if colname == "Name" and value != "":
            if not TestIdentifier(value):
                message = _("\"%s\" is not a valid identifier!") % value
            elif value.upper() in IEC_KEYWORDS:
                message = _("\"%s\" is a keyword. It can't be used!") % value
            elif value.upper() in [var["Name"].upper()
                                   for var_row, var in enumerate(self.Table.data)
                                   if var_row != row]:
                message = _("A variable with \"%s\" as name already exists!") % value
            else:
                self.RefreshModel()
                wx.CallAfter(self.RefreshView)
        else:
            self.RefreshModel()
            wx.CallAfter(self.RefreshView)

        if message is not None:
            dialog = wx.MessageDialog(self, message, _("Error"), wx.OK|wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()
            event.Veto()
        else:
            event.Skip()

    def DoGetBestSize(self):
        return self.ParentWindow.GetPanelBestSize()

    def OnVariablesGridEditorShown(self, event):
        event.Skip()

    def GetVariableTypeFunction(self, base_type):
        def VariableTypeFunction(event):
            row = self.VariablesGrid.GetGridCursorRow()
            self.Table.SetValueByName(row, "Data type", base_type)
            self.Table.ResetView(self.VariablesGrid)
            self.RefreshModel()
            self.RefreshView()
            event.Skip()
        return VariableTypeFunction

    def OnVariablesGridCellLeftClick(self, event):
        if event.GetCol() == 0:
            row = event.GetRow()
            data_type = self.Table.GetValueByName(row, "Data type")
            var_name = self.Table.GetValueByName(row, "Name")
            data = wx.TextDataObject(str((var_name, "Global", data_type,
                                          self.Controler.GetCurrentLocation())))
            dragSource = wx.DropSource(self.VariablesGrid)
            dragSource.SetData(data)
            dragSource.DoDragDrop()
            return
        event.Skip()

    def RefreshBuffer(self):
        self.Controler.BufferCodeFile()
        self.ParentWindow.RefreshTitle()
        self.ParentWindow.RefreshFileMenu()
        self.ParentWindow.RefreshEditMenu()
        self.ParentWindow.RefreshPageTitles()


