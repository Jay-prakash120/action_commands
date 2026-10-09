#!/usr/bin/env python3
import os
import sys
import re
import subprocess

# Ensure UTF-8 output encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def enable_vt_mode():
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        hStdOut = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode)):
            kernel32.SetConsoleMode(hStdOut, mode.value | 0x0004)
    except Exception:
        pass

enable_vt_mode()

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RED = "\033[31m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"

B_GREEN = "\033[1;32m"
B_YELLOW = "\033[1;33m"
B_CYAN = "\033[1;36m"
B_RED = "\033[1;31m"
B_WHITE = "\033[1;37m"

def get_current_connected_ssid():
    try:
        out = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], text=True, errors='ignore')
        for line in out.splitlines():
            if 'SSID' in line and 'BSSID' not in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    return parts[1].strip()
    except Exception:
        pass
    return None

def get_adapter_admin_state():
    try:
        out = subprocess.check_output(['netsh', 'interface', 'show', 'interface', 'name=Wi-Fi'], text=True, errors='ignore')
        for line in out.splitlines():
            if 'Administrative state' in line:
                return line.split(':', 1)[1].strip().lower()
    except Exception:
        pass
    return None

def get_saved_profiles():
    profiles = set()
    try:
        out = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], text=True, errors='ignore')
        for line in out.splitlines():
            if ':' in line and 'All User Profile' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    profiles.add(parts[1].strip())
    except Exception:
        pass
    return profiles

