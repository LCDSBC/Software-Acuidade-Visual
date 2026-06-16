@echo off
setlocal

cd /d "%~dp0"

echo Teste em equipamento real - Optotipos Profissional
echo.
echo Este roteiro deve ser executado no computador Windows conectado ao monitor/TV/projetor real.
echo.

if not exist Dados\validacao_campo.json (
    echo Criando Dados\validacao_campo.json a partir do modelo...
    copy /Y Dados\modelo_validacao_campo.json Dados\validacao_campo.json >nul
    echo.
    echo Edite Dados\validacao_campo.json com:
    echo - modelo do computador;
    echo - versao do Windows;
    echo - modelo da TV/monitor;
    echo - resolucao;
    echo - medidas fisicas da regua e do optotipo;
    echo - checks operacionais.
    echo.
)

echo Verificando executaveis...
if exist Optotipos.exe (
    echo OK: Optotipos.exe encontrado.
) else (
    echo AVISO: Optotipos.exe nao encontrado nesta pasta.
)

if exist Configurador.exe (
    echo OK: Configurador.exe encontrado.
) else (
    echo AVISO: Configurador.exe nao encontrado nesta pasta.
)

echo.
echo Gerando relatorio inicial...
call validar_fase4_windows.bat
if errorlevel 1 exit /b 1

echo.
echo Abrindo arquivos de apoio...
start "" notepad Dados\validacao_campo.json
if exist Logs\ValidacaoClinica_Fase4.md start "" notepad Logs\ValidacaoClinica_Fase4.md

echo.
echo Passos fisicos obrigatorios:
echo 1. Abrir Configurador.exe e calibrar a regua virtual de 100 mm.
echo 2. Abrir Optotipos.exe.
echo 3. Medir o optotipo 20/20 na distancia configurada.
echo 4. Testar TelaUnica, DuasTelas e Espelhamento.
echo 5. Testar inversao horizontal/vertical se usar espelho/projetor.
echo 6. Testar Wireless pelo celular na mesma rede Wi-Fi.
echo 7. Preencher Dados\validacao_campo.json e rodar este script novamente.
echo.
echo Quando todos os dados estiverem preenchidos, a secao "Confianca clinica" indicara o status.

endlocal
