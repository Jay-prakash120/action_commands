@echo off
if exist "%USERPROFILE%\.scripts\wifi_tool.py" (
    python -u "%USERPROFILE%\.scripts\wifi_tool.py" %*
) else (
    python -u "%~dp0..\scripts\wifi_tool.py" %*
)
