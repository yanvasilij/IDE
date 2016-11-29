#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@file MK201IOCodeGenerator.py
@brief Базовый класс для кодогенрации для всех IO
@Author Vasilij
"""

DIV_BEGIN = "/" + ("*"*82) + "\n\t\t\t"
DIV_END = "\n" + ("*"*82) + "/\n"

class MK201IOCodeGenerator:

    def  __init__(self, controller):
        self.Controller = controller

    def GenerateVars(self):
        pass

    def GenerateInit(self):
        pass

