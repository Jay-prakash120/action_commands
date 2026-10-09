# ==============================================================================
# Action Commands - PowerShell / Windows Installer
# ==============================================================================

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Action Commands - Windows Setup" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

$scriptDir = $PSScriptRoot

# 1. Install python dependencies
Write-Host "`n[*] Installing Python packages..." -ForegroundColor Yellow
pip install -r "$scriptDir\requirements.txt" --quiet

# 2. Setup user directories
$userScripts = "$HOME\.scripts"
$userBin = "$HOME\bin"

if (-not (Test-Path $userScripts)) { New-Item -ItemType Directory -Path $userScripts -Force | Out-Null }
if (-not (Test-Path $userBin)) { New-Item -ItemType Directory -Path $userBin -Force | Out-Null }

Write-Host "[*] Copying scripts to $userScripts and wrappers to $userBin..." -ForegroundColor Yellow
Copy-Item -Path "$scriptDir\scripts\*" -Destination $userScripts -Recurse -Force
Copy-Item -Path "$scriptDir\bin\*" -Destination $userBin -Recurse -Force

# 3. Add ~/bin to user PATH if not present
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$userBin*") {
    Write-Host "[*] Adding $userBin to User PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$userBin", "User")
    $env:Path = "$env:Path;$userBin"
    Write-Host "[+] PATH updated." -ForegroundColor Green
}

# 4. Configure PowerShell Profile
$profilePath = $PROFILE
$profileDir = Split-Path -Path $profilePath
if (-not (Test-Path $profileDir)) { New-Item -ItemType Directory -Path $profileDir -Force | Out-Null }
if (-not (Test-Path $profilePath)) { New-Item -ItemType File -Path $profilePath -Force | Out-Null }

$completionScript = "$scriptDir\shell\profile_completions.ps1"
$importCmd = ". `"$completionScript`""

$existingContent = Get-Content -Path $profilePath -Raw -ErrorAction SilentlyContinue
if ($existingContent -notlike "*profile_completions.ps1*") {
    Write-Host "[*] Adding autocompletions to PowerShell profile ($profilePath)..." -ForegroundColor Yellow
    Add-Content -Path $profilePath -Value "`n# Action Commands Completion`n$importCmd`n"
    Write-Host "[+] Profile updated." -ForegroundColor Green
}

Write-Host "`n✨ Installation complete! Restart terminal or run '. `$PROFILE' to start." -ForegroundColor Green
