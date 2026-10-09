@echo off
if exist "%USERPROFILE%\.scripts\hotspot_tool.py" (
    python -u "%USERPROFILE%\.scripts\hotspot_tool.py" %*
) else (
    python -u "%~dp0..\scripts\hotspot_tool.py" %*
)
