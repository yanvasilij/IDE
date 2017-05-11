# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'
import time
import wx

from threading import Thread
from Queue import Queue

from wx.lib.pubsub import Publisher

from mk201_proto import mk201_proto

class serialWorker(Thread):
    def __init__(self, serialObject):
        self.serialObject = serialObject
        self.connectionStatus = True
        Thread.__init__(self)
        self.standartComandsList = []
        self.ConsoleCommandsQueue = Queue()
        self.thredStatus = True
    # def startThread(self):
    #     self.start() # start the thread

    def run(self):
        while self.connectionStatus and self.thredStatus:
            time.sleep(0.05)
            param = {}
            if not self.ConsoleCommandsQueue.empty():
                cmd = self.ConsoleCommandsQueue.get()
                try:
                    portNum = cmd["str"].split()[1]
                except:
                    portNum = '0'
                param = self.sendParam(cmd["str"], cmd["responseFormat"])
                # print(cmd)
                # переделать под формат
                if param is not None:
                    queueParam = {cmd["str"]: cmd["responseFormat"], u'result': param}
                    queueParam[u"portNum"] = portNum
                    wx.CallAfter(Publisher().sendMessage, "result", queueParam)
                else:
                    print 'Read error ', cmd, param
            self.standartComands()
            self.checkConection()

    def standartComands(self):
        if not (len(self.standartComandsList) == 0):
            for el in self.standartComandsList:
                self.ConsoleCommandsQueue.put(el)
        else:
            pass

    def checkConection(self):
        self.connectionStatus = self.serialObject.checkConnection()
        if not self.connectionStatus:
            wx.CallAfter(Publisher().sendMessage, "lostConection", "Conection lost")

    def stopThread(self):
        self.thredStatus = False

    def sendParam(self, cmd, responceFormat):
        try:
            print('cmd', cmd)
            self.serialObject.serial.write(cmd)
            # param = self.serialObject.serial.read(len(cmd))
            param1 = self.serialObject.read()
            print('param 1 ', param1 )
            param2 = self.serialObject.read()
            print('param 2 ', param2 )
            if not (len(param1) == (len(cmd) + 1)):
                print('suka bly')
                self.serialObject.serial.write('\n')
                self.serialObject.read()
                self.serialObject.read()
                self.serialObject.read()
                self.serialObject.read()
                return ''
            if param2 is not None:
                return param2
            else:
                return None
        except StandardError as err:
            print u"get param error " + str(err)

