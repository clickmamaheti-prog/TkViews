#!/usr/bin/env bash
# ============================================================
# TkViews Auto-Installer v1.0
# Satu perintah — langsung jalan!
# ============================================================
# Cara pakai:
#   curl -sSL https://raw.githubusercontent.com/clickmamaheti-prog/TkViews/master/install.sh | bash
#
# ATAU dari folder repo:
#   chmod +x install.sh && ./install.sh
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

banner() {
    echo ""
    echo "${CYAN}${BOLD}  ████████╗██╗  ██╗██╗   ██╗██╗███████╗${RESET}"
    echo "${CYAN}${BOLD}  ╚══██╔══╝██║ ██╔╝██║   ██║██║██╔════╝${RESET}"
    echo "${PINK}${BOLD}     ██║   █████╔╝ ██║   ██║██║███████╗${RESET}"
    echo "${PINK}${BOLD}     ██║   ██╔═██╗ ╚██╗ ██╔╝██║╚════██║${RESET}"
    echo "${CYAN}${BOLD}     ██║   ██║  ██╗ ╚████╔╝ ██║███████║${RESET}"
    echo "${CYAN}${BOLD}     ╚═╝   ╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝${RESET}"
    echo ""
    echo "${BOLD}         🎯 TikTok Viewbot Installer v1.0${RESET}"
    echo "${YELLOW}         Auto Install — Satu Klik Langsung Jalan${RESET}"
    echo ""
}

step() {
    echo "  ${CYAN}➤${RESET} $1"
}

ok() {
    echo "  ${GREEN}✅ $1${RESET}"
}

warn() {
    echo "  ${YELLOW}⚠️  $1${RESET}"
}

err() {
    echo "  ${RED}❌ $1${RESET}"
}

detect_os() {
    if [ -f /etc/debian_version ]; then
        OS="debian"
    elif [ -f /etc/redhat-release ]; then
        OS="redhat"
    elif [ -f /etc/alpine-release ]; then
        OS="alpine"
    elif [[ "$(uname)" == "Darwin" ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
    step "OS terdeteksi: ${BOLD}$OS${RESET}"
}

install_git() {
    step "Mengecek git..."
    if command -v git &>/dev/null; then
        ok "Git sudah terinstall ($(git --version))"
        return 0
    fi
    warn "Git tidak ditemukan — menginstall..."
    case $OS in
        debian)
            sudo apt update -qq && sudo apt install -y -qq git
            ;;
        redhat)
            sudo yum install -y git 2>/dev/null || sudo dnf install -y git
            ;;
        alpine)
            sudo apk add git
            ;;
        macos)
            if command -v brew &>/dev/null; then
                brew install git
            else
                xcode-select --install
            fi
            ;;
        *)
            err "Tidak bisa install git otomatis. Install manual: https://git-scm.com"
            exit 1
            ;;
    esac
    ok "Git terinstall"
}

install_python() {
    step "Mengecek Python3..."
    if command -v python3 &>/dev/null; then
        PY_VER=$(python3 --version 2>&1)
        ok "Python sudah terinstall ($PY_VER)"
        return 0
    fi
    warn "Python3 tidak ditemukan — menginstall..."
    case $OS in
        debian)
            sudo apt update -qq && sudo apt install -y -qq python3
            ;;
        redhat)
            sudo yum install -y python3 2>/dev/null || sudo dnf install -y python3
            ;;
        alpine)
            sudo apk add python3
            ;;
        macos)
            brew install python3
            ;;
        *)
            err "Tidak bisa install Python3 otomatis."
            exit 1
            ;;
    esac
    ok "Python3 terinstall ($(python3 --version 2>&1))"
}

install_pip() {
    step "Mengecek pip..."
    if command -v pip3 &>/dev/null; then
        ok "pip3 sudah terinstall"
        return 0
    fi
    warn "pip3 tidak ditemukan — menginstall..."
    case $OS in
        debian)
            sudo apt install -y -qq python3-pip
            ;;
        redhat)
            sudo yum install -y python3-pip 2>/dev/null || sudo dnf install -y python3-pip
            ;;
        alpine)
            sudo apk add py3-pip
            ;;
        macos)
            python3 -m ensurepip --upgrade
            ;;
        *)
            # Fallback: ensurepip
            python3 -m ensurepip --upgrade 2>/dev/null || {
                err "Tidak bisa install pip otomatis."
                exit 1
            }
            ;;
    esac
    ok "pip3 terinstall"
}

clone_repo() {
    step "Clone repo TkViews..."
    if [ -d "$FOLDER" ]; then
        warn "Folder $FOLDER sudah ada — update dari GitHub..."
        cd "$FOLDER" && git pull origin master
        cd ..
    else
        git clone "$REPO_URL"
    fi
    ok "Repo TkViews siap"
}

install_deps() {
    step "Install Python dependencies..."
    cd "$FOLDER"
    python3 -m pip install --quiet requests
    ok "requests terinstall"
    cd ..
}

run_bot() {
    echo ""
    echo "  ${GREEN}${BOLD}╔══════════════════════════════════════════╗${RESET}"
    echo "  ${GREEN}${BOLD}║  ✅ Install selesai! Siap dijalankan!  ║${RESET}"
    echo "  ${GREEN}${BOLD}╚══════════════════════════════════════════╝${RESET}"
    echo ""
    read -p "  🚀 Jalankan bot sekarang? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$FOLDER" && python3 bot_final.py
    else
        ok "Untuk jalankan nanti:"
        echo "      cd $FOLDER && python3 bot_final.py"
        echo ""
        ok "Atau dari mana saja:"
        echo "      curl -sSL https://raw.githubusercontent.com/clickmamaheti-prog/TkViews/master/install.sh | bash"
    fi
}

# ── Main ─────────────────────────────────────────────────────
banner
detect_os
echo ""
install_git
install_python
install_pip
echo ""
clone_repo
install_deps
run_bot
