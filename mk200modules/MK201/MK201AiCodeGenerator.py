#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@file MK201AiCodeGenerator.py
@brief Кодогенерация всего связнного с AI на MK201
@Author Vasilij
"""
from MK201AiInputEditor import NUM_OF_AI
from MK201IOCodeGenerator import *

class MK201AiCodeGenerator(MK201IOCodeGenerator):
    """
    Генератор исходного кода, для AI на MK201
    """

    def GenerateVars(self):
        """
        Генерирует текст с объеялвением всех переменных для работы с AI
        :return:
        """
        iecChannel = self.Controller.GetFullIEC_Channel()[:1]
        text = DIV_BEGIN + "AI" + DIV_END
        for i in range(0, NUM_OF_AI):
            text += "float *" + "__QD" + iecChannel + "_0_{0} = &onBoardAiCurrent[{1}];\n".format(i,i)
        return text

    def GenerateInit(self):
        """
        Генерирует инициализацию AI
        """
        channelsConfig = self.Controller.GetVariables()
        channelsConfig = [i for i in channelsConfig if i["Description"] == "On board AI"]
        text = "\t//ai init\n"
        for config, i in zip(channelsConfig, range(0, len(channelsConfig))):
            channelIsOn = 1
            if config["Options"] == "Off":
                channelIsOn = 0
            text += "\tonBoardAiEnabled[{0}] = {1};\n".format(i, channelIsOn)
        return text

