#!/usr/bin/env python3
"""
TikTok Viewbot v4 - Zefoy Direct Edition
Menggunakan Zefoy.com langsung via HTTP requests
Tidak perlu Selenium/Chrome - pure requests

Flow:
1. Buka zefoy.com → ambil PHPSESSID + captcha token
2. Solve captcha (manual input / OCR)
3. Submit captcha → dapatkan session
4. Kirim views berulang

Usage: python3 bot_v4.py
"""

import requests
import re
import time
import os
import sys
import base64
import json
from urllib.parse import unquote

# ============================================================
# KONFIGURASI
# ============================================================

ZEFOY_URL = "https://zefoy.com"
CAPTCHA_SOLVER_URL = "https://platipus9999.pythonanywhere.com/"

# Service mapping (base64 encoded endpoints)
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
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.sessid = None
        self.sent = 0
        self.errors = 0

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def banner(self):
        print("""
 ╦  ╦╦╔═╗╦ ╦╔╗ ╔═╗╔╦╗
 ╚╗╔╝║║╣ ║║║╠╩╗║ ║ ║
  ╚╝ ╩╚═╝╚╩╝╚═╝╚═╝ ╩
  TikTok Viewbot v4 (Zefoy Direct)
  ─────────────────────────────────
        """)

    def get_session(self):
        """Ambil PHPSESSID dari zefoy.com."""
        print("  🔍 Mengakses zefoy.com...")
        r = self.session.get(ZEFOY_URL, timeout=15)
        if r.status_code != 200:
            print(f"  ❌ Gagal akses zefoy.com (HTTP {r.status_code})")
            return False

        self.sessid = self.session.cookies.get('PHPSESSID')
        if not self.sessid:
            print("  ❌ Tidak dapat PHPSESSID")
            return False

        print(f"  ✅ Session: {self.sessid[:16]}...")
        return True

    def get_captcha_data(self):
        """Ambil data captcha dari halaman zefoy."""
        r = self.session.get(ZEFOY_URL, timeout=15)
        html = r.text

        # Cari captcha image
        captcha_match = re.findall(r'<img[^>]*src="([^"]*captch[^"]*)"', html, re.IGNORECASE)
        if not captcha_match:
            captcha_match = re.findall(r'<img[^>]*src="([^"]*[^"]*)"', html, re.IGNORECASE)

        # Cari hidden token
        token_match = re.findall(r'<input type="hidden" name="([^"]*)"', html)

        # Cari input name untuk captcha answer
        input_match = re.findall(r'type="text" name="([^"]*)" oninput=', html)

        return {
            'html': html,
            'captcha_imgs': captcha_match,
            'tokens': token_match,
            'input_name': input_match[0] if input_match else None,
        }

    def solve_captcha_manual(self):
        """Solve captcha dengan input manual."""
        data = self.get_captcha_data()

        print()
        print("  ═══════════════════════════════════")
        print("  🔐 CAPTCHA REQUIRED")
        print("  ═══════════════════════════════════")
        print()
        print(f"  Buka browser: {ZEFOY_URL}")
        print(f"  Session: {self.sessid[:16]}...")
        print()

        # Coba download captcha image
        if data['captcha_imgs']:
            captcha_url = data['captcha_imgs'][0]
            if not captcha_url.startswith('http'):
                captcha_url = ZEFOY_URL + captcha_url

            try:
                r = self.session.get(captcha_url, timeout=10)
                if r.status_code == 200:
                    # Save captcha
                    with open('/tmp/zefoy_captcha.png', 'wb') as f:
                        f.write(r.content)
                    print(f"  📸 Captcha disimpan: /tmp/zefoy_captcha.png")
            except:
                pass

        # Input manual
        try:
            captcha_answer = input("  📝 Masukkan jawaban captcha: ").strip()
        except KeyboardInterrupt:
            return None

        return {
            'answer': captcha_answer,
            'input_name': data['input_name'],
            'tokens': data['tokens'],
        }

    def solve_captcha_ocr(self):
        """Solve captcha dengan OCR (otomatis)."""
        data = self.get_captcha_data()

        if not data['captcha_imgs']:
            print("  ❌ Tidak menemukan captcha image")
            return None

        captcha_url = data['captcha_imgs'][0]
        if not captcha_url.startswith('http'):
            captcha_url = ZEFOY_URL + captcha_url

        try:
            # Download captcha
            r = self.session.get(captcha_url, timeout=10)
            if r.status_code != 200:
                print("  ❌ Gagal download captcha")
                return None

            # Encode ke base64
            encoded = base64.b64encode(r.content).decode('utf-8')

            # Kirim ke OCR solver
            print("  🔍 Solving captcha via OCR...")
            ocr_r = requests.post(CAPTCHA_SOLVER_URL, json={
                'captcha': encoded,
                'current_time': time.strftime("%H:%M:%S")
            }, timeout=30)

            if ocr_r.status_code == 200:
                result = ocr_r.json()
                captcha_answer = result.get('result', '')
                print(f"  ✅ OCR Result: {captcha_answer}")
                return {
                    'answer': captcha_answer,
                    'input_name': data['input_name'],
                    'tokens': data['tokens'],
                }
            else:
                print(f"  ❌ OCR failed: HTTP {ocr_r.status_code}")
                return None
        except Exception as e:
            print(f"  ❌ OCR error: {e}")
            return None

    def submit_captcha(self, captcha_data):
        """Submit jawaban captcha ke zefoy."""
        if not captcha_data:
            return False

        data = {
            captcha_data['input_name']: captcha_data['answer'],
            'token': '',
        }

        # Tambahkan hidden tokens
        for token_name in captcha_data.get('tokens', []):
            if token_name and token_name != 'token':
                data[token_name] = ''

        r = self.session.post(ZEFOY_URL, data=data, timeout=15)

        # Cek apakah berhasil
        if 'captcha' not in r.text.lower() or 'incorrect' not in r.text.lower():
            print("  ✅ Captcha solved!")
            return True
        else:
            print("  ❌ Captcha salah!")
            return False

    def decrypt(self, data):
        """Decrypt response dari zefoy."""
        try:
            return base64.b64decode(unquote(data[::-1])).decode()
        except:
            return data

    def decrypt_timer(self, data):
        """Extract timer dari response."""
        import re as re2
        if len(re2.findall(r' \d{3}', data)) != 0:
            timer = re2.findall(r' \d{3}', data)[0]
        else:
            timer = data.split('= ')[1].split('\n')[0]
        return int(timer)

    def send_views(self, video_url, service="views"):
        """Kirim views ke video TikTok."""
        service_endpoint = SERVICES.get(service, SERVICES["views"])

        print(f"  🎯 Service: {service}")
        print(f"  📹 URL: {video_url}")
        print(f"  🔄 Mengirim... (Ctrl+C untuk stop)")
        print()

        while True:
            try:
                # Step 1: Request form
                r = self.session.post(
                    f"{ZEFOY_URL}/{service_endpoint}",
                    headers={
                        'origin': ZEFOY_URL,
                        'x-requested-with': 'XMLHttpRequest',
                    },
                    data={
                        f'{self.get_alpha_key(video_url)}': video_url,
                    },
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

                # Cari beta key
                import re as re2
                beta_match = re2.findall(r'name="([^"]*)" type="text"', decrypted)
                if not beta_match:
                    print("  ⚠️ Tidak menemukan form, retry...")
                    time.sleep(5)
                    continue

                beta_key = beta_match[0]

                # Step 2: Submit video URL
                r2 = self.session.post(
                    f"{ZEFOY_URL}/{service_endpoint}",
                    headers={
                        'origin': ZEFOY_URL,
                        'x-requested-with': 'XMLHttpRequest',
                    },
                    data={beta_key: video_url},
                    timeout=15
                )

                decrypted2 = self.decrypt(r2.text)

                if "Too many requests" in decrypted2:
                    print("  ⏳ Rate limited, tunggu 120s...")
                    time.sleep(120)
                    continue

                # Extract timer
                try:
                    timer = self.decrypt_timer(decrypted2)
                    self.sent += 1
                    print(f"  ✅ [#{self.sent}] Views terkirim! Cooldown: {timer}s")
                    time.sleep(timer)
                except:
                    self.sent += 1
                    print(f"  ✅ [#{self.sent}] Views terkirim!")
                    time.sleep(60)

            except KeyboardInterrupt:
                print("\n  ⏹️ Dihentikan")
                break
            except Exception as e:
                self.errors += 1
                print(f"  ❌ Error: {e}")
                time.sleep(10)

    def get_alpha_key(self, video_url):
        """Get alpha key dari zefoy."""
        service_endpoint = SERVICES.get("views")

        r = self.session.post(
            f"{ZEFOY_URL}/{service_endpoint}",
            headers={
                'origin': ZEFOY_URL,
                'x-requested-with': 'XMLHttpRequest',
            },
            data={'': video_url},
            timeout=15
        )

        import re as re2
        alpha_match = re2.findall(r'name="([a-z0-9]{16})"', r.text)
        return alpha_match[0] if alpha_match else None

    def run(self):
        """Main loop."""
        self.clear()
        self.banner()

        # Step 1: Get session
        if not self.get_session():
            return

        # Step 2: Solve captcha
        print()
        print("  Pilih metode captcha:")
        print("  1. Manual (input sendiri)")
        print("  2. OCR (otomatis, mungkin gagal)")
        print()

        try:
            choice = input("  Pilih (1/2, default=1): ").strip()
        except KeyboardInterrupt:
            return

        if choice == "2":
            captcha_data = self.solve_captcha_ocr()
        else:
            captcha_data = self.solve_captcha_manual()

        if not captcha_data or not self.submit_captcha(captcha_data):
            print("  ❌ Gagal solve captcha!")
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
        print("  1. Views")
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

        # Step 5: Jalankan
        self.clear()
        self.banner()
        self.send_views(video_url, service)

        # Ringkasan
        print()
        print("  ═══════════════════════════════")
        print(f"  📊 Ringkasan:")
        print(f"     ✅ Berhasil: {self.sent}")
        print(f"     ❌ Error:    {self.errors}")
        print("  ═══════════════════════════════")


if __name__ == "__main__":
    bot = ZefoyBot()
    bot.run()
