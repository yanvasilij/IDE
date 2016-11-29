"""
@brief Target class for mk200
@Author yanvasilij
"""
import os
from toolchain_gcc import toolchain_gcc

class MKLogik200_target(toolchain_gcc):
    dlopen_prefix = ""
    extension = ".elf"
    def getSTM32Config(self, flagsname):
        """ Get stm32-config from target parameters """
        stm32_config=self.CTRInstance.GetTarget().getcontent().getSTM32Config()
        if stm32_config:
            from util.ProcessLogger import ProcessLogger
            status, result, err_result = ProcessLogger(self.CTRInstance.logger,
                                                       stm32_config + " --skin=native --"+flagsname,
                                                       no_stdout=True).spin()
            if status:
                self.CTRInstance.logger.write_error(_("Unable to get STM32's %s \n")%flagsname)
            return [result.strip()]
        return []

    def getBuilderLDFLAGS(self):
        objFile = os.path.dirname(os.path.realpath(__file__))
        objFile = "".join(os.path.split(objFile)[0])
        objFile = "".join(os.path.split(objFile)[0])
        objFile = "".join(os.path.split(objFile)[0])
        objFileDir = objFile + r'/beremizStm32Port/CMakeFiles/BeremizPort.elf.dir'

        additionalobjects = []

        sourceDir = objFileDir + r'/source/src'
        additionalobjects = additionalobjects + [sourceDir + r'/syscalls.c.obj']

        runTime = objFile + r'/beremizStm32Port/librunTime.a'
        additionalobjects = additionalobjects + [runTime]

        stm32_ldflags = self.getSTM32Config("ldflags")
        ldscript = ['-T'] + [objFile + r'/beremizStm32Port/linkScript/STM32F407ZG_FLASH.ld'] #[os.path.dirname(os.path.realpath(__file__)) + r'/port/STM32F407ZG_FLASH.ld']
        return additionalobjects + toolchain_gcc.getBuilderLDFLAGS(self) + stm32_ldflags + ldscript# + ["-shared"]

    def getBuilderCFLAGS(self):
        includePathes = [r'-I ' + os.path.dirname(os.path.realpath(__file__)) + r'\beremizStm32Port\source\inc']
        includePathes.append(r'-I ' + os.path.dirname(os.path.realpath(__file__)) + r'\..\..\..\beremizStm32Port\modbusMasterLib\inc')
        includePathes.append(r'-I ' + os.path.dirname(os.path.realpath(__file__)) + r'\..\..\..\FreeModbus\xCpp\include')
        stm32_cflags = self.getSTM32Config("cflags") + includePathes
        return toolchain_gcc.getBuilderCFLAGS(self) + stm32_cflags # + ["-fPIC"]

_base_path = path.split(__file__)[0]
mk200targets = {'MKLogik200': {'code': {'plc_MKLogik200_main.c': path.join(_base_path, 'plc_MKLogik200_main.c')},
                               'class': MKLogik200_target, 'xsd':path.join(_base_path, 'XSD')}}

