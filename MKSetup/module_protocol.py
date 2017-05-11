__author__ = 'Yanikeev-as'


import wx

EVT_PROGRESS_ID = wx.NewId()

def EVT_PROGRESS(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_PROGRESS_ID, func)

class ProgressEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_PROGRESS_ID)
        self.data = data


# классы описывающие протоколы работы с модулями MK200

class MK200Protocol(object):
    def __init__(self, serialObject):
        self.serialObject = serialObject

    def loadHex_MK201(self, hexfile):


    def stringSpliter(self, string):
        data_len = len(string)
        step_len = data_len / 10
        data_list = []
        for i in range(0, data_len, step_len):
            data_list.append(string[i:i+step_len])
        return data_list