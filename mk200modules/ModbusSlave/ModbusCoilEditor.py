from ModbusSlaveEditorBase import ModbusSlaveRegEditor

DESCRIPTION = "Modus slave coils"
HEADER_TEXT = "    Coils"
COLUMNS = ["#", "Name", "Address", "Len"]


class ModbusCoilEditor(ModbusSlaveRegEditor):

    def __init__(self, parent, window, controler):
        ModbusSlaveRegEditor.__init__(self, parent, window, controler, HEADER_TEXT, DESCRIPTION, COLUMNS)
        self.VariablesDefaultValue = {
            "Name": "Coil0",
            "Address": "1",
            "Len": "1",
            "Type": "BOOL",
            "Description": DESCRIPTION}
