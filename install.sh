#!/bin/bash
# Gentoo Updater Installationsskript

set -e

# Farben für Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktionen
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Header
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           GENTOO UPDATER - INSTALLATION                            ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Prüfe Root-Rechte
if [ "$EUID" -ne 0 ]; then 
    print_error "Bitte als root ausführen: sudo ./install.sh"
    exit 1
fi

# Prüfe ob Python 3 installiert ist
print_info "Prüfe Python 3 Installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 ist nicht installiert!"
    print_info "Installiere mit: emerge --ask dev-lang/python"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_success "Gefunden: $PYTHON_VERSION"

# Prüfe ob wir auf Gentoo sind
print_info "Prüfe Gentoo Linux..."
if [ ! -f /etc/gentoo-release ]; then
    print_warning "Dies scheint kein Gentoo Linux zu sein!"
    read -p "Trotzdem fortfahren? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_success "Gentoo Linux erkannt: $(cat /etc/gentoo-release)"
fi

# Installiere Skript
print_info "Installiere gentoo-updater..."
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="gentoo-updater"

# Kopiere Skript
cp gentoo-updater.py "$INSTALL_DIR/$SCRIPT_NAME"
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

print_success "Installiert nach: $INSTALL_DIR/$SCRIPT_NAME"

# Prüfe optionale Abhängigkeiten
echo ""
print_info "Prüfe optionale Abhängigkeiten..."

# eix
if ! command -v eix &> /dev/null; then
    print_warning "eix ist nicht installiert (empfohlen für schnellere Paket-Suche)"
    echo "          Installieren mit: emerge --ask app-portage/eix"
else
    print_success "eix ist installiert"
fi

# gentoolkit (revdep-rebuild)
if ! command -v revdep-rebuild &> /dev/null; then
    print_warning "gentoolkit ist nicht installiert (empfohlen für revdep-rebuild)"
    echo "          Installieren mit: emerge --ask app-portage/gentoolkit"
else
    print_success "gentoolkit ist installiert"
fi

# Fertig
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           INSTALLATION ABGESCHLOSSEN                               ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

print_success "gentoo-updater wurde erfolgreich installiert!"
echo ""
print_info "Verwendung:"
echo "  sudo gentoo-updater                          # Vollständiges System-Update"
echo "  sudo gentoo-updater --dry-run                # Test-Modus"
echo "  sudo gentoo-updater --log-level DEBUG        # Debug-Ausgabe"
echo "  sudo gentoo-updater --only-sync              # Nur Repository-Sync"
echo "  sudo gentoo-updater --skip-cleanup           # Überspringe depclean"
echo "  sudo gentoo-updater --max-packages 50        # Limit: max. 50 Pakete"
echo "  GENTOO_UPDATER_DRY_RUN=true gentoo-updater  # Dry-Run via Env-Variable"
echo "  sudo gentoo-updater --help                   # Detaillierte Hilfe"
echo ""

# Frage ob optional dependencies installiert werden sollen
if ! command -v eix &> /dev/null || ! command -v revdep-rebuild &> /dev/null; then
    echo ""
    read -p "Möchten Sie die empfohlenen Pakete jetzt installieren? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if ! command -v eix &> /dev/null; then
            print_info "Installiere eix..."
            emerge --ask app-portage/eix
        fi
        if ! command -v revdep-rebuild &> /dev/null; then
            print_info "Installiere gentoolkit..."
            emerge --ask app-portage/gentoolkit
        fi
    fi
fi

echo ""
print_info "Sie können gentoo-updater jetzt mit 'sudo gentoo-updater' ausführen"
echo ""
