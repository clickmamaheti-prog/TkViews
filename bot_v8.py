#!/usr/bin/env python3
"""
TikTok Viewbot v8 - Playwright Captcha Bypass
Menggunakan Playwright (headless browser) untuk:
1. Render JavaScript di Zefoy.com
2. Ambil captcha image
3. Solve dengan OCR
4. Submit dan kirim views

Usage: python3 bot_v8.py
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

# ============================================================

class PlaywrightCaptchaSolver:
    """Captcha solver menggunakan Playwright untuk JS rendering."""

    def __init__(self):
        self.playwright_path = None
        self._find_playwright()

    def _find_playwright(self):
        """Cari playwright executable."""
        import shutil
        self.playwright_path = shutil.which('npx') or shutil.which('playwright')

    def get_captcha_with_playwright(self, url=ZEFOY_URL):
        """Gunakan Playwright untuk render page dan ambil captcha."""
        script = f'''
const {{ chromium }} = require('playwright');

(async () => {{
  const browser = await chromium.launch({{ headless: true }});
  const context = await browser.newContext({{
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  }});
  const page = await context.newPage();

  // Navigate to zefoy
  await page.goto('{url}', {{ waitUntil: 'networkidle', timeout: 30000 }});

  // Wait for captcha image to load
  await page.waitForSelector('#captcha-img', {{ timeout: 10000 }}).catch(() => {{}});

  // Get captcha image src
  const captchaSrc = await page.$eval('#captcha-img', img => img.src).catch(() => null);

  // Get all cookies
  const cookies = await context.cookies();
  const phpSessid = cookies.find(c => c.name === 'PHPSESSID');

  // Get page content
  const content = await page.content();

  // Try to screenshot the captcha area
  const captchaElement = await page.$('#captcha-img');
  let captchaBase64 = null;
  if (captchaElement) {{
    const buffer = await captchaElement.screenshot();
    captchaBase64 = buffer.toString('base64');
  }}

  // Get all image sources
  const images = await page.$$eval('img', imgs => imgs.map(img => ({{ src: src, id: img.id, class: img.className }})));

  console.log(JSON.stringify({{
    success: true,
    captchaSrc: captchaSrc,
    captchaBase64: captchaBase64,
    phpSessid: phpSessid ? phpSessid.value : null,
    images: images,
    contentLength: content.length
  }}));

  await browser.close();
}})().catch(err => {{
  console.log(JSON.stringify({{ success: false, error: err.message }});
  process.exit(1);
}});
'''
        try:
            result = subprocess.run(
                ['node', '-e', script],
                capture_output=True,
                timeout=60,
                cwd='/tmp'
            )

            if result.returncode == 0:
                output = result.stdout.decode('utf-8').strip()
                # Find JSON in output
                json_match = re.search(r'\{.*\}', output, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return data

            return {'success': False, 'error': result.stderr.decode('utf-8')[:500]}
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def solve_captcha(self, url=ZEFOY_URL):
        """Full flow: render page, get captcha, solve with OCR."""
        print("    🌐 Rendering page dengan Playwright...")

        result = self.get_captcha_with_playwright(url)

        if not result.get('success'):
            print(f"    ❌ Playwright error: {result.get('error')}")
            return None, None

        print(f"    ✅ Page rendered ({result.get('contentLength', 0)} bytes)")

        # Get session
        sessid = result.get('phpSessid')
        if sessid:
            print(f"    ✅ Session: {sessid[:20]}...")

        # Get captcha image
        captcha_base64 = result.get('captchaBase64')
        if not captcha_base64:
            # Try from src
            captcha_src = result.get('captchaSrc')
            if captcha_src and captcha_src.startswith('http'):
                try:
                    r = requests.get(captcha_src, timeout=10)
                    captcha_base64 = base64.b64encode(r.content).decode('utf-8')
                except:
                    pass

        if not captcha_base64:
            print("    ❌ Tidak bisa ambil captcha image")
            # Print images found
            images = result.get('images', [])
            print(f"    📸 Images found: {len(images)}")
            for img in images[:10]:
                print(f"       id={img.get('id')}, src={img.get('src', '')[:80]}")
            return None, sessid

        # Decode and save captcha
        image_data = base64.b64decode(captcha_base64)
        with open('/tmp/zefoy_captcha.png', 'wb') as f:
            f.write(image_data)
        print(f"    📸 Captcha saved: /tmp/zefoy_captcha.png ({len(image_data)} bytes)")

        # OCR
        answer = self._ocr_image(image_data)
        return answer, sessid

    def _ocr_image(self, image_data):
        """OCR dengan Tesseract."""
        try:
            import pytesseract
            from PIL import Image, ImageEnhance

            img = Image.open(BytesIO(image_data))

            # Preprocess
            img = img.convert('L')
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)

            # Resize
            width, height = img.size
            img = img.resize((width * 3, height * 3), Image.Resampling.LANCZOS)

            # Threshold
            img = img.point(lambda x: 255 if x > 128 else 0)

            # Save processed
            img.save('/tmp/captcha_processed.png')

            # OCR
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            text = pytesseract.image_to_string('/tmp/captcha_processed.png', config=custom_config)
            answer = re.sub(r'[^a-zA-Z0-9]', '', text).strip().lower()

            if answer and len(answer) >= 3:
                print(f"    ✅ OCR result: {answer}")
                return answer

            # Try different PSM
            for psm in [7, 6, 10, 13]:
                config = f'--oem 3 --psm {psm}'
                text = pytesseract.image_to_string('/tmp/captcha_processed.png', config=config)
                answer = re.sub(r'[^a-zA-Z0-9]', '', text).strip().lower()
                if answer and len(answer) >= 3:
                    print(f"    ✅ OCR result (PSM {psm}): {answer}")
                    return answer

            print(f"    ❌ OCR gagal: '{text[:50]}'")
            return None
        except Exception as e:
            print(f"    ❌ OCR error: {e}")
            return None


class TikTokViewbot:
    """TikTok Viewbot dengan Playwright captcha bypass."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
        self.sessid = None
        self.sent = 0
        self.errors = 0
        self.running = True
        self.captcha_solver = PlaywrightCaptchaSolver()

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def banner(self):
        print("""
 ╦  ╦╦╔═╗╦ ╦╔╗ ╔═╗╔╦╗
 ╚╗╔╝║║╣ ║║║╠╩╗║ ║ ║
  ╚╝ ╩╚═╝╚╩╝╚═╝╚═╝ ╩
  TikTok Viewbot v8 (Playwright Bypass)
  ─────────────────────────────────────
        """)

    def solve_captcha(self):
        """Solve captcha dengan Playwright + OCR."""
        print()
        print("  ═══════════════════════════════════")
        print("  🔐 AUTO SOLVING CAPTCHA (Playwright)")
        print("  ═══════════════════════════════════")
        print()

        for attempt in range(5):
            print(f"  Attempt {attempt + 1}/5:")

            answer, sessid = self.captcha_solver.solve_captcha()

            if answer:
                # Update session
                if sessid:
                    self.sessid = sessid
                    self.session.cookies.set('PHPSESSID', sessid, domain='zefoy.com')

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
            r = self.session.get(ZEFOY_URL, timeout=15)
            html = r.text

            input_match = re.findall(r'type="search"[^>]*name="([^"]*)"', html)
            if not input_match:
                input_match = re.findall(r'type="text"[^>]*name="([a-z0-9]{16,})"', html)
            if not input_match:
                return False

            data = {
                input_match[0]: answer,
                'captcha_encoded': '',
            }

            r = self.session.post(ZEFOY_URL, data=data, timeout=15)

            if 'incorrect' in r.text.lower():
                return False

            time.sleep(1)
            r2 = self.session.post(
                f'{ZEFOY_URL}/{SERVICES["views"]}',
                headers={'origin': ZEFOY_URL, 'x-requested-with': 'XMLHttpRequest'},
                data={'': 'https://www.tiktok.com/@test/video/123'},
                timeout=15
            )

            alpha_match = re.findall(r'name="([a-z0-9]{16})"', r2.text)
            return bool(alpha_match)

        except Exception as e:
            print(f"    ❌ Submit error: {e}")
            return False

    def decrypt(self, data):
        try: return base64.b64decode(unquote(data[::-1])).decode()
        except: return data

    def decrypt_timer(self, data):
        try:
            if len(re.findall(r' \d{3}', data)) != 0:
                timer = re.findall(r' \d{3}', data)[0].strip()
            else:
                parts = data.split('= ')
                timer = parts[1].split('\n')[0].strip() if len(parts) > 1 else '60'
            return int(timer)
        except: return 60

    def send_views(self, video_url, max_count=None):
        """Kirim views."""
        service_endpoint = SERVICES["views"]
        print(f"  🎯 Service: VIEWS")
        print(f"  📹 URL: {video_url}")
        print(f"  🔄 Memulai... (Ctrl+C untuk stop)")
        print()

        count = 0
        while self.running:
            if max_count and count >= max_count:
                print(f"  ✅ Target {max_count} views tercapai!")
                break
            try:
                r = self.session.post(
                    f'{ZEFOY_URL}/{service_endpoint}',
                    headers={'origin': ZEFOY_URL, 'x-requested-with': 'XMLHttpRequest'},
                    data={'': video_url}, timeout=15
                )
                decrypted = self.decrypt(r.text)

                if decrypted.strip().startswith('<') or 'captcha' in decrypted.lower():
                    print("  🔐 Captcha detected, auto solving...")
                    if not self.solve_captcha():
                        return False
                    continue

                alpha_match = re.findall(r'name="([a-z0-9]{16})"', r.text)
                if not alpha_match:
                    self.errors += 1
                    print(f"  ⚠️ No alpha key ({self.errors})")
                    if self.errors > 10: return False
                    time.sleep(5)
                    continue

                r2 = self.session.post(
                    f'{ZEFOY_URL}/{service_endpoint}',
                    headers={'origin': ZEFOY_URL, 'x-requested-with': 'XMLHttpRequest'},
                    data={alpha_match[0]: video_url}, timeout=15
                )
                decrypted2 = self.decrypt(r2.text)

                if "This service is currently not working" in decrypted2:
                    time.sleep(30); continue
                if "Server too busy" in decrypted2:
                    time.sleep(10); continue
                if "function updatetimer()" in decrypted2:
                    time.sleep(self.decrypt_timer(decrypted2)); continue

                beta_match = re.findall(r'name="([a-z0-9]{16})" type="text"', decrypted2)
                if not beta_match: beta_match = re.findall(r'name="([a-z0-9]{16})"', decrypted2)
                if not beta_match:
                    self.errors += 1; time.sleep(5); continue

                time.sleep(1)
                r3 = self.session.post(
                    f'{ZEFOY_URL}/{service_endpoint}',
                    headers={'origin': ZEFOY_URL, 'x-requested-with': 'XMLHttpRequest'},
                    data={beta_match[0]: video_url}, timeout=15
                )
                decrypted3 = self.decrypt(r3.text)

                if "Too many requests" in decrypted3:
                    time.sleep(120); continue

                try: timer = self.decrypt_timer(decrypted3)
                except: timer = 60

                self.sent += 1; count += 1; self.errors = 0
                print(f"  ✅ [#{self.sent}] Views terkirim! Cooldown: {timer}s")
                time.sleep(timer)

            except KeyboardInterrupt:
                print("\n  ⏹️ Dihentikan"); self.running = False; break
            except Exception as e:
                self.errors += 1; print(f"  ❌ Error: {e}"); time.sleep(10)
        return True

    def run(self, video_url, max_count=None):
        self.clear(); self.banner()
        print(f"  📹 Video: {video_url}\n")

        # Get initial session
        print("  🔍 Getting session...")
        r = self.session.get(ZEFOY_URL, timeout=15)
        self.sessid = self.session.cookies.get('PHPSESSID')
        print(f"  ✅ Session: {self.sessid}\n")

        # Auto solve captcha
        if not self.solve_captcha():
            print("  ❌ Gagal solve captcha!"); return

        # Send views
        self.clear(); self.banner()
        self.send_views(video_url, max_count)

        print(f"\n  ═══════════════════════════════")
        print(f"  📊 RINGKASAN:")
        print(f"     ✅ Views terkirim: {self.sent}")
        print(f"     ❌ Error: {self.errors}")
        print(f"  ═══════════════════════════════")


if __name__ == "__main__":
    VIDEO_URL = "https://www.tiktok.com/@tizar110/video/7586933665398131988"
    bot = TikTokViewbot()
    bot.run(VIDEO_URL, max_count=50)
