#!/usr/bin/env python3
import os
import sys
import time
import getpass
import psutil
import subprocess

# Ensure UTF-8 output encoding on Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Enable ANSI escape sequence processing in Windows terminals
os.system('')

# ANSI Colors & Styling
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

B_RED = "\033[1;31m"
B_GREEN = "\033[1;32m"
B_YELLOW = "\033[1;33m"
B_BLUE = "\033[1;34m"
B_MAGENTA = "\033[1;35m"
B_CYAN = "\033[1;36m"
B_WHITE = "\033[1;37m"

PROTECTED_PROCESSES = {
    "system", "system idle process", "registry", "smss.exe", "csrss.exe",
    "wininit.exe", "services.exe", "lsass.exe", "svchost.exe", "winlogon.exe",
    "fontdrvhost.exe", "dwm.exe", "explorer.exe", "conhost.exe", "sihost.exe",
    "ctfmon.exe", "taskhostw.exe", "runtimebroker.exe", "searchhost.exe",
    "shellexperiencehost.exe", "startmenuexperiencehost.exe", "securityhealthservice.exe",
    "antigravity.exe", "agy.exe", "textinputhost.exe", "syntpenh.exe", "syntphelper.exe",
    "smartaudio3.exe", "igfxem.exe", "igcctray.exe"
}

def get_protected_pids():
    """Returns PIDs of current process and all ancestor processes (shells, terminals, editors)."""
    pids = set()
    try:
        curr = psutil.Process()
        pids.add(curr.pid)
        for parent in curr.parents():
            pids.add(parent.pid)
    except Exception:
        pass
    return pids

def close_user_processes(dry_run=False, force=False, pace=True):
    current_user = getpass.getuser().lower()
    protected_pids = get_protected_pids()
    candidates = []

    print(f"\n{CYAN}🔍  Scanning active user applications...{RESET}", flush=True)
    if pace:
        time.sleep(0.3)

    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            name = proc.info.get('name')
            username = proc.info.get('username')
            pid = proc.info.get('pid')

            if not name or name.lower() in PROTECTED_PROCESSES:
                continue
            if pid in protected_pids:
                continue
            if not username or current_user not in username.lower():
                continue

            candidates.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if not candidates:
        print(f"{B_GREEN}✔  No active user applications found to close.{RESET}\n", flush=True)
        return

    total = len(candidates)
    width = len(str(total))
    print(f"{B_YELLOW}📦  Found {total} application(s) to close:{RESET}\n", flush=True)
    if pace:
        time.sleep(0.15)

    for idx, p in enumerate(candidates, 1):
        try:
            p_name = p.info.get('name', 'Unknown')
            p_pid = p.info.get('pid')
            prefix = f"{DIM}[{idx:>{width}}/{total}]{RESET}"

            if dry_run:
                print(f"  {prefix} {YELLOW}▶ [DRY-RUN]{RESET} Would close: {B_WHITE}{p_name}{RESET} {DIM}(PID: {p_pid}){RESET}", flush=True)
            else:
                if force:
                    p.kill()
                    print(f"  {prefix} {B_RED}✖ Force-killed:{RESET} {B_WHITE}{p_name}{RESET} {DIM}(PID: {p_pid}){RESET}", flush=True)
                else:
                    p.terminate()
                    print(f"  {prefix} {RED}✖ Closed:{RESET} {B_WHITE}{p_name}{RESET} {DIM}(PID: {p_pid}){RESET}", flush=True)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

        if pace:
            time.sleep(0.04)  # 40ms stream pacing for readability

    if not dry_run and not force:
        # Wait up to 2 seconds for graceful exit, then kill hung ones
        gone, alive = psutil.wait_procs(candidates, timeout=2.0)
        for p in alive:
            try:
                p.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    if pace:
        time.sleep(0.2)
    print(f"\n{B_GREEN}✔  All user applications closed successfully.{RESET}", flush=True)
    if pace:
        time.sleep(0.15)

