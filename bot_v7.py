#!/usr/bin/env python3
"""
TikTok Viewbot v7 - Auto Bypass Captcha
Menggunakan multi-teknik OCR untuk solve captcha otomatis:
1. Tesseract OCR (lokal)
2. OCR.space API (gratis)
3. Image preprocessing untuk akurasi tinggi

Usage: python3 bot_v7.py
"""

import requests
import re
import base64
import time
import os
import sys
import json
import subprocess
from urllib.parse import unquote
from io import BytesIO

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

# OCR.space API key (gratis, 25000 req/bulan)
OCR_SPACE_API_KEY = "K89675679888957"  # public demo key

# ============================================================

class CaptchaSolver:
    """Multi-teknik captcha solver."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })

    def get_captcha_image(self, sessid):
        """Ambil gambar captcha dari zefoy."""
        # Kunjungi halaman utama
        r = self.session.get(ZEFOY_URL, headers={'cookie': f'PHPSESSID={sessid}'}, timeout=15)
        html = r.text

        # Cari captcha image URL
        img_match = re.findall(r'<img[^>]*id="captcha-img"[^>]*src="([^"]*)"', html)
        if not img_match:
            img_match = re.findall(r'<img[^>]*src="([^"]*captch[^"]*)"', html, re.IGNORECASE)
        if not img_match:
            img_match = re.findall(r'url\([\"\']([^\"\']*captch[^\"\']*)[\"\']\)', html, re.IGNORECASE)

        if img_match:
            img_url = img_match[0]
            if not img_url.startswith('http'):
                img_url = ZEFOY_URL + '/' + img_url.lstrip('/')

            try:
                r_img = self.session.get(img_url, headers={'cookie': f'PHPSESSID={sessid}'}, timeout=10)
                if r_img.status_code == 200 and len(r_img.content) > 100:
                    return r_img.content
            except:
                pass

        # Alternatif: coba URL captcha langsung
        for captcha_path in ['/captcha.php', '/assets/captcha.php', '/captcha', '/api/captcha']:
            try:
                r_img = self.session.get(f'{ZEFOY_URL}{captcha_path}', headers={'cookie': f'PHPSESSID={sessid}'}, timeout=10)
                if r_img.status_code == 200 and len(r_img.content) > 100:
                    content_type = r_img.headers.get('content-type', '')
                    if 'image' in content_type or r_img.content[:4] in [b'\x89PNG', b'\xff\xd8', b'GIF8']:
                        return r_img.content
            except:
                pass

        return None

    def preprocess_image(self, image_data):
        """Preprocessing image untuk OCR yang lebih akurat."""
        try:
            from PIL import Image, ImageFilter, ImageEnhance

            img = Image.open(BytesIO(image_data))

            # Convert to grayscale
            img = img.convert('L')

            # Increase contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)

            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)

            # Resize (larger = better OCR)
            width, height = img.size
            img = img.resize((width * 3, height * 3), Image.LANCZOS)

            # Threshold (binary)
            threshold = 128
            img = img.point(lambda x: 255 if x > threshold else 0)

            # Save to temp
            temp_path = '/tmp/captcha_processed.png'
            img.save(temp_path)
            return temp_path
        except Exception as e:
            print(f"    ⚠️ Preprocess error: {e}")
            # Save original
            temp_path = '/tmp/captcha_original.png'
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            return temp_path

    def solve_tesseract(self, image_data):
        """Solve captcha dengan Tesseract OCR (lokal)."""
        try:
            import pytesseract

            # Preprocess
            processed_path = self.preprocess_image(image_data)

            # OCR dengan config optimal untuk captcha
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            text = pytesseract.image_to_string(processed_path, config=custom_config)

            # Bersihkan hasil
            answer = re.sub(r'[^a-zA-Z0-9]', '', text).strip().lower()

            if answer and len(answer) >= 3:
                return answer

            # Coba dengan PSM berbeda
            for psm in [7, 6, 13]:
                config = f'--oem 3 --psm {psm}'
                text = pytesseract.image_to_string(processed_path, config=config)
                answer = re.sub(r'[^a-zA-Z0-9]', '', text).strip().lower()
                if answer and len(answer) >= 3:
                    return answer

            return None
        except Exception as e:
            print(f"    ⚠️ Tesseract error: {e}")
            return None

    def solve_ocrspace(self, image_data):
        """Solve captcha dengan OCR.space API (gratis)."""
        try:
            url = f"https://api.ocr.space/parse/image"
            payload = {
                'apikey': OCR_SPACE_API_KEY,
                'isOverlayRequired': False,
                'detectOrientation': True,
                'scale': True,
                'OCREngine': 2,
            }
            files = {'file': ('captcha.png', image_data, 'image/png')}

            r = requests.post(url, data=payload, files=files, timeout=30)

            if r.status_code == 200:
                result = r.json()
                if result.get('ParsedResults'):
                    text = result['ParsedResults'][0].get('ParsedText', '')
                    answer = re.sub(r'[^a-zA-Z0-9]', '', text).strip().lower()
                    if answer and len(answer) >= 3:
                        return answer

            return None
        except Exception as e:
            print(f"    ⚠️ OCR.space error: {e}")
            return None

    def solve_2captcha(self, image_data, api_key=None):
        """Solve captcha dengan 2Captcha API (berbayar, sangat akurat)."""
        if not api_key:
            return None

        try:
            # Upload captcha
            upload_url = "http://2captcha.com/in.php"
            files = {'file': ('captcha.png', image_data, 'image/png')}
            data = {'key': api_key, 'method': 'post'}

            r = requests.post(upload_url, data=data, files=files, timeout=30)
            if r.status_code != 200:
                return None

            captcha_id = r.text.split('|')[-1] if '|' in r.text else None
            if not captcha_id:
                return None

            # Poll for result
            result_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}"
            for _ in range(30):
                time.sleep(2)
                r = requests.get(result_url, timeout=10)
                if 'CAPCHA_NOT_READY' not in r.text:
                    answer = r.text.split('|')[-1] if '|' in r.text else r.text
                    return answer.strip().lower()

            return None
        except Exception as e:
            print(f"    ⚠️ 2Captcha error: {e}")
            return None

    def solve(self, sessid, twocaptcha_key=None):
        """Solve captcha dengan multi-teknik."""
        print("    📸 Mengambil captcha image...")
        image_data = self.get_captcha_image(sessid)

        if not image_data:
            print("    ❌ Gagal mengambil captcha image")
            return None

        # Save captcha untuk debug
        with open('/tmp/zefoy_captcha.png', 'wb') as f:
            f.write(image_data)
        print(f"    📸 Captcha saved: /tmp/zefoy_captcha.png ({len(image_data)} bytes)")

        # Teknik 1: Tesseract OCR
        print("    🔍 Teknik 1: Tesseract OCR...")
        answer = self.solve_tesseract(image_data)
        if answer:
            print(f"    ✅ Tesseract: {answer}")
            return answer

        # Teknik 2: OCR.space
        print("    🔍 Teknik 2: OCR.space API...")
        answer = self.solve_ocrspace(image_data)
        if answer:
            print(f"    ✅ OCR.space: {answer}")
            return answer

        # Teknik 3: 2Captcha (jika ada key)
        if twocaptcha_key:
            print("    🔍 Teknik 3: 2Captcha...")
            answer = self.solve_2captcha(image_data, twocaptcha_key)
            if answer:
                print(f"    ✅ 2Captcha: {answer}")
                return answer

        print("    ❌ Semua teknik gagal")
        return None


class TikTokViewbot:
    """TikTok Viewbot dengan auto bypass captcha."""

    def __init__(self, twocaptcha_key=None):
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
        self.captcha_solver = CaptchaSolver()
        self.twocaptcha_key = twocaptcha_key

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def banner(self):
        print("""
 ╦  ╦╦╔═╗╦ ╦╔╗ ╔═╗╔╦╗
 ╚╗╔╝║║╣ ║║║╠╩╗║ ║ ║
  ╚╝ ╩╚═╝╚╩╝╚═╝╚═╝ ╩
  TikTok Viewbot v7 (Auto Bypass)
  ────────────────────────────────
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

    def solve_captcha(self):
        """Solve captcha otomatis."""
        print()
        print("  ═══════════════════════════════════")
        print("  🔐 AUTO SOLVING CAPTCHA...")
        print("  ═══════════════════════════════════")
        print()

        for attempt in range(5):
            print(f"  Attempt {attempt + 1}/5:")

            # Sync session dengan captcha solver
            self.captcha_solver.session = self.session
            self.captcha_solver.session.cookies.set('PHPSESSID', self.sessid, domain='zefoy.com')

            answer = self.captcha_solver.solve(self.sessid, self.twocaptcha_key)

            if answer:
                # Submit captcha
                if self.submit_captcha(answer):
                    print(f"  ✅ Captcha solved: {answer}")
                    return True
                else:
                    print(f"    ⚠️ Jawaban '{answer}' salah, coba lagi...")
            else:
                print(f"    ⚠️ Gagal solve, coba lagi...")

            time.sleep(2)

        return False

    def submit_captcha(self, answer):
        """Submit jawaban captcha."""
        try:
            # Get fresh page
            r = self.session.get(ZEFOY_URL, timeout=15)
            html = r.text

            # Cari input name
            input_match = re.findall(r'type="search"[^>]*name="([^"]*)"', html)
            if not input_match:
                input_match = re.findall(r'type="text"[^>]*name="([a-z0-9]{16,})"', html)

            if not input_match:
                return False

            captcha_input_name = input_match[0]

            # Submit
            data = {
                captcha_input_name: answer,
                'captcha_encoded': '',
            }

            r = self.session.post(ZEFOY_URL, data=data, timeout=15)

            # Cek hasil
            if 'incorrect' in r.text.lower():
                return False

            # Test jika sudah bisa akses form
            time.sleep(1)
            r2 = self.session.post(
                f'{ZEFOY_URL}/{SERVICES["views"]}',
                headers={
                    'origin': ZEFOY_URL,
                    'x-requested-with': 'XMLHttpRequest',
                },
                data={'': 'https://www.tiktok.com/@test/video/123'},
                timeout=15
            )

            alpha_match = re.findall(r'name="([a-z0-9]{16})"', r2.text)
            if alpha_match:
                return True

            return 'captcha' not in r2.text.lower()

        except Exception as e:
            print(f"    ❌ Submit error: {e}")
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
                # Get alpha key
                r = self.session.post(
                    f'{ZEFOY_URL}/{service_endpoint}',
                    headers={
                        'origin': ZEFOY_URL,
                        'x-requested-with': 'XMLHttpRequest',
                    },
                    data={'': video_url},
                    timeout=15
                )

                decrypted = self.decrypt(r.text)

                # Cek captcha
                if decrypted.strip().startswith('<') or 'captcha' in decrypted.lower():
                    print("  🔐 Captcha detected, auto solving...")
                    if not self.solve_captcha():
                        print("  ❌ Gagal solve captcha setelah 5 attempt")
                        return False
                    continue

                # Cari alpha key
                alpha_match = re.findall(r'name="([a-z0-9]{16})"', r.text)
                if not alpha_match:
                    consecutive_errors += 1
                    print(f"  ⚠️ No alpha key ({consecutive_errors})")
                    if consecutive_errors > 10:
                        print("  ❌ Terlalu banyak error")
                        return False
                    time.sleep(5)
                    continue

                alpha_key = alpha_match[0]

                # Submit video URL
                r2 = self.session.post(
                    f'{ZEFOY_URL}/{service_endpoint}',
                    headers={
                        'origin': ZEFOY_URL,
                        'x-requested-with': 'XMLHttpRequest',
                    },
                    data={alpha_key: video_url},
                    timeout=15
                )

                decrypted2 = self.decrypt(r2.text)

                if "This service is currently not working" in decrypted2:
                    print("  ❌ Service not working, retry 30s...")
                    time.sleep(30)
                    continue

                if "Server too busy" in decrypted2:
                    print("  ⏳ Server busy, retry 10s...")
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
                    print(f"  ⚠️ No beta key ({consecutive_errors})")
                    time.sleep(5)
                    continue

                beta_key = beta_match[0]

                # Send views
                time.sleep(1)
                r3 = self.session.post(
                    f'{ZEFOY_URL}/{service_endpoint}',
                    headers={
                        'origin': ZEFOY_URL,
                        'x-requested-with': 'XMLHttpRequest',
                    },
                    data={beta_key: video_url},
                    timeout=15
                )

                decrypted3 = self.decrypt(r3.text)

                if "Too many requests" in decrypted3:
                    print("  ⏳ Rate limited, retry 120s...")
                    time.sleep(120)
                    continue

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
                print("\n  ⏹️ Dihentikan")
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

        # Get session
        if not self.get_session():
            print("  ❌ Gagal memulai session!")
            return

        # Auto solve captcha
        if not self.solve_captcha():
            print("  ❌ Gagal solve captcha!")
            print("  💡 Coba solve manual di browser")
            return

        # Jalankan
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
    # 2Captcha key (opsional, untuk akurasi tinggi)
    # Dapatkan di https://2captcha.com (gratis $0.10 untuk testing)
    TWOCAPTCHA_KEY = None  # Isi dengan key Anda jika punya

    bot = TikTokViewbot(twocaptcha_key=TWOCAPTCHA_KEY)
    bot.run(VIDEO_URL, max_count=50)
