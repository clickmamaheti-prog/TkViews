# do not spam or it will kill devices and ruin fun for others

import base64
from pystyle import *
import os
import sys
import ssl
import re
import time
import random
import threading
import requests
import hashlib
import json
import socket

# ============================================================
# AUTO-PROXY FETCHER — Remote Include Technique
# Otomatis ambil proxy terbaru dari GitHub setiap dijalankan
# ============================================================

PROXY_REMOTE_URL = "https://raw.githubusercontent.com/clickmamaheti-prog/TkViews/master/proxies.txt"
PROXY_LOCAL_FILE = "proxies.txt"
HTTP_PORTS = {80, 443, 3128, 8080, 8081, 8888, 9090, 8090, 7443, 9000, 999, 1080, 1081, 1082, 5678, 4145, 4153, 9050, 10808}
PROXY_TIMEOUT = 5
MAX_VALIDATE = 100  # max proxy untuk divalidasi (hemat waktu)

def auto_fetch_proxies():
    """Ambil proxy terbaru dari GitHub repo."""
    try:
        print(Colorate.Horizontal(Colors.yellow_to_red, "  🔄 Fetching proxy terbaru dari GitHub..."))
        response = requests.get(PROXY_REMOTE_URL, timeout=15)
        response.raise_for_status()
        
        # Simpan ke file lokal
        with open(PROXY_LOCAL_FILE, 'w') as f:
            f.write(response.text)
        
        lines = [l.strip() for l in response.text.strip().split('\n') if l.strip() and ':' in l]
        print(Colorate.Horizontal(Colors.green_to_white, f"  ✅ {len(lines)} proxy di-fetch dari GitHub"))
        return lines
    except Exception as e:
        print(Colorate.Horizontal(Colors.red, f"  ⚠️ Gagal fetch proxy: {e}"))
        print(Colorate.Horizontal(Colors.yellow, f"  📂 Menggunakan proxy lokal: {PROXY_LOCAL_FILE}"))
        try:
            with open(PROXY_LOCAL_FILE, 'r') as f:
                return f.read().splitlines()
        except:
            return []

def validate_proxy(proxy):
    """Cek apakah proxy aktif."""
    ip, port = proxy.split(':')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(PROXY_TIMEOUT)
        result = sock.connect_ex((ip, int(port)))
        sock.close()
        return result == 0
    except:
        return False

def validate_proxies_parallel(proxies, max_workers=50):
    """Validasi proxy secara paralel, return yang online."""
    online = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(validate_proxy, p): p for p in proxies}
        for future in concurrent.futures.as_completed(futures):
            proxy = futures[future]
            try:
                if future.result():
                    online.append(proxy)
            except:
                pass
    return online

# ============================================================
# KODE ASLI BOT (tidak diubah)
# ============================================================

if "linux" in sys.platform.lower():
    os.system("clear")
elif "win" in sys.platform.lower():
    os.system("cls")
else:
    os.system("clear")

print("PLEASE SUBSCRIBE MY CHANNEL GUYS.!!")
os.system("xdg-open https://youtube.com/@jokichannel55")
if "linux" in sys.platform.lower():
    os.system("clear")
elif "win" in sys.platform.lower():
    os.system("cls")
else:
    os.system("clear")

from urllib3.exceptions import InsecureRequestWarning
from http import cookiejar

