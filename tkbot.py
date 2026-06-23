#!/usr/bin/env python3
# ============================================================
# TkViews v3.0 — All-in-One TikTok Tool (Zefoy Clone)
# Fitur lengkap: Views, Likes, Followers, Shares, Comments
# ============================================================

import os, sys, ssl, re, time, random, threading, requests, json, socket

# ── Config ───────────────────────────────────────────────────
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
    if align == ">": return text + " " * pad
    elif align == "^":
        left = pad // 2; right = pad - left
        return " " * left + text + " " * right
    return text + " " * pad

def box_top(): print(f"  {C.CYAN}╔{'═' * W}╗{C.RESET}")
def box_mid(): print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")
def box_bot(): print(f"  {C.CYAN}╚{'═' * W}╝{C.RESET}")
def box_l(text=""): print(f"  {C.CYAN}║{C.RESET} {_pad(text, W-1)}{C.CYAN}║{C.RESET}")
def box_c(text=""): print(f"  {C.CYAN}║{C.RESET}{_pad(text, W, '^')}{C.CYAN}║{C.RESET}")

def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print()
    box_top()
    box_c("")
    box_c(f"{C.HOT_PINK}{C.BOLD}████████╗██╗  ██╗██╗   ██╗██╗███████╗{C.RESET}")
    box_c(f"{C.HOT_PINK}{C.BOLD}╚══██╔══╝██╗ ██╔╝██║   ██║██║╚════██║{C.RESET}")
    box_c(f"{C.PINK}{C.BOLD}   ██║   █████╔╝ ██║   ██║██║███████╗{C.RESET}")
    box_c(f"{C.PINK}{C.BOLD}   ██║   ██╔═██╗ ╚██╗ ██╔╝██║╚════██║{C.RESET}")
    box_c(f"{C.CYAN}{C.BOLD}   ██║   ██║  ██╗ ╚████╔╝ ██║███████║{C.RESET}")
    box_c(f"{C.CYAN}{C.BOLD}   ╚═╝   ╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝{C.RESET}")
    box_c("")
    box_c(f"{C.CYAN}{C.BOLD}T I K T O K   V I E W B O T{C.RESET}")
    box_c(f"{C.HOT_PINK}{C.BOLD}v 3 . 0{C.RESET}")
    box_c(f"{C.DIM}All-in-One TikTok Tool — Zefoy Clone{C.RESET}")
    box_c("")
    box_mid()
    box_c(f"{C.GREEN}●{C.RESET} Views   {C.PINK}●{C.RESET} Likes   {C.CYAN}●{C.RESET} Followers   {C.YELLOW}●{C.RESET} Shares")
    box_c(f"{C.GREEN}●{C.RESET} Comments   {C.PINK}●{C.RESET} Live Views   {C.CYAN}●{C.RESET} Profile Views")
    box_bot()
    print()

# ── Suppress warnings ────────────────────────────────────────
from urllib3.exceptions import InsecureRequestWarning
from http import cookiejar

