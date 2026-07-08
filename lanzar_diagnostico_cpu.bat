@echo off
setlocal

set "ROOT=%~dp0"
set "HOST=127.0.0.1"
set "PORT=8000"
set "PHP_EXE="

if exist "%ROOT%php\php.exe" set "PHP_EXE=%ROOT%php\php.exe"

if not defined PHP_EXE for %%I in (php.exe) do set "PHP_EXE=%%~$PATH:I"

if not defined PHP_EXE (
    echo No se encontro php.exe.
    echo Coloca php.exe en PATH o en .\php\php.exe dentro del proyecto.
    pause
    exit /b 1
)

pushd "%ROOT%"
start "DiagnosticoCpuWeb" "%PHP_EXE%" -S %HOST%:%PORT%
timeout /t 2 /nobreak >nul
start "" "http://%HOST%:%PORT%/?run=1"
echo Servidor iniciado en http://%HOST%:%PORT%/
echo Cierra la ventana titulada DiagnosticoCpuWeb para detenerlo.
popd
exit /b 0