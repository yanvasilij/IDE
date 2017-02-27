#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'Yanikeev-as'

NUM_TEST = 5

DIV_BEGIN = "/" + ("*"*82) + "\n\t\t\t"
DIV_END = "\n" + ("*"*82) + "/\n"

from MK201IOCodeGenerator import *


class MK201RTCCodeGenerator(MK201IOCodeGenerator):
    """
    Генератор исходного кода, для AI на MK201
    """

    def GenerateRTCValueVars(self):
        """
        Генерирует текст с объеялвением переменных чтения времени и даты для работы с RTC
        :return:
        """
        iecChannel = self.Controller.GetFullIEC_Channel()[:1]
        text = DIV_BEGIN + "RTC value" + DIV_END
        text += "__UINT32_TYPE__ getMilliseconsd(void); // init RTC function for milliseconds \n"
        text += "__UINT16_TYPE__ globalTimeArray[3];\n"
        text += "__UINT16_TYPE__ globalDateArray[3];\n"
        text += "__UINT32_TYPE__ globMillisec;\n"
        text += "__UINT32_TYPE__ *" + "__QW" + iecChannel + "_5_0 = &globMillisec; // RTC millisecond\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_5_1 = &globalTimeArray[0]; // RTC second\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_5_2 = &globalTimeArray[1]; // RTC minutes\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_5_3 = &globalTimeArray[2]; // RTC hours\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_5_4 = &globalDateArray[0]; // RTC Date\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_5_5 = &globalDateArray[1]; // RTC Month\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_5_6 = &globalDateArray[2]; // RTC Year\n"
        return text

    def GenerateRTCSetVars(self):
        """
        Генерирует текст с объеялвением переменных настройки времени и даты для работы с RTC
        :return:
        """
        iecChannel = self.Controller.GetFullIEC_Channel()[:1]
        text = DIV_BEGIN + "RTC set" + DIV_END
        text += "__UINT16_TYPE__ setTimeArray[3];\n"
        text += "__UINT16_TYPE__ setDateArray[3];\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_6_1 = &setTimeArray[0]; // RTC second\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_6_2 = &setTimeArray[1]; // RTC minutes\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_6_3 = &setTimeArray[2]; // RTC hours\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_6_4 = &setDateArray[0]; // RTC Date\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_6_5 = &setDateArray[1]; // RTC Month\n"
        text += "__UINT16_TYPE__ *" + "__QW" + iecChannel + "_6_6 = &setDateArray[2]; // RTC Year\n"
        return text

    def GenerateRetrieveMillisec(self):
        """
        Генерирует текст с объеялвением переменных со значением миллисекунд для работы с RTC
        метод используется
        :return:
        """
        text = "globMillisec = getMilliseconsd(); // RTC millisec\n"
        return text


    def GenerateInitRTCSet(self):
        """
        Генерирует инициализацию RTC set
        """
        iecChannel = self.Controller.GetFullIEC_Channel()[:1]
        text = "\t// RTC set init\n"
        text += "\t*__QW" + iecChannel + "_6_1 = &globalTimeArray[0];\n"
        text += "\t*__QW" + iecChannel + "_6_2 = &globalTimeArray[1];\n"
        text += "\t*__QW" + iecChannel + "_6_3 = &globalTimeArray[2];\n"

        return text

