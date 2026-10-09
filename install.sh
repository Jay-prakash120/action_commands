#!/usr/bin/env bash
set -e

# ==============================================================================
# Action Commands - Git Bash / Bash Installer
# ==============================================================================

echo -e "\033[1;36m╭──────────────────────────────────────────────────╮\033[0m"
echo -e "\033[1;36m│  ⚡ Installing Action Commands for Windows       │\033[0m"
echo -e "\033[1;36m╰──────────────────────────────────────────────────╯\033[0m"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Install Python dependencies
echo -e "\n\033[1;33m[*] Installing Python dependencies...\033[0m"
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet

# 2. Setup ~/.scripts and ~/bin
mkdir -p "$HOME/.scripts"
mkdir -p "$HOME/bin"

echo -e "\033[1;33m[*] Copying scripts and wrappers...\033[0m"
cp -r "$SCRIPT_DIR/scripts/"* "$HOME/.scripts/"
cp -r "$SCRIPT_DIR/bin/"* "$HOME/bin/"
cp "$SCRIPT_DIR/shell/action_commands.bash" "$HOME/.scripts/"

# 3. Configure ~/.bashrc
BASHRC="$HOME/.bashrc"
LOAD_CMD='source "$HOME/.scripts/action_commands.bash"'

if [ -f "$BASHRC" ] && grep -Fxq "$LOAD_CMD" "$BASHRC"; then
  echo -e "\033[1;32m✔   ~/.bashrc already configured.\033[0m"
else
  echo -e "\033[1;33m[*] Adding Action Commands to ~/.bashrc...\033[0m"
  echo "" >> "$BASHRC"
  echo "# --- Action Commands Suite ---" >> "$BASHRC"
  echo "$LOAD_CMD" >> "$BASHRC"
  echo -e "\033[1;32m✔   Updated ~/.bashrc.\033[0m"
fi

echo -e "\n\033[1;32m✨ Installation complete!\033[0m"
echo -e "Run \033[1;36msource ~/.bashrc\033[0m to start using commands immediately."
