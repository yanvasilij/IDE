#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@file MK201DoCodeGenerator.py
@brief Кодогенерация всего связнного с DO на MK201
@Author Vasilij
"""
from MK201DoEditor import NUM_OF_ON_BOARD_DO, DESCRIPTION
from MK201IOCodeGenerator import *

class MK201DoCodeGenerator(MK201IOCodeGenerator):
    """
    Генератор исходного кода для DO встроенных в MK201
    """

    def GenerateVars(self):
        """
        Герерирует текст с объявлением всех переменных для работы с DO
        :return:
        """
        iecChannel = self.Controller.GetFullIEC_Channel()[:1]
        text = ""
        text += DIV_BEGIN + "DO" + DIV_END
	text += "extern unsigned char onBoardDoEnabled[{}];\n".format(NUM_OF_ON_BOARD_DO)
	text += "extern unsigned char onBoardDoValue[{}];\n".format(NUM_OF_ON_BOARD_DO)

        for i in range(0, (NUM_OF_ON_BOARD_DO)):
            text += "unsigned char *" + "__QX" + iecChannel + "_4_{0} = &onBoardDoValue[{1}];\n".format(i,i)
        return text

    def GenerateInit(self):
        """
        Генерирует инициализацию do
        """
        config = self.Controller.GetVariables()
        config = [i for i in config if i["Description"] == DESCRIPTION]
        text = "\t//digital outputs\n"
        for channelConfig, i in zip(config, range(0, len(config))):
            enabled = 0
            if channelConfig["Options"] == "On":
                enabled = 1
            text += "\tonBoardDoEnabled[{0}] = {1};\n".format(i, enabled)
        return text

