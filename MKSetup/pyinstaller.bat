
rmdir /S /Q build dist

rem кириллица в пути к папке с проектом не допускается. 
python c:/Python27/Lib/pyinstaller/pyinstaller.py  --noconsole gui.py
rem python d:\work\python\Lib\pyinstaller\pyinstaller.py --name=MK500setup --runtime-hook= --onefile --noconsole gui.py
rem python c:/Python27/Lib/pyinstaller/pyinstaller.py --name=configurator --onefile terminal.py
rem python c:/Python27/Lib/pyinstaller/utils/Build.py configurator.spec
rem copy dist\configurator.exe .

