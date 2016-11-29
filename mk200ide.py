#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@brief IDE for mk200 PLC
@Author yanvasilij
"""
__author__ = 'yanvasilij'

import __builtin__
from yaplcide import *

_dist_folder = os.path.split(sys.path[0])[0]
_beremiz_folder = os.path.join(_dist_folder, "beremiz")
sys.path.append(_beremiz_folder)
yaplc_dir = os.path.dirname(os.path.realpath(__file__))

features.catalog = [
    ('canfestival', _('CANopen support'), _('Map located variables over CANopen'), 'canfestival.canfestival.RootClass'),
    ('c_ext', _('C extension'), _('Add C code accessing located variables synchronously'), 'c_ext.CFile'),
    ('py_ext', _('Python file'), _('Add Python code executed asynchronously'), 'py_ext.PythonFile'),
    ('wxglade_hmi', _('WxGlade GUI'), _('Add a simple WxGlade based GUI.'), 'wxglade_hmi.WxGladeHMI'),
    ('svgui', _('SVGUI'), _('Experimental web based HMI'), 'svgui.SVGUI'),
    ('MK200ModbusSlave', _('MK200 Modbus slave'), _('Plugin for modbus slave'), 'mk200modules.ModbusSlave.ModbusSlaveFile'),
    ('MKLogic201', _('MKLogic 201'), _('Plugin for MK201'), 'mk200modules.MK201.MK201ModuleFile'),
    ('MK200ModubsRequest', _('MK200 Modbus master request'), _('Plugin for MK201'), 'mk200modules.ModbusMaster.MK200ModbusRequestFile') ]

from mk200targets import mk200targets
targets.targets.update(mk200targets)

if __name__ == '__main__':

    projectOpen = None
    buildpath = None

    if os.path.exists("BEREMIZ_DEBUG"):
        __builtin__.__dict__["BMZ_DBG"] = True
    else:
        __builtin__.__dict__["BMZ_DBG"] = False

    if wx.VERSION >= (3, 0, 0):
        app = wx.App(redirect=BMZ_DBG)
    else:
        app = wx.PySimpleApp(redirect=BMZ_DBG)

    # Ready to show default splash screen
    splash = ShowYAPLCSplashScreen()

    # this would run a new application with window (Beremiz)
    app.SetAppName('beremiz')
    if wx.VERSION < (3, 0, 0):
        wx.InitAllImageHandlers()

    from util.misc import InstallLocalRessources

    InstallLocalRessources(_beremiz_folder)

from Beremiz import *

# This is where we start our application
if __name__ == '__main__':

    from threading import Thread, Timer, Semaphore

    projectOpen = None
    buildpath = None

    # Command log for debug, for viewing from wxInspector
    if BMZ_DBG:
        __builtins__.cmdlog = []

    # Install a exception handle for bug reports
    # AddExceptHook(os.getcwd(), __version__)
    from util.BitmapLibrary import AddBitmapFolder
    AddBitmapFolder(os.path.join(os.path.dirname(__file__), "images"))

    frame = Beremiz(None, projectOpen, buildpath)
    if splash:
        splash.Close()

    frame.Show()
    app.MainLoop()
