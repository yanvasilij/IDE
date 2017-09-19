# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'

import sys
import os


from threading import Lock
from threading import Thread
from Queue import Queue
import wx
# from wx.lib.pubsub import Publisher # importing Publisher for old wx version
from wx.lib.pubsub import pub as Publisher
from MKSetup.MK200Transaction import *
from MKSetup.mk201_proto import mk201_proto
from MKSetup.configurator_MK201setup import Configurator_MK201
from mk200ide import _dist_folder


class MK201Object():
    def __init__(self, confnodesroot, comportstr):
        self._confnodesroot = confnodesroot
        self.SerialConnection = mk201_proto(self._confnodesroot.AppFrame)
        self.logViewer = confnodesroot.AppFrame.LogViewer
        self.TransactionLock = Lock()
        self.IsProgramming = False
        self.failure = None
        self.StatusMethods = self._confnodesroot.StatusMethods # список методов и элементов toolbar'а | List of methods and elements of the toolbar

        # self._confnodesroot._callConfigurator = self._Configurator
        # перегружаю метод _Disconnect
        # overload the _Disconnect method
        self._confnodesroot._Disconnect = self.disconnect
        self._confnodesroot.CloseProject = self._closeProject
        # в список объектов toolBar-а добавляю вызов конфигуратора
        # In the list of toolBar objects I add a call to the configurator
        self.StatusMethods.append({"bitmap" : "configurator",
                                   "shown" : False,
                                   "name" : _("configurator"),
                                   "tooltip" : u"Конфигуратор MK201Setup",
                                   "method" : '_callConfigurator'})
        self.projectPath = self._confnodesroot.GetProjectPath()
        self.projectName = self._confnodesroot.GetProjectName()
        self.hexfilepath = self._confnodesroot.GetProjectPath() + '\\build\\' + self.projectName + '.hex'
        self.PLCStatus = "Disconnected"
        self.comport = comportstr
        self.TransactionLock.acquire()
        self.connect()
        self.TransactionLock.release()
        # self.MenuToolBar.Realize()

    """ метод "разбрикивания" контроллера (запускается в потоке) """
    def unbreacking(self):
        startTime = 0
        breackingStatus = ""
        # делаю условие по времени, однако на самом деле это условие стартует, только после появления сообщение "StopThread"
        # в очереди, пока это сообщение не появится цикл вертеться ВЕЧНО!!!
        # I make the condition by time, but in fact this condition starts, only after the appearance of the message "StopThread"
        # in the queue until this message appears cycle to rotate FOREVER!!!
        while (startTime < 1):
            if not(self.breakingQueue.empty()):
                breackingStatus = self.breakingQueue.get()
            # иниуирую границчное значение времени условия выхода из цикла
            # Initialize the timeout value of the exit condition from the loop
            if breackingStatus == "StopThread":
                startTime = time.time()
            # каждую итерацию дергаю порт...
            # check the port every Iteration...
            try:
                self.SerialConnection.serial.close()
                self.SerialConnection.serial.port = self.comport
                self.SerialConnection.serial.open()
            except:
                pass
            # ...и пробую разбрикнуть
            # ...and try to unbreak
            breakRes = self.SerialConnection.breakCheck()
            if breakRes:
                # основному процессу передаю сообщение об успешном разбрикивании
                # To the main process I pass the message about the successful unbreaking
                self.breakingQueue.put("Connected")
                break
            # иниуирую границчное значение времени условия выхода из цикла
            # Initialize the timeout value of the exit condition from the loop
            if breackingStatus == "StopThred":
                startTime = (time.time() - startTime)
        self.SerialConnection.serial.close()
        sys.exit(0)
        return 0

    def connect(self):
        self.breakingQueue = Queue() # очередь использую для межпоточного обмена
        breakingThread = Thread(target=self.unbreacking, args=()) # поток для процесса разбрикивания

        connctRes = self.SerialConnection.connect(self.comport)
        breakRes = self.SerialConnection.breakCheck()

        if not(breakRes) and (connctRes == 'Connected'):
            breakingThread.start()
            self.dialogMessage(u'Модуль не отвечает, передерните питание и нажмите Ок!')
            time.sleep(1)
            self.breakingQueue.put("StopThread")
            connctRes = self.SerialConnection.connect(self.comport)
            time.sleep(1)
        if not(self.breakingQueue.empty()):
            connctRes = self.breakingQueue.get()
        if not (connctRes == 'Connected'):
            self.dialogMessage(u'Ошибка подключения, COM-порт не доступен.')
            wx.CallAfter(self.disconnect)
        return

    def disconnect(self):
        if not(self.SerialConnection is None):
            self.setLogout(True) # включаю логи по завершению работы
            self.SerialConnection.serial.close()
        self.SerialConnection = None
        self._confnodesroot.ShowMethod('_Connect_MK201', True)
        self._confnodesroot.ShowMethod('_setMK201Connector', True)
        self._confnodesroot.UpdateMethodsFromPLCStatus()
        self._confnodesroot._SetConnector(None)

    def setLogout(self, enable):
        try:
            if enable == True:
                self.SerialConnection.serial.write("logenable 1\r\n")
            if enable == False:
                self.SerialConnection.serial.write("logenable 0\r\n")
        except:
            pass

    def _closeProject(self):
        self.disconnect()
        self._confnodesroot.ClearChildren()
        self._confnodesroot.ResetAppFrame(None)

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
            self._confnodesroot.logger.write_error(self.failure + "\n")
            res = None
        return res

    def StartPLC(self):
        pass

    def StopPLC(self):
        pass

    def NewPLC(self, md5sum, data, extrafiles):
        self.IsProgramming = True
        self.progressDialog = loadDilog(self._confnodesroot.AppFrame, self.hexfilepath, self.comport, self.SerialConnection)
        res = self.progressDialog.ShowModal()
        # self.progressDialog.Destroy()
        self.IsProgramming = False
        self.parent = None
        # return self.PLCStatus == "Stopped"
        return True

    def GetPLCstatus(self):
        # if self.IsProgramming:
        #    return "Stopped", [1]
        # res = self.HandleSerialTransaction(GET_PLCStatusTransaction(self.SerialConnection))
        # if res is None:
        #     # убираю из toolbar-а мой виджет, т.к. далее в беремизе конектор удаляется, а мой виджет остается внутри беремиза
        #     self._confnodesroot.ShowMethod('_callConfigurator', False)
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


