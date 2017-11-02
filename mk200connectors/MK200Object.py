#!/usr/bin/env python
# -*- coding: utf-8 -*-

# YAPLC connector, based on LPCObject.py and LPCAppObjet.py
# from PLCManager


import os
import sys
    
if __name__ == "__main__":
    __builtins__.BMZ_DBG = True
    append_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    sys.path.append(append_path)

from threading import Lock
import ctypes
from MK200Proto import *
from targets.typemapping import LogLevelsCount, TypeTranslator, UnpackDebugBuffer
from util.ProcessLogger import ProcessLogger

import pdb


class MK200Object():
    def __init__(self, libfile, confnodesroot, comportstr):

        self.IsProgramming = False
        self.TransactionLock = Lock()
        self.PLCStatus = "Disconnected"
        self.libfile = libfile
        self.confnodesroot = confnodesroot
        self.PLCprint = confnodesroot.logger.writeyield
        self._Idxs = []

        self.TransactionLock.acquire()
        try:
            self.connect(libfile, comportstr, 115200, 20)
        except Exception, e:
            self.confnodesroot.logger.write_error(str(e) + "\n")
            self.SerialConnection = None
            self.PLCStatus = None  # ProjectController is responsible to set "Disconnected" status
        self.TransactionLock.release()

    def connect(self, libfile, comportstr, baud, timeout):
        self.SerialConnection = MK200Proto(libfile, comportstr, 115200, 1)

    def _HandleSerialTransaction(self, transaction, must_do_lock):
        res = None
        failure = None
        # Must acquire the lock
        if must_do_lock:
            self.TransactionLock.acquire()
        if self.SerialConnection is not None:
            # Do the job
            try:
                self.PLCStatus, res = \
                    self.SerialConnection.HandleTransaction(transaction)
            except YAPLCProtoError, e:
                if self.SerialConnection is not None:
                    self.SerialConnection.Close()
                    self.SerialConnection = None
                failure = str(transaction) + str(e)
                self.PLCStatus = None  # ProjectController is responsible to set "Disconnected" status
            except Exception, e:
                failure = str(transaction) + str(e)
        # Must release the lock
        if must_do_lock:
            self.TransactionLock.release()
        return res, failure

    def HandleSerialTransaction(self, transaction):
        res = None;
        failure = None;
        res, failure = self._HandleSerialTransaction(transaction, True)
        if failure is not None:
            # print(failure + "\n")
            self.confnodesroot.logger.write_warning(failure + "\n")
        return res

    def StartPLC(self):
        self.HandleSerialTransaction(STARTTransaction())

    def StopPLC(self):
        self.HandleSerialTransaction(STOPTransaction())
        return True

    def NewPLC(self, md5sum, data, extrafiles):
        self.IsProgramming = True
        if self.MatchMD5(md5sum) == False:
            res = None;
            failure = None;

            self.confnodesroot.logger.write_warning(
                _("Will now upload firmware to PLC.\nThis may take some time, don't close the program.\n"))
            self.TransactionLock.acquire()
            # Will now boot target
            self._HandleSerialTransaction(BOOTTransaction(), False)
            self._HandleSerialTransaction(SetMd5Transaction(md5sum), False)
            time.sleep(0.1)
            res, failure = self._HandleSerialTransaction(DownloadTransaction(data, self.confnodesroot), False)
            time.sleep(3.0)
            # Close connection
            self.SerialConnection.Close()
            self.IsProgramming = False
            # bootloader command
            # data contains full command line except serial port string which is passed to % operator
            # Reopen connection
            self.SerialConnection.Open()
            self.TransactionLock.release()

            if failure is not None:
                self.confnodesroot.logger.write_warning(failure + "\n")
                return False
            else:
                self.StopPLC();
                return self.PLCStatus == "Stopped"
        else:
            self.IsProgramming = False
            self.StopPLC();
            return self.PLCStatus == "Stopped"

    def GetPLCstatus(self):
        if self.IsProgramming:
            return "Stopped", [1]
        res = self.HandleSerialTransaction(GET_LOGCOUNTSTransaction())
        if res is None:
            return None, [1]
        else:
            return "Stopped", [1]

    def MatchMD5(self, MD5):
        md5inplc = self.HandleSerialTransaction(GetMD5Transaction())
        return md5inplc == MD5

    def SetTraceVariablesList(self, idxs):
        """
        Call ctype imported function to append
        these indexes to registred variables in PLC debugger
        """
        if idxs:
            buff = ""
            # keep a copy of requested idx
            self._Idxs = idxs[:]
            for idx, iectype, force in idxs:
                idxstr = ctypes.string_at(
                    ctypes.pointer(
                        ctypes.c_uint32(idx)), 4)
                if force != None:
                    c_type, unpack_func, pack_func = TypeTranslator.get(iectype, (None, None, None))
                    forced_type_size = ctypes.sizeof(c_type) \
                        if iectype != "STRING" else len(force) + 1
                    forced_type_size_str = chr(forced_type_size)
                    forcestr = ctypes.string_at(
                        ctypes.pointer(
                            pack_func(c_type, force)),
                        forced_type_size)
                    buff += idxstr + forced_type_size_str + forcestr
                else:
                    buff += idxstr + chr(0)
        else:
            buff = ""
            self._Idxs = []
        self.HandleSerialTransaction(SET_TRACE_VARIABLETransaction(buff))

    def GetTraceVariables(self):
        """
        Return a list of variables, corresponding to the list of required idx
        """
        strbuf = self.HandleSerialTransaction(GET_TRACE_VARIABLETransaction())
        TraceVariables = []
        if strbuf is not None and len(strbuf) >= 4 and self.PLCStatus == "Started":
            size = len(strbuf) - 4
            ctick = ctypes.create_string_buffer(strbuf[:4])
            tick = ctypes.cast(ctick, ctypes.POINTER(ctypes.c_uint32)).contents
            if size > 0:
                cbuff = ctypes.create_string_buffer(strbuf[4:])
                buff = ctypes.cast(cbuff, ctypes.c_void_p)
                TraceBuffer = ctypes.string_at(buff.value, size)
                # Add traces
                TraceVariables.append((tick.value, TraceBuffer))
        return self.PLCStatus, TraceVariables

    def ResetLogCount(self):
        self.HandleSerialTransaction(RESET_LOGCOUNTSTransaction())

    def GetLogMessage(self, level, msgid):
        strbuf = self.HandleSerialTransaction(GET_LOGMSGTransaction(level, msgid))
        if strbuf is not None and len(strbuf) > 12:
            cbuf = ctypes.cast(
                ctypes.c_char_p(strbuf[:12]),
                ctypes.POINTER(ctypes.c_uint32))
            return (strbuf[12:],) + tuple(int(cbuf[idx]) for idx in range(3))
        return None

    def ForceReload(self):
        raise YAPLCProtoError("Not implemented")

    def RemoteExec(self, script, **kwargs):
        return (-1, "RemoteExec is not supported by YAPLC target!")