def scan_networks():
    try:
        out = subprocess.check_output(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'], text=True, errors='ignore')
    except Exception:
        return []

    networks = []
    current_net = {}
    for line in out.splitlines():
        line = line.strip()
        if line.startswith('SSID'):
            m = re.match(r'SSID\s+\d+\s*:\s*(.*)', line)
            if m:
                if current_net.get('ssid'):
                    networks.append(current_net)
                current_net = {'ssid': m.group(1), 'auth': 'Open', 'signal': 0}
        elif line.startswith('Authentication'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                auth = parts[1].strip()
                if 'WPA3' in auth: current_net['auth'] = 'WPA3'
                elif 'WPA2' in auth: current_net['auth'] = 'WPA2'
                elif 'Open' in auth: current_net['auth'] = 'Open'
                else: current_net['auth'] = auth
        elif line.startswith('Signal'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                sig_str = parts[1].strip().replace('%', '')
                try:
                    sig = int(sig_str)
                    if sig > current_net.get('signal', 0):
                        current_net['signal'] = sig
                except ValueError:
                    pass

    if current_net.get('ssid'):
        networks.append(current_net)

    # Filter out empty SSIDs and sort by signal strength descending
    valid_nets = [n for n in networks if n['ssid'].strip()]
    valid_nets.sort(key=lambda x: x['signal'], reverse=True)
    return valid_nets

def render_signal_bar(signal):
    if signal >= 80:
        bar = f"{B_GREEN}████{RESET}"
    elif signal >= 60:
        bar = f"{GREEN}███░{RESET}"
    elif signal >= 35:
        bar = f"{YELLOW}██░░{RESET}"
    else:
        bar = f"{RED}█░░░{RESET}"
    return f"[{bar} {signal:>3}%]"

def create_wifi_profile(ssid, password=None):
    if password:
        xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
    else:
        xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>open</authentication>
                <encryption>none</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
        </security>
    </MSM>
</WLANProfile>"""

    import tempfile
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.xml') as f:
        f.write(xml)
        temp_name = f.name

    try:
        subprocess.run(f'netsh wlan add profile filename="{temp_name}"', shell=True, check=True, capture_output=True)
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)

def connect_to_network(ssid, auth='WPA2'):
    saved = get_saved_profiles()
    current = get_current_connected_ssid()

    if current == ssid:
        print(f"\n{B_GREEN}✔  Already connected to {B_WHITE}{ssid}{B_GREEN}!{RESET}\n")
        return

    if ssid not in saved:
        if auth != 'Open':
            print(f"\n{B_YELLOW}🔐  Network '{ssid}' requires a password.{RESET}")
            try:
                import getpass
                pwd = getpass.getpass("Enter password: ")
            except KeyboardInterrupt:
                print("\n[-] Connection aborted.")
                return
            if not pwd:
                print("[-] Password cannot be empty.")
                return
            create_wifi_profile(ssid, pwd)
        else:
            create_wifi_profile(ssid, None)

    print(f"\n{CYAN}📡  Connecting to {B_WHITE}{ssid}{CYAN}...{RESET}")
    res = subprocess.run(f'netsh wlan connect name="{ssid}"', shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"{B_GREEN}✔  Successfully requested connection to {B_WHITE}{ssid}{B_GREEN}!{RESET}\n")
    else:
        print(f"{B_RED}✖  Connection failed:{RESET} {res.stderr.strip() or res.stdout.strip()}\n")

def get_networks_and_connected():
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_conn = ex.submit(get_current_connected_ssid)
        f_nets = ex.submit(scan_networks)
        return f_conn.result(), f_nets.result()

def show_interactive_menu():
    while True:
        connected, networks = get_networks_and_connected()

        if not networks:
            print(f"\n{YELLOW}⚠️  No Wi-Fi networks found in range.{RESET}")
            return

        print(f"\n{B_CYAN}╭── 📡 Available Wi-Fi Networks ──────────────────────────────────────────╮{RESET}")
        for idx, net in enumerate(networks, 1):
            ssid = net['ssid']
            auth = f"[{net['auth']}]"
            bar = render_signal_bar(net['signal'])
            conn_tag = f" {B_GREEN}(Connected){RESET}" if ssid == connected else ""

            # Pad SSID cleanly
            disp_ssid = (ssid[:28] + '..') if len(ssid) > 30 else ssid
            print(f"{B_CYAN}│{RESET}  {B_WHITE}[{idx:>2}]{RESET} {disp_ssid:<30} {bar}  {DIM}{auth:<8}{RESET}{conn_tag}")
        print(f"{B_CYAN}╰─────────────────────────────────────────────────────────────────────────╯{RESET}")

        try:
            choice = input(f"\n{B_YELLOW}Enter # to connect {DIM}(or 'r' to refresh, Enter/q to quit):{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if not choice or choice.lower() in ('q', 'quit', 'exit'):
            break
        elif choice.lower() in ('r', 'refresh'):
            print(f"\n{CYAN}🔄  Rescanning networks...{RESET}")
            continue
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(networks):
                target = networks[idx - 1]
                connect_to_network(target['ssid'], target['auth'])
                break
            else:
                print(f"{B_RED}Invalid network number.{RESET}")
        else:
            print(f"{B_RED}Invalid input.{RESET}")

def main():
    if len(sys.argv) < 2:
        show_interactive_menu()
        return

    cmd = sys.argv[1].lower()

    if cmd == "list":
        connected, networks = get_networks_and_connected()
        print(f"\n{B_CYAN}╭── 📡 Visible Wi-Fi Networks ────────────────────────────────────────────╮{RESET}")
        for idx, net in enumerate(networks, 1):
            ssid = net['ssid']
            bar = render_signal_bar(net['signal'])
            auth = f"[{net['auth']}]"
            conn_tag = f" {B_GREEN}(Connected){RESET}" if ssid == connected else ""
            print(f"{B_CYAN}│{RESET}  {B_WHITE}[{idx:>2}]{RESET} {ssid:<30} {bar}  {DIM}{auth:<8}{RESET}{conn_tag}")
        print(f"{B_CYAN}╰─────────────────────────────────────────────────────────────────────────╯{RESET}\n")

    elif cmd == "connect":
        if len(sys.argv) < 3:
            print(f"{B_RED}Usage:{RESET} wifi connect <SSID>")
            return
        ssid = sys.argv[2]
        connect_to_network(ssid)

    elif cmd in ("on", "enable"):
        state = get_adapter_admin_state()
        if state == "enabled":
            print(f"\n{B_YELLOW}ℹ  Wi-Fi adapter is already enabled (ON).{RESET}\n")
            return
        print(f"{CYAN}📡  Enabling Wi-Fi adapter...{RESET}")
        res = subprocess.run('netsh interface set interface name="Wi-Fi" admin=ENABLE', shell=True)
        if res.returncode == 0:
            print(f"{B_GREEN}✔  Wi-Fi adapter enabled.{RESET}\n")
        else:
            print(f"{B_RED}✖  Failed to enable Wi-Fi. Admin privileges may be required.{RESET}\n")

    elif cmd in ("off", "disable"):
        state = get_adapter_admin_state()
        if state == "disabled":
            print(f"\n{B_YELLOW}ℹ  Wi-Fi adapter is already disabled (OFF).{RESET}\n")
            return
        print(f"{CYAN}📡  Disabling Wi-Fi adapter...{RESET}")
        res = subprocess.run('netsh interface set interface name="Wi-Fi" admin=DISABLE', shell=True)
        if res.returncode == 0:
            print(f"{B_GREEN}✔  Wi-Fi adapter disabled.{RESET}\n")
        else:
            print(f"{B_RED}✖  Failed to disable Wi-Fi. Admin privileges may be required.{RESET}\n")

    elif cmd in ("status", "info"):
        connected = get_current_connected_ssid()
        if connected:
            print(f"\n{B_GREEN}🟢 Connected to:{RESET} {B_WHITE}{connected}{RESET}")
        else:
            print(f"\n{YELLOW}⚪ Wi-Fi is disconnected.{RESET}")

    else:
        print(f"{B_RED}Unknown command:{RESET} {cmd}")
        print("Usage: wifi [list | connect <SSID> | on | off | status]")

if __name__ == "__main__":
    main()
