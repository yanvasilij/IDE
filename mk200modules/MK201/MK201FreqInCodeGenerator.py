#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@file MK201FreqInCodeGenerator.py
@brief Кодогенерация всего связнного с частотными и счетными входами на MK201
@Author Vasilij
"""

from MK201FreqInEditor import NUM_OF_FRQ_IN, DESCRIPTION, FREQIN_MODES
from MK201IOCodeGenerator import *

MODE_VALUES = dict(zip(FREQIN_MODES, range(0,3)))

class MK201FreqInCodeGenerator(MK201IOCodeGenerator):
    """
    Генератор исходного кода для частотных/счетных входов встроенных в MK201
    """

    def GenerateVars(self):
        """
        Герерирует текст с объявлением всех переменных для работы с AO
        :return:
        """
        iecChannel = self.Controller.GetFullIEC_Channel()[:1]
        text = ""
        text += DIV_BEGIN + "Frq in" + DIV_END

        for i in range(0, (NUM_OF_FRQ_IN)):
            text += "u8 *" + "__QB" + iecChannel + "_2_0_{0} = &onBoardFrqInMode[{1}];\n".format(i,i)
            text += "float *" + "__QD" + iecChannel + "_2_1_{0} = &onBoardFrequency[{1}];\n".format(i,i)
            text += "u8 *" + "__QX" + iecChannel + "_2_2_{0} = &onBoardCounterRun[{1}];\n".format(i,i)
            text += "u32 *" + "__QD" + iecChannel + "_2_3_{0} = &onBoardCounter[{1}];\n\n".format(i,i)
        return text

    def GenerateInit(self):
        """
        Генерирует инициализацию freq in
        """
        config = self.Controller.GetVariables()
        config = [i for i in config if i["Description"] == DESCRIPTION]
        text = "\t//freq inputs\n"
        for channelConfig, i in zip(config, range(0, len(config))):
            """ Режим работы частотног входа """
            mode = MODE_VALUES[channelConfig["Options"]]
            text += "\tonBoardFrqInMode[{0}] = {1};\n".format(i, mode)
        return text


