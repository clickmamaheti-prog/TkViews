#!/usr/bin/env bash
# ============================================================
# TkViews Auto-Updater v1.0
# Update repo TkViews ke versi terbaru dari GitHub
# ============================================================
# Cara pakai:
#   curl -sSL https://raw.githubusercontent.com/clickmamaheti-prog/TkViews/master/update.sh | bash
#
# ATAU dari folder repo:
#   chmod +x update.sh && ./update.sh
# ============================================================

set -e

REPO_URL="https://github.com/clickmamaheti-prog/TkViews.git"
FOLDER="TkViews"

# ── Warna ────────────────────────────────────────────────────
if command -v tput &>/dev/null; then
    CYAN=$(tput setaf 6 2>/dev/null || echo "")
    PINK=$(tput setaf 5 2>/dev/null || echo "")
    GREEN=$(tput setaf 2 2>/dev/null || echo "")
    YELLOW=$(tput setaf 3 2>/dev/null || echo "")
    RED=$(tput setaf 1 2>/dev/null || echo "")
    BOLD=$(tput bold 2>/dev/null || echo "")
    RESET=$(tput sgr0 2>/dev/null || echo "")
else
    CYAN="" PINK="" GREEN="" YELLOW="" RED="" BOLD="" RESET=""
fi

W=60

box_top()    { echo "  ${CYAN}╔$(printf '═%.0s' $(seq 1 $W))╗${RESET}"; }
box_mid()    { echo "  ${CYAN}╠$(printf '═%.0s' $(seq 1 $W))╣${RESET}"; }
box_bot()    { echo "  ${CYAN}╚$(printf '═%.0s' $(seq 1 $W))╝${RESET}"; }
box_line()   { printf "  ${CYAN}║${RESET} %-$(($W-1))s${CYAN}║${RESET}\n" "$1"; }
box_center() {
    local w=$W
    local s="$1"
    local len=${#s}
    local left=$(( (w - len) / 2 ))
    local right=$(( w - len - left ))
    printf "  ${CYAN}║${RESET}%*s%s%*s${CYAN}║${RESET}\n" "$left" "" "$s" "$right" ""
}

banner() {
    echo ""
    box_top
    box_center ""
    box_center "${BOLD}${PINK}████████╗██╗  ██╗██╗   ██╗██╗███████╗${RESET}"
    box_center "${BOLD}${PINK}╚══██╔══╝██║ ██╔╝██║   ██║██║╚════██║${RESET}"
    box_center "${BOLD}${CYAN}   ██║   █████╔╝ ██║   ██║██║███████╗${RESET}"
    box_center "${BOLD}${CYAN}   ██║   ██╔═██╗ ╚██╗ ██╔╝██║╚════██║${RESET}"
    box_center "${BOLD}${PINK}   ██║   ██║  ██╗ ╚████╔╝ ██║███████║${RESET}"
    box_center "${BOLD}${PINK}   ╚═╝   ╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝${RESET}"
    box_center ""
    box_center "${BOLD}${CYAN}T I K T O K   V I E W B O T${RESET}"
    box_center "${BOLD}${PINK}U P D A T E R${RESET}"
    box_center "${YELLOW}Auto Update — Git Pull dari GitHub${RESET}"
    box_center ""
    box_mid
    box_line "${GREEN}●${RESET} Pull latest code dari GitHub"
    box_line "${GREEN}●${RESET} Update dependencies (requests)"
    box_line "${GREEN}●${RESET} Tampilkan changelog versi terbaru"
    box_line "${GREEN}●${RESET} Jalankan bot setelah update"
    box_bot
    echo ""
}

step()  { box_line "${YELLOW}🔄${RESET} $1"; }
ok()    { box_line "${GREEN}✅${RESET} $1"; }
warn()  { box_line "${YELLOW}⚠️${RESET}  $1"; }
err()   { box_line "${RED}❌${RESET} $1"; }

# ── Cek apakah folder repo ada ──────────────────────────────
check_repo() {
    if [ ! -d "$FOLDER/.git" ]; then
        err "Folder $FOLDER tidak ditemukan atau bukan repo git"
        echo ""
        step "Clone repo baru..."
        git clone "$REPO_URL"
        cd "$FOLDER"
        ok "Repo berhasil di-clone"
    else
        cd "$FOLDER"
        ok "Repo ditemukan — akan di-update"
    fi
}

# ── Git pull ─────────────────────────────────────────────────
do_update() {
    step "Pull latest code dari GitHub..."
    
    # Simpan hash sebelum pull
    OLD_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    
    # Pull dari GitHub
    if git pull origin master 2>/dev/null || git pull origin main 2>/dev/null; then
        NEW_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
        
        if [ "$OLD_HASH" = "$NEW_HASH" ]; then
            ok "Sudah versi terbaru ($NEW_HASH)"
        else
            ok "Update berhasil! $OLD_HASH → $NEW_HASH"
            echo ""
            box_mid
            box_line "${BOLD}${CYAN}  CHANGELOG:${RESET}"
            box_mid
            
            # Tampilkan commit log
            git log --oneline "$OLD_HASH".."$NEW_HASH" 2>/dev/null | head -10 | while read line; do
                box_line "  ${DIM}$line${RESET}"
            done
            
            if [ -z "$(git log --oneline "$OLD_HASH".."$NEW_HASH" 2>/dev/null)" ]; then
                box_line "  ${DIM}(tidak ada commit baru)${RESET}"
            fi
        fi
    else
        err "Gagal pull dari GitHub — cek koneksi internet"
        exit 1
    fi
}

# ── Update dependencies ──────────────────────────────────────
update_deps() {
    step "Update Python dependencies..."
    python3 -m pip install --quiet requests 2>/dev/null && ok "requests updated" || warn "requests sudah up-to-date"
}

# ── Run bot ──────────────────────────────────────────────────
run_bot() {
    echo ""
    box_mid
    read -p "  ${CYAN}║${RESET}  ${PINK}❯${RESET} ${WHITE}Jalankan bot sekarang? (y/n) ${RESET}" -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        box_bot
        echo ""
        python3 bot_final.py
    else
        box_bot
        echo ""
        ok "Untuk jalankan nanti:"
        echo "      cd $FOLDER && python3 bot_final.py"
        echo ""
        ok "Untuk update lagi nanti:"
        echo "      cd $FOLDER && git pull origin master"
    fi
}

# ── Main ─────────────────────────────────────────────────────
banner
check_repo
echo ""
do_update
echo ""
update_deps
run_bot
