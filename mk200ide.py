#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@brief IDE for mk200 PLC
@Author yanvasilij
"""
import __builtin__
import os
import sys
import serial
import serial.tools.list_ports
import xml.etree.ElementTree as ET
_dist_folder = os.path.split(sys.path[0])[0]
_beremiz_folder = os.path.join(_dist_folder, "beremiz")
sys.path.append(_beremiz_folder)

from Beremiz import BeremizIDELauncher

class MK200Beremiz(BeremizIDELauncher):

    def __init__(self):
        BeremizIDELauncher.__init__(self)
        splashPath = os.path.dirname(os.path.realpath(__file__))
        splashPath = os.path.join(splashPath, "images", "splash.png")
        self.splashPath = splashPath

    def ImportModules(self):
        import features
        features.catalog = [
            ('c_ext', _('C extension'), _('Add C code accessing located variables synchronously'), 'c_ext.CFile'),
            ('MKLogic201', _('MKLogic 201'), _('Plugin for MK201'), 'mk200modules.MK201.MK201ModuleFile'),
            ('MK200CANOpen', _('MK200 CANOpen'), _('External MK200 modules'), 'mk200modules.MK200CANOpen.RootClass'),
            ('ModbusTCP master', _('ModbusTCP master'), _('ModbusTCP master'), 'mk200modules.ModbusTcpMaster.RootClass'),
            ('MK200ModubsRequest', _('MK200 Modbus master request'), _('Plugin for MK201'), 'mk200modules.ModbusMaster.MK200ModbusRequestFile')]

        features.libraries = [
            ('Native', 'NativeLib.NativeLibrary'),
            ('MK200',  'mk200libs.MK200Library'),
            ('MK200Modbus',  'mk200libs.MK200Modbus'),
            ('AdditionalConversionTypes',  'mk200libs.MK200AdditionalConversion')]

        from util.BitmapLibrary import AddBitmapFolder
        images = os.path.join(os.path.dirname(os.path.realpath(__file__)),"images")
        AddBitmapFolder(images)
        import targets
        from mk200targets import mk200targets
        targets.targets = {}
        targets.targets.update(mk200targets)
        BeremizIDELauncher.ImportModules(self)
        import BeremizIDE
        BeremizIDE.ProjectController.GetDefaultTargetName = lambda x: "MKLogik200"
        import connectors
        import mk200connectors
        connectors.connectors = {}
        connectors.connectors["MK200"] = lambda: mk200connectors.MK200_connector_factory
        connectors.connectors["MK201"] = lambda: mk200connectors.MK201_connector_factory

        """ Adding creation folders inc and src after creation new project """
        NewProject = BeremizIDE.ProjectController.NewProject
        def NewProjectWrapper (self_, ProjectPath, BuildPath=None):
            rez = NewProject(self_, ProjectPath, BuildPath)
            if rez == None:
                includeDir = os.path.join(ProjectPath, "inc")
                sourceDir = os.path.join(ProjectPath, "src")
                if not os.path.exists(includeDir):
                    os.mkdir(includeDir)
                if not os.path.exists(sourceDir):
                    os.mkdir(sourceDir)
            return rez
        BeremizIDE.ProjectController.NewProject = NewProjectWrapper
        # в списко методов PorjectController-а добавляю метод вызова конфигуратора для МК201
        # in the list of methods ProductController I add a method of a call of the configurator for MK201
        BeremizIDE.ProjectController._callConfigurator = self._Configurator
        BeremizIDE.ProjectController.StatusMethods.append({"bitmap" : "configurator",
                                   "shown" : True,
                                   "name" : _("configurator"),
                                   "tooltip" : u"Конфигуратор MK201Setup",
                                   "method" : '_callConfigurator'})
        BeremizIDE.ProjectController._setMK201Connector = self._setMK201Connector
        BeremizIDE.ProjectController.StatusMethods.insert(-2,{"bitmap" : "set_port",
                                   "shown" : True,
                                   "name" : _("_setMK201Connector"),
                                   "tooltip" : u"Конфигуратор MK201Setup",
                                   "method" : '_setMK201Connector'})
        BeremizIDE.ProjectController._Connect_MK201 = self._Connect_MK201
        for element in BeremizIDE.ProjectController.StatusMethods:
            for key in element.keys():
                if element["method"] == "_Connect":
                    element["method"] = "_Connect_MK201"


    def _setMK201Connector(self):
        from mk201connectorDialog import ConnectDialog
        xmlPath = os.path.join(self.frame.CTR.ProjectPath, "beremiz.xml")
        tree = ET.parse(xmlPath)
        root = tree.getroot()
        connectDialog = ConnectDialog(self.frame)
        res = connectDialog.ShowModal()
        # 5100 это значение wx.ID_OK, которое возвращает мой диалог, сделал так чтобы не импортировать из wx, т.к. проблема с
        # выбором версии wx-а
        if res == 5100: # it's magic, magic, ma-a-a-gic!
            comPort = connectDialog.getPort()
            connectDialog.Destroy()
            root.set("URI_location", "MK201://{}".format(comPort))
            tree.write(xmlPath)
            self.frame.CTR.LoadXMLParams()
            self.frame.CTR.RefreshConfNodesBlockLists()
            return 1
        elif res == 5101:
            return 0

    def _Connect_MK201(self):
        xmlPath = os.path.join(self.frame.CTR.ProjectPath,"beremiz.xml")
        tree = ET.parse(xmlPath)
        root = tree.getroot()
        curUri = root.get('URI_location')
        if curUri is None:
            res = self._setMK201Connector()
            if res == 0:
                return 1
        # врзможно на отображение метовод требуется наложить условие, как это сделано в  .CTR._Connect()
        self.frame.CTR.ShowMethod("_setMK201Connector", False)
        self.frame.CTR.ShowMethod("_Connect_MK201", False)
        self.frame.CTR._Connect()
        self.frame.CTR.UpdateMethodsFromPLCStatus()

    def _Configurator(self):
        from MKSetup.configurator_MK201setup import Configurator_MK201
        projectPath = self.frame.CTR.ProjectPath + os.path.sep
        serialObject = None
        connector = self.frame.CTR._connector
        if not(connector is None):
            serialObject = connector.SerialConnection
        myDialog = Configurator_MK201(parent=self.frame, modulObject=serialObject, projectPath=projectPath)
        res = myDialog.ShowModal()




if __name__ == '__main__':
    beremizApp = MK200Beremiz()
    beremizApp.Start()
