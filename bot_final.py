# ============================================================
# TikTok Viewbot v2.1 — Fixed & Working ✅
# Auto-proxy, multi-threaded, updated UA + headers
# ============================================================
# Jangan spam — akan merusak devices dan pengalaman orang lain
# ============================================================

import os, sys, ssl, re, time, random, threading, requests, json, socket

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

W = 60  # box inner width (between ║ chars)

def _vis_len(text):
    """Get visible length (without ANSI codes)."""
    return len(re.sub(r'\033\[[0-9;]*m', '', text))

def _pad(text, width=W, align="<"):
    """Pad text to exact visible width."""
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
    """Left-aligned with 1 space indent."""
    print(f"  {C.CYAN}║{C.RESET} {_pad(text, W-1)}{C.CYAN}║{C.RESET}")

def box_c(text=""):
    """Center-aligned."""
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
    """Ambil proxy terbaru dari GitHub repo."""
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

# ── Suppress warnings ────────────────────────────────────────
from urllib3.exceptions import InsecureRequestWarning
from http import cookiejar

class BlockCookies(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *a, **kw: False
    netscape = True; rfc2965 = hide_cookie2 = False

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# ── API Endpoints ────────────────────────────────────────────
API_ENDPOINTS = [
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/?",
    "https://api21.tiktokv.com/aweme/v1/aweme/stats/?",
    "https://api19-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/?",
    "https://api16-va.tiktokv.com/aweme/v1/aweme/stats/?",
]

# ── Updated User-Agent ───────────────────────────────────────
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

# ── Globals ──────────────────────────────────────────────────
reqs = 0; success_count = 0; fails = 0; rpm = 0; rps = 0
_lock = threading.Lock()

# ── Send views ───────────────────────────────────────────────
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

            # If proxy failed, retry without proxy
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

# ── RPS monitor ──────────────────────────────────────────────
def rps_loop():
    global rps, rpm
    while True:
        init = reqs
        time.sleep(1.5)
        rps = round((reqs - init) / 1.5, 1)
        rpm = round(rps * 60, 1)

# ── Main ─────────────────────────────────────────────────────
if __name__ == "__main__":
    banner()

    # ── Input URL ──
    print(f"  {C.CYAN}╔{'═' * W}╗{C.RESET}")
    box_l(f"{C.BOLD}{C.HOT_PINK}  TARGET INPUT{C.RESET}")
    print(f"  {C.CYAN}╠{'═' * W}╣{C.RESET}")

    try:
        link = input(f"  {C.CYAN}║{C.RESET}  {C.PINK}❯{C.RESET} {C.WHITE}Video link: {C.RESET}")
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

    # Spawn threads
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
