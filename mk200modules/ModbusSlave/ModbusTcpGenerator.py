#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Кодогенарция modbus tcp
@Author Vasilij
"""

from ModbusTCPEditor import DESCRIPTION
from CodeGenerationCommon import *
import re


class ModbusTcpGenerator:

    def __init__(self, controler):
        self.Controler = controler
        self.Variables = [var for var in self.Controler.GetVariables()
                          if var["Description"] == DESCRIPTION]
        self.Variables = self.Variables[0]

    def DeclareNetworkParam(self, name):
        text = ""
        text += "\tuint8_t "+name+"[] = {"
        p = re.split('\.', self.Variables[name])
        if len(p) != 4:
            text += "0,0,0,0};\n"
        else:
            text += p[0] + ", "
            text += p[1] + ", "
            text += p[2] + ", "
            text += p[3] + "};\n"
        return text


    def GenerateInit (self):
        text = ""
        text += self.DeclareNetworkParam("Ipaddr")
        text += self.DeclareNetworkParam("Submask")
        text += self.DeclareNetworkParam("Gateway")
        text += self.DeclareNetworkParam("Dns")
        text += "\t" + INIT_TCP_PORT + "(Ipaddr, Submask, Gateway, Dns);\n"
        text += "\t" + INIT_MBTCP_PORT + "("
        text += INPUT_REGISTER_CALL_BACK_NAME + ","
        text += HOLDING_REGISTER_CALL_BACK_NAME + ","
        text += COIL_CALL_BACK_NAME + ","
        text += DISC_CALL_BACK_NAME + ");\n"
        return text



