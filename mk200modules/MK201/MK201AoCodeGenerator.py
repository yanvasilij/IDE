#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@file MK201AiCodeGenerator.py
@brief Кодогенерация всего связнного с AO на MK201
@Author Vasilij
"""
from MK201AoEditor import NUM_OF_AO
from MK201IOCodeGenerator import *

class MK201AoCodeGenerator(MK201IOCodeGenerator):
    """
    Генератор исходного кода, для AO на MK201
    """

    def GenerateVars(self):
        """
        Герерирует текст с объявлением всех переменных для работы с AO
        :return:
        """
        iecChannel = self.Controller.GetFullIEC_Channel()[:1]
        text = ""
        text += DIV_BEGIN + "AO" + DIV_END
        text += "extern float onBoardAoCurrents[2];\n"
        text += "extern unsigned char onBoardAoEnable[2];\n"
        for i in range(0, NUM_OF_AO):
            text += "float *" + "__QD" + iecChannel + "_1_{0} = &onBoardAoCurrents[{1}];\n".format(i,i)
        return text

    def GenerateInit(self):
        """
        Генерирует инициализацию AO
        """
        channelsConfig = self.Controller.GetVariables()
        channelsConfig = [i for i in channelsConfig if i["Description"] == "On board AO"]
        text = "\t//ao init\n"
        for config, i in zip(channelsConfig, range(0, len(channelsConfig))):
            channelIsOn = 1
            if config["Options"] == "Off":
                channelIsOn = 0
            text += "\tonBoardAoEnable[{0}] = {1};\n".format(i, channelIsOn)
        return text

