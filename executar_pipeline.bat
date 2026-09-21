@echo off

title Pipeline ENADE 2023

cd /d "%~dp0"

echo ==========================================
echo PIPELINE DE DADOS - ENADE 2023
echo ==========================================
echo.

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo ERRO: ambiente virtual nao encontrado.
    echo Caminho esperado:
    echo %PYTHON_EXE%
    echo.
    echo Consulte o README para preparar o ambiente.
    pause
    exit /b 1
)

echo Iniciando a execucao dos notebooks...
echo.

"%PYTHON_EXE%" "%~dp0run_pipeline.py"

if errorlevel 1 (
    echo.
    echo ==========================================
    echo PIPELINE INTERROMPIDO COM ERRO
    echo ==========================================
    echo Consulte as mensagens apresentadas acima.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo PIPELINE CONCLUIDO COM SUCESSO
echo ==========================================
echo.
echo Banco criado em:
echo data\database\enade.duckdb
echo.

pause