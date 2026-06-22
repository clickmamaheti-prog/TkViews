#!/usr/bin/env python3
"""
TikTok Viewbot v3 - Zefoy API Edition
Menggunakan API zefame-free.com (Zefoy.com backend)
Tidak perlu X-Gorgon signature - langsung via API

Usage: python3 bot_v3.py
"""

import requests
import json
import time
import os
import sys
import uuid
import threading
from datetime import datetime

# ============================================================
# KONFIGURASI
# ============================================================

API_BASE = "https://zefame-free.com/api_free.php"
# Alternatif API (jika utama down):
API_ALTERNATIVES = [
    "https://zefame-free.com/api_free.php",
    "https://zefoy.com/api_free.php",
]

# Service IDs
SERVICES = {
    "views": 229,
    "followers": 228,
    "likes": 232,
    "shares": 235,
    "favorites": 236,
}

# ============================================================

class TikTokViewbot:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
        self.sent = 0
        self.errors = 0
        self.running = True

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def banner(self):
        print("""
 ╦  ╦╦╔═╗╦ ╦╔╗ ╔═╗╔╦╗
 ╚╗╔╝║║╣ ║║║╠╩╗║ ║ ║
  ╚╝ ╩╚═╝╚╩╝╚═╝╚═╝ ╩
  TikTok Viewbot v3 (Zefoy API)
  ─────────────────────────────
        """)

    def get_services(self):
        """Ambil daftar service yang tersedia dari API."""
        try:
            r = self.session.get(f"{API_BASE}?action=config", timeout=15)
            data = r.json()
            services = data.get('data', {}).get('tiktok', {}).get('services', [])
            return services
        except Exception as e:
            print(f"  ❌ Gagal ambil services: {e}")
            return []

    def check_video(self, video_url):
        """Cek dan parse video ID dari URL."""
        try:
            # Coba extract dari URL langsung
            import re
            match = re.findall(r'(\d{18,19})', video_url)
            if match:
                return match[0]

            # Coba dari API
            r = self.session.post(API_BASE, data={
                "action": "checkVideoId",
                "link": video_url
            }, timeout=15)
            data = r.json()
            video_id = data.get("data", {}).get("videoId")
            return video_id
        except Exception as e:
            print(f"  ❌ Gagal parse video ID: {e}")
            return None

    def send_views(self, video_url, service_id=229, max_requests=None):
        """Kirim views ke video TikTok."""
        video_id = self.check_video(video_url)
        if not video_id:
            print("  ❌ Video ID tidak valid!")
            return False

        print(f"  📹 Video ID: {video_id}")
        print(f"  🔄 Mengirim views... (Ctrl+C untuk stop)")
        print()

        count = 0
        while self.running:
            if max_requests and count >= max_requests:
                break

            try:
                order = self.session.post(f"{API_BASE}?action=order", data={
                    "service": service_id,
                    "link": video_url,
                    "uuid": str(uuid.uuid4()),
                    "videoId": video_id
                }, timeout=30)

                result = order.json()

                if result.get("success"):
                    self.sent += 1
                    count += 1
                    next_available = result.get("data", {}).get("nextAvailable")
                    print(f"  ✅ [#{self.sent}] Views terkirim! Next: {next_available}")
                else:
                    self.errors += 1
                    msg = result.get("message", "Unknown error")
                    print(f"  ⚠️ [ERROR] {msg}")

                # Handle cooldown
                if next_available:
                    try:
                        wait_time = float(next_available)
                        current_time = time.time()
                        if wait_time > current_time:
                            sleep_duration = wait_time - current_time
                            if sleep_duration > 0 and sleep_duration < 300:  # max 5 menit
                                print(f"  ⏳ Cooldown: {sleep_duration:.0f}s...")
                                time.sleep(sleep_duration)
                            elif sleep_duration >= 300:
                                print(f"  ⏳ Cooldown terlalu lama ({sleep_duration:.0f}s), skip...")
                                time.sleep(10)
                    except:
                        time.sleep(10)
                else:
                    time.sleep(10)

            except KeyboardInterrupt:
                print("\n  ⏹️ Dihentikan oleh user")
                self.running = False
                break
            except Exception as e:
                self.errors += 1
                print(f"  ❌ Error: {e}")
                time.sleep(5)

        return True

    def run(self):
        """Main loop."""
        self.clear()
        self.banner()

        # Cek services
        print("  🔍 Mengecek services...")
        services = self.get_services()

        if not services:
            print("  ❌ Tidak bisa connect ke API!")
            print("  💡 Coba: pip install requests")
            return

        available = [s for s in services if s.get('available')]
        print(f"  ✅ {len(available)}/{len(services)} services available")
        print()

        # Pilih service
        print("  Pilih service:")
        print("  1. Views (229)")
        print("  2. Followers (228)")
        print("  3. Likes (232)")
        print("  4. Shares (235)")
        print("  5. Favorites (236)")
        print()

        try:
            choice = input("  Pilih (1-5, default=1): ").strip()
            if not choice:
                choice = "1"
            service_map = {"1": 229, "2": 228, "3": 232, "4": 235, "5": 236}
            service_id = service_map.get(choice, 229)
        except KeyboardInterrupt:
            return

        # Input URL
        print()
        try:
            video_url = input("  Masukkan URL video TikTok: ").strip()
        except KeyboardInterrupt:
            return

        if not video_url:
            print("  ❌ URL tidak boleh kosong!")
            return

        # Konfirmasi
        print()
        print(f"  📹 URL: {video_url}")
        print(f"  🎯 Service ID: {service_id}")
        print()

        try:
            confirm = input("  Lanjut? (y/n): ").strip().lower()
            if confirm != 'y':
                return
        except KeyboardInterrupt:
            return

        # Jalankan
        self.clear()
        self.banner()
        self.send_views(video_url, service_id)

        # Ringkasan
        print()
        print("  ═══════════════════════════════")
        print(f"  📊 Ringkasan:")
        print(f"     ✅ Berhasil: {self.sent}")
        print(f"     ❌ Error:    {self.errors}")
        print("  ═══════════════════════════════")


if __name__ == "__main__":
    bot = TikTokViewbot()
    bot.run()
