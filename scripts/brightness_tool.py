#!/usr/bin/env python3
import os
import sys
import msvcrt

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

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
WHITE = "\033[37m"
RED = "\033[31m"

B_CYAN = "\033[1;36m"
B_GREEN = "\033[1;32m"
B_YELLOW = "\033[1;33m"
B_WHITE = "\033[1;37m"
B_RED = "\033[1;31m"

_wmi_services = None

def get_wmi_services():
    global _wmi_services
    if _wmi_services is None:
        import win32com.client
        _wmi_services = win32com.client.GetObject('winmgmts:\\\\.\\root\\wmi')
    return _wmi_services

def get_brightness():
    try:
        wmi = get_wmi_services()
        for m in wmi.InstancesOf('WmiMonitorBrightness'):
            return int(m.CurrentBrightness)
    except Exception:
        pass
    return None

def set_brightness(val):
    val = max(0, min(100, val))
    try:
        wmi = get_wmi_services()
        for m in wmi.InstancesOf('WmiMonitorBrightnessMethods'):
            in_param = m.Methods_('WmiSetBrightness').inParameters.SpawnInstance_()
            in_param.Properties_('Timeout').Value = 0
            in_param.Properties_('Brightness').Value = val
            m.ExecMethod_('WmiSetBrightness', in_param)
        return val
    except Exception:
        return None

def render_bar(val, width=20):
    val = max(0, min(100, val))
    filled = int(round(val / 100 * width))
    empty = width - filled
    bar = f"{B_CYAN}{'█' * filled}{RESET}{DIM}{'░' * empty}{RESET}"
    return f"\r☀️  Brightness: [{bar}] {B_WHITE}{val:>3}%{RESET}  {DIM}(←/↓ -5%, →/↑ +5%, Enter to save){RESET} "

def interactive_mode():
    curr = get_brightness()
    if curr is None:
        print(f"{B_RED}✖ Error:{RESET} Could not communicate with display monitor.")
        return

    sys.stdout.write(f"\n{render_bar(curr)}")
    sys.stdout.flush()

    while True:
        try:
            ch = msvcrt.getwch()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        key = None
        if ch in ('\x00', '\xe0'):
            ch2 = msvcrt.getwch()
            if ch2 in ('H',): key = 'UP'
            elif ch2 in ('P',): key = 'DOWN'
            elif ch2 in ('K',): key = 'LEFT'
            elif ch2 in ('M',): key = 'RIGHT'
        elif ch == '\x1b':
            if msvcrt.kbhit():
                ch2 = msvcrt.getwch()
                if ch2 == '[':
                    ch3 = msvcrt.getwch()
                    if ch3 == 'A': key = 'UP'
                    elif ch3 == 'B': key = 'DOWN'
                    elif ch3 == 'D': key = 'LEFT'
                    elif ch3 == 'C': key = 'RIGHT'
            else:
                key = 'ESC'
        elif ch in ('\r', '\n'):
            key = 'ENTER'
        elif ch in ('q', 'Q'):
            key = 'QUIT'
        elif ch in ('+', '='):
            key = 'UP'
        elif ch in ('-', '_'):
            key = 'DOWN'

        if key in ('UP', 'RIGHT'):
            curr = min(100, curr + 5)
            set_brightness(curr)
            sys.stdout.write(render_bar(curr))
            sys.stdout.flush()
        elif key in ('DOWN', 'LEFT'):
            curr = max(0, curr - 5)
            set_brightness(curr)
            sys.stdout.write(render_bar(curr))
            sys.stdout.flush()
        elif key in ('ENTER', 'ESC', 'QUIT'):
            print(f"\n\n{B_GREEN}✔  Brightness set to {curr}%.{RESET}\n")
            break

def main():
    if len(sys.argv) < 2:
        interactive_mode()
        return

    arg = sys.argv[1].strip()
    curr = get_brightness()
    if curr is None:
        print(f"{B_RED}✖ Error:{RESET} Could not access display monitor.")
        return

    if arg.startswith('+') or arg.startswith('-'):
        try:
            delta = int(arg)
            if curr >= 100 and delta > 0:
                print(f"\n{B_YELLOW}ℹ  Brightness is already at maximum (100%).{RESET}\n")
                return
            if curr <= 0 and delta < 0:
                print(f"\n{B_YELLOW}ℹ  Brightness is already at minimum (0%).{RESET}\n")
                return
            new_val = max(0, min(100, curr + delta))
            if new_val == curr:
                print(f"\n{B_YELLOW}ℹ  Brightness is already at {curr}%.{RESET}\n")
                return
            set_brightness(new_val)
            print(f"\n{B_GREEN}✔  Brightness adjusted from {curr}% to {new_val}%.{RESET}\n")
        except ValueError:
            print(f"{B_RED}Invalid adjustment value:{RESET} {arg}")
    elif arg.isdigit():
        val = int(arg)
        if 0 <= val <= 100:
            if val == curr:
                print(f"\n{B_YELLOW}ℹ  Brightness is already set to {curr}%.{RESET}\n")
                return
            set_brightness(val)
            print(f"\n{B_GREEN}✔  Brightness set to {val}%.{RESET}\n")
        else:
            print(f"{B_RED}Brightness must be between 0 and 100.{RESET}")
    else:
        print(f"{B_RED}Unknown brightness argument:{RESET} {arg}")
        print("Usage: bright [value (0-100) | +delta | -delta]")

if __name__ == "__main__":
    main()