class BlockCookies(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *a, **kw: False
    netscape = True; rfc2965 = hide_cookie2 = False

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# ── API Endpoints ────────────────────────────────────────────
API_VIEWS = [
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/?",
    "https://api21.tiktokv.com/aweme/v1/aweme/stats/?",
    "https://api19-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/?",
    "https://api16-va.tiktokv.com/aweme/v1/aweme/stats/?",
]

API_LIKES = [
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/like/?",
    "https://api21.tiktokv.com/aweme/v1/aweme/like/?",
]

API_FOLLOW = [
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/commit/follow/user/?",
    "https://api21.tiktokv.com/aweme/v1/commit/follow/user/?",
]

API_SHARE = [
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/share/?",
    "https://api21.tiktokv.com/aweme/v1/aweme/share/?",
]

API_COMMENT = [
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/comment/publish/?",
    "https://api21.tiktokv.com/aweme/v1/aweme/comment/publish/?",
]

API_PROFILE = [
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/user/profile/?",
    "https://api21.tiktokv.com/aweme/v1/aweme/user/profile/?",
]

# ── User Agents ──────────────────────────────────────────────
def get_ua():
    return (
        'com.zhiliaoapp.musically/2023100000 '
        '(Linux; U; Android 13; en_US; Pixel 7; '
        'Build/TQ3A.230805.001; '
        'Cronet/TTNetVersion:8eac09b7 2023-07-03 '
        'QuicVersion:6ea22060 2023-05-18)'
    )

def get_headers(extra=None):
    h = {
        'User-Agent': get_ua(),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'sdk-version': '2',
        'x-ss-req-ticket': str(int(time.time() * 1000)),
        'x-tt-store-regionc': 'US',
        'x-tt-store-region-src': 'did',
    }
    if extra:
        h.update(extra)
    return h

# ── Globals ──────────────────────────────────────────────────
reqs = 0; success_count = 0; fails = 0; rpm = 0; rps = 0
_lock = threading.Lock()

# ── Proxy functions ──────────────────────────────────────────
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

# ── RPS monitor ──────────────────────────────────────────────
def rps_loop():
    global rps, rpm
    while True:
        init = reqs
        time.sleep(1.5)
        rps = round((reqs - init) / 1.5, 1)
        rpm = round(rps * 60, 1)

# ── Generic sender ───────────────────────────────────────────
def generic_send(did, iid, endpoints, payload, headers_extra=None, label="Request"):
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
            api_url = random.choice(endpoints) + params
            headers = get_headers(headers_extra)

            proxy = ""
            use_proxy = config['proxy']['use-proxy'] and proxies
            if use_proxy:
                proxy = random.choice(proxies)

            proxy_dict = {}
            if proxy:
                proxy_dict = {"http": proxy_format + proxy, "https": proxy_format + proxy}

            resp = requests.post(
                api_url, data=payload, headers=headers,
                verify=False, timeout=15, proxies=proxy_dict
            )

            if not resp.text.strip() and use_proxy:
                resp = requests.post(
                    api_url, data=payload, headers=headers,
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
                    box_l(f"{C.GREEN}✔{C.RESET} {C.WHITE}{label}{C.RESET}  {C.DIM}{impr}{C.RESET}  {C.CYAN}│{C.RESET}  {C.DIM}total:{reqs}{C.RESET}")
                else:
                    fails += 1
                    sys.stdout.write("\033[2K")
                    box_l(f"{C.YELLOW}⚠{C.RESET} {C.WHITE}{label} status {status_code}{C.RESET}  {C.CYAN}│{C.RESET}  {C.DIM}fails:{fails}{C.RESET}")
                _lock.release()
            except:
                if _lock.locked(): _lock.release()
                fails += 1
        except:
            pass

# ── Feature: Views ───────────────────────────────────────────
def send_views(did, iid, cdid, openudid):
    global reqs, success_count, fails
    payload = f"item_id={__aweme_id}&play_delta=1"
    generic_send(did, iid, API_VIEWS, payload, label="View")

# ── Feature: Likes ───────────────────────────────────────────
def send_likes(did, iid, cdid, openudid):
    global reqs, success_count, fails
    payload = f"item_id={__aweme_id}&action=1"
    generic_send(did, iid, API_LIKES, payload, label="Like")

# ── Feature: Followers ───────────────────────────────────────
def send_followers(did, iid, cdid, openudid):
    global reqs, success_count, fails
    payload = f"user_id={__author_id}"
    generic_send(did, iid, API_FOLLOW, payload, label="Follow")

# ── Feature: Shares ──────────────────────────────────────────
def send_shares(did, iid, cdid, openudid):
    global reqs, success_count, fails
    payload = f"item_id={__aweme_id}"
    generic_send(did, iid, API_SHARE, payload, label="Share")

# ── Feature: Comments ────────────────────────────────────────
def send_comments(did, iid, cdid, openudid):
    global reqs, success_count, fails
    comment_text = random.choice(comments_list)
    payload = f"item_id={__aweme_id}&text={comment_text}"
    generic_send(did, iid, API_COMMENT, payload, label="Comment")

# ── Feature: Profile Views ───────────────────────────────────
def send_profile_views(did, iid, cdid, openudid):
    global reqs, success_count, fails
    payload = f"user_id={__author_id}"
    generic_send(did, iid, API_PROFILE, payload, label="Profile")

# ── Comments list ────────────────────────────────────────────
comments_list = [
    "Nice video! 🔥", "Amazing! ❤️", "Love this! 💯",
    "Great content! 👏", "Awesome! 🎉", "So cool! 😍",
    "Best video ever! ⭐", "Incredible! 💪", "Wow! 🤩",
    "Perfect! ✨", "Beautiful! 💕", "Fantastic! 🌟",
    "Brilliant! 🎯", "Superb! 🏆", "Wonderful! 🌈",
]

# ── Run feature ──────────────────────────────────────────────
def run_feature(feature_func, feature_name):
    global config, proxies, proxy_format, __aweme_id, __author_id, reqs, success_count, fails

    banner()

    print(f"  {C.CYAN}╔{'═' * W}╗{C.RESET}")
    box_l(f"{C.BOLD}{C.HOT_PINK}  {feature_name.upper()}{C.RESET}")
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")

    # Input
    if feature_func == send_profile_views or feature_func == send_followers:
        try:
            print(f"  {C.CYAN}║{C.RESET}  {C.PINK}❯{C.RESET} {C.WHITE}Username (without @): {C.RESET}", end="", flush=True)
            username = input().strip().lstrip('@')
            # Get user ID from username
            resp = requests.get(
                f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/user/uniqueid/?unique_id={username}",
                headers=get_headers(), verify=False, timeout=10
            )
            data = resp.json()
            __author_id = data.get('data', {}).get('user_id', '')
            if not __author_id:
                box_l(f"{C.RED}✘{C.RESET} {C.WHITE}User tidak ditemukan!{C.RESET}")
                input()
                return
            box_l(f"{C.GREEN}✔{C.RESET} {C.WHITE}User ID:{C.RESET}  {C.BOLD}{C.CYAN}{__author_id}{C.RESET}")
        except Exception as e:
            box_l(f"{C.RED}✘{C.RESET} {C.WHITE}Error: {e}{C.RESET}")
            input()
            return
    else:
        try:
            print(f"  {C.CYAN}║{C.RESET}  {C.PINK}❯{C.RESET} {C.WHITE}Video link: {C.RESET}", end="", flush=True)
            link = input()
            __aweme_id = str(
                re.findall(r"(\d{18,19})", link)[0]
                if re.findall(r"(\d{18,19})", link)
                else re.findall(r"(\d{18,19})", requests.head(link, allow_redirects=True, timeout=5).url)[0]
            )
            box_l(f"{C.GREEN}✔{C.RESET} {C.WHITE}Video ID:{C.RESET}  {C.BOLD}{C.CYAN}{__aweme_id}{C.RESET}")
        except:
            box_l(f"{C.RED}✘{C.RESET} {C.WHITE}Invalid link!{C.RESET}")
            input()
            return

    print(f"  {C.CYAN}╚{'═' * W}╝{C.RESET}")
    print()

    # Load config
    with open('config.json') as f:
        config = json.load(f)

    with open('devices.txt') as f:
        raw = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    devices = []
    for line in raw:
        parts = line.split(':')
        if len(parts) >= 4 and len(parts[0]) >= 15 and len(parts[1]) >= 10:
            devices.append(line)

    # Init
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

    # Start
    print(f"  {C.CYAN}╔{'═' * W}╗{C.RESET}")
    box_l(f"{C.BOLD}{C.GREEN}  ▶ RUNNING — {feature_name.upper()}{C.RESET}")
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")
    box_l(f"{C.DIM}Menunggu {feature_name.lower()} terkirim... (Ctrl+C untuk stop){C.RESET}")
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")

    reqs = 0; success_count = 0; fails = 0
    threading.Thread(target=rps_loop, daemon=True).start()
    time.sleep(1)

    try:
        while True:
            device = random.choice(devices)
            if threading.active_count() < 100:
                parts = device.split(':')
                did, iid, cdid, openudid = parts[0], parts[1], parts[2], parts[3]
                threading.Thread(target=feature_func, args=(did, iid, cdid, openudid), daemon=True).start()
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

# ── Interactive menu ─────────────────────────────────────────
def interactive_mode():
    banner()

    print(f"  {C.CYAN}╔{'═' * W}╗{C.RESET}")
    box_l(f"{C.BOLD}{C.HOT_PINK}  TKBOT INTERACTIVE — v3.0{C.RESET}")
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")
    box_l(f"{C.GREEN}1{C.RESET} {C.WHITE}▶ Views{C.RESET}          {C.DIM}— Kirim views ke video{C.RESET}")
    box_l(f"{C.PINK}2{C.RESET} {C.WHITE}❤️  Likes{CRESET}           {C.DIM}— Kirim likes ke video{C.RESET}")
    box_l(f"{C.CYAN}3{C.RESET} {C.WHITE}👥 Followers{CRESET}       {C.DIM}— Kirim followers ke user{C.RESET}")
    box_l(f"{C.YELLOW}4{C.RESET} {C.WHITE}🔄 Shares{CRESET}          {C.DIM}— Kirim shares ke video{C.RESET}")
    box_l(f"{C.HOT_PINK}5{C.RESET} {C.WHITE}💬 Comments{CRESET}        {C.DIM}— Kirim comments ke video{C.RESET}")
    box_l(f"{C.GREEN}6{C.RESET} {C.WHITE}👤 Profile Views{CRESET}   {C.DIM}— Kirim profile views{C.RESET}")
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")
    box_l(f"{C.CYAN}7{C.RESET} {C.WHITE}🔄 Update{CRESET}          {C.DIM}— Pull versi terbaru{C.RESET}")
    box_l(f"{C.PINK}8{C.RESET} {C.WHITE}📊 Status{CRESET}           {C.DIM}— Info & statistik{C.RESET}")
    box_l(f"{C.YELLOW}9{C.RESET} {C.WHITE}⚙️  Settings{CRESET}         {C.DIM}— Edit config.json{C.RESET}")
    box_l(f"{C.RED}0{C.RESET} {C.WHITE}✘  Exit{CRESET}             {C.DIM}— Keluar{C.RESET}")
    print(f"  {C.CYAN}╚{'═' * W}╝{C.RESET}")
    print()

    choice = input(f"  {C.PINK}❯{C.RESET} {C.WHITE}Pilih [0-9]: {C.RESET}").strip()

    features = {
        "1": (send_views, "VIEWS"),
        "2": (send_likes, "LIKES"),
        "3": (send_followers, "FOLLOWERS"),
        "4": (send_shares, "SHARES"),
        "5": (send_comments, "COMMENTS"),
        "6": (send_profile_views, "PROFILE VIEWS"),
    }

    if choice in features:
        print()
        run_feature(features[choice][0], features[choice][1])
        input(f"  {C.DIM}Tekan Enter untuk kembali...{C.RESET}")
        interactive_mode()
    elif choice == "7":
        print()
        SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
        os.chdir(SCRIPT_DIR)
        os.system("git pull origin master 2>/dev/null || git pull origin main 2>/dev/null")
        print(f"\n  {C.GREEN}✅ Update selesai!{C.RESET}")
        input(f"  {C.DIM}Tekan Enter untuk kembali...{C.RESET}")
        interactive_mode()
    elif choice == "8":
        print()
        box_top()
        box_c(f"{C.BOLD}{C.CYAN}  TKBOT STATUS{C.RESET}")
        box_mid()
        git_hash = os.popen("git rev-parse --short HEAD 2>/dev/null").read().strip()
        box_l(f"{C.CYAN}📂{C.RESET} {C.WHITE}Version{C.RESET}  {C.BOLD}{git_hash}{C.RESET}")
        try:
            with open('devices.txt') as f:
                dc = sum(1 for l in f if l.strip() and not l.startswith('#'))
            box_l(f"{C.CYAN}📱{C.RESET} {C.WHITE}Devices{C.RESET}  {C.BOLD}{dc}{C.RESET}")
        except: pass
        try:
            with open('proxies.txt') as f:
                pc = sum(1 for l in f if l.strip() and ':' in l)
            box_l(f"{C.PINK}🌐{C.RESET} {C.WHITE}Proxies{C.RESET}  {C.BOLD}{pc}{C.RESET}")
        except: pass
        box_bot()
        print()
        input(f"  {C.DIM}Tekan Enter untuk kembali...{C.RESET}")
        interactive_mode()
    elif choice == "9":
        print()
        os.system("nano config.json 2>/dev/null || vi config.json")
        print(f"  {C.GREEN}✅ Config di-update!{C.RESET}")
        input(f"  {C.DIM}Tekan Enter untuk kembali...{C.RESET}")
        interactive_mode()
    elif choice == "0":
        print()
        box_top()
        box_c(f"{C.DIM}Sampai jumpa lagi! 👋{C.RESET}")
        box_bot()
        print()
        sys.exit(0)
    else:
        print(f"  {C.RED}❌ Pilihan tidak valid!{C.RESET}")
        time.sleep(1)
        interactive_mode()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        features = {
            "views": (send_views, "VIEWS"),
            "likes": (send_likes, "LIKES"),
            "followers": (send_followers, "FOLLOWERS"),
            "shares": (send_shares, "SHARES"),
            "comments": (send_comments, "COMMENTS"),
            "profile": (send_profile_views, "PROFILE VIEWS"),
        }
        if cmd in features:
            run_feature(features[cmd][0], features[cmd][1])
        elif cmd in ("update", "u"):
            SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
            os.chdir(SCRIPT_DIR)
            os.system("git pull origin master 2>/dev/null || git pull origin main 2>/dev/null")
            print(f"\n  {C.GREEN}✅ Update selesai!{C.RESET}\n")
        elif cmd in ("status", "s"):
            print()
            box_top()
            box_c(f"{C.BOLD}{C.CYAN}  TKBOT STATUS{C.RESET}")
            box_mid()
            git_hash = os.popen("git rev-parse --short HEAD 2>/dev/null").read().strip()
            box_l(f"{C.CYAN}📂{C.RESET} {C.WHITE}Version{C.RESET}  {C.BOLD}{git_hash}{C.RESET}")
            box_bot()
            print()
        elif cmd in ("help", "h"):
            print()
            box_top()
            box_c(f"{C.BOLD}{C.CYAN}  TKBOT v3.0 — HELP{C.RESET}")
            box_mid()
            box_l(f"{C.GREEN}tkbot{C.RESET}              {C.DIM}—{C.RESET} {C.WHITE}Interactive menu{C.RESET}")
            box_l(f"{C.GREEN}tkbot views{C.RESET}         {C.DIM}—{C.RESET} {C.WHITE}Kirim views{C.RESET}")
            box_l(f"{C.GREEN}tkbot likes{CRESET}          {C.DIM}—{C.RESET} {C.WHITE}Kirim likes{C.RESET}")
            box_l(f"{C.GREEN}tkbot followers{CRESET}      {C.DIM}—{C.RESET} {C.WHITE}Kirim followers{C.RESET}")
            box_l(f"{C.GREEN}tkbot shares{CRESET}         {C.DIM}—{C.RESET} {C.WHITE}Kirim shares{C.RESET}")
            box_l(f"{C.GREEN}tkbot comments{CRESET}       {C.DIM}—{C.RESET} {C.WHITE}Kirim comments{C.RESET}")
            box_l(f"{C.GREEN}tkbot profile{CRESET}       {C.DIM}—{CRESET} {C.WHITE}Profile views{C.RESET}")
            box_l(f"{C.GREEN}tkbot update{CRESET}        {C.DIM}—{C.RESET} {C.WHITE}Update{C.RESET}")
            box_l(f"{C.GREEN}tkbot status{CRESET}        {C.DIM}—{C.RESET} {C.WHITE}Status{C.RESET}")
            box_l(f"{C.GREEN}tkbot help{CRESET}          {C.DIM}—{CRESET} {C.WHITE}Bantuan{C.RESET}")
            box_bot()
            print()
        else:
            print(f"  {C.RED}❌ Perintah tidak dikenal: {cmd}{C.RESET}")
            print(f"  {C.DIM}Ketik 'tkbot help' untuk bantuan.{C.RESET}")
    else:
        interactive_mode()
