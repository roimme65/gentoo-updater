#!/bin/bash
# Gentoo Updater Installation Script

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

# Check root privileges
if [ "$EUID" -ne 0 ]; then 
    print_error "This script requires root privileges: sudo ./install.sh"
    exit 1
fi

# Check if Python 3 is installed
print_info "Checking Python 3 installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    print_info "Install with: emerge --ask dev-lang/python"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_success "Found: $PYTHON_VERSION"

# Check if running on Gentoo
print_info "Checking Gentoo Linux..."
if [ ! -f /etc/gentoo-release ]; then
    print_warning "This doesn't appear to be Gentoo Linux!"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_success "Gentoo Linux detected: $(cat /etc/gentoo-release)"
fi

# Install script
print_info "Installing gentoo-updater..."
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="gentoo-updater"

# Copy script
cp gentoo-updater.py "$INSTALL_DIR/$SCRIPT_NAME"
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

print_success "Installed to: $INSTALL_DIR/$SCRIPT_NAME"

# Check optional dependencies
echo ""
print_info "Checking optional dependencies..."

# eix
if ! command -v eix &> /dev/null; then
    print_warning "eix is not installed (recommended for faster package searches)"
    echo "          Install with: emerge --ask app-portage/eix"
else
    print_success "eix is installed"
fi

# gentoolkit (revdep-rebuild)
if ! command -v revdep-rebuild &> /dev/null; then
    print_warning "gentoolkit is not installed (recommended for revdep-rebuild)"
    echo "          Install with: emerge --ask app-portage/gentoolkit"
else
    print_success "gentoolkit is installed"
fi

# Done
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           INSTALLATION COMPLETED                                   ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

print_success "gentoo-updater has been successfully installed!"
echo ""
print_info "Usage examples:"
echo "  sudo gentoo-updater                          # Full system update"
echo "  sudo gentoo-updater --dry-run                # Test mode"
echo "  sudo gentoo-updater --lang de                # Use German language"
echo "  sudo gentoo-updater --log-level DEBUG        # Debug output"
echo "  sudo gentoo-updater --only-sync              # Repository sync only"
echo "  sudo gentoo-updater --skip-cleanup           # Skip depclean"
echo "  sudo gentoo-updater --mirrors 'url1 url2'    # Custom mirrors"
echo "  sudo gentoo-updater --max-packages 50        # Limit: max 50 packages"
echo "  sudo gentoo-updater --repository             # Show GitHub repository info"
echo "  sudo gentoo-updater --support                # Show support & issue templates"
echo "  GENTOO_UPDATER_DRY_RUN=true gentoo-updater  # Dry-run via environment variable"
echo "  sudo gentoo-updater --help                   # Detailed help"
echo ""

# Ask about optional dependencies
if ! command -v eix &> /dev/null || ! command -v revdep-rebuild &> /dev/null; then
    echo ""
    read -p "Would you like to install the recommended packages now? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if ! command -v eix &> /dev/null; then
            print_info "Installing eix..."
            emerge --ask app-portage/eix
        fi
        if ! command -v revdep-rebuild &> /dev/null; then
            print_info "Installing gentoolkit..."
            emerge --ask app-portage/gentoolkit
        fi
    fi
fi

echo ""
print_info "You can now run gentoo-updater with: sudo gentoo-updater"
echo ""
