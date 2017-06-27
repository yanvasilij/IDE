#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@brief IDE for mk200 PLC
@Author yanvasilij
"""
import __builtin__
import os
import sys

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
            ('MK200ModubsRequest', _('MK200 Modbus master request'), _('Plugin for MK201'), 'mk200modules.ModbusMaster.MK200ModbusRequestFile')]

        features.libraries = [
            ('Native', 'NativeLib.NativeLibrary'),
            ('MK200',  'mk200libs.MK200Library'),
            ('MK200Modbus',  'mk200libs.MK200Modbus')]

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
        # PC = BeremizIDE.ProjectController
        #
        # BeremizIDE.ProjectController.IDEFrame.ConnectionStatusBar.SetStatusText(
        #     _("Connected to URI: %s") % self.BeremizRoot.getURI_location().strip(), 1)
        # PC.AppFrame.ConnectionStatusBar.SetStatusText(self.GetTextStatus(status), 2)
        # a = Beremiz.IDEFrame.
    # def .AppFrame.ConnectionStatusBar.SetStatusText('kek', 2)


if __name__ == '__main__':
    beremizApp = MK200Beremiz()
    beremizApp.Start()
