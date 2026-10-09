@echo off
if exist "%USERPROFILE%\.scripts\brightness_tool.py" (
    python -u "%USERPROFILE%\.scripts\brightness_tool.py" %*
) else (
    python -u "%~dp0..\scripts\brightness_tool.py" %*
)
