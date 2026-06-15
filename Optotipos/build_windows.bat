@echo off
setlocal

cd /d "%~dp0"

echo Verificando Python...
py --version
if errorlevel 1 (
    echo Python nao encontrado. Instale Python 3.10+ para gerar os executaveis.
    exit /b 1
)

echo Instalando dependencias de build...
py -m pip install -r ..\requirements-build.txt
if errorlevel 1 exit /b 1

echo Executando testes automatizados...
cd /d "%~dp0.."
py -m unittest discover -s tests
if errorlevel 1 exit /b 1
cd /d "%~dp0"

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

echo Gerando pacote portatil para teste...
if exist dist\Optotipos_Portatil rmdir /S /Q dist\Optotipos_Portatil
mkdir dist\Optotipos_Portatil
xcopy /E /I /Y Configuracoes dist\Optotipos_Portatil\Configuracoes
xcopy /E /I /Y Perfis dist\Optotipos_Portatil\Perfis
xcopy /E /I /Y Testes dist\Optotipos_Portatil\Testes
xcopy /E /I /Y Dados dist\Optotipos_Portatil\Dados
xcopy /E /I /Y Backup dist\Optotipos_Portatil\Backup
xcopy /E /I /Y Logs dist\Optotipos_Portatil\Logs
copy /Y Optotipos.exe dist\Optotipos_Portatil\Optotipos.exe
copy /Y Configurador.exe dist\Optotipos_Portatil\Configurador.exe

echo Gerando relatorio de validacao inicial...
py ValidacaoClinica.py --saida Logs\ValidacaoClinica_Fase4.md
if errorlevel 1 exit /b 1
copy /Y Logs\ValidacaoClinica_Fase4.md dist\Optotipos_Portatil\Logs\ValidacaoClinica_Fase4.md

echo.
echo Build concluido.
echo Executaveis:
echo   %cd%\Optotipos.exe
echo   %cd%\Configurador.exe
echo Pacote portatil:
echo   %cd%\dist\Optotipos_Portatil
echo Relatorio:
echo   %cd%\Logs\ValidacaoClinica_Fase4.md
echo.
echo Copie a pasta Optotipos inteira para pendrive, notebook, desktop ou mini PC.

endlocal
