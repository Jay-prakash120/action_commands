#!/usr/bin/env python3
import os
import sys
import subprocess

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

os.system('')

RESET = "\033[0m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
WHITE = "\033[37m"

B_CYAN = "\033[1;36m"
B_GREEN = "\033[1;32m"
B_YELLOW = "\033[1;33m"
B_WHITE = "\033[1;37m"
B_RED = "\033[1;31m"

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "hotspot_helper.ps1")

def query_hotspot(action="status", param=""):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", SCRIPT_PATH, action]
    if param:
        cmd.append(param)

    res = subprocess.run(cmd, capture_output=True, text=True)
    info = {"state": "Off", "ssid": "Unknown", "password": "None", "band": "2.4 GHz", "clients": "0", "already": None}
    for line in res.stdout.splitlines():
        if line.startswith("ALREADY:"):
            info["already"] = line.split(":", 1)[1].strip()
        elif line.startswith("STATE:"):
            info["state"] = line.split(":", 1)[1].strip()
        elif line.startswith("SSID:"):
            info["ssid"] = line.split(":", 1)[1].strip()
        elif line.startswith("PASSWORD:"):
            info["password"] = line.split(":", 1)[1].strip()
        elif line.startswith("BAND:"):
            raw_band = line.split(":", 1)[1].strip()
            if "Five" in raw_band:
                info["band"] = "5 GHz"
            elif "TwoPointFour" in raw_band:
                info["band"] = "2.4 GHz"
            else:
                info["band"] = "Any / Auto"
        elif line.startswith("CLIENTS:"):
            info["clients"] = line.split(":", 1)[1].strip()
    return info

def print_card(info):
    is_on = info["state"].lower() == "on"
    status_tag = f"{B_GREEN}🟢 ACTIVE{RESET}" if is_on else f"{DIM}⚪ INACTIVE{RESET}"
    ssid = info["ssid"]
    pwd = info["password"]
    band = info["band"]
    clients = f"{info['clients']} device(s) connected"

    print(f"\n{B_CYAN}╭── 📶 Windows Mobile Hotspot ────────────────────────╮{RESET}")
    print(f"{B_CYAN}│{RESET}   {B_WHITE}Status{RESET}   :  {status_tag}")
    print(f"{B_CYAN}│{RESET}   {B_WHITE}SSID{RESET}     :  {B_YELLOW}{ssid}{RESET}")
    print(f"{B_CYAN}│{RESET}   {B_WHITE}Password{RESET} :  {B_CYAN}{pwd}{RESET}")
    print(f"{B_CYAN}│{RESET}   {B_WHITE}Band{RESET}     :  {B_WHITE}{band}{RESET}")
    print(f"{B_CYAN}│{RESET}   {B_WHITE}Clients{RESET}  :  {DIM}{clients}{RESET}")
    print(f"{B_CYAN}╰─────────────────────────────────────────────────────╯{RESET}\n")

def main():
    if len(sys.argv) < 2:
        info = query_hotspot("status")
        print_card(info)
        return

    action = sys.argv[1].lower()

    if action in ("status", "info"):
        info = query_hotspot("status")
        print_card(info)

    elif action in ("on", "start"):
        info = query_hotspot("start")
        if info.get("already") == "ON":
            print(f"\n{B_YELLOW}ℹ  Hotspot is already ACTIVE (ON).{RESET}")
        else:
            print(f"\n{B_GREEN}✔  Hotspot started successfully.{RESET}")
        print_card(info)

    elif action in ("off", "stop"):
        info = query_hotspot("stop")
        if info.get("already") == "OFF":
            print(f"\n{B_YELLOW}ℹ  Hotspot is already INACTIVE (OFF).{RESET}")
        else:
            print(f"\n{B_CYAN}✔  Hotspot stopped.{RESET}")
        print_card(info)

    elif action == "toggle":
        info = query_hotspot("toggle")
        is_on = info["state"].lower() == "on"
        tag = f"{B_GREEN}ACTIVE (ON){RESET}" if is_on else f"{DIM}INACTIVE (OFF){RESET}"
        print(f"\n{CYAN}⚡  Hotspot toggled to {tag}.{RESET}")
        print_card(info)

    elif action == "band":
        if len(sys.argv) < 3:
            print(f"\n{B_YELLOW}Usage:{RESET} hotspot band <2.4 | 5 | any>")
            info = query_hotspot("status")
            print(f"Current Band: {B_WHITE}{info['band']}{RESET}\n")
            return
        target = sys.argv[2]
        info = query_hotspot("band", target)
        if info.get("already") == "BAND":
            print(f"\n{B_YELLOW}ℹ  Hotspot is already configured to {info['band']}.{RESET}")
        else:
            print(f"\n{B_GREEN}✔  Hotspot frequency band updated to {info['band']}.{RESET}")
        print_card(info)

    else:
        print(f"{B_RED}Unknown action:{RESET} {action}")
        print("Usage: hotspot [on | off | status | toggle | band <2.4|5|any>]")

if __name__ == "__main__":
    main()
