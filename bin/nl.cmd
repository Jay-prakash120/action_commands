@echo off
if exist "%USERPROFILE%\.scripts\nightlight_tool.py" (
    python -u "%USERPROFILE%\.scripts\nightlight_tool.py" %*
) else (
    python -u "%~dp0..\scripts\nightlight_tool.py" %*
)
