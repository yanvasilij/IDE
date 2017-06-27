__author__ = 'Yanikeev-as'
# -*- coding: UTF-8 -*-
import sys
import os


from threading import Lock
from threading import Thread
import wx
from wx.lib.pubsub import Publisher

from MKSetup.MK200Transaction import *
from MKSetup.mk201_proto import mk201_proto
from MKSetup.configurator_MK201setup import Configurator_MK201
from mk200ide import _dist_folder


class MK201Object():
    def __init__(self, confnodesroot, comportstr):
        self.confnodesroot = confnodesroot
        self.SerialConnection = mk201_proto()
        self.TransactionLock = Lock()
        self.IsProgramming = False
        self.failure = None
        self.StatusMethods = self.confnodesroot.StatusMethods # список методов и элементов toolbar'а
        # в списко методов PorjectController-а добавляю метод вызова конфигуратора для МК201
        self.confnodesroot._callConfigurator = self._Configurator
        # перегружаю метод _Disconnect, чтобы выполнить свои дейсвтия
        self.confnodesroot._Disconnect = self.disconnect
        self.confnodesroot.CloseProject = self._closeProject
        # в список объектов toolBar-а добавляю вызов конфигуратора
        self.StatusMethods.append({"bitmap" : "configurator",
                                   "shown" : False,
                                   "name" : _("configurator"),
                                   "tooltip" : u"Конфигуратор MK201Setup",
                                   "method" : '_callConfigurator'})
        self.projectPath = self.confnodesroot.GetProjectPath()
        self.projectName = self.confnodesroot.GetProjectName()
        self.hexfilepath = self.confnodesroot.GetProjectPath() + '\\build\\' + self.projectName + '.hex'
        self.PLCStatus = "Disconnected"
        self.comport = comportstr
        self.TransactionLock.acquire()
        self.connect()
        self.TransactionLock.release()
        # self.MenuToolBar.Realize()


    def connect(self):
        res = self.SerialConnection.connect(self.comport)
        self.confnodesroot.ShowMethod('_callConfigurator', True)
        if not (res == 'Connected'):
            self.dialogMessage(u'Ошибка подключения, COM-порт не доступен.')
            wx.CallAfter(self.disconnect)

    def disconnect(self):
        self.SerialConnection.serial.close()
        self.confnodesroot.ShowMethod('_callConfigurator', False)
        self.confnodesroot._SetConnector(None)

    def _closeProject(self):
        self.disconnect()
        self.confnodesroot.ClearChildren()
        self.confnodesroot.ResetAppFrame(None)



    def dialogMessage(self, message):
        dialog = wx.MessageBox(message, u'Ошибка!', wx.OK | wx.ICON_INFORMATION)

    def _HandleSerialTransaction(self, transaction, must_do_lock):
        res = None
        failure = None
        # Must acquire the lock
        if must_do_lock:
            self.TransactionLock.acquire()
        if self.SerialConnection is not None:
            # Do the job
            transaction.SendCommand()
            self.PLCStatus, res = transaction.GetCommandAck()
            if self.PLCStatus is None:
                failure = res
                self.PLCStatus = None
        if must_do_lock:
            self.TransactionLock.release()
        return res, failure

    def HandleSerialTransaction(self, transaction):
        res = None;
        failure = None;
        res, self.failure = self._HandleSerialTransaction(transaction, True)
        if self.failure is not None:
            self.confnodesroot.logger.write_error(self.failure + "\n")
            res = None
        return res

    def StartPLC(self):
        pass

    def StopPLC(self):
        pass

    def NewPLC(self, md5sum, data, extrafiles):
        self.IsProgramming = True
        self.progressDialog = loadDilog(self.confnodesroot.AppFrame, self.hexfilepath, self.comport, self.SerialConnection)
        res = self.progressDialog.ShowModal()
        # self.progressDialog.Destroy()
        self.IsProgramming = False
        self.parent = None
        return self.PLCStatus == "Stopped"
        return True

    def _Configurator(self):
        self.IsProgramming = True
        myDialog = Configurator_MK201(self.confnodesroot.AppFrame, self.SerialConnection, self.hexfilepath)
        res = myDialog.ShowModal()
        myDialog.Destroy()
        self.IsProgramming = False

    def GetPLCstatus(self):
        # if self.IsProgramming:
        #    return "Stopped", [1]
        # res = self.HandleSerialTransaction(GET_PLCStatusTransaction(self.SerialConnection))
        # if res is None:
        #     # убираю из toolbar-а мой виджет, т.к. далее в беремизе конектор удаляется, а мой виджет остается внутри беремиза
        #     self.confnodesroot.ShowMethod('_callConfigurator', False)
        #     return None, [1]
        # else:
            return "Stopped", [1]

    def MatchMD5(self, MD5):
        # return False
        pass

    def GetTraceVariables(self):
        return "Stoped", []

    def SetTraceVariablesList(self, idxs):
        pass

    def GetLogMessage(self, level, msgid):
        return None

    def __del__(self):
        print "__del__ of connector"

class loadDilog(wx.Dialog):
    def __init__(self, parent, hexFilePath, port, moduleObject):
        self.downloadStatus = False

        self.hexFilePath = hexFilePath
        # self.modulOpject = mk201_proto()
        self.modulOpject = moduleObject
        self.modulOpject.connect(port)
        wx.Dialog.__init__(self, parent = parent, id = wx.NewId(), title  = u'Загрузка', size = (300, 120), pos = (150,150))
        self.statusTextCtrl = wx.StaticText(self, label = u'Идёт загрузка, пожалуйста не отключайте модуль', id = wx.ID_ANY,
                                            size = (270, 20), pos = (15, 10))
        self.progressBar = wx.Gauge(self, id = wx.ID_ANY, range = 100, size = (270, 20), pos = (15, 35))
        self.statusBar = wx.StatusBar(self, id = wx.ID_ANY)
        self.startThread()
        # self.Bind(wx.EVT_CLOSE, self.closeDialog)
        wx.EVT_CLOSE(self, self.closeDialog)
        Publisher().subscribe(self.loadStatus, "update")

    def closeDialog(self, event):
        if self.downloadStatus == True:
            self.Destroy()
        else:
            pass

    def startThread(self):
        self.loadThred = Thread(target = self.modulOpject.load_hex_mk201, args=(self.hexFilePath, '0'))
        # self.loadThred = Thread(target = self.# printLol)
        self.loadThred.start()

    def loadStatus(self, msg):
        answer = msg.data
        # FIXME: почему-та иногда падает на этом месте, wx ругается на то что объект был удален
        if (type(answer) == int):
            self.progressBar.SetValue((answer - 1) * 10)
            self.statusBar.SetStatusText(str( (answer - 1)*10) + '%')
        if (type(answer) is str):
            # print answer
            # if 'Download' in str(answer):
            #     # print('Download success')
            # if 'Done' in answer:
            #     downloadStatusMsg = 'Download success'
            # else:
            #     downloadStatusMsg = 'Download canceled. Error: %s. ' % str(answer)
            time.sleep(5) # ожидание для того чтобы в модуле прошла начальная инициализация и он смог отвечать
            downloadStatusMsg = 'Download success'
            self.statusBar.SetStatusText(downloadStatusMsg)
            # print(downloadStatusMsg)
            self.downloadStatus = True
            self.Destroy()

