#!/usr/bin/env python3
"""
TikTok Viewbot v6 - Captcha Helper
Menampilkan link captcha Zefoy.com untuk di-solve secara manual
Setelah captcha solved, bot akan kirim views otomatis

Usage: python3 bot_v6.py
"""

import requests
import re
import time
import os
import sys
import base64
import json
import threading
from urllib.parse import unquote
from datetime import datetime

# ============================================================
# KONFIGURASI
# ============================================================

ZEFOY_URL = "https://zefoy.com"

SERVICES = {
    "followers": "c2VuZF9mb2xsb3dlcnNfdGlrdG9r",
    "hearts": "c2VuZE9nb2xsb3dlcnNfdGlrdG9r",
    "comment_hearts": "c2VuZC9mb2xsb3dlcnNfdGlrdG9r",
    "views": "c2VuZC9mb2xsb3dlcnNfdGlrdG9V",
    "shares": "c2VuZC9mb2xsb3dlcnNfdGlrdG9s",
    "favorites": "c2VuZF9mb2xsb3dlcnNfdGlrdG9L",
}

# ============================================================

class ZefoyBot:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.sessid = None
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
  TikTok Viewbot v6
  ──────────────────
        """)

    def get_session(self):
        """Ambil session dari zefoy."""
        print("  🔍 Mengakses zefoy.com...")
        r = self.session.get(ZEFOY_URL, timeout=15)
        self.sessid = self.session.cookies.get('PHPSESSID')
        if self.sessid:
            print(f"  ✅ Session: {self.sessid}")
            return True
        return False

    def show_captcha_link(self):
        """Tampilkan link captcha untuk di-solve."""
        print()
        print("  ═══════════════════════════════════════════════")
        print("  🔐 CAPTCHA REQUIRED — IKUTI LANGKAH INI:")
        print("  ═══════════════════════════════════════════════")
        print()
        print(f"  1. Buka link ini di browser:")
        print(f"     {ZEFOY_URL}/")
        print()
        print(f"  2. Buka Developer Tools (F12) → Application → Cookies")
        print(f"  3. Set cookie 'PHPSESSID' ke nilai ini:")
        print(f"     {self.sessid}")
        print()
        print(f"  4. Refresh halaman → Solve captcha")
        print(f"  5. Setelah captcha solved, tekan Enter di sini")
        print()
        print(f"  ═══════════════════════════════════════════════")
        print()

        # Coba ambil captcha image URL dari JS
        r = self.session.get(ZEFOY_URL, timeout=15)
        html = r.text

        # Download semua JS dan cari captcha URL pattern
        ext_js = re.findall(r'<script[^>]*src="([^"]*)"', html)
        captcha_urls = []

        for js_url in ext_js:
            if not js_url.startswith('http'):
                js_url = ZEFOY_URL + '/' + js_url.lstrip('/')
            try:
                js_r = session.get(js_url, timeout=10)
                # Cari URL pattern untuk captcha
                urls = re.findall(r'["\']([^"\']*captcha[^"\']*)["\']', js_r.text, re.IGNORECASE)
                captcha_urls.extend(urls)
            except:
                pass

        if captcha_urls:
            print("  📸 Kemungkinan URL captcha:")
            for url in set(captcha_urls)[:5]:
                if not url.startswith('http'):
                    url = ZEFOY_URL + '/' + url.lstrip('/')
                print(f"     {url}")
            print()

        # Alternatif: buat URL captcha langsung
        print("  📸 Atau coba buka URL captcha langsung:")
        print(f"     {ZEFOY_URL}/captcha.php")
        print(f"     {ZEFOY_URL}/assets/captcha.php")
        print(f"     {ZEFOY_URL}/captcha")
        print()

    def wait_for_captcha(self):
        """Tunggu user solve captcha."""
        try:
            input("  ⏳ Tekan Enter setelah solve captcha...")
            return True
        except KeyboardInterrupt:
            return False

    def decrypt(self, data):
        try:
            return base64.b64decode(unquote(data[::-1])).decode()
        except:
            return data

    def decrypt_timer(self, data):
        try:
            if len(re.findall(r' \d{3}', data)) != 0:
                timer = re.findall(r' \d{3}', data)[0].strip()
            else:
                parts = data.split('= ')
                timer = parts[1].split('\n')[0].strip() if len(parts) > 1 else '60'
            return int(timer)
        except:
            return 60

    def test_captcha_solved(self, video_url):
        """Test apakah captcha sudah solved dengan mencoba akses form."""
        service_endpoint = SERVICES["views"]

        try:
            r = self.session.post(
                f"{ZEFOY_URL}/{service_endpoint}",
                headers={
                    'origin': ZEFOY_URL,
                    'x-requested-with': 'XMLHttpRequest',
                    'cookie': f'PHPSESSID={self.sessid}',
                },
                data={'': video_url},
                timeout=15
            )

            decrypted = self.decrypt(r.text)

            # Cek apakah captcha masih diminta
            if 'captcha' in decrypted.lower() and ('incorrect' in decrypted.lower() or 'solve' in decrypted.lower()):
                return False, "Captcha belum solved atau salah"

            # Cek apakah ada form video
            if 'video' in decrypted.lower() or 'url' in decrypted.lower() or 'enter' in decrypted.lower():
                return True, "Captcha solved! Form video ditemukan"

            # Cek alpha key
            alpha_match = re.findall(r'name="([a-z0-9]{16})"', r.text)
            if alpha_match:
                return True, f"Captcha solved! Alpha key: {alpha_match[0]}"

            return None, f"Response: {decrypted[:200]}"

        except Exception as e:
            return False, f"Error: {e}"

    def send_views(self, video_url, max_count=None):
        """Kirim views ke video TikTok."""
        service_endpoint = SERVICES["views"]

        print(f"  🎯 Service: VIEWS")
        print(f"  📹 URL: {video_url}")
        print(f"  🔄 Memulai... (Ctrl+C untuk stop)")
        print()

        count = 0
        consecutive_errors = 0

        while self.running:
            if max_count and count >= max_count:
                print(f"  ✅ Target {max_count} views tercapai!")
                break

            try:
                # Step 1: Get alpha key
                r = self.session.post(
                    f"{ZEFOY_URL}/{service_endpoint}",
                    headers={
                        'origin': ZEFOY_URL,
                        'x-requested-with': 'XMLHttpRequest',
                        'cookie': f'PHPSESSID={self.sessid}',
                    },
                    data={'': video_url},
                    timeout=15
                )

                decrypted = self.decrypt(r.text)

                # Cek captcha
                if 'captcha' in decrypted.lower():
                    print("  ❌ Captcha masih diminta! Solve captcha dulu.")
                    return False

                # Cari alpha key
                alpha_match = re.findall(r'name="([a-z0-9]{16})"', r.text)
                if not alpha_match:
                    consecutive_errors += 1
                    print(f"  ⚠️ Gagal get alpha key ({consecutive_errors})")
                    if consecutive_errors > 5:
                        return False
                    time.sleep(5)
                    continue

                alpha_key = alpha_match[0]

                # Step 2: Submit video URL
                r2 = self.session.post(
                    f"{ZEFOY_URL}/{service_endpoint}",
                    headers={
                        'origin': ZEFOY_URL,
                        'x-requested-with': 'XMLHttpRequest',
                        'cookie': f'PHPSESSID={self.sessid}',
                    },
                    data={alpha_key: video_url},
                    timeout=15
                )

                decrypted2 = self.decrypt(r2.text)

                if "This service is currently not working" in decrypted2:
                    print("  ❌ Service sedang tidak available")
                    time.sleep(30)
                    continue

                if "Server too busy" in decrypted2:
                    print("  ⏳ Server busy, tunggu 10s...")
                    time.sleep(10)
                    continue

                if "function updatetimer()" in decrypted2:
                    timer = self.decrypt_timer(decrypted2)
                    print(f"  ⏳ Timer: {timer}s")
                    time.sleep(timer)
                    continue

                # Cari beta key
                beta_match = re.findall(r'name="([a-z0-9]{16})" type="text"', decrypted2)
                if not beta_match:
                    beta_match = re.findall(r'name="([a-z0-9]{16})"', decrypted2)

                if not beta_match:
                    consecutive_errors += 1
                    print(f"  ⚠️ Gagal get beta key")
                    time.sleep(5)
                    continue

                beta_key = beta_match[0]

                # Step 3: Submit untuk kirim views
                time.sleep(1)
                r3 = self.session.post(
                    f"{ZEFOY_URL}/{service_endpoint}",
                    headers={
                        'origin': ZEFOY_URL,
                        'x-requested-with': 'XMLHttpRequest',
                        'cookie': f'PHPSESSID={self.sessid}',
                    },
                    data={beta_key: video_url},
                    timeout=15
                )

                decrypted3 = self.decrypt(r3.text)

                if "Too many requests" in decrypted3:
                    print("  ⏳ Rate limited, tunggu 120s...")
                    time.sleep(120)
                    continue

                # Success!
                try:
                    timer = self.decrypt_timer(decrypted3)
                except:
                    timer = 60

                self.sent += 1
                count += 1
                consecutive_errors = 0

                print(f"  ✅ [#{self.sent}] Views terkirim! Cooldown: {timer}s")

                time.sleep(timer)

            except KeyboardInterrupt:
                print("\n  ⏹️ Dihentikan oleh user")
                self.running = False
                break
            except Exception as e:
                self.errors += 1
                consecutive_errors += 1
                print(f"  ❌ Error: {e}")
                time.sleep(10)

        return True

    def run(self, video_url, max_count=None):
        """Main loop."""
        self.clear()
        self.banner()

        print(f"  📹 Video: {video_url}")
        print()

        # Step 1: Get session
        if not self.get_session():
            print("  ❌ Gagal memulai session!")
            return

        # Step 2: Show captcha link
        self.show_captcha_link()

        # Step 3: Wait for captcha
        if not self.wait_for_captcha():
            return

        # Step 4: Test captcha
        print("  🔍 Testing captcha...")
        for attempt in range(3):
            solved, msg = self.test_captcha_solved(video_url)
            print(f"     Attempt {attempt+1}: {msg}")
            if solved:
                break
            if attempt < 2:
                print("     Coba solve captcha lagi...")
                self.wait_for_captcha()

        # Step 5: Jalankan
        self.clear()
        self.banner()
        self.send_views(video_url, max_count)

        # Ringkasan
        print()
        print("  ═══════════════════════════════")
        print(f"  📊 RINGKASAN:")
        print(f"     ✅ Views terkirim: {self.sent}")
        print(f"     ❌ Error: {self.errors}")
        print("  ═══════════════════════════════")


if __name__ == "__main__":
    VIDEO_URL = "https://www.tiktok.com/@tizar110/video/7586933665398131988"
    bot = ZefoyBot()
    bot.run(VIDEO_URL, max_count=10)
