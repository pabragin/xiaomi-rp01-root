@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 --version >nul 2>&1
if not errorlevel 1 (
    py -3 run.py
    goto done
)
python --version >nul 2>&1
if not errorlevel 1 (
    python run.py
    goto done
)
echo Установите Python 3 с https://www.python.org/downloads/windows/
echo При установке включите Add python.exe to PATH, затем повторите запуск.
:done
pause
