@echo off
if exist "%USERPROFILE%\.scripts\myip_tool.py" (
    python -u "%USERPROFILE%\.scripts\myip_tool.py" %*
) else (
    python -u "%~dp0..\scripts\myip_tool.py" %*
)
