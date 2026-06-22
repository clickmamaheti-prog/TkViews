<div align="center">

```
  ████████╗██╗  ██╗██╗   ██╗██╗███████╗██╗    ██╗███████╗
  ╚══██╔══╝██║ ██╔╝██║   ██║██║██╔════╝██║    ██║██╔════╝
     ██║   █████╔╝ ██║   ██║██║███████╗██║ █╗ ██║███████╗
     ██║   ██╔═██╗ ╚██╗ ██╔╝██║╚════██║██║███╗██║╚════██║
     ██║   ██║  ██╗ ╚████╔╝ ██║███████║╚███╔███╔╝███████║
     ╚═╝   ╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚══════╝
         🎯 TikTok Viewbot — Auto Proxy · Multi-Thread
```

### 🎯 TikTok Viewbot — Auto Proxy · Multi-Thread · Zero Signature

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge&logo=open-source-initiative&logoColor=white)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20Mac-inactive?style=for-the-badge&logo=linux&logoColor=white)]()

</div>

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|:------|:----------|
| 🔄 **Auto-Proxy** | Otomatis fetch & validasi proxy dari GitHub setiap dijalankan |
| 🧵 **Multi-Thread** | Hingga 100 thread paralel untuk pengiriman views |
| 🛡️ **Proxy Fallback** | Otomatis retry tanpa proxy jika proxy gagal |
| 📱 **Updated UA** | User-Agent TikTok versi terbaru (2023.10) |
| 🎯 **Multi-Endpoint** | 4 endpoint TikTok API dengan rotasi otomatis |
| 📊 **Real-time Stats** | Monitor RPS (Request Per Second) dan RPM secara live |
| 🔒 **Zero Signature** | Tidak butuh Gorgon/X-Bogus — langsung jalan |

---

## 📸 Preview

```
╦  ╦╦╔═╗╦ ╦╔╗ ╔═╗╔╦╗
╚╗╔╝║║╣ ║║║╠╩╗║ ║ ║
 ╚╝ ╩╚═╝╚╩╝╚═╝╚═╝ ╩
  TikTok Viewbot v2.1
  Fixed — Updated UA + Headers

  🎯 Target video ID: 7586933665398131988
  🚀 Memulai proses...

  📋 90 valid devices loaded
  📋 128 proxy siap digunakan!

  ✅ View OK — 20260623064024AE404DE9CAFD0722FFE6 | total: 1
  ✅ View OK — 202606230640259AB82B27ED4F2022B6A3 | total: 2
  ✅ View OK — 20260623064027365DB53079417B0C8A89 | total: 3
```

---

## 🚀 Quick Start

### ⚡ Opsi 1 — Auto-Installer (Rekomendasi)

```bash
curl -sSL https://raw.githubusercontent.com/clickmamaheti-prog/TkViews/master/install.sh | bash
```

> 📌 **Satu klik, langsung jalan!** Script otomatis:
> - 🔍 Deteksi OS (Debian/Ubuntu, CentOS, Alpine, Mac)
> - 📦 Install git, python3, pip (jika belum)
> - 📥 Clone/update repo dari GitHub
> - 📦 Install dependency (`requests`)
> - 🚀 Jalankan bot

### ⚡ Opsi 2 — Satu Perintah Manual

```bash
git clone https://github.com/clickmamaheti-prog/TkViews.git && cd TkViews && python3 -m pip install requests && python3 bot_final.py
```

### 📋 Apa yang Dilakukan Perintah Di Atas:

| # | Perintah | Fungsi |
|:--|:---------|:-------|
| 1 | `git clone ...` | Download repo TkViews |
| 2 | `cd TkViews` | Masuk ke folder |
| 3 | `python3 -m pip install requests` | Install dependency |
| 4 | `python3 bot_final.py` | Jalankan bot |

> 💡 **Tidak punya pip?** Coba salah satu:
> ```bash
> # Debian/Ubuntu
> sudo apt update && sudo apt install -y python3-pip
> 
> # ATAU pakai ensurepip
> python3 -m ensurepip --upgrade
> ```

### 🎯 Input Link TikTok

```
  ❯ Video link: https://www.tiktok.com/@tizar110/video/7586933665398131988
```

### ✅ Views Terkirim!

```
  ✔ View sent  20260623064024AE404DE9CAFD0722FFE6  │  total:1
  ✔ View sent  202606230640259AB82B27ED4F2022B6A3  │  total:2
  ✔ View sent  20260623064027365DB53079417B0C8A89  │  total:3
```

### 🔄 Jalankan Ulang

```bash
tkbot
```

---

## 🎮 Perintah `tkbot` — Interactive CLI

Setelah install, ketik `tkbot` di terminal mana saja untuk membuka menu interaktif:

```bash
tkbot
```

### Menu Interaktif

```
╔════════════════════════════════════════════════════════════╗
║  TKBOT INTERACTIVE                                         ║
╠════════════════════════════════════════════════════════════╣
║  1 ▶ Run Bot        — Kirim views                          ║
║  2 🔄 Update         — Pull versi terbaru                  ║
║  3 📊 Status          — Info & statistik                    ║
║  4 ⚙️  Settings        — Edit config.json                   ║
║  5 ✘  Exit            — Keluar                              ║
╚════════════════════════════════════════════════════════════╝
```

### Shortcut Perintah

