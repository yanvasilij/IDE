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
        objFileDir = objFile + r'/beremizStm32Port/CMakeFiles/BeremizPort.elf.dir'

        additionalobjects = []

        sourceDir = objFileDir + r'/source/common/src'
        additionalobjects = additionalobjects + ["\"" + sourceDir + r'/syscalls.c.obj' + "\""]

        runTime = "\"" + objFile + r'/beremizStm32Port/librunTime.a' + "\""
        additionalobjects = additionalobjects + [runTime]

        stm32_ldflags = self.getSTM32Config("ldflags")
        ldscript = ['-T'] + ["\"" + objFile + r'/beremizStm32Port/linkScript/STM32F407ZG_FLASH.ld' + "\""] #[os.path.dirname(os.path.realpath(__file__)) + r'/port/STM32F407ZG_FLASH.ld']
        return additionalobjects + toolchain_gcc.getBuilderLDFLAGS(self) + stm32_ldflags + ldscript# + ["-shared"]

    def getBuilderCFLAGS(self):
        base_folder = os.path.dirname(os.path.realpath(__file__)) + r'\..\..'
        includePathes = [r'-I ' + "\"" + base_folder + r'\beremizStm32Port\inc' + "\""]
        """ Adding matiec\lib\C\ """
        includePathes.append(r'-I' + "\"" + base_folder +r'\matiec\lib\C' + "\"")
        """ Adding folder ./inc and ./src to include pathes """
        additionincludepath = os.path.split(self.exe_path)[0]
        additionincludepath = os.path.split(additionincludepath)[0]
        incFolder = os.path.join(additionincludepath, "inc")
        srcFolder = os.path.join(additionincludepath, "src")
        buildFolder = os.path.join(additionincludepath, "build")
        includePathes.append(r'-I' + "\"" + incFolder + "\"")
        includePathes.append(r'-I' + "\"" + srcFolder + "\"")
        includePathes.append(r'-I' + "\"" + buildFolder + "\"")
        stm32_cflags = self.getSTM32Config("cflags") + includePathes
        return toolchain_gcc.getBuilderCFLAGS(self) + stm32_cflags # + ["-fPIC"]

    @staticmethod
    def update_creation_time(path):
        f = open(path, "a")
        f.write(" ")
        f.seek(-1, os.SEEK_END)
        f.truncate()
        f.close()

    def build(self):
        srcDir = os.path.split(self.exe_path)[0]
        srcDir = os.path.split(srcDir)[0]
        srcDir = os.path.join(srcDir, "src")
        if os.path.isdir(srcDir):
            listOfSrcFiles = [f for f in os.listdir(srcDir) if os.path.isfile(os.path.join(srcDir, f))]
            listOfSrcFiles = [f for f in listOfSrcFiles if f.endswith(".c") or f.endswith(".cpp")]
            cfileAndCFlag = []
            for srcFile in listOfSrcFiles:
                fileName = os.path.join(srcDir, srcFile)
                """For forced recompilation there is need to update creation time"""
                self.update_creation_time(fileName)
                cfileAndCFlag.append((fileName, ''))
            cfileAndCFlag = ('', cfileAndCFlag, True)
            self.CTRInstance.LocationCFilesAndCFLAGS.append(cfileAndCFlag)
        return toolchain_gcc.build(self)

_base_path = os.path.split(__file__)[0]
mk200targets = {'MKLogik200': {'code': {'plc_MKLogik200_main.c': os.path.join(_base_path, 'plc_MKLogik200_main.c')},
                               'class': lambda: MKLogik200_target, 'xsd':os.path.join(_base_path, 'XSD')}}

