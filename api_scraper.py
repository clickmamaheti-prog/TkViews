#!/usr/bin/env python3
"""
Auto-Scrape TikTok API Endpoint
Mencari dan memvalidasi API endpoint TikTok yang masih aktif.
Menggunakan teknik scraping dari berbagai sumber.

Usage: python3 api_scraper.py
"""

import requests
import concurrent.futures
import time
import json
import re
import os

# ============================================================
# KONFIGURASI
# ============================================================

# Sumber untuk scrape API endpoint
SCRAPE_SOURCES = [
    # GitHub repos yang sering update API TikTok
    "https://raw.githubusercontent.com/xtekky/TikTok-Viewbot/main/bot.py",
    "https://raw.githubusercontent.com/0xbyt4/TikTok-Viewbot/main/bot.py",
]

# API endpoints yang akan divalidasi
API_ENDPOINTS = [
    "https://api16-va.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api19-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api22-normal-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api21.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api16-core-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/",
    "https://api19-core-c-useast1a.tiktokv.com/aweme/v1/aweme/stats/",
]

# Parameter default untuk test
TEST_PARAMS = {
    "device_id": "1234567890123456789",
    "iid": "123456789012345",
    "device_type": "SM-G973N",
    "app_name": "musically_go",
    "host_abi": "armeabi-v7a",
    "channel": "googleplay",
    "device_platform": "android",
    "version_code": "160904",
    "device_brand": "samsung",
    "os_version": "9",
    "aid": "1340"
}

TEST_PAYLOAD = {
    "item_id": "7126536525008882949",
    "play_delta": "1"
}

MAX_WORKERS = 10
OUTPUT_FILE = "api_endpoints.json"

# ============================================================

def scrape_github_for_api(url):
    """Scrape GitHub repo untuk cari API endpoint."""
    endpoints = []
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            # Cari pattern URL API TikTok
            patterns = [
                r'https://api[\w\-.]+\.tiktokv\.com[/\w]+',
                r'https://api[\w\-.]+\.tiktok\.com[/\w]+',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, response.text)
                endpoints.extend(matches)
    except:
        pass
    return list(set(endpoints))

def validate_api_endpoint(url):
    """Validasi API endpoint TikTok."""
    try:
        headers = {
            'cookie': 'sessionid=test',
            'x-gorgon': 'test',
            'x-khronos': 'test',
            'user-agent': 'okhttp/3.10.0.1'
        }
        response = requests.post(
            url,
            params=TEST_PARAMS,
            data=TEST_PAYLOAD,
            headers=headers,
            timeout=10,
            verify=False
        )
        return {
            "url": url,
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "content_length": len(response.content),
            "working": response.status_code == 200
        }
    except Exception as e:
        return {
            "url": url,
            "status_code": 0,
            "response_time": 0,
            "content_length": 0,
            "working": False,
            "error": str(e)
        }

def main():
    print("=" * 55)
    print("🔍 AUTO-SCRAPE TIKTOK API ENDPOINT")
    print("=" * 55)
    print(f"⏰ Waktu: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print()

    # Step 1: Scrape dari GitHub
    print("📡 Step 1: Scraping GitHub untuk API endpoints...")
    scraped_endpoints = set()
    for url in SCRAPE_SOURCES:
        print(f"  📥 {url.split('/')[3]}/{url.split('/')[4]}")
        endpoints = scrape_github_for_api(url)
        scraped_endpoints.update(endpoints)
        print(f"     → {len(endpoints)} endpoint ditemukan")

    # Gabungkan dengan endpoint default
    all_endpoints = list(set(API_ENDPOINTS) | scraped_endpoints)
    print(f"\n  📊 Total endpoint unik: {len(all_endpoints)}")

    # Step 2: Validasi endpoint
    print()
    print("📡 Step 2: Validasi endpoint (paralel)...")
    results = []
    working = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(validate_api_endpoint, url): url for url in all_endpoints}
        done = 0
        for future in concurrent.futures.as_completed(futures):
            done += 1
            result = future.result()
            results.append(result)
            status = "✅" if result["working"] else "❌"
            print(f"  [{done}/{len(all_endpoints)}] {status} {result['url'].split('tiktokv.com')[0].split('//')[1]}... → HTTP {result['status_code']} ({result['response_time']:.2f}s)")
            if result["working"]:
                working.append(result)

    # Step 3: Simpan hasil
    print()
    print("📡 Step 3: Menyimpan hasil...")
    output = {
        "last_update": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_endpoints": len(all_endpoints),
        "working_endpoints": len(working),
        "results": results,
        "working": working
    }
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    # Ringkasan
    print()
    print("=" * 55)
    print("📊 HASIL:")
    print(f"  📥 Total dicek    : {len(all_endpoints)}")
    print(f"  ✅ Working        : {len(working)}")
    print(f"  ❌ Not working    : {len(all_endpoints) - len(working)}")
    print(f"  💾 Disimpan ke    : {OUTPUT_FILE}")
    print()

    if working:
        print("--- Endpoint yang WORKING ---")
        for w in working:
            print(f"  ✅ {w['url']} (HTTP {w['status_code']}, {w['response_time']:.2f}s)")
    print("=" * 55)

if __name__ == "__main__":
    main()
