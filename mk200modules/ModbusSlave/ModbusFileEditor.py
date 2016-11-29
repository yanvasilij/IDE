
import wx
import wx.grid
import wx.lib.buttons
from editors.CodeFileEditor import CodeEditor
from ModbusHoldingRegisterEditor import ModbusHoldingRegisterEditor
from ModbusInputRegisterEditor import ModbusInputRegisterEditor
from ModbusCoilEditor import ModbusCoilEditor
from ModbusDiscEditor import ModbusDiscEditor
from ModbusPortEditor import ModbusPortEditor
from ModbusTCPEditor import ModbusTCPEditor
from editors.CodeFileEditor import CodeFileEditor
from editors.ConfTreeNodeEditor import ConfTreeNodeEditor

class ModbusEditor(CodeEditor):

    def __init__(self, parent, window, controler):
        pass

    def SetCodeLexer(self):
        pass

    def RefreshBuffer(self):
        pass

    def ResetBuffer(self):
        pass

    def GetCodeText(self):
        pass

    def RefreshView(self, scroll_to_highlight=False):
        pass

#-------------------------------------------------------------------------------
#                          CFileEditor Main Frame Class
#-------------------------------------------------------------------------------

class ModbusFileEditor(CodeFileEditor):

    CONFNODEEDITOR_TABS = [
        (_("C code"), "_create_CodePanel")]
    CODE_EDITOR = ModbusEditor

    def __init__(self, parent, controler, window):
        ConfTreeNodeEditor.__init__(self, parent, controler, window)

    def _create_CodePanel(self, prnt):
        self.CodeEditorPanel = wx.Panel(prnt)
        """Creating sizer and notebook for panels"""
        sizer = wx.BoxSizer()
        notebook = wx.Notebook(self.CodeEditorPanel)
        """Holding registers editor panel"""
        self.VariablesPanel = ModbusHoldingRegisterEditor(notebook, self.ParentWindow,
                                                          self.Controler)
        """Input registers editor panel"""
        self.InputRegistersEditor = ModbusInputRegisterEditor(notebook, self.ParentWindow,
                                                          self.Controler)
        """Coil editor panel"""
        self.CoilEditor = ModbusCoilEditor(notebook, self.ParentWindow, self.Controler)
        """Disc editor panel"""
        self.DiscEditor = ModbusDiscEditor(notebook, self.ParentWindow, self.Controler)
        """Port settings"""
        self.PortEditor = ModbusPortEditor(notebook, self.ParentWindow, self.Controler)
        """TCP port settings"""
        self.TcpEditor = ModbusTCPEditor(notebook, self.ParentWindow, self.Controler)
        """Adding panels to tabs"""
        notebook.AddPage(self.VariablesPanel, "Holding registers")
        notebook.AddPage(self.InputRegistersEditor, "Input registers")
        notebook.AddPage(self.CoilEditor, "Coils")
        notebook.AddPage(self.DiscEditor, "Discretes")
        notebook.AddPage(self.PortEditor, "RTU port")
        notebook.AddPage(self.TcpEditor, "TCP port")
        sizer.Add(notebook, 1, wx.EXPAND)
        self.CodeEditorPanel.SetSizer(sizer)

        self.CodeEditor = self.CODE_EDITOR(self.CodeEditorPanel, self.ParentWindow, self.Controler)
        return self.CodeEditorPanel

    def RefreshView(self):
        CodeFileEditor.RefreshView(self)
        self.CoilEditor.RefreshView()
        self.DiscEditor.RefreshView()
        self.InputRegistersEditor.RefreshView()
        self.PortEditor.RefreshView()
        self.TcpEditor.RefreshView()

#    def RefreshTitle (self):
#        pass

#    def __init__(self, parent, controler, window):
#        ConfTreeNodeEditor.__init__(self, parent, controler, window)
#        wx.CallAfter(self.CodeEditorPanel.SetSashPosition, 150)

#    def CodeFileName(self):
#        return os.path.join(self.CTNPath(), "cfile.xml")


