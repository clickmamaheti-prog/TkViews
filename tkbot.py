#!/usr/bin/env python3
# ============================================================
# TkViews CLI — Interactive Tool
# Ketik: tkbot
# ============================================================

import os
import sys
import ssl
import re
import time
import random
import threading
import requests
import json
import socket

# ── Remote proxy source ──────────────────────────────────────
PROXY_REMOTE_URL = "https://raw.githubusercontent.com/clickmamaheti-prog/TkViews/master/proxies.txt"
PROXY_LOCAL_FILE = "proxies.txt"
PROXY_TIMEOUT    = 5
MAX_VALIDATE     = 100

# ── Cyberpunk Color Theme ────────────────────────────────────
class C:
    if os.name != "nt":
        CYAN      = "\033[96m"
        PINK      = "\033[95m"
        HOT_PINK  = "\033[38;5;206m"
        GREEN     = "\033[92m"
        YELLOW    = "\033[93m"
        RED       = "\033[91m"
        WHITE     = "\033[97m"
        DIM       = "\033[2m"
        BOLD      = "\033[1m"
        RESET     = "\033[0m"
    else:
        CYAN=PINK=HOT_PINK=GREEN=YELLOW=RED=WHITE=DIM=BOLD=RESET=""

W = 60

def _vis_len(text):
    return len(re.sub(r'\033\[[0-9;]*m', '', text))

def _pad(text, width=W, align="<"):
    vlen = _vis_len(text)
    pad = max(0, width - vlen)
    if align == ">":
        return text + " " * pad
    elif align == "^":
        left = pad // 2
        right = pad - left
        return " " * left + text + " " * right
    return text + " " * pad

def box_top():
    print(f"  {C.CYAN}╔{'═' * W}╗{C.RESET}")

def box_mid():
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")

def box_bot():
    print(f"  {C.CYAN}╚{'═' * W}╝{C.RESET}")

def box_l(text=""):
    print(f"  {C.CYAN}║{C.RESET} {_pad(text, W-1)}{C.CYAN}║{C.RESET}")

def box_c(text=""):
    print(f"  {C.CYAN}║{C.RESET}{_pad(text, W, '^')}{C.CYAN}║{C.RESET}")

def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print()
    box_top()
    box_c("")
    box_c(f"{C.HOT_PINK}{C.BOLD}████████╗██╗  ██╗██╗   ██╗██╗███████╗{C.RESET}")
    box_c(f"{C.HOT_PINK}{C.BOLD}╚══██╔══╝██║ ██╔╝██║   ██║██║╚════██║{C.RESET}")
    box_c(f"{C.PINK}{C.BOLD}   ██║   █████╔╝ ██║   ██║██║███████╗{C.RESET}")
    box_c(f"{C.PINK}{C.BOLD}   ██║   ██╔═██╗ ╚██╗ ██╔╝██║╚════██║{C.RESET}")
    box_c(f"{C.CYAN}{C.BOLD}   ██║   ██║  ██╗ ╚████╔╝ ██║███████║{C.RESET}")
    box_c(f"{C.CYAN}{C.BOLD}   ╚═╝   ╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝{C.RESET}")
    box_c("")
    box_c(f"{C.CYAN}{C.BOLD}T I K T O K   V I E W B O T{C.RESET}")
    box_c(f"{C.HOT_PINK}{C.BOLD}v 2 . 1{C.RESET}")
    box_c(f"{C.DIM}Fixed — Updated UA + Headers{C.RESET}")
    box_c("")
    box_mid()
    box_c(f"{C.GREEN}●{C.RESET} Auto-Proxy   {C.PINK}●{C.RESET} Multi-Thread   {C.CYAN}●{C.RESET} Zero Signature")
    box_c(f"{C.GREEN}●{C.RESET} Proxy Fallback {C.PINK}●{C.RESET} 100 Threads   {C.CYAN}●{C.RESET} 4 Endpoints")
    box_bot()
    print()

