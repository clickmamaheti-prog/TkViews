#!/usr/bin/env python3
"""
Auto-Update Proxy Fetcher
Mengambil proxy terbaru dari VPSLab Free Proxy List di GitHub
dan validasi proxy yang masih aktif.

Usage: python3 proxy_updater.py
"""

import requests
import concurrent.futures
import time
import json
import os
import sys

# ============================================================
# KONFIGURASI — Ganti sesuai kebutuhan
# ============================================================

# Sumber proxy (raw GitHub URLs)
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/all_proxies.txt",
    "https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/all_elite.txt",
    "https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/all_ssl.txt",
]

# Port yang relevan untuk TikTok Viewbot (HTTP/HTTPS)
HTTP_PORTS = {80, 443, 3128, 8080, 8081, 8888, 9090, 8090, 7443, 9000, 999, 1080, 1081, 1082, 5678, 4145, 4153, 9050, 10808}

# Jumlah thread untuk validasi paralel
MAX_WORKERS = 100

# Timeout koneksi per proxy (detik)
PROXY_TIMEOUT = 5

# File output
OUTPUT_FILE = "proxies.txt"
PROXY_CACHE_FILE = ".proxy_cache.json"

# ============================================================

def fetch_proxies_from_url(url):
    """Ambil proxy dari URL GitHub raw."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        lines = response.text.strip().split('\n')
        proxies = []
        for line in lines:
            line = line.strip().replace('\r', '')
            if line and not line.startswith('#') and ':' in line:
                parts = line.split(':')
                if len(parts) == 2 and parts[0].count('.') == 3:
                    try:
                        port = int(parts[1])
                        if port in HTTP_PORTS:
                            proxies.append(line)
                    except ValueError:
                        continue
        return proxies
    except Exception as e:
        print(f"  ⚠️  Gagal fetch dari {url}: {e}")
        return []

def check_proxy(proxy):
    """Cek apakah proxy masih aktif."""
    import socket
    ip, port = proxy.split(':')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(PROXY_TIMEOUT)
        result = sock.connect_ex((ip, int(port)))
        sock.close()
        if result == 0:
            return (proxy, True)
    except:
        pass
    return (proxy, False)

def get_all_proxies():
    """Ambil proxy dari semua sumber."""
    all_proxies = set()
    for url in PROXY_SOURCES:
        print(f"  📥 Fetching: {url.split('/')[-1]}")
        proxies = fetch_proxies_from_url(url)
        print(f"     → {len(proxies)} proxy ditemukan")
        all_proxies.update(proxies)
    return list(all_proxies)

def validate_proxies(proxies):
    """Validasi proxy secara paralel."""
    print(f"\n  🔍 Validasi {len(proxies)} proxy (paralel {MAX_WORKERS} thread)...")
    online = []
    done = 0
    total = len(proxies)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_proxy, p): p for p in proxies}
        for future in concurrent.futures.as_completed(futures):
            done += 1
            proxy, status = future.result()
            if status:
                online.append(proxy)
            if done % 50 == 0 or done == total:
                print(f"     [{done}/{total}] ✅ {len(online)} online", end='\r')

    return online

def save_proxies(proxies, filename):
    """Simpan proxy ke file."""
    with open(filename, 'w') as f:
        for p in sorted(proxies):
            f.write(p + '\n')

def save_cache(online_count, total_count):
    """Simpan cache metadata."""
    cache = {
        "last_update": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "online": online_count,
        "total": total_count,
        "rate": f"{online_count/total_count*100:.1f}%" if total_count > 0 else "0%"
    }
    with open(PROXY_CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def main():
    print("=" * 55)
    print("🔄 AUTO-UPDATE PROXY FETCHER")
    print("=" * 55)
    print(f"⏰ Waktu: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print()

    # Step 1: Ambil proxy dari semua sumber
    print("📡 Step 1: Mengambil proxy dari sumber...")
    all_proxies = get_all_proxies()
    print(f"\n  📊 Total proxy (dedup): {len(all_proxies)}")

    if not all_proxies:
        print("  ❌ Tidak ada proxy ditemukan!")
        sys.exit(1)

    # Step 2: Validasi proxy
    print()
    print("📡 Step 2: Validasi proxy...")
    start_time = time.time()
    online_proxies = validate_proxies(all_proxies)
    elapsed = time.time() - start_time

    # Step 3: Simpan hasil
    print()
    print()
    print("📡 Step 3: Menyimpan hasil...")
    save_proxies(online_proxies, OUTPUT_FILE)
    save_cache(len(online_proxies), len(all_proxies))

    # Ringkasan
    print()
    print("=" * 55)
    print("📊 HASIL:")
    print(f"  📥 Total diambil  : {len(all_proxies)}")
    print(f"  ✅ Online         : {len(online_proxies)}")
    print(f"  ❌ Offline        : {len(all_proxies) - len(online_proxies)}")
    print(f"  📈 Rate           : {len(online_proxies)/len(all_proxies)*100:.1f}%")
    print(f"  ⏱️  Waktu validasi : {elapsed:.1f} detik")
    print(f"  💾 Disimpan ke    : {OUTPUT_FILE}")
    print("=" * 55)

if __name__ == "__main__":
    main()
