@echo off
setlocal

REM Acessa automaticamente a pasta onde este arquivo esta salvo
cd /d "%~dp0"

echo ==========================================
echo CONFIGURACAO DO AMBIENTE DO PROJETO
echo ==========================================
echo.

REM Verifica se o ambiente virtual ja existe
if exist ".venv\Scripts\python.exe" (
    echo O ambiente virtual .venv ja existe.
) else (
    echo Criando o ambiente virtual .venv...

    where py >nul 2>&1

    if not errorlevel 1 (
        py -3 -m venv .venv
    ) else (
        python -m venv .venv
    )

    if errorlevel 1 goto erro
)

echo.
echo Atualizando o pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip

if errorlevel 1 goto erro

echo.
echo Instalando as bibliotecas do projeto...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

if errorlevel 1 goto erro

echo.
echo ==========================================
echo AMBIENTE CONFIGURADO COM SUCESSO
echo ==========================================
echo.
echo A pasta .venv foi criada e as bibliotecas
echo necessarias foram instaladas.
echo.
pause
exit /b 0

:erro
echo.
echo ==========================================
echo ERRO NA CONFIGURACAO
echo ==========================================
echo.
echo Verifique se o Python esta instalado e
echo disponivel no PATH do Windows.
echo.
pause
exit /b 1