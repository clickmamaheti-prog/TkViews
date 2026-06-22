#!/bin/bash
# Cron script untuk auto-update proxy dari VPSLab
# Jalankan setiap 6 jam untuk proxy segar

cd /root/TkViews
python3 proxy_updater.py >> .proxy_update.log 2>&1
