@echo off
setlocal

cd /d "%~dp0"

echo Instalando dependencias de build...
py -m pip install -r ..\requirements-build.txt
if errorlevel 1 exit /b 1

echo Gerando Optotipos.exe...
py -m PyInstaller --clean --noconfirm Optotipos.spec
if errorlevel 1 exit /b 1

echo Gerando Configurador.exe...
py -m PyInstaller --clean --noconfirm Configurador.spec
if errorlevel 1 exit /b 1

copy /Y dist\Optotipos.exe .\Optotipos.exe
copy /Y dist\Configurador.exe .\Configurador.exe

if not exist ..\Configurador mkdir ..\Configurador
copy /Y .\Configurador.exe ..\Configurador\Configurador.exe

echo.
echo Build concluido.
echo Executaveis:
echo   %cd%\Optotipos.exe
echo   %cd%\Configurador.exe
echo.
echo Copie a pasta Optotipos inteira para pendrive, notebook, desktop ou mini PC.

endlocal