| Perintah | Shortcut | Deskripsi |
|:---------|:---------|:----------|
| `tkbot` | — | Interactive menu |
| `tkbot run` | `tkbot r` | Langsung jalankan bot |
| `tkbot update` | `tkbot u` | Update ke versi terbaru |
| `tkbot status` | `tkbot s` | Lihat status & info |
| `tkbot help` | `tkbot h` | Tampilkan bantuan |

### Contoh Penggunaan

```bash
# Install (sekali saja)
curl -sSL https://raw.githubusercontent.com/clickmamaheti-prog/TkViews/master/install.sh | bash

# Setiap hari — cukup ketik:
tkbot

# Atau langsung run:
tkbot run

# Update ke versi terbaru:
tkbot update

# Cek status:
tkbot status
```

### ⚙️ (Opsional) Aktifkan/Nonaktifkan Proxy

```bash
nano config.json
# Ubah "use-proxy": true  (atau false untuk tanpa proxy)
```

---

## 🔄 Update ke Versi Terbaru

> **Punya repo lama?** Langsung update satu perintah — tampilan baru, fiture baru, semua otomatis!

### ⚡ Opsi 1 — Auto-Updater (Rekomendasi)

```bash
curl -sSL https://raw.githubusercontent.com/clickmamaheti-prog/TkViews/master/update.sh | bash
```

> 📌 Script otomatis:
> - 🔍 Deteksi repo lama
> - 📥 Git pull dari GitHub (kode terbaru)
> - 📦 Update dependencies
> - 📋 Tampilkan changelog
> - 🚀 Jalankan bot setelah update

### ⚡ Opsi 2 — Satu Perintah Manual

```bash
cd TkViews && git pull origin master && python3 bot_final.py
```

### ⚡ Opsi 3 — Hapus & Clone Ulang (Clean Install)

```bash
rm -rf TkViews && git clone https://github.com/clickmamaheti-prog/TkViews.git && cd TkViews && python3 bot_final.py
```

---

## 📂 Struktur File

```
TkViews/
├── 📄 tkbot.py              ← 🎮 Interactive CLI (NEW)
├── 📄 bot_final.py          ← ✅ Bot utama (v2.1 — Working)
├── 📄 bot.py                ← Bot original (dengan Gorgon)
├── 📄 bot_auto_proxy.py     ← Bot auto-fetch proxy
├── 📄 proxy_updater.py       ← Update proxy berkala
├── 📄 install.sh             ← 🚀 Auto-installer
├── 📄 update.sh             ← 🔄 Auto-updater
├── 📄 devices.txt            ← 90 device IDs
├── 📄 proxies.txt            ← 128 active proxies
├── 📄 config.json            ← Konfigurasi proxy
├── 📄 LICENSE                ← MIT License
├── 📄 README.md              ← File ini
└── 📁 to update/             ← File original (viewbot.py, mobile, golang)
```

---

## ⚙️ Konfigurasi

Edit `config.json` untuk mengatur proxy:

```json
{
  "proxy": {
    "use-proxy": true,
    "proxy-type": "http",
    "auth": false,
    "credential": ""
  }
}
```

| Parameter | Deskripsi | Default |
|:----------|:----------|:--------|
| `use-proxy` | Aktifkan/nonaktifkan proxy | `true` |
| `proxy-type` | Tipe proxy (`http` / `socks5`) | `http` |
| `auth` | Gunakan autentikasi proxy | `false` |
| `credential` | Username:Password proxy | `""` |

---

## 🔧 Troubleshooting

| Masalah | Solusi |
|:--------|:-------|
| ❌ `ModuleNotFoundError: requests` | `pip3 install requests` |
| ❌ `Connection timed out` | Proxy mati — bot otomatis retry tanpa proxy |
| ❌ `Invalid link` | Pastikan link TikTok valid atau gunakan video ID langsung |
| ⚠️ Banyak fails | Proxy banyak mati — jalankan ulang untuk fetch proxy baru |

---

## 📊 Cara Kerja

```
┌─────────────────────────────────────────────────┐
│                  TkViews v2.1                    │
├─────────────────────────────────────────────────┤
│                                                  │
│  1️⃣  Input URL TikTok                            │
│         ↓                                        │
│  2️⃣  Extract Video ID (18-19 digit)              │
│         ↓                                        │
│  3️⃣  Fetch & Validasi Proxy dari GitHub          │
│         ↓                                        │
│  4️⃣  Load Device IDs (90 devices)                │
│         ↓                                        │
│  5️⃣  Spawn Multi-Thread (max 100)                │
│         ↓                                        │
│  6️⃣  Kirim Request ke TikTok API                 │
│      ├─ Dengan proxy → OK ✅                     │
│      └─ Proxy gagal → Retry tanpa proxy ✅       │
│         ↓                                        │
│  7️⃣  Monitor RPS/RPM Real-time                   │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## ⚠️ Disclaimer

> **Gunakan dengan bijak.** Spam request dapat menyebabkan:
> - Device ID diblokir TikTok
> - IP diblokir TikTok
> - Akun TikTok dibanned
>
> **Author tidak bertanggung jawab atas penyalahgunaan ini.**

---

## 📜 License

MIT License — Lihat [LICENSE](LICENSE) untuk detail.

---

<div align="center">

**Dibuat dengan ❤️ oleh [clickmamaheti-prog](https://github.com/clickmamaheti-prog)**

[![GitHub followers](https://img.shields.io/github/followers/clickmamaheti-prog?style=social)](https://github.com/clickmamaheti-prog)

</div>
