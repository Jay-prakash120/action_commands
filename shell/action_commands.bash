#!/usr/bin/env bash
# ==============================================================================
# Action Commands - Shell Definitions & Autocompletions (Git Bash / Bash)
# ==============================================================================

# Determine scripts directory (installed in ~/.scripts or relative to repo)
if [ -d "$HOME/.scripts" ] && [ -f "$HOME/.scripts/power_tools.py" ]; then
  ACTION_SCRIPTS_DIR="$HOME/.scripts"
else
  ACTION_SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" && pwd)"
fi

# Safe PC Shutdown: closes user apps, waits for Enter, then powers off
shutdown() {
  python -u "$ACTION_SCRIPTS_DIR/power_tools.py" shutdown "$@"
}

# Safe PC Restart: closes user apps, waits for Enter, then reboots
restart() {
  python -u "$ACTION_SCRIPTS_DIR/power_tools.py" restart "$@"
}

# Kill any process holding a specific port (e.g. killport 3000)
killport() {
  python -u "$ACTION_SCRIPTS_DIR/power_tools.py" killport "$@"
}

# Lock Windows workstation
lock() {
  echo -e "\033[1;33m🔒  Locking Windows workstation...\033[0m"
  sleep 0.2
  rundll32.exe user32.dll,LockWorkStation
}

# Open Windows Explorer in current directory or specified path
here() {
  explorer.exe "${1:-.}"
}

# Restart Windows Explorer / taskbar
restartexplorer() {
  echo -e "\033[1;36m🔄  Restarting Windows Explorer / Taskbar...\033[0m"
  taskkill //F //IM explorer.exe >/dev/null 2>&1
  start explorer.exe
  echo -e "\033[1;32m✔   Windows Explorer restarted successfully.\033[0m"
}

# Show Local and Public IP
myip() {
  python -u "$ACTION_SCRIPTS_DIR/myip_tool.py" "$@"
}

# Flush DNS Cache
flushdns() {
  echo -e "\033[1;36m🌊  Flushing Windows DNS Resolver Cache...\033[0m"
  ipconfig.exe /flushdns >/dev/null 2>&1
  echo -e "\033[1;32m✔   DNS cache flushed successfully.\033[0m"
}

# Wi-Fi Manager
wifi() {
  python -u "$ACTION_SCRIPTS_DIR/wifi_tool.py" "$@"
}

# Screen Brightness Control (interactive slider or direct level)
bright() {
  python -u "$ACTION_SCRIPTS_DIR/brightness_tool.py" "$@"
}
brightness() {
  bright "$@"
}

# Windows Night Light Control
nl() {
  python -u "$ACTION_SCRIPTS_DIR/nightlight_tool.py" "$@"
}
nightlight() {
  nl "$@"
}

# Windows Mobile Hotspot Control
hotspot() {
  python -u "$ACTION_SCRIPTS_DIR/hotspot_tool.py" "$@"
}

# ==============================================================================
# Autocompletion for Custom Commands
# ==============================================================================

_power_tools_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local opts="--now --dry-run --force"
  COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
}
complete -F _power_tools_complete shutdown restart

_killport_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local common_ports="3000 3001 4000 4200 5000 5173 8000 8080 8888 9000"
  COMPREPLY=( $(compgen -W "${common_ports}" -- "${cur}") )
}
complete -F _killport_complete killport

_wifi_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local opts="list connect on off status"
  COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
}
complete -F _wifi_complete wifi

_nl_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local opts="on off status toggle"
  COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
}
complete -F _nl_complete nl nightlight

_hotspot_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local prev="${COMP_WORDS[COMP_CWORD-1]}"
  if [ "$prev" = "band" ]; then
    COMPREPLY=( $(compgen -W "2.4 5 any" -- "${cur}") )
  else
    COMPREPLY=( $(compgen -W "on off status toggle band" -- "${cur}") )
  fi
}
complete -F _hotspot_complete hotspot

_bright_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local opts="+10 -10 +20 -20 25 50 75 100"
  COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
}
complete -F _bright_complete bright brightness
 
_myip_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local opts="-r --refresh -f"
  COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
}
complete -F _myip_complete myip