def auto_fetch_proxies():
    try:
        box_l(f"{C.YELLOW}🔄{C.RESET} Fetching proxy terbaru dari GitHub...")
        resp = requests.get(PROXY_REMOTE_URL, timeout=15)
        resp.raise_for_status()
        with open(PROXY_LOCAL_FILE, 'w') as f:
            f.write(resp.text)
        lines = [l.strip() for l in resp.text.strip().split('\n') if l.strip() and ':' in l]
        box_l(f"{C.GREEN}✅{C.RESET} {len(lines)} proxy di-fetch dari GitHub")
        return lines
    except Exception as e:
        box_l(f"{C.RED}⚠️{C.RESET} Gagal fetch proxy: {e}")
        try:
            with open(PROXY_LOCAL_FILE) as f:
                return [l.strip() for l in f if l.strip() and ':' in l]
        except:
            return []

def validate_proxy(proxy):
    ip, port = proxy.split(':')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(PROXY_TIMEOUT)
        ok = s.connect_ex((ip, int(port))) == 0
        s.close()
        return ok
    except:
        return False

def validate_proxies_parallel(proxy_list, max_workers=50):
    import concurrent.futures
    online = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(validate_proxy, p): p for p in proxy_list}
        for f in concurrent.futures.as_completed(futs):
            try:
                if f.result():
                    online.append(futs[f])
            except:
                pass
    return online

from urllib3.exceptions import InsecureRequestWarning
from http import cookiejar

