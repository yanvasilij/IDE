#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@brief IDE for mk200 PLC
@Author Vasilij
"""

import os
from POULibrary import POULibrary

class MK200Library(POULibrary):
    def GetLibraryPath(self):
        return os.path.join(os.path.split(__file__)[0], "lib.xml")

class MK200Modbus(POULibrary):
    def GetLibraryPath(self):
        return os.path.join(os.path.split(__file__)[0], "modbuslib.xml")

class MK200AdditionalConversion(POULibrary):
    def GetLibraryPath(self):
        return os.path.join(os.path.split(__file__)[0], "typeConvershionalLib.xml")
