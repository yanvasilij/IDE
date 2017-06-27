#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@file MK201DiCodeGenerator.py
@brief Кодогенерация всего связнного с DI на MK201
@Author Vasilij
"""
from MK201DiEditor import NUM_OF_ON_BOARD_DI, DESCRIPTION
from MK201IOCodeGenerator import *

class MK201DiCodeGenerator(MK201IOCodeGenerator):
    """
    Генератор исходного кода для DI встроенных в MK201
    """

    def GenerateVars(self):
        """
        Герерирует текст с объявлением всех переменных для работы с DI
        :return:
        """
        iecChannel = self.Controller.GetFullIEC_Channel()[:1]
        text = ""
        text += DIV_BEGIN + "DI" + DIV_END

        for i in range(0, (NUM_OF_ON_BOARD_DI)):
            text += "unsigned char *" + "__QX" + iecChannel + "_3_{0} = &onBoardDiValue[{1}];\n".format(i,i)
        return text

    def GenerateInit(self):
        """
        Генерирует инициализацию di
        """
        config = self.Controller.GetVariables()
        config = [i for i in config if i["Description"] == DESCRIPTION]
        text = "\t//digital inputs\n"
        for channelConfig, i in zip(config, range(0, len(config))):
            enabled = 0
            if channelConfig["Options"] == "On":
                enabled = 1
            text += "\tonBoardDiEnabled[{0}] = {1};\n".format(i, enabled)
        return text

