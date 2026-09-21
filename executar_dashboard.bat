@echo off
setlocal

title Dashboard ENADE 2023

cd /d "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
set "BANCO=%~dp0data\database\enade.duckdb"

if not exist "%PYTHON_EXE%" (
    echo ERRO: ambiente virtual nao encontrado.
    echo Execute primeiro configurar_ambiente.bat.
    pause
    exit /b 1
)

if not exist "%BANCO%" (
    echo ERRO: banco de dados nao encontrado.
    echo Execute primeiro executar_pipeline.bat.
    pause
    exit /b 1
)

echo Iniciando o dashboard...
echo O navegador sera aberto em http://127.0.0.1:8050
echo Para encerrar, feche esta janela.

"%PYTHON_EXE%" "%~dp0dashboard\app.py"

pause
