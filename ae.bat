echo off
REM Default is Python 3.8

if "%1"=="3.6" goto py_36
if "%1"=="3.7" goto py_37
if "%1"=="3.12" goto py_312

:py_38
venv-token3.8scripts\activate
goto end

:py_312
venv-token3.12\scripts\activate
goto end

:py_36
venv-token3.6\scripts\activate
goto end

:py_37
venv-token3.7\scripts\activate

:end
