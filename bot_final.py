# ============================================================
# TikTok Viewbot v2.0 — Final Clean Version
# Auto-proxy, multi-threaded, Gorgon signature
# ============================================================
# Jangan spam — akan merusak devices dan pengalaman orang lain
# ============================================================

import base64, os, sys, ssl, re, time, random, threading, requests, hashlib, json, socket

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
                return f.read().splitlines()
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

def validate_proxies_parallel(proxies, max_workers=50):
    import concurrent.futures
    online = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(validate_proxy, p): p for p in proxies}
        for f in concurrent.futures.as_completed(futs):
            try:
                if f.result():
                    online.append(futs[f])
            except:
                pass
    return online

# ── Gorgon signature ─────────────────────────────────────────
class Gorgon:
    def __init__(self, params, data, cookies, unix):
        self.unix = unix; self.params = params; self.data = data; self.cookies = cookies

    def hash(self, data):
        try:    return str(hashlib.md5(data.encode()).hexdigest())
        except: return str(hashlib.md5(data).hexdigest())

    def get_base_string(self):
        b = self.hash(self.params)
        b += self.hash(self.data) if self.data else '0' * 32
        b += self.hash(self.cookies) if self.cookies else '0' * 32
        return b

    def get_value(self):
        return self.encrypt(self.get_base_string())

    def encrypt(self, data):
        unix = self.unix; ln = 20
        key = [223,119,185,64,185,155,132,131,209,185,203,209,247,194,185,133,195,208,251,195]
        pl = []
        for i in range(0, 12, 4):
            tmp = data[8*i:8*(i+1)]
            for j in range(4):
                pl.append(int(tmp[j*2:(j+1)*2], 16))
        pl.extend([0, 6, 11, 28])
        H = int(hex(unix), 16)
        pl.extend([(H & 4278190080) >> 24, (H & 16711680) >> 16, (H & 65280) >> 8, H & 255])
        eor = [a ^ b for a, b in zip(pl, key)]
        for i in range(ln):
            C = self.reverse(eor[i])
            D = eor[(i + 1) % ln]
            E = C ^ D
            F = self.rbit_algorithm(E)
            H2 = (F ^ 4294967295 ^ ln) & 255
            eor[i] = H2
        result = ''.join(self.hex_string(p) for p in eor)
        return {'X-Gorgon': '0404b0d30000' + result, 'X-Khronos': str(unix)}

    def rbit_algorithm(self, num):
        s = bin(num)[2:].zfill(8)
        return int(s[::-1], 2)

    def hex_string(self, num):
        s = hex(num)[2:]
        return s if len(s) >= 2 else '0' + s

    def reverse(self, num):
        s = self.hex_string(num)
        return int(s[1:] + s[:1], 16)

# ── Suppress warnings ────────────────────────────────────────
from urllib3.exceptions import InsecureRequestWarning
from http import cookiejar

class BlockCookies(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *a, **kw: False
    netscape = True; rfc2965 = hide_cookie2 = False

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

r = requests.Session()
r.cookies.set_policy(BlockCookies())

# ── Globals ──────────────────────────────────────────────────
reqs = 0; success = 0; fails = 0; rpm = 0; rps = 0
_lock = threading.Lock()

# ── Send views ───────────────────────────────────────────────
def send(did, iid, cdid, openudid):
    global reqs, success, fails
    for _ in range(10):
        try:
            params  = (f"device_id={did}&iid={iid}&device_type=SM-G973N"
                       f"&app_name=musically_go&host_abi=armeabi-v7a"
                       f"&channel=googleplay&device_platform=android"
                       f"&version_code=160904&device_brand=samsung"
                       f"&os_version=9&aid=1340")
            payload = f"item_id={__aweme_id}&play_delta=1"
            sig     = Gorgon(params=params, cookies=None, data=None, unix=int(time.time())).get_value()

            proxy = random.choice(proxies) if config['proxy']['use-proxy'] else ""
            resp  = requests.post(
                "https://api16-va.tiktokv.com/aweme/v1/aweme/stats/?" + params,
                data=payload,
                headers={
                    'cookie': 'sessionid=90c38a59d8076ea0fbc01c8643efbe47',
                    'x-gorgon': sig['X-Gorgon'],
                    'x-khronos': sig['X-Khronos'],
                    'user-agent': 'okhttp/3.10.0.1'
                },
                verify=False,
                proxies={"http": proxy_format + proxy, "https": proxy_format + proxy} if config['proxy']['use-proxy'] else {}
            )
            reqs += 1
            try:
                _lock.acquire()
                print(f"  ✅ View sent — {resp.json()['log_pb']['impr_id']} | total: {reqs}")
                _lock.release()
                success += 1
            except:
                if _lock.locked(): _lock.release()
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
  TikTok Viewbot v2.0
  Auto-Proxy + Multi-Thread
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

    with open('devices.txt') as f:
        devices = f.read().splitlines()

    # Fetch & validate proxies
    if config['proxy']['use-proxy']:
        proxy_format = (f'{config["proxy"]["proxy-type"].lower()}://'
                        f'{config["proxy"]["credential"] + "@" if config["proxy"]["auth"] else ""}')
        all_proxies = auto_fetch_proxies()
        if all_proxies:
            sample = random.sample(all_proxies, min(MAX_VALIDATE, len(all_proxies)))
            print(f"  🔍 Validasi {len(sample)} proxy...")
            online = validate_proxies_parallel(sample)
            proxies = online if online else all_proxies
            print(f"  ✅ {len(proxies)} proxy siap digunakan!\n")
        else:
            print("  ❌ Tidak ada proxy tersedia!")
            sys.exit(1)
    else:
        proxy_format = ''
        proxies = []

    threading.Thread(target=rps_loop, daemon=True).start()
    time.sleep(1)

    # Spawn threads
    while True:
        device = random.choice(devices)
        if threading.active_count() < 100:
            did, iid, cdid, openudid = device.split(':')
            threading.Thread(target=send, args=(did, iid, cdid, openudid), daemon=True).start()
