@echo off
setlocal

cd /d "%~dp0"

echo Validacao Fase 4 - Optotipos Profissional
echo.

if not exist Optotipos.exe (
    echo AVISO: Optotipos.exe nao encontrado nesta pasta.
) else (
    echo OK: Optotipos.exe encontrado.
)

if not exist Configurador.exe (
    echo AVISO: Configurador.exe nao encontrado nesta pasta.
) else (
    echo OK: Configurador.exe encontrado.
)

py --version >nul 2>nul
if errorlevel 1 (
    echo Python nao encontrado. Use o relatorio ja gerado em Logs\ValidacaoClinica_Fase4.md.
    exit /b 0
)

py ValidacaoClinica.py --saida Logs\ValidacaoClinica_Fase4.md --imprimir
if errorlevel 1 exit /b 1

echo.
echo Relatorio atualizado em Logs\ValidacaoClinica_Fase4.md

endlocal
