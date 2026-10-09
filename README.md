# ⚡ Action Commands

> Fast, beautiful, and system-level custom terminal commands for **Windows** with full support for **Git Bash**, **PowerShell**, and **Command Prompt (CMD)**.

![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue?style=flat-square)
![Shells](https://img.shields.io/badge/Shells-Git%20Bash%20%7C%20PowerShell%20%7C%20CMD-black?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🌟 Highlights

* **Safe & Graceful Power Management**: Systematically closes running applications one by one with a smooth matrix-style cascade, protects the active terminal from suicide, and waits for your confirmation before turning off.
* **Interactive Wi-Fi Manager**: Clean numbered list of visible networks with signal bars and security badges. Type the number to connect—prompts for masked password if it's a new network. Pressing Enter with empty input immediately exits.
* **Interactive Brightness Slider**: Arrow-key interactive slider (`←/↓`, `→/↑`, `Enter`) that live-adjusts display brightness in 0ms without UI flicker.
* **Hardware Night Light**: Uses low-level Win32 Display Driver Gamma Ramps (`gdi32.dll -> SetDeviceGammaRamp`) to physically filter blue light with instant response.
* **Mobile Hotspot Controller**: Reads SSID & passwords directly from Windows Runtime (WinRT) and allows switching frequency bands (`2.4 GHz` vs `5 GHz`).
* **Developer Utilities**: One-command port killing (`killport 3000`), local & WAN IP lookup (`myip`), workstation locking (`lock`), explorer restarts, and DNS flushing.
* **State-Aware Error Handling**: Knows when a feature is already active (e.g., `hotspot on` when already running outputs *"Hotspot is already ACTIVE"*).
* **Tab Autocompletion**: Built-in autocompleters for Git Bash and PowerShell.

---

## 🚀 Quick Install

### Prerequisites
* Windows 10 or 11
* Python 3.10+ installed and available in `PATH`

### 1. In Git Bash / Bash:
```bash
git clone https://github.com/your-username/action_commands.git
cd action_commands
./install.sh
source ~/.bashrc
```

### 2. In PowerShell:
```powershell
git clone https://github.com/your-username/action_commands.git
cd action_commands
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install.ps1
```

---

## 📖 Command Reference

### 1. Power Controls
| Command | Description | Example |
| :--- | :--- | :--- |
| `shutdown` | Gracefully closes user apps, keeps terminal open, prompts Enter to shut down PC | `shutdown` |
| `shutdown --dry-run` | Simulates the shutdown without terminating apps or powering off | `shutdown --dry-run` |
| `shutdown --now` | Closes apps and immediately shuts down without confirmation prompt | `shutdown --now` |
| `shutdown --force` | Force-terminates apps immediately instead of graceful signal | `shutdown --force` |
| `restart` | Same graceful sequence, but reboots the PC | `restart` |

### 2. Wi-Fi Manager
| Command | Description | Example |
| :--- | :--- | :--- |
| `wifi` | Launches interactive numbered menu (press Enter with no input to quit) | `wifi` |
| `wifi list` | Prints all visible SSIDs, signal strength bars, and security types | `wifi list` |
| `wifi status` | Shows current connected network | `wifi status` |
| `wifi on` / `wifi off` | Toggles the Wi-Fi hardware adapter on/off | `wifi on` |
| `wifi connect <SSID>` | Connects directly to a network (prompts for password if new) | `wifi connect "Home-5G"` |

```text
╭── 📡 Available Wi-Fi Networks ──────────────────────────────────────────╮
│  [ 1] Home-Fiber_5G                  [████  94%]  [WPA2]   (Connected)  │
│  [ 2] Office_Guest                   [███░  65%]  [WPA2]                │
│  [ 3] CoffeeShop_Free                [█░░░  30%]  [Open]                │
╰─────────────────────────────────────────────────────────────────────────╯
Enter # to connect (or 'r' to refresh, Enter/q to quit): 
```

### 3. Screen Brightness
| Command | Description | Example |
| :--- | :--- | :--- |
| `bright` | Opens live interactive arrow-key slider | `bright` |
| `bright <0-100>` | Sets brightness level directly | `bright 80` |
| `bright +<delta>` | Increments brightness relatively | `bright +10` |
| `bright -<delta>` | Decrements brightness relatively | `bright -10` |

```text
☀️  Brightness: [████████░░░░░░░░]  40%  (←/↓ -5%, →/↑ +5%, Enter to save)
```

### 4. Windows Night Light
| Command | Description | Example |
| :--- | :--- | :--- |
| `nl` | Toggles hardware Night Light warm amber tint | `nl` |
| `nl on` | Forces Night Light ON 🌙 | `nl on` |
| `nl off` | Restores normal neutral display ☀️ | `nl off` |
| `nl status` | Prints current Night Light state | `nl status` |
| `nl <20-100>` | Sets custom blue-light spectrum filter | `nl 50` |

### 5. Mobile Hotspot
| Command | Description | Example |
| :--- | :--- | :--- |
| `hotspot` | Displays status card with SSID, password, band & client count | `hotspot` |
| `hotspot on` | Starts mobile hotspot broadcast | `hotspot on` |
| `hotspot off` | Stops mobile hotspot broadcast | `hotspot off` |
| `hotspot toggle` | Toggles hotspot state | `hotspot toggle` |
| `hotspot band 2.4` | Configures hotspot broadcast to 2.4 GHz | `hotspot band 2.4` |
| `hotspot band 5` | Configures hotspot broadcast to 5 GHz | `hotspot band 5` |
| `hotspot band any` | Allows dynamic dual-band auto selection | `hotspot band any` |

```text
╭── 📶 Windows Mobile Hotspot ────────────────────────╮
│   Status   :  🟢 ACTIVE                             │
│   SSID     :  My-Laptop-Hotspot                     │
│   Password :  securePassword123                     │
│   Band     :  5 GHz                                 │
│   Clients  :  1 device(s) connected                 │
╰─────────────────────────────────────────────────────╯
```

### 6. Developer & System Utilities
| Command | Description |
| :--- | :--- |
| `killport <port>` | Finds which PID is locking port 3000, 8080, etc. and terminates it immediately |
| `myip` | Prints local IPv4 adapter address and public WAN IP in a clean card |
| `flushdns` | Flushes Windows DNS Resolver Cache |
| `lock` | Instantly locks Windows workstation (`LockWorkStation`) |
| `here` | Opens Windows File Explorer at current working directory (`explorer.exe .`) |
| `restartexplorer` | Restarts `explorer.exe` (taskbar/desktop) if frozen |
| `reload` | Reloads `~/.bashrc` without restarting the terminal window |

---

## 🛠️ Architecture

* **Python 3**: Core process scanning (`psutil`), dynamic WLAN profile generation (`subprocess` + XML), and non-blocking arrow-key detection (`msvcrt`).
* **Win32 C APIs (`ctypes`)**: Direct bindings to `gdi32.dll` (`SetDeviceGammaRamp`) for 0ms hardware color temperature changes without Settings app popups.
* **Windows Runtime (`WinRT`)**: Low-level COM tethering APIs (`Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager`) for Mobile Hotspot control and frequency band switching.
* **Bash Shell Functions**: Zero-overhead functions in `~/.bashrc` with programmable autocompletion (`complete -F`).
* **CMD Wrappers**: Portable `.cmd` scripts in `%USERPROFILE%\bin` for native Command Prompt and PowerShell accessibility.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
