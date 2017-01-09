#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Modbus Slave
@Author Vasilij
"""

import os, re, traceback
from lxml import etree
from ModbusHoldingRegisterEditor import DESCRIPTION as MODDBUS_HOLDING_DESC
from ModbusDiscEditor import DESCRIPTION as MODBUS_DISC_DESC
from ModbusCoilEditor import DESCRIPTION as MODBUS_COIL_DESC
from ModbusInputRegisterEditor import DESCRIPTION as MODBUS_INPUT_DESC
from ModbusFileEditor import ModbusFileEditor
from CodeFileTreeNode import CodeFile
from PLCControler import LOCATION_CONFNODE, LOCATION_GROUP, LOCATION_VAR_MEMORY
from CodeGenerator import CodeGenerator
from xmlclass import GenerateParserFromXSDstring
from ConfigTreeNode import XSDSchemaErrorMessage
from MODBUS_SLAVE_XSD import SECTION_TAG_ELEMENT, CODEFILE_XSD


class ModbusSlaveFile(CodeFile):

    CODEFILE_NAME = "mk200mbSlave"
    SECTIONS_NAMES = [ "includes", "globals", "initFunction", "cleanUpFunction", "retrieveFunction", "publishFunction"]

    EditorType = ModbusFileEditor

    def __init__(self):
        sections_str = {"codefile_name": self.CODEFILE_NAME}
        if "includes" in self.SECTIONS_NAMES:
            sections_str["includes_section"] = SECTION_TAG_ELEMENT % "includes"
        else:
            sections_str["includes_section"] = ""
        sections_str["sections"] = "\n".join(
            [SECTION_TAG_ELEMENT % name
             for name in self.SECTIONS_NAMES if name != "includes"])

        self.CodeFileParser = GenerateParserFromXSDstring(
            CODEFILE_XSD % sections_str)
        self.CodeFileVariables = etree.XPath("variables/variable")

        filepath = self.CodeFileName()

        if os.path.isfile(filepath):
            xmlfile = open(filepath, 'r')
            codefile_xml = xmlfile.read()
            xmlfile.close()

            codefile_xml = codefile_xml.replace(
                '<%s>' % self.CODEFILE_NAME,
                '<%s xmlns:xhtml="http://www.w3.org/1999/xhtml">' % self.CODEFILE_NAME)
            for cre, repl in [
                (re.compile("(?<!<xhtml:p>)(?:<!\[CDATA\[)"), "<xhtml:p><![CDATA["),
                (re.compile("(?:]]>)(?!</xhtml:p>)"), "]]></xhtml:p>")]:
                codefile_xml = cre.sub(repl, codefile_xml)

            try:
                self.CodeFile, error = self.CodeFileParser.LoadXMLString(codefile_xml)
                if error is not None:
                    self.GetCTRoot().logger.write_warning(
                        XSDSchemaErrorMessage % ((self.CODEFILE_NAME,) + error))
                self.CreateCodeFileBuffer(True)
            except Exception, exc:
                self.GetCTRoot().logger.write_error(_("Couldn't load confnode parameters %s :\n %s") % (CTNName, unicode(exc)))
                self.GetCTRoot().logger.write_error(traceback.format_exc())
        else:
            self.CodeFile = self.CodeFileParser.CreateRoot()
            self.CreateCodeFileBuffer(False)
            self.OnCTNSave()


    def GetVariableLocationTree(self):
        """
        Отдает "наверх" список переменных доступных для работы с плагином.
        """
        return {}

    def GetConfNodeGlobalInstances(self):
        return []

    def GetVariables(self):
        datas = []
        for var in self.CodeFileVariables(self.CodeFile):
            datas.append({"Name" : var.getname(),
                          "Type" : var.gettype().replace(" ", ""),
                          "Initial" : var.getinitial(),
                          "Description" : var.getdesc(),
                          "OnChange"    : var.getonchange(),
                          "Options"     : var.getopts(),
                          "Address" : var.getaddress(),
                          "Len": var.getlen(),
                          "Id": var.getdevid(),
                          "Parity": var.gettxtype(),
                          "Ipaddr": var.getipaddr(),
                          "Submask": var.getsubmask(),
                          "Gateway": var.getgateway(),
                          "Dns": var.getdns(),
                          })
        return datas

    def SetVariables(self, variables):
        self.CodeFile.variables.setvariable([])

        def setVariable(dest, methodstr, var, varkey):
            try:
                method = getattr(dest, methodstr)
                method(var[varkey])
            except:
                pass
        for var in variables:
            variable = self.CodeFileParser.CreateElement("variable", "variables")
            setVariable(variable, "setname", var, "Name")
            setVariable(variable, "settype", var, "Type")
            setVariable(variable, "setinitial", var, "Initial")
            setVariable(variable, "setdesc", var, "Description")
            setVariable(variable, "setonchange", var, "OnChange")
            setVariable(variable, "setopts", var, "Options")
            setVariable(variable, "setaddress", var, "Address")
            setVariable(variable, "setlen", var, "Len")
            setVariable(variable, "settxtype", var, "Parity")
            setVariable(variable, "setdevid", var, "Id")
            setVariable(variable, "setipaddr", var, "Ipaddr")
            setVariable(variable, "setsubmask", var, "Submask")
            setVariable(variable, "setgateway", var, "Gateway")
            setVariable(variable, "setdns", var, "Dns")
            self.CodeFile.variables.appendvariable(variable)

    def GetIconName(self):
        return "CFile"

    def CodeFileName(self):
        return os.path.join(self.CTNPath(), "mbslave.xml")

    def CTNGenerate_C(self, buildpath, locations):
        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))
        codeGenerator = CodeGenerator(self)

        text = ""

        text += codeGenerator.GenerateCode()

        text += "int __init_%s(int argc,char **argv)\n{\n"%location_str
        text += "\t" + codeGenerator.GeneretaInit()
        text += "\n}\n\n"

        text += "void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "void __retrieve_%s(void)\n{\n"%location_str
        text += "   ;\n"
        text += "\n}\n\n"

        text += "void __publish_%s(void)\n{\n"%location_str
        text += "\n"
        text += "\n}\n\n"

        Gen_Cfile_path = os.path.join(buildpath, "mbSlave_%s.c"%location_str)
        cfile = open(Gen_Cfile_path,'w')
        cfile.write(text)
        cfile.close()

        matiec_flags = '"-I%s"'%os.path.abspath(self.GetCTRoot().GetIECLibPath())

        return [(Gen_Cfile_path, str(matiec_flags))],str(""),True

    def CTNGlobalInstances(self):
        variables = self.CodeFileVariables(self.CodeFile)
        ret = []
        for variable in variables:
            if variable.getdesc() not in (MODDBUS_HOLDING_DESC, MODBUS_INPUT_DESC, MODBUS_DISC_DESC, MODBUS_COIL_DESC):
                continue
            varLen = int(variable.getlen())
            varType = variable.gettype()
            if varLen > 1:
                varType = "ARRAY [0..{0}] OF {1}".format(varLen-1, varType)
            ret.append((variable.getname(), varType, variable.getinitial()))
        ret.extend([("On"+variable.getname()+"Change", "python_poll", "")
                    for variable in variables
                    if variable.getonchange()])
        return ret

