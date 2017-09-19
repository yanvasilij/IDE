# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'
import time
import wx
import sys

from threading import Thread
from Queue import Queue

# from wx.lib.pubsub import Publisher # importing Publisher for old wx version ( must use Publisher. instead of Publisher())
from wx.lib.pubsub import pub as Publisher

from mk201_proto import mk201_proto

class CountEvent(wx.PyCommandEvent):
    """Event to signal that a count value is ready"""
    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        """Returns the value from the event.
        @return: the value of this event

        """
        return self._value

class serialWorker(object):
# class serialWorker(Thread):


    def __init__(self, serialObject, wxParent):
        self._serialObject = serialObject
        self._wxParent = wxParent
        self.connectionStatus = True
        # Thread.__init__(self)
        self.standartComandsList = []
        self.ConsoleCommandsQueue = Queue()
        self.thredStatus = True
        self._serialObject.serial.timeout = 0.05
        self.typeEVT_RESOULT = wx.NewEventType()
        self.EVT_RESOULT = wx.PyEventBinder(self.typeEVT_RESOULT, 1)

    # def startThread(self):
    #     self.start() # start the thread

    def run(self):
        self.cleanSerialBuffer()
        # while self.connectionStatus and self.thredStatus:
        # self.cleanSerialBuffer()
        time.sleep(0.05)
        param = {}
        while not(self.ConsoleCommandsQueue.empty()):
        # if not self.ConsoleCommandsQueue.empty():
            cmd = self.ConsoleCommandsQueue.get()
            try:
                portNum = cmd["str"].split()[1]
            except:
                portNum = '0'
            param = self.sendParam(cmd)
            # print(cmd)
            # переделать под формат
            if param is not None:
                queueParam = {cmd["str"]: cmd["responseFormat"], u'result': param}
                queueParam[u"portNum"] = portNum
                # wx.CallAfter(Publisher.sendMessage, "result", queueParam)
                evt = CountEvent(self.typeEVT_RESOULT, -1, queueParam)
                wx.PostEvent(self._wxParent, evt)
            else:
                pass
                # print 'Read error ', cmd, param
        # self.checkConection()
        # sys.exit(0)

    def standartComands(self):
        if not (len(self.standartComandsList) == 0):
            for el in self.standartComandsList:
                self.ConsoleCommandsQueue.put(el)
        else:
            pass

    def checkConection(self):
        self.connectionStatus = self._serialObject.checkConnection()
        # print 'self.connectionStatus ', self.connectionStatus
        if not self.connectionStatus:
            # print 'lostConection'
            # wx.CallAfter(Publisher.sendMessage, "lostConection")
            evt = CountEvent(self.typeEVT_RESOULT, -1, lostConection)
            wx.PostEvent(self._wxParent, evt)

    def stopThread(self):
        self.thredStatus = False

    def cleanSerialBuffer(self):
        self._serialObject.serial.write('')
        self._serialObject.serial.reset_input_buffer()
        self._serialObject.serial.reset_output_buffer()

    def sendParam(self, cmd):
        try:
            # self.cleanSerialBuffer()
            # print('cmd', cmd)
            msg = cmd["str"]
            self._serialObject.serial.write(msg)
            param1 = self._serialObject.read()
            # print('param 1 ', param1 )
            param2 = self._serialObject.read()
            # print('param 2 ', param2 )
            if not (len(param1) == (len(msg) + 1)):
                # print('suka bly')
                self.cleanSerialBuffer()
                self.ConsoleCommandsQueue.put(cmd)
            if param2 is not None:
                return param2
            else:
                return None
        except StandardError as err:
            return u"Error: " + str(err[0])

