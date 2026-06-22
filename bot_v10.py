#!/usr/bin/env python3
"""
TikTok Viewbot v10 - Hybrid (Browser + Auto Views)
1. Buka browser untuk solve captcha
2. Bot kirim views otomatis setelah captcha solved

Usage: python3 bot_v10.py "https://www.tiktok.com/@user/video/123"
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

# ============================================================
# KONFIGURASI
# ============================================================

ZEFOY_URL = "https://zefoy.com"
SERVICES = {"views": "c2VuZC9mb2xsb3dlcnNfdGlrdG9V"}
MAX_VIEWS = 50

# ============================================================

def get_captcha_and_session():
    """Gunakan Playwright untuk ambil captcha + session."""
    script = '''
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  await page.goto('https://zefoy.com/', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(3000);

  // Wait for captcha
  await page.waitForFunction(() => {
    const img = document.querySelector('#captcha-img');
    return img && img.src && img.src.length > 50 && img.complete && img.naturalWidth > 0;
  }, { timeout: 10000 }).catch(() => {});

  // Screenshot captcha
  const captchaEl = await page.$('#captcha-img');
  let captchaBase64 = null;
  if (captchaEl) {
    const buf = await captchaEl.screenshot();
    captchaBase64 = buf.toString('base64');
    fs.writeFileSync('/tmp/captcha_user.png', buf);
  }

  // Get session
  const cookies = await context.cookies();
  const phpSessid = cookies.find(c => c.name === 'PHPSESSID');

  // Get input name
  const inputName = await page.$eval('#captchatoken', el => el.name).catch(() => null);

  console.log(JSON.stringify({
    success: true,
    captchaBase64: captchaBase64,
    phpSessid: phpSessid ? phpSessid.value : null,
    inputName: inputName
  }));

  // Keep browser open for user to solve captcha
  // Wait for captcha to be solved (check for form change)
  await page.waitForFunction(() => {
    // Check if we're past the captcha (video form visible)
    const videoForm = document.querySelector('input[name*="video"], input[placeholder*="video"], input[placeholder*="URL"]');
    const captchaStillThere = document.querySelector('#captcha-img');
    return videoForm || !captchaStillThere;
  }, { timeout: 120000 }).catch(() => {});

  // Get updated cookies after captcha solved
  const newCookies = await context.cookies();
  const newSessid = newCookies.find(c => c.name === 'PHPSESSID');

  console.log(JSON.stringify({
    captchaSolved: true,
    phpSessid: newSessid ? newSessid.value : null
  }));

  await browser.close();
})().catch(err => {
  console.log(JSON.stringify({ success: false, error: err.message }));
  process.exit(1);
});
'''
    result = subprocess.run(['node', '-e', script], capture_output=True, timeout=150, cwd='/tmp')
    output = result.stdout.decode('utf-8').strip()

    # Parse JSON outputs
    lines = [l for l in output.split('\n') if l.strip().startswith('{')]
    if lines:
        return json.loads(lines[0])
    return {'success': False, 'error': output[:500]}

def send_views_requests(sessid, video_url):
    """Kirim views via requests setelah captcha solved."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    session.cookies.set('PHPSESSID', sessid, domain='zefoy.com')

    sent = 0
    errors = 0

    for i in range(MAX_VIEWS):
        try:
            # Get alpha key
            r = session.post(
                f'{ZEFOY_URL}/{SERVICES["views"]}',
                headers={'origin': ZEFOY_URL, 'x-requested-with': 'XMLHttpRequest'},
                data={'': video_url},
                timeout=15
            )

            try:
                decrypted = base64.b64decode(unquote(r.text[::-1])).decode()
            except:
                decrypted = r.text

            if decrypted.strip().startswith('<') or 'captcha' in decrypted.lower():
                print(f'  ❌ Captcha expired, perlu solve ulang')
                return sent, errors

            alpha_match = re.findall(r'name="([a-z0-9]{16})"', r.text)
            if not alpha_match:
                errors += 1
                print(f'  ⚠️ No alpha key ({errors})')
                if errors > 5:
                    return sent, errors
                time.sleep(5)
                continue

            alpha_key = alpha_match[0]

            # Submit video
            r2 = session.post(
                f'{ZEFOY_URL}/{SERVICES["views"]}',
                headers={'origin': ZEFOY_URL, 'x-requested-with': 'XMLHttpRequest'},
                data={alpha_key: video_url},
                timeout=15
            )

            try:
                decrypted2 = base64.b64decode(unquote(r2.text[::-1])).decode()
            except:
                decrypted2 = r2.text

            if 'not working' in decrypted2.lower():
                print('  Service down, retry 30s...')
                time.sleep(30)
                continue
            if 'too busy' in decrypted2.lower():
                print('  Busy, retry 10s...')
                time.sleep(10)
                continue
            if 'updatetimer' in decrypted2.lower():
                try:
                    timer = int(re.findall(r' \d{3}', decrypted2)[0].strip())
                except:
                    timer = 60
                print(f'  Timer: {timer}s')
                time.sleep(timer)
                continue

            # Get beta key
            beta_match = re.findall(r'name="([a-z0-9]{16})" type="text"', decrypted2)
            if not beta_match:
                beta_match = re.findall(r'name="([a-z0-9]{16})"', decrypted2)
            if not beta_match:
                errors += 1
                print(f'  ⚠️ No beta key ({errors})')
                time.sleep(5)
                continue

            # Send views
            time.sleep(1)
            r3 = session.post(
                f'{ZEFOY_URL}/{SERVICES["views"]}',
                headers={'origin': ZEFOY_URL, 'x-requested-with': 'XMLHttpRequest'},
                data={beta_match[0]: video_url},
                timeout=15
            )

            try:
                decrypted3 = base64.b64decode(unquote(r3.text[::-1])).decode()
            except:
                decrypted3 = r3.text

            if 'Too many requests' in decrypted3:
                print('  Rate limited, 120s...')
                time.sleep(120)
                continue

            try:
                timer = int(re.findall(r' \d{3}', decrypted3)[0].strip())
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
            print(f'  ❌ Error: {e}')
            time.sleep(10)

    return sent, errors

