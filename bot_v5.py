#!/usr/bin/env python3
"""
TikTok Viewbot v5 - Working Edition
Menggunakan Zefoy.com dengan hybrid approach:
- Requests untuk session management
- Manual captcha input (paling reliable)
- Auto-retry dan multi-endpoint

CARA PAKAI:
1. Jalankan: python3 bot_v5.py
2. Masukkan URL video TikTok
3. Buka zefoy.com di browser, solve captcha
4. Masukkan jawaban captcha ke bot
5. Bot akan kirim views otomatis

Atau gunakan mode AUTO dengan OCR (jika tersedia).
"""

import requests
import re
import time
import os
import sys
import base64
import hashlib
import json
import threading
from urllib.parse import unquote, quote
from datetime import datetime

# ============================================================
# KONFIGURASI
# ============================================================

ZEFOY_URL = "https://zefoy.com"

# Service endpoints (base64 encoded)
SERVICES = {
    "followers": "c2VuZF9mb2xsb3dlcnNfdGlrdG9r",
    "hearts": "c2VuZE9nb2xsb3dlcnNfdGlrdG9r",
    "comment_hearts": "c2VuZC9mb2xsb3dlcnNfdGlrdG9r",
    "views": "c2VuZC9mb2xsb3dlcnNfdGlrdG9V",
    "shares": "c2VuZC9mb2xsb3dlcnNfdGlrdG9s",
    "favorites": "c2VuZF9mb2xsb3dlcnNfdGlrdG9L",
}

# OCR solver URL (alternatif)
OCR_SOLVERS = [
    "https://platipus9999.pythonanywhere.com/",
]

# User agents rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# ============================================================

