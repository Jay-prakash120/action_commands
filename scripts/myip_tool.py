#!/usr/bin/env python3
import os
import sys
import time
import json
import socket
import urllib.request

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

RESET = "\033[0m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"
B_CYAN = "\033[1;36m"
B_GREEN = "\033[1;32m"
B_MAGENTA = "\033[1;35m"
B_WHITE = "\033[1;37m"
B_YELLOW = "\033[1;33m"

CACHE_FILE = os.path.join(os.path.dirname(__file__), ".ip_cache.json")
CACHE_TTL = 900  # 15 minutes

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except Exception:
        pass
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "127.0.0.1"

def fetch_live_public_ip():
    endpoints = ['https://api.ipify.org', 'https://icanhazip.com']
    for url in endpoints:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.88.1'})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                ip = resp.read().decode('utf-8').strip()
                if ip:
                    return ip
        except Exception:
            continue
    return None

def get_public_ip(force_refresh=False):
    cached_ip = None
    cached_time = 0
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                cached_ip = data.get('ip')
                cached_time = data.get('timestamp', 0)
        except Exception:
            pass

    now = time.time()
    if not force_refresh and cached_ip and (now - cached_time < CACHE_TTL):
        return cached_ip, False

    live_ip = fetch_live_public_ip()
    if live_ip:
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump({'ip': live_ip, 'timestamp': now}, f)
        except Exception:
            pass
        return live_ip, True

    if cached_ip:
        return f"{cached_ip} (cached)", False

    return "Offline / Unavailable", False

def main():
    force_refresh = any(arg in sys.argv[1:] for arg in ('-r', '--refresh', '-f', '--force'))
    local_ip = get_local_ip()
    pub_ip, is_fresh = get_public_ip(force_refresh)

    fresh_tag = f" {DIM}(live){RESET}" if is_fresh else ""

    print(f"\n{B_CYAN}╭── 🌐 Network Information ─────────────────────────╮{RESET}")
    print(f"{B_CYAN}│{RESET}   {B_GREEN}Local IPv4{RESET}  :  {B_WHITE}{local_ip:<24}{RESET}{B_CYAN}│{RESET}")
    print(f"{B_CYAN}│{RESET}   {B_MAGENTA}Public IP{RESET}   :  {B_WHITE}{pub_ip:<24}{RESET}{fresh_tag}{B_CYAN}│{RESET}")
    print(f"{B_CYAN}╰───────────────────────────────────────────────────╯{RESET}\n")

if __name__ == "__main__":
    main()
