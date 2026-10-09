#!/usr/bin/env python3
import os
import sys
import json
import ctypes
from ctypes import wintypes

# Ensure UTF-8 output encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def enable_vt_mode():
    try:
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
YELLOW = "\033[33m"
WHITE = "\033[37m"

B_CYAN = "\033[1;36m"
B_GREEN = "\033[1;32m"
B_YELLOW = "\033[1;33m"
B_WHITE = "\033[1;37m"
B_RED = "\033[1;31m"

STATE_FILE = os.path.join(os.path.dirname(__file__), ".nl_state.json")

# Win32 GDI structures for Gamma Ramp
gdi32 = ctypes.windll.gdi32
user32 = ctypes.windll.user32

word_array = wintypes.WORD * 256
ramp_type = word_array * 3

def get_saved_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"enabled": False, "blue_percent": 60}

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except Exception:
        pass

def make_ramp(r_scale=1.0, g_scale=0.85, b_scale=0.60):
    ramp = ramp_type()
    for i in range(256):
        val = i * 256
        ramp[0][i] = min(65535, int(val * r_scale))
        ramp[1][i] = min(65535, int(val * g_scale))
        ramp[2][i] = min(65535, int(val * b_scale))
    return ramp

def apply_gamma(enabled, blue_percent=60):
    hdc = user32.GetDC(None)
    if not hdc:
        return False

    try:
        if enabled:
            b_ratio = max(0.2, min(1.0, blue_percent / 100.0))
            g_ratio = 0.85 if b_ratio < 0.9 else 1.0
            ramp = make_ramp(1.0, g_ratio, b_ratio)
        else:
            ramp = make_ramp(1.0, 1.0, 1.0)

        success = bool(gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(ramp)))
        return success
    finally:
        user32.ReleaseDC(None, hdc)

def main():
    state = get_saved_state()
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "toggle"

    if action in ("status", "info"):
        if state["enabled"]:
            print(f"\n{B_YELLOW}🌙  Night Light:{RESET} {B_GREEN}[ON]{RESET} {DIM}(Warm amber tint active){RESET}\n")
        else:
            print(f"\n{B_CYAN}☀️   Night Light:{RESET} {DIM}[OFF] (Standard display active){RESET}\n")

    elif action in ("on", "enable"):
        if state["enabled"]:
            print(f"\n{B_YELLOW}ℹ  Night Light is already [ON].{RESET} {DIM}(Warm amber tint active){RESET}\n")
            return
        state["enabled"] = True
        apply_gamma(True, state.get("blue_percent", 60))
        save_state(state)
        print(f"\n{B_YELLOW}🌙  Night Light:{RESET} {B_GREEN}[ON]{RESET} {DIM}(Warm amber tint applied){RESET}\n")

    elif action in ("off", "disable"):
        if not state["enabled"]:
            print(f"\n{B_YELLOW}ℹ  Night Light is already [OFF].{RESET} {DIM}(Standard display active){RESET}\n")
            return
        state["enabled"] = False
        apply_gamma(False)
        save_state(state)
        print(f"\n{B_CYAN}☀️   Night Light:{RESET} {DIM}[OFF] (Normal screen restored){RESET}\n")

    elif action == "toggle":
        new_state = not state["enabled"]
        state["enabled"] = new_state
        apply_gamma(new_state, state.get("blue_percent", 60))
        save_state(state)
        if new_state:
            print(f"\n{B_YELLOW}🌙  Night Light toggled:{RESET} {B_GREEN}[ON]{RESET} {DIM}(Warm amber tint applied){RESET}\n")
        else:
            print(f"\n{B_CYAN}☀️   Night Light toggled:{RESET} {DIM}[OFF] (Normal screen restored){RESET}\n")

    else:
        # Check if user specified a warmth percentage, e.g. nl 50
        if action.isdigit():
            val = int(action)
            if 20 <= val <= 100:
                state["enabled"] = True
                state["blue_percent"] = val
                apply_gamma(True, val)
                save_state(state)
                print(f"\n{B_YELLOW}🌙  Night Light set to {val}% blue spectrum:{RESET} {B_GREEN}[ON]{RESET}\n")
                return

        print(f"{B_RED}Unknown action:{RESET} {action}")
        print("Usage: nl [on | off | status | toggle | <20-100>]")

if __name__ == "__main__":
    main()