class BlockCookies(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *a, **kw: False
    netscape = True; rfc2965 = hide_cookie2 = False

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

API_ENDPOINTS = [
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/?",
    "https://api21.tiktokv.com/aweme/v1/aweme/stats/?",
    "https://api19-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/?",
    "https://api16-va.tiktokv.com/aweme/v1/aweme/stats/?",
]

def get_headers():
    return {
        'User-Agent': (
            'com.zhiliaoapp.musically/2023100000 '
            '(Linux; U; Android 13; en_US; Pixel 7; '
            'Build/TQ3A.230805.001; '
            'Cronet/TTNetVersion:8eac09b7 2023-07-03 '
            'QuicVersion:6ea22060 2023-05-18)'
        ),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'sdk-version': '2',
        'x-ss-req-ticket': str(int(time.time() * 1000)),
        'x-tt-store-regionc': 'US',
        'x-tt-store-region-src': 'did',
    }

reqs = 0; success_count = 0; fails = 0; rpm = 0; rps = 0
_lock = threading.Lock()

def send(did, iid, cdid, openudid):
    global reqs, success_count, fails
    for attempt in range(10):
        try:
            params = (
                f"device_id={did}&iid={iid}&device_type=SM-G973N"
                f"&app_name=musically_go&host_abi=armeabi-v7a"
                f"&channel=googleplay&device_platform=android"
                f"&version_code=160904&device_brand=samsung"
                f"&os_version=9&aid=1340"
            )
            payload = f"item_id={__aweme_id}&play_delta=1"
            api_url = random.choice(API_ENDPOINTS) + params

            proxy = ""
            use_proxy = config['proxy']['use-proxy'] and proxies
            if use_proxy:
                proxy = random.choice(proxies)

            proxy_dict = {}
            if proxy:
                proxy_dict = {"http": proxy_format + proxy, "https": proxy_format + proxy}

            resp = requests.post(
                api_url, data=payload, headers=get_headers(),
                verify=False, timeout=15, proxies=proxy_dict
            )

            if not resp.text.strip() and use_proxy:
                resp = requests.post(
                    api_url, data=payload, headers=get_headers(),
                    verify=False, timeout=15
                )

            reqs += 1
            try:
                data = resp.json()
                status_code = data.get('status_code', -1)
                impr = data.get('log_pb', {}).get('impr_id', '')
                _lock.acquire()
                if status_code == 0:
                    success_count += 1
                    sys.stdout.write("\033[2K")
                    box_l(f"{C.GREEN}✔{C.RESET} {C.WHITE}View sent{C.RESET}  {C.DIM}{impr}{C.RESET}  {C.CYAN}│{C.RESET}  {C.DIM}total:{reqs}{C.RESET}")
                else:
                    fails += 1
                    sys.stdout.write("\033[2K")
                    box_l(f"{C.YELLOW}⚠{C.RESET} {C.WHITE}Status {status_code}{C.RESET}  {C.CYAN}│{C.RESET}  {C.DIM}fails:{fails}{C.RESET}")
                _lock.release()
            except:
                if _lock.locked():
                    _lock.release()
                fails += 1
        except:
            pass

def rps_loop():
    global rps, rpm
    while True:
        init = reqs
        time.sleep(1.5)
        rps = round((reqs - init) / 1.5, 1)
        rpm = round(rps * 60, 1)

def run_bot():
    global config, proxies, proxy_format, __aweme_id

    # Auto-detect script directory
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(SCRIPT_DIR)

    banner()

    # ── Input URL ──
    print(f"  {C.CYAN}╔{'═' * W}╗{C.RESET}")
    box_l(f"{C.BOLD}{C.HOT_PINK}  TARGET INPUT{C.RESET}")
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")

    try:
        print(f"  {C.CYAN}║{C.RESET}  {C.PINK}❯{C.RESET} {C.WHITE}Video link: {C.RESET}", end="", flush=True)
        link = input()
        __aweme_id = str(
            re.findall(r"(\d{18,19})", link)[0]
            if re.findall(r"(\d{18,19})", link)
            else re.findall(r"(\d{18,19})", requests.head(link, allow_redirects=True, timeout=5).url)[0]
        )
    except:
        box_l(f"{C.RED}✘{C.RESET} {C.WHITE}Invalid link! Tekan Enter untuk keluar.{C.RESET}")
        input()
        sys.exit(0)

    box_l(f"{C.GREEN}✔{C.RESET} {C.WHITE}Video ID:{C.RESET}  {C.BOLD}{C.CYAN}{__aweme_id}{C.RESET}")
    print(f"  {C.CYAN}╚{'═' * W}╝{C.RESET}")
    print()

    # ── Load config ──
    with open('config.json') as f:
        config = json.load(f)

    with open('devices.txt') as f:
        raw = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    devices = []
    for line in raw:
        parts = line.split(':')
        if len(parts) >= 4 and len(parts[0]) >= 15 and len(parts[1]) >= 10:
            devices.append(line)

    # ── Fetch & validate proxies ──
    print(f"  {C.CYAN}╔{'═' * W}╗{C.RESET}")
    box_l(f"{C.BOLD}{C.HOT_PINK}  INITIALIZATION{C.RESET}")
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")

    box_l(f"{C.CYAN}📦{C.RESET} {C.WHITE}Devices loaded{C.RESET}  {C.BOLD}{C.CYAN}{len(devices)} valid{C.RESET}")

    if config['proxy']['use-proxy']:
        proxy_format = (
            f'{config["proxy"]["proxy-type"].lower()}://'
            f'{config["proxy"]["credential"] + "@" if config["proxy"]["auth"] else ""}'
        )
        all_proxies = auto_fetch_proxies()
        if all_proxies:
            sample = random.sample(all_proxies, min(MAX_VALIDATE, len(all_proxies)))
            box_l(f"{C.YELLOW}🔍{C.RESET} {C.WHITE}Validating {len(sample)} proxy...{C.RESET}")
            online = validate_proxies_parallel(sample)
            proxies = online if online else all_proxies
            box_l(f"{C.PINK}🌐{C.RESET} {C.WHITE}Proxy ready{C.RESET}  {C.BOLD}{C.PINK}{len(proxies)} online{C.RESET}")
        else:
            box_l(f"{C.RED}⚠️{C.RESET} {C.WHITE}Tidak ada proxy — koneksi langsung{C.RESET}")
            proxies = []
    else:
        proxy_format = ''
        proxies = []
        box_l(f"{C.DIM}📋{C.RESET} {C.WHITE}Mode: tanpa proxy{C.RESET}")

    print(f"  {C.CYAN}╚{'═' * W}╝{C.RESET}")
    print()

    # ── Start ──
    print(f"  {C.CYAN}╔{'═' * W}╗{C.RESET}")
    box_l(f"{C.BOLD}{C.GREEN}  ▶ RUNNING{C.RESET}")
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")
    box_l(f"{C.DIM}Menunggu views terkirim... (Ctrl+C untuk stop){C.RESET}")
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")

    threading.Thread(target=rps_loop, daemon=True).start()
    time.sleep(1)

    try:
        while True:
            device = random.choice(devices)
            if threading.active_count() < 100:
                parts = device.split(':')
                did, iid, cdid, openudid = parts[0], parts[1], parts[2], parts[3]
                threading.Thread(target=send, args=(did, iid, cdid, openudid), daemon=True).start()
    except KeyboardInterrupt:
        print()
        print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")
        box_l(f"{C.BOLD}{C.YELLOW}  ■ STOPPED{C.RESET}")
        print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")
        box_l(f"{C.WHITE}Total requests:{C.RESET}  {C.BOLD}{reqs}{C.RESET}")
        box_l(f"{C.GREEN}Success:{C.RESET}  {C.BOLD}{success_count}{C.RESET}")
        box_l(f"{C.RED}Failed:{C.RESET}  {C.BOLD}{fails}{C.RESET}")
        print(f"  {C.CYAN}╚{'═' * W}╝{C.RESET}")
        print()

def cmd_run():
    """Run bot — shortcut: tkbot run"""
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(SCRIPT_DIR)
    run_bot()

def cmd_update():
    """Update repo — shortcut: tkbot update"""
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(SCRIPT_DIR)

    print()
    box_top()
    box_c(f"{C.BOLD}{C.HOT_PINK}  🔄 UPDATING TK VIEWS{C.RESET}")
    box_mid()

    # Get current hash
    old_hash = os.popen("git rev-parse --short HEAD 2>/dev/null").read().strip()
    box_l(f"{C.CYAN}📂{C.RESET} {C.WHITE}Current{C.RESET}  {C.BOLD}{old_hash}{C.RESET}")

    # Pull
    box_l(f"{C.YELLOW}🔄{C.RESET} {C.WHITE}Pulling dari GitHub...{C.RESET}")
    pull_result = os.popen("git pull origin master 2>/dev/null || git pull origin main 2>/dev/null").read().strip()

    new_hash = os.popen("git rev-parse --short HEAD 2>/dev/null").read().strip()

    if old_hash == new_hash:
        box_l(f"{C.GREEN}✅{C.RESET} {C.WHITE}Sudah versi terbaru!{C.RESET}")
    else:
        box_l(f"{C.GREEN}✅{C.RESET} {C.WHITE}Updated{C.RESET}  {C.BOLD}{old_hash} → {new_hash}{C.RESET}")

        # Show changelog
        box_mid()
        box_l(f"{C.BOLD}{C.CYAN}  CHANGELOG:{C.RESET}")
        commits = os.popen(f'git log --oneline "{old_hash}..{new_hash}" 2>/dev/null').read().strip()
        if commits:
            for line in commits.split('\n')[:10]:
                box_l(f"  {C.DIM}{line}{C.RESET}")
        else:
            box_l(f"  {C.DIM}(detail lihat: git log){C.RESET}")

        # Show files changed
        files_changed = os.popen(f'git diff --name-only "{old_hash}..{new_hash}" 2>/dev/null').read().strip()
        if files_changed:
            box_mid()
            box_l(f"{C.BOLD}{C.PINK}  FILES CHANGED:{C.RESET}")
            for f in files_changed.split('\n')[:10]:
                box_l(f"  {C.WHITE}{f}{C.RESET}")

    # Update tkbot global command
    box_mid()
    box_l(f"{C.YELLOW}🔧{C.RESET} {C.WHITE}Updating tkbot command...{C.RESET}")
    try:
        # Copy updated tkbot.py to /usr/local/bin/
        import shutil
        shutil.copy2(os.path.join(SCRIPT_DIR, "tkbot.py"), "/usr/local/bin/tkbot")
        os.chmod("/usr/local/bin/tkbot", 0o755)
        box_l(f"{C.GREEN}✅{C.RESET} {C.WHITE}tkbot command updated{C.RESET}")
    except:
        box_l(f"{C.YELLOW}⚠️{C.RESET} {C.WHITE}Skip (need root for /usr/local/bin){C.RESET}")

    box_bot()
    print()

def cmd_status():
    """Show status — shortcut: tkbot status"""
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(SCRIPT_DIR)
    print()
    box_top()
    box_c(f"{C.BOLD}{C.CYAN}  TKBOT STATUS{C.RESET}")
    box_mid()

    # Check git
    git_hash = os.popen("git rev-parse --short HEAD 2>/dev/null").read().strip()
    git_branch = os.popen("git branch --show-current 2>/dev/null").read().strip()
    box_l(f"{C.CYAN}📂{C.RESET} {C.WHITE}Version{C.RESET}  {C.BOLD}{git_hash}{C.RESET} ({git_branch})")

    # Check devices
    try:
        with open('devices.txt') as f:
            dev_count = sum(1 for l in f if l.strip() and not l.startswith('#'))
        box_l(f"{C.CYAN}📱{C.RESET} {C.WHITE}Devices{C.RESET}  {C.BOLD}{dev_count}{C.RESET}")
    except:
        box_l(f"{C.RED}📱{C.RESET} {C.WHITE}Devices{C.RESET}  {C.RED}file not found{C.RESET}")

    # Check proxies
    try:
        with open('proxies.txt') as f:
            prox_count = sum(1 for l in f if l.strip() and ':' in l)
        box_l(f"{C.PINK}🌐{C.RESET} {C.WHITE}Proxies{C.RESET}  {C.BOLD}{prox_count}{C.RESET}")
    except:
        box_l(f"{C.RED}🌐{C.RESET} {C.WHITE}Proxies{C.RESET}  {C.RED}file not found{C.RESET}")

    # Check config
    try:
        with open('config.json') as f:
            cfg = json.load(f)
        proxy_on = cfg.get('proxy', {}).get('use-proxy', False)
        status_text = f"{C.GREEN}ON{C.RESET}" if proxy_on else f"{C.RED}OFF{C.RESET}"
        box_l(f"{C.YELLOW}⚙️{C.RESET}  {C.WHITE}Proxy{C.RESET}  {status_text}")
    except:
        box_l(f"{C.RED}⚙️{C.RESET}  {C.WHITE}Config{C.RESET}  {C.RED}not found{C.RESET}")

    box_bot()
    print()

def cmd_help():
    """Show help — shortcut: tkbot help"""
    print()
    box_top()
    box_c(f"{C.BOLD}{C.CYAN}  TKBOT — COMMAND REFERENCE{C.RESET}")
    box_mid()
    box_l(f"{C.GREEN}tkbot{C.RESET}            {C.DIM}—{C.RESET} {C.WHITE}Interactive mode (default){C.RESET}")
    box_l(f"{C.GREEN}tkbot run{C.RESET}        {C.DIM}—{C.RESET} {C.WHITE}Langsung jalankan bot{C.RESET}")
    box_l(f"{C.GREEN}tkbot update{C.RESET}     {C.DIM}—{C.RESET} {C.WHITE}Update ke versi terbaru{C.RESET}")
    box_l(f"{C.GREEN}tkbot status{C.RESET}     {C.DIM}—{C.RESET} {C.WHITE}Lihat status & info{C.RESET}")
    box_l(f"{C.GREEN}tkbot help{C.RESET}       {C.DIM}—{C.RESET} {C.WHITE}Tampilkan bantuan ini{C.RESET}")
    box_mid()
    box_l(f"{C.DIM}Shortcut:{C.RESET} {C.PINK}r{C.RESET} = run  {C.PINK}u{C.RESET} = update  {C.PINK}s{C.RESET} = status  {C.PINK}h{C.RESET} = help")
    box_bot()
    print()

def interactive_mode():
    """Main interactive menu — tkbot"""
    banner()

    print(f"  {C.CYAN}╔{'═' * W}╗{C.RESET}")
    box_l(f"{C.BOLD}{C.HOT_PINK}  TKBOT INTERACTIVE{C.RESET}")
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")
    box_l(f"{C.GREEN}1{C.RESET} {C.WHITE}▶ Run Bot{C.RESET}        {C.DIM}— Kirim views{C.RESET}")
    box_l(f"{C.PINK}2{C.RESET} {C.WHITE}🔄 Update{C.RESET}         {C.DIM}— Pull versi terbaru{C.RESET}")
    box_l(f"{C.CYAN}3{C.RESET} {C.WHITE}📊 Status{C.RESET}          {C.DIM}— Info & statistik{C.RESET}")
    box_l(f"{C.YELLOW}4{C.RESET} {C.WHITE}⚙️  Settings{C.RESET}        {C.DIM}— Edit config.json{C.RESET}")
    box_l(f"{C.RED}5{C.RESET} {C.WHITE}✘  Exit{C.RESET}            {C.DIM}— Keluar{C.RESET}")
    print(f"  {C.CYAN}╚{'═' * W}╝{C.RESET}")
    print()

    while True:
        choice = input(f"  {C.PINK}❯{C.RESET} {C.WHITE}Pilih [1-5]: {C.RESET}").strip()

        if choice == "1" or choice.lower() == "r":
            print()
            run_bot()
            break
        elif choice == "2" or choice.lower() == "u":
            print()
            cmd_update()
            input(f"  {C.DIM}Tekan Enter untuk kembali...{C.RESET}")
            interactive_mode()
            break
        elif choice == "3" or choice.lower() == "s":
            cmd_status()
            input(f"  {C.DIM}Tekan Enter untuk kembali...{C.RESET}")
            interactive_mode()
            break
        elif choice == "4" or choice.lower() == "e":
            print()
            os.system("nano config.json 2>/dev/null || notepad config.json 2>/dev/null || vi config.json")
            print(f"  {C.GREEN}✅ Config di-update!{C.RESET}")
            input(f"  {C.DIM}Tekan Enter untuk kembali...{C.RESET}")
            interactive_mode()
            break
        elif choice == "5" or choice.lower() == "q" or choice.lower() == "exit":
            print()
            box_top()
            box_c(f"{C.DIM}Sampai jumpa lagi! 👋{C.RESET}")
            box_bot()
            print()
            sys.exit(0)
        else:
            print(f"  {C.RED}❌ Pilihan tidak valid!{C.RESET}")
            time.sleep(1)
            # Clear screen and redraw
            banner()
            print(f"  {C.CYAN}╔{'═' * W}╗{C.RESET}")
            box_l(f"{C.BOLD}{C.HOT_PINK}  TKBOT INTERACTIVE{C.RESET}")
            print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")
            box_l(f"{C.GREEN}1{C.RESET} {C.WHITE}▶ Run Bot{C.RESET}        {C.DIM}— Kirim views{C.RESET}")
            box_l(f"{C.PINK}2{C.RESET} {C.WHITE}🔄 Update{C.RESET}         {C.DIM}— Pull versi terbaru{C.RESET}")
            box_l(f"{C.CYAN}3{C.RESET} {C.WHITE}📊 Status{C.RESET}          {C.DIM}— Info & statistik{C.RESET}")
            box_l(f"{C.YELLOW}4{C.RESET} {C.WHITE}⚙️  Settings{C.RESET}        {C.DIM}— Edit config.json{C.RESET}")
            box_l(f"{C.RED}5{C.RESET} {C.WHITE}✘  Exit{C.RESET}            {C.DIM}— Keluar{C.RESET}")
            print(f"  {C.CYAN}╚{'═' * W}╝{C.RESET}")
            print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ("run", "r"):
            cmd_run()
        elif cmd in ("update", "u"):
            cmd_update()
        elif cmd in ("status", "s"):
            cmd_status()
        elif cmd in ("help", "h", "--help", "-h"):
            cmd_help()
        else:
            print(f"  {C.RED}❌ Perintah tidak dikenal: {cmd}{C.RESET}")
            print(f"  {C.DIM}Ketik 'tkbot help' untuk bantuan.{C.RESET}")
    else:
        interactive_mode()