class BlockCookies(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

r = requests.Session()
r.cookies.set_policy(BlockCookies())

class Gorgon:
    def __init__(self,params:str,data:str,cookies:str,unix:int)->None:self.unix=unix;self.params=params;self.data=data;self.cookies=cookies
    def hash(self,data:str)->str:
        try:_hash=str(hashlib.md5(data.encode()).hexdigest())
        except Exception:_hash=str(hashlib.md5(data).hexdigest())
        return _hash
    def get_base_string(self)->str:base_str=self.hash(self.params);base_str=base_str+self.hash(self.data)if self.data else base_str+str('0'*32);base_str=base_str+self.hash(self.cookies)if self.cookies else base_str+str('0'*32);return base_str
    def get_value(self)->json:base_str=self.get_base_string();return self.encrypt(base_str)
    def encrypt(self,data:str)->json:
        unix=self.unix;len=20;key=[223,119,185,64,185,155,132,131,209,185,203,209,247,194,185,133,195,208,251,195];param_list=[]
        for i in range(0,12,4):
            temp=data[8*i:8*(i+1)]
            for j in range(4):H=int(temp[j*2:(j+1)*2],16);param_list.append(H)
        param_list.extend([0,6,11,28]);H=int(hex(unix),16);param_list.append((H&4278190080)>>24);param_list.append((H&16711680)>>16);param_list.append((H&65280)>>8);param_list.append((H&255)>>0);eor_result_list=[]
        for (A,B) in zip(param_list,key):eor_result_list.append(A^B)
        for i in range(len):C=self.reverse(eor_result_list[i]);D=eor_result_list[(i+1)%len];E=C^D;F=self.rbit_algorithm(E);H=(F^4294967295^len)&255;eor_result_list[i]=H
        result=''
        for param in eor_result_list:result+=self.hex_string(param)
        return{'X-Gorgon':'0404b0d30000'+result,'X-Khronos':str(unix)}
    def rbit_algorithm(self,num):
        result='';tmp_string=bin(num)[2:]
        while len(tmp_string)<8:tmp_string='0'+tmp_string
        for i in range(0,8):result=result+tmp_string[7-i]
        return int(result,2)
    def hex_string(self,num):
        tmp_string=hex(num)[2:]
        if len(tmp_string)<2:tmp_string='0'+tmp_string
        return tmp_string
    def reverse(self,num):tmp_string=self.hex_string(num);return int(tmp_string[1:]+tmp_string[:1],16)

def send(did, iid, cdid, openudid):
    global reqs, _lock, success, fails
    
    for x in range(10):
        try:
            params  = f"device_id={did}&iid={iid}&device_type=SM-G973N&app_name=musically_go&host_abi=armeabi-v7a&channel=googleplay&device_platform=android&version_code=160904&device_brand=samsung&os_version=9&aid=1340"
            payload = f"item_id={__aweme_id}&play_delta=1"
            sig     = Gorgon(params=params, cookies=None, data=None, unix=int(time.time())).get_value()

            proxy = random.choice(proxies) if config['proxy']['use-proxy'] else ""
            response = requests.post(
                url = (
                    "https://api16-va.tiktokv.com/aweme/v1/aweme/stats/?" + params
                ),
                data    = payload,
                headers = {'cookie':'sessionid=90c38a59d8076ea0fbc01c8643efbe47','x-gorgon':sig['X-Gorgon'],'x-khronos':sig['X-Khronos'],'user-agent':'okhttp/3.10.0.1'},
                verify  = False,
                proxies = {"http": proxy_format+proxy, "https": proxy_format+proxy} if config['proxy']['use-proxy'] else {}
            )
            reqs += 1
            try:
                _lock.acquire()
                print(Colorate.Horizontal(Colors.green_to_white, f"+ - Bot views {response.json()['log_pb']['impr_id']} {__aweme_id} {reqs}"))
                _lock.release()
                success += 1
            except:
                if _lock.locked():_lock.release()
                fails += 1
                continue

        except Exception as e:
            pass

def rpsm_loop():
    global rps, rpm
    while True:
        initial = reqs
        time.sleep(1.5)
        rps = round((reqs - initial) / 1.5, 1)
        rpm = round(rps * 60, 1)

def title_loop():
    global rps, rpm, success, fails, reqs
        
    if os.name == "nt":
        while True:
            os.system(f'title TikTok Viewbot by @xtekky ^| success: {success} fails: {fails} reqs: {reqs} rps: {rps} rpm: {rpm}')
            time.sleep(0.1)

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear"); os.system("title TikTok Viewbot by @xtekky" if os.name == "nt" else "")
    txt = """\n\n ╦  ╦╦╔═╗╦ ╦╔╗ ╔═╗╔╦╗\n ╚╗╔╝║║╣ ║║║╠╩╗║ ║ ║ \n  ╚╝ ╩╚═╝╚╩╝╚═╝╚═╝ ╩\n- Youtube: Joki Channel\n- Script : VIEW TikTok.V.1.3 (Auto-Proxy)\n- Author : Rezha Rosdiansyah"""
    print(
        Colorate.Vertical(
            Colors.DynamicMIX((Col.light_blue, Col.purple)), Center.XCenter(txt)
        )
    )
    
    try:
        link = str(Write.Input("\n\n            + Input vidio link: ", Colors.yellow_to_red, interval=0.0001))
        __aweme_id = str(
            re.findall(r"(\d{18,19})", link)[0]
            if len(re.findall(r"(\d{18,19})", link)) == 1
            else re.findall(
                r"(\d{18,19})",
                requests.head(link, allow_redirects=True, timeout=5).url
            )[0]
        )
    except:
        os.system("cls" if os.name == "nt" else "clear")
        input(Col.red + "x - Invalid link, try inputting video id only" + Col.reset)
        sys.exit(0)
    
    os.system("cls" if os.name == "nt" else "clear")
    print("Proses Berlangsung...")
    
    _lock = threading.Lock()
    reqs = 0
    success = 0
    fails = 0
    rpm = 0
    rps = 0
    
    threading.Thread(target=rpsm_loop).start()
    threading.Thread(target=title_loop).start()

    with open('devices.txt', 'r') as f:
        devices = f.read().splitlines()
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # ============================================================
    # AUTO-FETCH PROXY dari GitHub (Remote Include)
    # ============================================================
    if config['proxy']['use-proxy']:
        proxy_format = f'{config["proxy"]["proxy-type"].lower()}://{config["proxy"]["credential"]+"@" if config["proxy"]["auth"] else ""}'
        
        # Fetch proxy terbaru dari GitHub
        proxies = auto_fetch_proxies()
        
        if proxies:
            # Validasi cepat (ambil sample acak untuk hemat waktu)
            sample = random.sample(proxies, min(MAX_VALIDATE, len(proxies)))
            print(Colorate.Horizontal(Colors.yellow_to_red, f"  🔍 Validasi {len(sample)} proxy..."))
            
            import concurrent.futures
            online = validate_proxies_parallel(sample)
            
            if online:
                proxies = online
                print(Colorate.Horizontal(Colors.green_to_white, f"  ✅ {len(proxies)} proxy online siap digunakan!"))
            else:
                print(Colorate.Horizontal(Colors.red, "  ⚠️ Tidak ada proxy online, menggunakan semua proxy"))
        else:
            print(Colorate.Horizontal(Colors.red, "  ❌ Tidak ada proxy tersedia!"))
            sys.exit(1)
    else:
        proxy_format = ''
        proxies = []
    
    time.sleep(2)
    
    while True:
        device = random.choice(devices)

        if eval(base64.b64decode("dGhyZWFkaW5nLmFjdGl2ZV9jb3VudCgpIDwgMTAwICMgZG9uJ3QgY2hhbmdlIGNvdW50IG9yIHUgd2lsbCBraWxsIGRldmljZXMgYW5kIHJ1aW4gZnVuIGZvciBvdGhlcnM=")):
            did, iid, cdid, openudid = device.split(':')
            eval(base64.b64decode('dGhyZWFkaW5nLlRocmVhZCh0YXJnZXQ9c2VuZCxhcmdzPVtkaWQsaWlkLGNkaWQsb3BlbnVkaWRdKS5zdGFydCgp'))
