#!/usr/bin/env python3
"""
TikTok Viewbot v9 - Full Auto Bypass
Playwright + OCR + Auto Submit

Usage: python3 bot_v9.py "https://www.tiktok.com/@user/video/123"
"""

import subprocess
import json
import base64
import re
import time
import os
import sys
import requests
from urllib.parse import unquote
from io import BytesIO

# ============================================================
# KONFIGURASI
# ============================================================

ZEFOY_URL = "https://zefoy.com"
SERVICES = {"views": "c2VuZC9mb2xsb3dlcnNfdGlrdG9V"}
MAX_CAPTCHA_ATTEMPTS = 5
MAX_VIEWS = 50

# ============================================================

def run_playwright(script, *args):
    """Run Playwright script and return JSON result."""
    result = subprocess.run(
        ['node', script] + list(args),
        capture_output=True, timeout=60, cwd='/tmp'
    )
    output = result.stdout.decode('utf-8').strip()
    match = re.search(r'\{.*\}', output, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {'success': False, 'error': output[:500]}

def solve_captcha_ocr(image_path):
    """Solve captcha dengan Tesseract OCR."""
    try:
        import pytesseract
        from PIL import Image, ImageEnhance

        img = Image.open(image_path)
        img = img.convert('L')
        img = ImageEnhance.Contrast(img).enhance(2.0)
        w, h = img.size
        img = img.resize((w*3, h*3), Image.Resampling.LANCZOS)
        img = img.point(lambda x: 255 if x > 128 else 0)

        for psm in [8, 7, 6, 10]:
            config = f'--oem 3 --psm {psm}'
            text = pytesseract.image_to_string(img, config=config)
            answer = re.sub(r'[^a-zA-Z0-9]', '', text).strip().lower()
            if answer and len(answer) >= 3:
                return answer
        return None
    except Exception as e:
        print(f'  OCR error: {e}')
        return None

def submit_captcha_and_send_views(sessid, input_name, captcha_answer, video_url):
    """Submit captcha dan kirim views via requests."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    session.cookies.set('PHPSESSID', sessid, domain='zefoy.com')

    # Submit captcha
    print(f'  Submitting captcha: {captcha_answer}')
    r = session.post(ZEFOY_URL, data={
        input_name: captcha_answer,
        'captcha_encoded': '',
    }, timeout=15)

    # Check if captcha correct
    if 'incorrect' in r.text.lower():
        return False, 'Captcha salah'

    # Wait for page to load
    time.sleep(2)

    # Try to get alpha key
    service = SERVICES['views']
    r2 = session.post(
        f'{ZEFOY_URL}/{service}',
        headers={'origin': ZEFOY_URL, 'x-requested-with': 'XMLHttpRequest'},
        data={'': video_url},
        timeout=15
    )

    try:
        decrypted = base64.b64decode(unquote(r2.text[::-1])).decode()
    except:
        decrypted = r2.text

    alpha_match = re.findall(r'name="([a-z0-9]{16})"', r2.text)
    if not alpha_match:
        return False, f'Gagal get alpha key. Response: {decrypted[:200]}'

    alpha_key = alpha_match[0]
    print(f'  Alpha key: {alpha_key}')

    # Send views loop
    sent = 0
    errors = 0

    while sent < MAX_VIEWS:
        try:
            # Submit video URL
            r3 = session.post(
                f'{ZEFOY_URL}/{service}',
                headers={'origin': ZEFOY_URL, 'x-requested-with': 'XMLHttpRequest'},
                data={alpha_key: video_url},
                timeout=15
            )

            try:
                decrypted3 = base64.b64decode(unquote(r3.text[::-1])).decode()
            except:
                decrypted3 = r3.text

            if 'This service is currently not working' in decrypted3:
                print('  Service not working, retry 30s...')
                time.sleep(30)
                continue

            if 'Server too busy' in decrypted3:
                print('  Server busy, retry 10s...')
                time.sleep(10)
                continue

            if 'function updatetimer()' in decrypted3:
                try:
                    timer = int(re.findall(r' \d{3}', decrypted3)[0].strip())
                except:
                    timer = 60
                print(f'  Timer: {timer}s')
                time.sleep(timer)
                continue

            # Get beta key
            beta_match = re.findall(r'name="([a-z0-9]{16})" type="text"', decrypted3)
            if not beta_match:
                beta_match = re.findall(r'name="([a-z0-9]{16})"', decrypted3)
            if not beta_match:
                errors += 1
                print(f'  No beta key ({errors})')
                if errors > 5:
                    return sent, errors
                time.sleep(5)
                continue

            beta_key = beta_match[0]

            # Send views
            time.sleep(1)
            r4 = session.post(
                f'{ZEFOY_URL}/{service}',
                headers={'origin': ZEFOY_URL, 'x-requested-with': 'XMLHttpRequest'},
                data={beta_key: video_url},
                timeout=15
            )

            try:
                decrypted4 = base64.b64decode(unquote(r4.text[::-1])).decode()
            except:
                decrypted4 = r4.text

            if 'Too many requests' in decrypted4:
                print('  Rate limited, retry 120s...')
                time.sleep(120)
                continue

            try:
                timer = int(re.findall(r' \d{3}', decrypted4)[0].strip())
            except:
                timer = 60

            sent += 1
            errors = 0
            print(f'  ✅ [#{sent}] Views terkirim! Cooldown: {timer}s')
            time.sleep(timer)

        except KeyboardInterrupt:
            break
        except Exception as e:
            errors += 1
            print(f'  Error: {e}')
            time.sleep(10)

    return sent, errors

def main():
    video_url = sys.argv[1] if len(sys.argv) > 1 else 'https://www.tiktok.com/@tizar110/video/7586933665398131988'

    print('=' * 55)
    print('TikTok Viewbot v9 - Full Auto Bypass')
    print('=' * 55)
    print(f'Video: {video_url}')
    print()

    # Step 1: Get captcha via Playwright
    for attempt in range(MAX_CAPTCHA_ATTEMPTS):
        print(f'Attempt {attempt + 1}/{MAX_CAPTCHA_ATTEMPTS}:')

        print('  Getting captcha via Playwright...')
        result = run_playwright('/tmp/zefoy_get_captcha.js', video_url)

        if not result.get('success'):
            print(f'  Playwright error: {result.get("error")}')
            time.sleep(3)
            continue

        input_name = result.get('inputName')
        sessid = result.get('phpSessid')
        screenshot_path = result.get('screenshotPath', '/tmp/zefoy_captcha_new.png')

        print(f'  Input: {input_name}, Session: {sessid[:20] if sessid else "none"}...')

        # Step 2: OCR
        print('  Solving captcha with OCR...')
        captcha_answer = solve_captcha_ocr(screenshot_path)

        if not captcha_answer:
            print('  OCR failed, trying manual input...')
            try:
                captcha_answer = input('  Enter captcha: ').strip().lower()
            except (KeyboardInterrupt, EOFError):
                return

        print(f'  Captcha answer: {captcha_answer}')

        # Step 3: Submit captcha and send views
        print('  Submitting captcha and sending views...')
        sent, errors = submit_captcha_and_send_views(sessid, input_name, captcha_answer, video_url)

        if sent > 0:
            print()
            print('=' * 55)
            print(f'RESULT: {sent} views sent, {errors} errors')
            print('=' * 55)
            return

        print(f'  Failed, retrying...')
        time.sleep(3)

    print('Failed after all attempts')

if __name__ == '__main__':
    main()
