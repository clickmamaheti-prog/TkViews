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

def auto_fetch_proxies():
    """Ambil proxy terbaru dari GitHub repo."""
    try:
        print("  🔄 Fetching proxy terbaru dari GitHub...")
        resp = requests.get(PROXY_REMOTE_URL, timeout=15)
        resp.raise_for_status()
        with open(PROXY_LOCAL_FILE, 'w') as f:
            f.write(resp.text)
        lines = [l.strip() for l in resp.text.strip().split('\n') if l.strip() and ':' in l]
        print(f"  ✅ {len(lines)} proxy di-fetch dari GitHub")
        return lines
    except Exception as e:
        print(f"  ⚠️ Gagal fetch proxy: {e}")
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
reqs = 0; success = 0; fails = 0; rpm = 0; rps = 0
_lock = threading.Lock()

# ── Send views ───────────────────────────────────────────────
def send(did, iid, cdid, openudid):
    global reqs, success, fails
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

            # Try with proxy first, fallback to direct
            proxy = ""
            use_proxy = config['proxy']['use-proxy'] and proxies
            if use_proxy:
                proxy = random.choice(proxies)

            proxy_dict = {}
            if proxy:
                proxy_dict = {"http": proxy_format + proxy, "https": proxy_format + proxy}

            resp = requests.post(
                api_url,
                data=payload,
                headers=get_headers(),
                verify=False,
                timeout=15,
                proxies=proxy_dict
            )

            # If proxy failed (empty body), retry without proxy
            if not resp.text.strip() and use_proxy:
                resp = requests.post(
                    api_url,
                    data=payload,
                    headers=get_headers(),
                    verify=False,
                    timeout=15
                )

            reqs += 1
            try:
                data = resp.json()
                status = data.get('status_code', -1)
                impr = data.get('log_pb', {}).get('impr_id', 'N/A')
                _lock.acquire()
                if status == 0:
                    success += 1
                    print(f"  ✅ View OK — {impr} | total: {reqs}")
                else:
                    fails += 1
                    print(f"  ⚠️ Status {status} | fails: {fails}")
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
    os.system("cls" if os.name == "nt" else "clear")
    banner = """
╦  ╦╦╔═╗╦ ╦╔╗ ╔═╗╔╦╗
╚╗╔╝║║╣ ║║║╠╩╗║ ║ ║
 ╚╝ ╩╚═╝╚╩╝╚═╝╚═╝ ╩
  TikTok Viewbot v2.1
  Fixed — Updated UA + Headers
"""
    print(banner)

    # Input URL
    try:
        link = input("\n  🔗 Input video link: ")
        __aweme_id = str(
            re.findall(r"(\d{18,19})", link)[0]
            if re.findall(r"(\d{18,19})", link)
            else re.findall(r"(\d{18,19})", requests.head(link, allow_redirects=True, timeout=5).url)[0]
        )
    except:
        input("  ❌ Invalid link! Coba input video ID langsung.")
        sys.exit(0)

    print(f"\n  🎯 Target video ID: {__aweme_id}")
    print("  🚀 Memulai proses...\n")

    # Load config
    with open('config.json') as f:
        config = json.load(f)

    # Load devices (skip comments & invalid lines)
    with open('devices.txt') as f:
        raw = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    devices = []
    for line in raw:
        parts = line.split(':')
        if len(parts) >= 4 and len(parts[0]) >= 15 and len(parts[1]) >= 10:
            devices.append(line)
    print(f"  📋 {len(devices)} valid devices loaded")

    # Fetch & validate proxies
    if config['proxy']['use-proxy']:
        proxy_format = (
            f'{config["proxy"]["proxy-type"].lower()}://'
            f'{config["proxy"]["credential"] + "@" if config["proxy"]["auth"] else ""}'
        )
        all_proxies = auto_fetch_proxies()
        if all_proxies:
            sample = random.sample(all_proxies, min(MAX_VALIDATE, len(all_proxies)))
            print(f"  🔍 Validasi {len(sample)} proxy...")
            online = validate_proxies_parallel(sample)
            proxies = online if online else all_proxies
            print(f"  ✅ {len(proxies)} proxy siap digunakan!\n")
        else:
            print("  ⚠️ Tidak ada proxy, menggunakan koneksi langsung")
            proxies = []
    else:
        proxy_format = ''
        proxies = []
        print("  📋 Mode: tanpa proxy\n")

    threading.Thread(target=rps_loop, daemon=True).start()
    time.sleep(1)

    # Spawn threads
    while True:
        device = random.choice(devices)
        if threading.active_count() < 100:
            parts = device.split(':')
            did, iid, cdid, openudid = parts[0], parts[1], parts[2], parts[3]
            threading.Thread(target=send, args=(did, iid, cdid, openudid), daemon=True).start()