class TikTokViewbot:
    def __init__(self):
        self.session = requests.Session()
        self.sessid = None
        self.sent = 0
        self.errors = 0
        self.running = True
        self.captcha_token = None
        self.alpha_key = None
        self._lock = threading.Lock()
        self._rotate_ua()

    def _rotate_ua(self):
        """Rotate user agent."""
        import random
        ua = random.choice(USER_AGENTS)
        self.session.headers.update({
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def banner(self):
        d = datetime.now()
        print(f"""
 ╦  ╦╦╔═╗╦ ╦╔╗ ╔═╗╔╦╗
 ╚╗╔╝║║╣ ║║║╠╩╗║ ║ ║
  ╚╝ ╩╚═╝╚╩╝╚═╝╚═╝ ╩
  TikTok Viewbot v5 (Working)
  ─────────────────────────────
  {d.strftime('%Y-%m-%d %H:%M:%S')}
        """)

    # ─── Session Management ─────────────────────────────────

    def get_session(self):
        """Ambil PHPSESSID dari zefoy.com."""
        print("  🔍 Mengakses zefoy.com...")
        try:
            r = self.session.get(ZEFOY_URL, timeout=15)
            if r.status_code != 200:
                print(f"  ❌ Gagal akses (HTTP {r.status_code})")
                return False

            self.sessid = self.session.cookies.get('PHPSESSID')
            if self.sessid:
                print(f"  ✅ Session: {self.sessid[:20]}...")
                return True
            else:
                print("  ❌ Tidak dapat PHPSESSID")
                return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    # ─── Captcha Handling ───────────────────────────────────

    def get_captcha_image(self):
        """Ambil gambar captcha dari zefoy."""
        try:
            r = self.session.get(ZEFOY_URL, timeout=15)
            html = r.text

            # Cari captcha image URL
            img_match = re.findall(r'<img[^>]*id="captcha-img"[^>]*src="([^"]*)"', html)
            if not img_match:
                img_match = re.findall(r'<img[^>]*src="([^"]*captch[^"]*)"', html, re.IGNORECASE)

            if img_match:
                img_url = img_match[0]
                if not img_url.startswith('http'):
                    img_url = ZEFOY_URL + '/' + img_url.lstrip('/')

                # Download captcha
                r_img = self.session.get(img_url, timeout=10)
                if r_img.status_code == 200 and len(r_img.content) > 100:
                    with open('/tmp/zefoy_captcha.png', 'wb') as f:
                        f.write(r_img.content)
                    return True

            return False
        except:
            return False

    def solve_captcha_manual(self):
        """Solve captcha dengan input manual."""
        print()
        print("  ═══════════════════════════════════")
        print("  🔐 CAPTCHA REQUIRED")
        print("  ═══════════════════════════════════")
        print()

        # Coba download captcha
        if self.get_captcha_image():
            print(f"  📸 Captcha disimpan: /tmp/zefoy_captcha.png")
        else:
            print(f"  ⚠️ Tidak bisa download captcha otomatis")

        print()
        print(f"  📋 CARA SOLVE CAPTCHA:")
        print(f"  1. Buka browser: {ZEFOY_URL}")
        print(f"  2. Selesaikan captcha di browser")
        print(f"  3. Masukkan jawaban captcha di sini")
        print()

        try:
            answer = input("  📝 Jawaban captcha: ").strip().lower()
            return answer if answer else None
        except KeyboardInterrupt:
            return None

    def solve_captcha_ocr(self):
        """Solve captcha dengan OCR."""
        if not self.get_captcha_image():
            return None

        try:
            with open('/tmp/zefoy_captcha.png', 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')

            for ocr_url in OCR_SOLVERS:
                try:
                    r = requests.post(ocr_url, json={
                        'captcha': encoded,
                        'current_time': datetime.now().strftime("%H:%M:%S")
                    }, timeout=30)

                    if r.status_code == 200:
                        result = r.json()
                        answer = result.get('result', '')
                        if answer:
                            print(f"  ✅ OCR: {answer}")
                            return answer
                except:
                    continue

            return None
        except:
            return None

    def submit_captcha(self, answer):
        """Submit jawaban captcha ke zefoy."""
        if not answer:
            return False

        try:
            # Get fresh page untuk ambil token
            r = self.session.get(ZEFOY_URL, timeout=15)
            html = r.text

            # Cari input name untuk captcha
            input_match = re.findall(r'type="search"[^>]*name="([^"]*)"', html)
            if not input_match:
                input_match = re.findall(r'type="text"[^>]*name="([a-z0-9]{16,})"', html)

            if not input_match:
                print("  ❌ Tidak menemukan captcha input field")
                return False

            captcha_input_name = input_match[0]

            # Submit
            data = {
                captcha_input_name: answer,
                'captcha_encoded': '',
            }

            r = self.session.post(ZEFOY_URL, data=data, timeout=15)

            # Cek hasil
            if 'incorrect' in r.text.lower() or 'wrong' in r.text.lower():
                print("  ❌ Captcha salah!")
                return False
            elif 'captcha' not in r.text.lower():
                print("  ✅ Captcha solved!")
                return True
            else:
                # Cek apakah sudah masuk (ada form video)
                if 'video' in r.text.lower() or 'url' in r.text.lower():
                    print("  ✅ Captcha solved!")
                    return True
                print("  ⚠️ Captcha mungkin salah, tapi lanjut...")
                return True

        except Exception as e:
            print(f"  ❌ Error submit captcha: {e}")
            return False

    # ─── Decrypt ────────────────────────────────────────────

    def decrypt(self, data):
        """Decrypt response dari zefoy."""
        try:
            return base64.b64decode(unquote(data[::-1])).decode()
        except:
            return data

    def decrypt_timer(self, data):
        """Extract timer dari response."""
        try:
            if len(re.findall(r' \d{3}', data)) != 0:
                timer = re.findall(r' \d{3}', data)[0].strip()
            else:
                parts = data.split('= ')
                timer = parts[1].split('\n')[0].strip() if len(parts) > 1 else '60'
            return int(timer)
        except:
            return 60

    # ─── Send Views ─────────────────────────────────────────

    def get_alpha_key(self, video_url, service_endpoint):
        """Get alpha key dari zefoy."""
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

            # Cari alpha key
            alpha_match = re.findall(r'name="([a-z0-9]{16})"', r.text)
            return alpha_match[0] if alpha_match else None
        except:
            return None

    def send_service(self, video_url, service="views", max_count=None):
        """Kirim service (views/followers/likes) ke video TikTok."""
        service_endpoint = SERVICES.get(service, SERVICES["views"])

        print(f"  🎯 Service: {service.upper()}")
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
                alpha_key = self.get_alpha_key(video_url, service_endpoint)
                if not alpha_key:
                    consecutive_errors += 1
                    print(f"  ⚠️ Gagal get alpha key (attempt {consecutive_errors})")
                    if consecutive_errors > 5:
                        print("  ❌ Terlalu banyak error, coba solve captcha ulang...")
                        return False
                    time.sleep(5)
                    continue

                # Step 2: Submit video URL
                r = self.session.post(
                    f"{ZEFOY_URL}/{service_endpoint}",
                    headers={
                        'origin': ZEFOY_URL,
                        'x-requested-with': 'XMLHttpRequest',
                        'cookie': f'PHPSESSID={self.sessid}',
                    },
                    data={alpha_key: video_url},
                    timeout=15
                )

                decrypted = self.decrypt(r.text)

                # Cek status
                if "This service is currently not working" in decrypted:
                    print("  ❌ Service sedang tidak available")
                    time.sleep(30)
                    continue

                if "Server too busy" in decrypted:
                    print("  ⏳ Server busy, tunggu 10s...")
                    time.sleep(10)
                    continue

                if "function updatetimer()" in decrypted:
                    timer = self.decrypt_timer(decrypted)
                    print(f"  ⏳ Timer: {time}s")
                    time.sleep(timer)
                    continue

                # Cari beta key
                beta_match = re.findall(r'name="([a-z0-9]{16})" type="text"', decrypted)
                if not beta_match:
                    beta_match = re.findall(r'name="([a-z0-9]{16})"', decrypted)

                if not beta_match:
                    consecutive_errors += 1
                    print(f"  ⚠️ Gagal get beta key")
                    time.sleep(5)
                    continue

                beta_key = beta_match[0]

                # Step 3: Submit untuk kirim
                time.sleep(1)
                r2 = self.session.post(
                    f"{ZEFOY_URL}/{service_endpoint}",
                    headers={
                        'origin': ZEFOY_URL,
                        'x-requested-with': 'XMLHttpRequest',
                        'cookie': f'PHPSESSID={self.sessid}',
                    },
                    data={beta_key: video_url},
                    timeout=15
                )

                decrypted2 = self.decrypt(r2.text)

                if "Too many requests" in decrypted2:
                    print("  ⏳ Rate limited, tunggu 120s...")
                    time.sleep(120)
                    continue

                # Success!
                try:
                    timer = self.decrypt_timer(decrypted2)
                except:
                    timer = 60

                with self._lock:
                    self.sent += 1
                    count += 1

                print(f"  ✅ [#{self.sent}] {service.upper()} terkirim! Cooldown: {timer}s")
                consecutive_errors = 0

                # Rotate UA setiap 10 request
                if self.sent % 10 == 0:
                    self._rotate_ua()

                time.sleep(timer)

            except KeyboardInterrupt:
                print("\n  ⏹️ Dihentikan oleh user")
                self.running = False
                break
            except Exception as e:
                with self._lock:
                    self.errors += 1
                    consecutive_errors += 1
                print(f"  ❌ Error: {e}")
                time.sleep(10)

        return True

    # ─── Main ───────────────────────────────────────────────

    def run(self):
        """Main loop."""
        self.clear()
        self.banner()

        # Step 1: Get session
        if not self.get_session():
            print("  ❌ Gagal memulai session!")
            return

        # Step 2: Solve captcha
        print()
        print("  Pilih metode captcha:")
        print("  1. Manual (buka zefoy.com di browser)")
        print("  2. OCR (otomatis, mungkin gagal)")
        print()

        try:
            choice = input("  Pilih (1/2, default=1): ").strip()
        except KeyboardInterrupt:
            return

        captcha_solved = False
        for attempt in range(3):
            if attempt > 0:
                print(f"\n  🔄 Retry captcha (attempt {attempt+1}/3)...")

            if choice == "2":
                answer = self.solve_captcha_ocr()
                if answer:
                    captcha_solved = self.submit_captcha(answer)
            else:
                answer = self.solve_captcha_manual()
                if answer:
                    captcha_solved = self.submit_captcha(answer)

            if captcha_solved:
                break

        if not captcha_solved:
            print("  ❌ Gagal solve captcha setelah 3 attempt!")
            return

        # Step 3: Input video URL
        print()
        try:
            video_url = input("  📹 Masukkan URL video TikTok: ").strip()
        except KeyboardInterrupt:
            return

        if not video_url:
            print("  ❌ URL tidak boleh kosong!")
            return

        # Step 4: Pilih service
        print()
        print("  Pilih service:")
        print("  1. Views (recommended)")
        print("  2. Followers")
        print("  3. Likes")
        print("  4. Shares")
        print("  5. Favorites")
        print()

        try:
            svc_choice = input("  Pilih (1-5, default=1): ").strip()
        except KeyboardInterrupt:
            return

        svc_map = {"1": "views", "2": "followers", "3": "hearts", "4": "shares", "5": "favorites"}
        service = svc_map.get(svc_choice, "views")

        # Step 5: Max count (optional)
        print()
        try:
            max_input = input("  🔢 Max views (kosong=unlimited): ").strip()
            max_count = int(max_input) if max_input else None
        except (KeyboardInterrupt, ValueError):
            max_count = None

        # Step 6: Konfirmasi
        print()
        print(f"  ═══════════════════════════════")
        print(f"  📹 URL: {video_url}")
        print(f"  🎯 Service: {service.upper()}")
        print(f"  🔢 Max: {max_count if max_count else 'Unlimited'}")
        print(f"  ═══════════════════════════════")
        print()

        try:
            confirm = input("  Lanjut? (y/n): ").strip().lower()
            if confirm != 'y':
                return
        except KeyboardInterrupt:
            return

        # Step 7: Jalankan
        self.clear()
        self.banner()
        self.send_service(video_url, service, max_count)

        # Ringkasan
        print()
        print("  ═══════════════════════════════")
        print(f"  📊 RINGKASAN:")
        print(f"     ✅ Berhasil : {self.sent}")
        print(f"     ❌ Error    : {self.errors}")
        if self.sent > 0:
            print(f"     📈 Rate     : {self.sent/(self.sent+self.errors)*100:.1f}%")
        print("  ═══════════════════════════════")


if __name__ == "__main__":
    bot = TikTokViewbot()
    bot.run()