def main():
    video_url = sys.argv[1] if len(sys.argv) > 1 else 'https://www.tiktok.com/@tizar110/video/7586933665398131988'

    print('=' * 55)
    print('TikTok Viewbot v10 - Hybrid Bypass')
    print('=' * 55)
    print(f'Video: {video_url}')
    print()

    # Step 1: Get captcha via Playwright
    print('Step 1: Membuka browser untuk captcha...')
    result = get_captcha_and_session()

    if not result.get('success'):
        print(f'Error: {result.get("error")}')
        return

    sessid = result.get('phpSessid')
    print(f'  Session: {sessid[:20]}...' if sessid else '  No session')

    # Show captcha
    if result.get('captchaBase64'):
        img_data = base64.b64decode(result['captchaBase64'])
        with open('/tmp/captcha_show.png', 'wb') as f:
            f.write(img_data)
        print(f'  Captcha saved: /tmp/captcha_show.png')

    print()
    print('  ═══════════════════════════════════')
    print('  🔐 SOLVE CAPTCHA DI BROWSER')
    print('  ═══════════════════════════════════')
    print()
    print('  Browser akan terbuka.')
    print('  Solve captcha di browser.')
    print('  Bot akan otomatis lanjut setelah captcha solved.')
    print()

    # Step 2: Send views
    print('Step 2: Mengirim views...')
    sent, errors = send_views_requests(sessid, video_url)

    print()
    print('=' * 55)
    print(f'📊 RESULT: {sent} views sent, {errors} errors')
    print('=' * 55)

if __name__ == '__main__':
    main()