def handle_killport(args, pace=True):
    if not args:
        print(f"{B_RED}Usage:{RESET} killport <port_number>")
        return
    try:
        target_port = int(args[0])
        if target_port < 1 or target_port > 65535:
            print(f"{B_RED}✖ Error:{RESET} Port number must be between 1 and 65535 (got {target_port}).")
            return
    except ValueError:
        print(f"{B_RED}✖ Error:{RESET} Invalid port number: {B_WHITE}{args[0]}{RESET}")
        return

    print(f"{CYAN}🔍  Scanning network connections for port {B_WHITE}{target_port}{CYAN}...{RESET}", flush=True)
    if pace:
        time.sleep(0.25)

    killed_pids = set()

    try:
        connections = psutil.net_connections(kind='inet')
    except (psutil.AccessDenied, Exception):
        connections = []

    for conn in connections:
        if conn.laddr and conn.laddr.port == target_port and conn.pid:
            if conn.pid in killed_pids:
                continue
            try:
                p = psutil.Process(conn.pid)
                p_name = p.name()
                p.kill()
                killed_pids.add(conn.pid)
                print(f"{B_GREEN}🎯  Killed {B_WHITE}{p_name}{B_GREEN} {DIM}(PID: {conn.pid}){B_GREEN} holding port {B_WHITE}{target_port}{B_GREEN}.{RESET}", flush=True)
                if pace:
                    time.sleep(0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied) as err:
                print(f"{B_RED}✖  Could not terminate PID {conn.pid}:{RESET} {err}", flush=True)

    if not killed_pids:
        # Fallback using netstat check via subprocess
        try:
            out = subprocess.check_output(f'netstat -ano | findstr :{target_port}', shell=True, text=True)
            lines = [line.strip() for line in out.strip().splitlines() if line.strip()]
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = int(parts[-1])
                    if pid and pid not in killed_pids:
                        try:
                            p = psutil.Process(pid)
                            p_name = p.name()
                            p.kill()
                            killed_pids.add(pid)
                            print(f"{B_GREEN}🎯  Killed {B_WHITE}{p_name}{B_GREEN} {DIM}(PID: {pid}){B_GREEN} holding port {B_WHITE}{target_port}{B_GREEN}.{RESET}", flush=True)
                            if pace:
                                time.sleep(0.1)
                        except Exception as e:
                            print(f"{B_RED}✖  Could not terminate PID {pid}:{RESET} {e}", flush=True)
        except subprocess.CalledProcessError:
            pass

    if pace:
        time.sleep(0.15)

    if not killed_pids:
        print(f"{YELLOW}ℹ   Port {B_WHITE}{target_port}{YELLOW} is not currently in use by any process.{RESET}\n", flush=True)
    else:
        print(f"{B_GREEN}✨  Port {B_WHITE}{target_port}{B_GREEN} is now completely free!{RESET}\n", flush=True)

def main():
    if len(sys.argv) < 2:
        print(f"\n{B_CYAN}⚡ Custom Power & Port Tools{RESET}")
        print(f"Usage: power_tools.py <shutdown|restart|killport> [options]")
        print("\nOptions:")
        print(f"  {YELLOW}--dry-run{RESET}   Simulate actions without closing apps or turning off PC")
        print(f"  {YELLOW}--force{RESET}     Force-kill apps immediately instead of graceful terminate")
        print(f"  {YELLOW}--now{RESET}       Execute shutdown/reboot immediately without asking for Enter\n")
        sys.exit(0)

    command = sys.argv[1].lower()
    options = sys.argv[2:]

    dry_run = "--dry-run" in options
    force = "--force" in options
    now = "--now" in options
    # Disable delays if user specified --now or --force for immediate action
    pace = not (now or force)

    if command == "shutdown":
        print(f"{B_CYAN}╭───────────────────────────────────────────────╮{RESET}")
        print(f"{B_CYAN}│  ⚡  Safe PC Shutdown Procedure               │{RESET}")
        print(f"{B_CYAN}╰───────────────────────────────────────────────╯{RESET}", flush=True)
        
        close_user_processes(dry_run=dry_run, force=force, pace=pace)
        if dry_run:
            print(f"{B_YELLOW}▶ [DRY-RUN] Simulation complete. No apps closed, PC will not shut down.{RESET}\n", flush=True)
            return

        if not now:
            try:
                input(f"\n{B_YELLOW}⚡ Press {B_WHITE}[ENTER]{B_YELLOW} to shut down PC {DIM}(or Ctrl+C to cancel)...{RESET} ")
            except KeyboardInterrupt:
                print(f"\n{B_RED}🛑 Shutdown cancelled by user.{RESET}\n", flush=True)
                return

        print(f"\n{B_GREEN}🚀 Initiating PC shutdown... Goodbye!{RESET}", flush=True)
        subprocess.run(["shutdown.exe", "/s", "/t", "0"])

    elif command in ("restart", "reboot"):
        print(f"{B_MAGENTA}╭───────────────────────────────────────────────╮{RESET}")
        print(f"{B_MAGENTA}│  🔄  Safe PC Restart Procedure                │{RESET}")
        print(f"{B_MAGENTA}╰───────────────────────────────────────────────╯{RESET}", flush=True)

        close_user_processes(dry_run=dry_run, force=force, pace=pace)
        if dry_run:
            print(f"{B_YELLOW}▶ [DRY-RUN] Simulation complete. No apps closed, PC will not restart.{RESET}\n", flush=True)
            return

        if not now:
            try:
                input(f"\n{B_YELLOW}🔄 Press {B_WHITE}[ENTER]{B_YELLOW} to restart PC {DIM}(or Ctrl+C to cancel)...{RESET} ")
            except KeyboardInterrupt:
                print(f"\n{B_RED}🛑 Restart cancelled by user.{RESET}\n", flush=True)
                return

        print(f"\n{B_GREEN}🚀 Initiating PC restart... See you soon!{RESET}", flush=True)
        subprocess.run(["shutdown.exe", "/r", "/t", "0"])

    elif command == "killport":
        handle_killport(options, pace=pace)
    else:
        print(f"{B_RED}✖ Unknown command:{RESET} {command}")
        print(f"Supported commands: {CYAN}shutdown{RESET}, {CYAN}restart{RESET}, {CYAN}killport{RESET}")

if __name__ == "__main__":
    main()
