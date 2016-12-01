
import wx
import wx.grid
import wx.lib.buttons
from editors.CodeFileEditor import VariablesEditor, CodeEditor
from editors.ConfTreeNodeEditor import ConfTreeNodeEditor


class DoEditor(CodeEditor):

    def SetCodeLexer(self):
        pass



#-------------------------------------------------------------------------------
#                          CFileEditor Main Frame Class
#-------------------------------------------------------------------------------

class DoFileEditor(ConfTreeNodeEditor):

    CONFNODEEDITOR_TABS = [
        (_("C code"), "_create_CodePanel")]
    CODE_EDITOR = DoEditor

    def _create_CodePanel(self, prnt):
        self.CodeEditorPanel = wx.Panel(prnt)
        wx.StaticText(self.CodeEditorPanel, -1, "NodeId", (3, 2))
        wx.Button(self.CodeEditorPanel, -1, "-", (40, 0), (20, 22))
        self.nodeIdTextCtrl = wx.TextCtrl(self.CodeEditorPanel, -1, '1', (60,0), (20, 22), style=wx.TE_RIGHT)
        self.nodeIdTextCtrl.Bind(wx.EVT_CHAR, self.handle_keypress)
        wx.Button(self.CodeEditorPanel, -1, "+", (80,0), (20, 22))
        return self.CodeEditorPanel


    def handle_keypress(self, event):
        raw_value = self.nodeIdTextCtrl.GetValue().strip()
        if all(x in '0123456789' for x in raw_value):
            pass
        else:
            event.Skip()
