echo off
REM Default is Python 3.9

if "%1"=="3.6" goto py_36
if "%1"=="3.7" goto py_37
if "%1"=="3.8" goto py_38
if "%1"=="3.9" goto py_39
if "%1"=="3.10" goto py_310
if "%1"=="3.11" goto py_311
if "%1"=="3.12" goto py_312
if "%1"=="3.13" goto py_313
if "%1"=="3.14" goto py_314

:py_39
venv-token3.9\scripts\activate
goto end

:py_36
venv-token3.6\scripts\activate
goto end

:py_37
venv-token3.7\scripts\activate
goto end 

:py_38
venv-token3.8\scripts\activate
goto end

:py_310
venv-token3.10\scripts\activate
goto end

:py_311
venv-token3.11\scripts\activate
goto end

:py_312
venv-token3.12\scripts\activate
goto end

:py_313
venv-token3.13\scripts\activate
goto end

:py_314
venv-token3.14\scripts\activate
goto end

:end
