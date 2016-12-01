
from editors.CodeFileEditor import CodeFileEditor, CodeEditor

class DoEditor(CodeEditor):

    def SetCodeLexer(self):
        pass



#-------------------------------------------------------------------------------
#                          CFileEditor Main Frame Class
#-------------------------------------------------------------------------------

class DoFileEditor(CodeFileEditor):

    CONFNODEEDITOR_TABS = [
        (_("C code"), "_create_CodePanel")]
    CODE_EDITOR = DoEditor