class loadDilog(wx.Dialog):
    def __init__(self, parent, hexFilePath, port, moduleObject):
        self.downloadStatus = False
        self.hexFilePath = hexFilePath
        self._modulOpject = moduleObject
        self._modulOpject._wxParent = self
        self._modulOpject.connect(port)
        wx.Dialog.__init__(self, parent=parent, id=wx.NewId(), title=u'Загрузка', size=(300, 120), pos=(150, 150))
        self.statusTextCtrl = wx.StaticText(self, label=u'Идёт загрузка, пожалуйста не отключайте модуль', id=wx.ID_ANY,
                                            size=(270, 20), pos=(15, 10))
        self.progressBar = wx.Gauge(self, id=wx.ID_ANY, range=100, size=(270, 20), pos=(15, 35))

        self.statusText = wx.StaticText(self, pos=(10,70), size=(270, 20), style=(wx.ALIGN_CENTRE_HORIZONTAL),
                                        label='0%')

        self.Bind(wx.EVT_CLOSE, self.closeDialog)
        self.loadThred = Thread(target = self._modulOpject.load_hex_mk201_CRC, args=(self.hexFilePath, '0')) # init loading thread
        # wx.EVT_CLOSE(self, self.closeDialog)

        self.Bind(self._modulOpject.EVT_UPDATE, self.loadStatus)
        self.Bind(self._modulOpject.LEN_CRC, self.setPartLen)

        wx.CallAfter(self.startThread)



    def closeDialog(self, event):
        self._modulOpject.stopLoadHex = True
        if self.downloadStatus == True:
            self.Destroy()
        else:
            pass

    def startThread(self):
        self.loadThred.start()

    def setPartLen(self, msg):
        partLen = msg.GetValue()
        self.partLen = partLen
        self.partInPercent = 100 / float(self.partLen)

    def setStatusText(self, text):
        self.statusText.SetLabel(text)

    def loadStatus(self, msg):
        answer = msg.GetValue()
        if (type(answer) == int):
            self.progressBar.SetValue((answer - 1) * self.partInPercent) # FIXME: почему-та иногда падает на этом месте, wx ругается на то что часть объекта была удаленаи доступ к атрибуту не возможен
            self.setStatusText('{}%'.format( int((answer - 1)*self.partInPercent)) )
        if (type(answer) is str):
            # print answer
            # if 'Download' in str(answer):
            #     # print('Download success')
            # if 'Done' in answer:
            #     downloadStatusMsg = 'Download success'
            # else:
            #     downloadStatusMsg = 'Download canceled. Error: %s. ' % str(answer)
            # проверка на разбрикивиние и само разбрикивиние
            # if not(answer == "Download canceled"):
            if "error" in answer:
                # print "Error" * 5
                dialog = wx.MessageBox(answer, u'Ошибка!', wx.OK | wx.ICON_INFORMATION)
                self.Destroy()
                return 0
            time.sleep(5) # ожидание для того чтобы в модуле прошла начальная инициализация и он смог отвечать
            downloadStatusMsg = 'Download success'
            self.setStatusText(downloadStatusMsg)
            # print(downloadStatusMsg)
            self.downloadStatus = True
            self.closeDialog(1)
            # self.Destroy()
