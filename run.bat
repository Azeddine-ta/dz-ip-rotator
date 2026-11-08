@echo off
title Algérie Télécom IP Rotator & Route Optimizer
chcp 65001 >nul
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python change_ip.py %*
    goto end
)

where python3 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python3 change_ip.py %*
    goto end
)

echo [ERROR] Python was not found on your system!
echo Please install Python from https://www.python.org/
echo (Make sure to check "Add Python to PATH" during installation)
echo.
pause

:end

