#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Работа с модулями расширения через протокол CANOpen
@Author Yanikeev-AS
"""
from MK211CANOpen import MK211CANOpenFile
from MK234CANOpen import MK234CANOpenFile
from MK243CANOpen import MK243CANOpenFile
from MK245CANOpen import MK245CANOpenFile

class RootClass:
    CTNChildrenTypes = [("MK211", MK211CANOpenFile, "MK211 module"),
                       ("MK234", MK234CANOpenFile, "MK232 module"),
                       ("MK243", MK243CANOpenFile, "MK243 module"),
                       ("MK245", MK245CANOpenFile, "MK245 module")]