if __name__ == "__main__":
    """
    "C:\Program Files\Beremiz\python\python.exe" YAPLCObject.py
    """


    class TestLogger():
        def __init__(self):
            self.lock = Lock()

        def write(self, v):
            self.lock.acquire()
            # print(v)
            self.lock.release()

        def writeyield(self, v):
            self.lock.acquire()
            # print(v)
            self.lock.release()

        def write_warning(self, v):
            if v is not None:
                self.lock.acquire()
                msg = "Warning: " + v
                # print(msg)
                self.lock.release()

        def write_error(self, v):
            if v is not None:
                self.lock.acquire()
                msg = "Warning: " + v
                # print(msg)
                self.lock.release()


    class TestRoot:
        def __init__(self):
            self.logger = TestLogger()


    if os.name in ("nt", "ce"):
        lib_ext = ".dll"
    else:
        lib_ext = ".so"

    TstLib = os.path.dirname(os.path.realpath(__file__)) + "/../../../YaPySerial/bin/libYaPySerial" + lib_ext

    TstRoot = TestRoot()
    # print "Construct PLC..."
    TstPLC = YAPLCObject(TstLib, TstRoot, "COM10")

    # print "Start PLC..."
    res = TstPLC.StartPLC()
    # print(res)

    # print "Get PLC status..."
    res = TstPLC.GetPLCstatus();
    print(res)

    print "MatchMD5..."
    res = TstPLC.MatchMD5("aaabbb")
    print(res)

    print "MatchMD5..."
    res = TstPLC.MatchMD5("2c2700c2c543f64e93747d21277de8fdUnknown#Uncnown#Uncnown")
    print(res)

    print "SetTraceVariablesList..."
    idxs = []
    idxs.append((0, "BOOL", 1))
    idxs.append((1, "BOOL", 1))
    res = TstPLC.SetTraceVariablesList(idxs)
    print(res)

    print "GetTraceVariables..."
    res = TstPLC.GetTraceVariables()
    print(res)

    print "GetLogMessage..."
    res = TstPLC.GetLogMessage(0, 0)
    print(res)

    print "ResetLogCount..."
    TstPLC.ResetLogCount()

    TstPLC.StopPLC()

    time.sleep(3)

