#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Плагины реализующие работу со всеми модулями серии MKLogik200
@Author Vasilij
"""
import wx
import os
import CodeFileTreeNode
from editors.CodeFileEditor import CodeEditor
from editors.CodeFileEditor import CodeFileEditor
from editors.ConfTreeNodeEditor import ConfTreeNodeEditor
from PLCControler import LOCATION_CONFNODE, LOCATION_GROUP, LOCATION_VAR_MEMORY
from MK201AiInputEditor import MK201AiInputEditor, NUM_OF_AI
from MK201AiCodeGenerator import MK201AiCodeGenerator
from MK201AoEditor import MK201AoEditor, NUM_OF_AO
from MK201AoCodeGenerator import MK201AoCodeGenerator
from MK201DiEditor import MK201DiEditor, NUM_OF_ON_BOARD_DI
from MK201DiCodeGenerator import MK201DiCodeGenerator
from MK201DoEditor import MK201DoEditor, NUM_OF_ON_BOARD_DO
from MK201DoCodeGenerator import MK201DoCodeGenerator
from MK201FreqInEditor import MK201FreqInEditor, NUM_OF_FRQ_IN
from MK201FreqInCodeGenerator import MK201FreqInCodeGenerator
from MK201_XSD import CODEFILE_XSD

CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
CodeFile = CodeFileTreeNode.CodeFile

DIV_BEGIN = "/" + ("*"*82) + "\n\t\t\t"
DIV_END = "\n" + ("*"*82) + "/\n"


class MK201Editor(CodeEditor):

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


class MK201FileEditor(CodeFileEditor):

    CONFNODEEDITOR_TABS = [
        (_("C code"), "_create_CodePanel")]
    CODE_EDITOR = MK201Editor

    def __init__(self, parent, controler, window):
        ConfTreeNodeEditor.__init__(self, parent, controler, window)

    def _create_CodePanel(self, prnt):
        """Main panel with notebook"""
        self.CodeEditorPanel = wx.Panel(prnt)
        sizer = wx.BoxSizer()
        notebook = wx.Notebook(self.CodeEditorPanel)
        """AI tab"""
        self.aiEditor = MK201AiInputEditor(notebook, self.ParentWindow, self.Controler)
        self.VariablesPanel = self.aiEditor
        notebook.AddPage(self.aiEditor, "AI Config")
        """Ao tab"""
        self.aoEditor = MK201AoEditor(notebook, self.ParentWindow, self.Controler)
        notebook.AddPage(self.aoEditor, "AO Config")
        """di tab"""
        self.diEditor = MK201DiEditor(notebook, self.ParentWindow, self.Controler)
        notebook.AddPage(self.diEditor, "DI Config")
        """do tab"""
        self.doEditor = MK201DoEditor(notebook, self.ParentWindow, self.Controler)
        notebook.AddPage(self.doEditor, "DO Config")
        """freq tab"""
        self.freqEditor = MK201FreqInEditor(notebook, self.ParentWindow, self.Controler)
        notebook.AddPage(self.freqEditor, "Freq input config")

        sizer.Add(notebook, 1, wx.EXPAND)
        self.CodeEditorPanel.SetSizer(sizer)
        return self.CodeEditorPanel

    def RefreshView(self):
        self.aiEditor.RefreshView()


class MK201ModuleFile (CodeFile):

    CODEFILE_NAME = "mk201Config"
    SECTIONS_NAMES = [ "includes", "globals", "initFunction", "cleanUpFunction", "retrieveFunction", "publishFunction"]

    EditorType = MK201FileEditor

    def GetIoVariableLocationTree(self, name, type, location, size, numOfChannles):
        variableTree = {"name": name, "type": LOCATION_GROUP, "location": "0", "children": []}
        for i in range(0, numOfChannles):
            variableTree["children"].append({
                'children':[],
                'var_name': 'Channel #{}'.format(i),
                'IEC_type': type,
                'name': 'Channel #{}'.format(i),
                'description': '',
                'type': LOCATION_VAR_MEMORY,
                'location': location+'.{}'.format(i),
                'size':  size})
        return variableTree


    def GetVariableLocationTree(self):
        """
        Отдает "наверх" список переменных доступных для работы с этим плагином. Подробное описание
        отдаваемого наверх можно посмотреть в Modbus.py
        """
        iecChannel = self.GetFullIEC_Channel()[:1]
        analogInputs = self.GetIoVariableLocationTree("Analog inputs", u'REAL', '%QD'+iecChannel+'.0', 'D', NUM_OF_AI)
        analogOutputs = self.GetIoVariableLocationTree("Analog outputs", u'REAL', '%QD'+iecChannel+'.1', 'D', NUM_OF_AO)

        frequncyMode = self.GetIoVariableLocationTree("Mode", u'BYTE', '%QB'+iecChannel+'.2.0', 'B', NUM_OF_FRQ_IN)
        frequncyValue = self.GetIoVariableLocationTree("Frequncy", u'REAL', '%QD'+iecChannel+'.2.1', 'D', NUM_OF_FRQ_IN)
        counterStart = self.GetIoVariableLocationTree("Counter start", u'BOOL', '%QX'+iecChannel+'.2.2', 'X', NUM_OF_FRQ_IN)
        counterValue = self.GetIoVariableLocationTree("Counter value", u'DINT', '%QD'+iecChannel+'.2.3', 'D', NUM_OF_FRQ_IN)
        frqInChildren = [frequncyMode, frequncyValue, counterStart, counterValue]
        freqInputs = {
                "name": "Frequency/Counter inputs",
                "type": LOCATION_CONFNODE,
                "location": '%QD'+iecChannel+'.2',
                "children": frqInChildren}

        digitalInputs = self.GetIoVariableLocationTree("Digital inputs", u'BOOL', '%QX'+iecChannel+'.3', 'X', NUM_OF_ON_BOARD_DI)
        digitalOutputs = self.GetIoVariableLocationTree("Digital outputs", u'BOOL', '%QX'+iecChannel+'.4', 'X', NUM_OF_ON_BOARD_DO)

        children = [analogInputs, analogOutputs, freqInputs, digitalInputs, digitalOutputs]
        return {"name": self.BaseParams.getName(),
                "type": LOCATION_CONFNODE,
                "location": self.GetFullIEC_Channel(),
                "children": children}

    def GetConfNodeGlobalInstances(self):
        return []

    def GetVariables(self):
        datas = []
        for var in self.CodeFileVariables(self.CodeFile):
            datas.append({"Name" : var.getname(),
                          "Type" : var.gettype(),
                          "Initial" : var.getinitial(),
                          "Description" : var.getdesc(),
                          "OnChange"    : var.getonchange(),
                          "Options"     : var.getopts(),
                          "Address" : var.getaddress(),
                          "Len" : var.getlen(),
                          })
        return datas

    def SetVariables(self, variables):
        self.CodeFile.variables.setvariable([])
        for var in variables:
            variable = self.CodeFileParser.CreateElement("variable", "variables")
            variable.setname(var["Name"])
            variable.settype(var["Type"])
            variable.setinitial(var["Initial"])
            variable.setdesc(var["Description"])
            variable.setonchange(var["OnChange"])
            variable.setopts(var["Options"])
            variable.setaddress(var["Address"])
            variable.setlen(var["Len"])
            self.CodeFile.variables.appendvariable(variable)

    def GetIconName(self):
        return "CFile"

    def CodeFileName(self):
        return os.path.join(self.CTNPath(), "mk201Config.xml")

    def CTNGenerate_C(self, buildpath, locations):

        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))
        text = ""

        self.AiCodeGenerator = MK201AiCodeGenerator(self)
        self.AoCodeGenerator = MK201AoCodeGenerator(self)
        self.FreqInCodeGenerator = MK201FreqInCodeGenerator(self)
        self.DiCodeGenerator = MK201DiCodeGenerator(self)
        self.DoCodeGenerator = MK201DoCodeGenerator(self)

        text += self.AiCodeGenerator.GenerateVars()
        text += self.AoCodeGenerator.GenerateVars()
        text += self.FreqInCodeGenerator.GenerateVars()
        text += self.DiCodeGenerator.GenerateVars()
        text += self.DoCodeGenerator.GenerateVars()

        text += DIV_BEGIN + "Publish and retrive" + DIV_END
        text += "int __init_%s(int argc,char **argv)\n{\n"%location_str
        text += self.AiCodeGenerator.GenerateInit()
        text += self.AoCodeGenerator.GenerateInit()
        text += self.FreqInCodeGenerator.GenerateInit()
        text += self.DiCodeGenerator.GenerateInit()
        text += self.DoCodeGenerator.GenerateInit()
        text += "  return 0;\n}\n\n"

        text += "void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "void __retrieve_%s(void)\n{\n"%location_str
        text += "   ;\n"
        text += "\n}\n\n"

        text += "void __publish_%s(void)\n{\n"%location_str
        text += "\n"
        text += "\n}\n\n"

        Gen_Cfile_path = os.path.join(buildpath, "mk201%s.c"%location_str)
        cfile = open(Gen_Cfile_path,'w')
        cfile.write(text)
        cfile.close()
        matiec_flags = '"-I%s"'%os.path.abspath(self.GetCTRoot().GetIECLibPath())
        return [(Gen_Cfile_path, str(matiec_flags))],str(""),True

