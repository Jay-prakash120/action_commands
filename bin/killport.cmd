@echo off
if exist "%USERPROFILE%\.scripts\power_tools.py" (
    python -u "%USERPROFILE%\.scripts\power_tools.py" killport %*
) else (
    python -u "%~dp0..\scripts\power_tools.py" killport %*
)
