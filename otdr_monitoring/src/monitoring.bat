@echo off
set PROJECT_ROOT=..\..
set VENVDIR=%PROJECT_ROOT%\.venv-windows

REM Check if the virtual environment directory exists
if exist "%VENVDIR%" (
    echo Using python virtualenv at %VENVDIR%
) else (
    python -m venv %VENVDIR%
    %VENVDIR%\Scripts\pip install -r requirements.txt
)

REM Add path to libusb-1.0.dll
set PATH=%PATH%;%PROJECT_ROOT%\3rdparty\libs

REM Run the python script
%VENVDIR%\Scripts\python __main__.py
