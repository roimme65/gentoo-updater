#!/bin/bash
#
# Gentoo Updater - Automatische Release-Erstellung
#
# Verwendung: ./scripts/create-release.sh [major|minor|patch]
#
# Beispiel: ./scripts/create-release.sh patch
#   → Bumpt 1.2.1 zu 1.2.2
#

set -e

# Farben
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

# Prüfe ob im richtigen Verzeichnis
if [ ! -f "gentoo-updater.py" ]; then
    print_error "Bitte aus dem Repository-Root ausführen"
    exit 1
fi

# Prüfe ob git sauber ist
if [ -n "$(git status --porcelain)" ]; then
    print_error "Git-Arbeitsverzeichnis nicht sauber. Bitte committe alle Änderungen."
    git status --short
    exit 1
fi

# Prüfe ob auf main Branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_error "Nicht auf main Branch. Aktuell auf: $CURRENT_BRANCH"
    exit 1
fi

# Hole aktuelle Version aus gentoo-updater.py
CURRENT_VERSION=$(grep "version='Gentoo Updater" gentoo-updater.py | grep -oP 'v\K[0-9]+\.[0-9]+\.[0-9]+')
print_info "Aktuelle Version: v$CURRENT_VERSION"

# Parse Version
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Bestimme neue Version
BUMP_TYPE=${1:-patch}

case $BUMP_TYPE in
    major)
        NEW_MAJOR=$((MAJOR + 1))
        NEW_MINOR=0
        NEW_PATCH=0
        ;;
    minor)
        NEW_MAJOR=$MAJOR
        NEW_MINOR=$((MINOR + 1))
        NEW_PATCH=0
        ;;
    patch)
        NEW_MAJOR=$MAJOR
        NEW_MINOR=$MINOR
        NEW_PATCH=$((PATCH + 1))
        ;;
    *)
        print_error "Ungültiger Bump-Typ: $BUMP_TYPE (Erlaubt: major, minor, patch)"
        exit 1
        ;;
esac

NEW_VERSION="${NEW_MAJOR}.${NEW_MINOR}.${NEW_PATCH}"
print_info "Neue Version: v$NEW_VERSION ($BUMP_TYPE bump)"

# Frage Nutzer um Bestätigung
read -p "$(echo -e ${YELLOW}Möchtest du mit dem Release v$NEW_VERSION fortfahren? [y/N] ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Release abgebrochen"
    exit 0
fi

# Schritt 1: Version in gentoo-updater.py aktualisieren
print_info "Aktualisiere Version in gentoo-updater.py..."
sed -i "s/version='Gentoo Updater v[0-9.]*'/version='Gentoo Updater v$NEW_VERSION'/" gentoo-updater.py
print_success "Version aktualisiert: v$NEW_VERSION"

# Schritt 2: Release-Notes Template erstellen
RELEASE_NOTES_FILE="releases/v${NEW_VERSION}.md"
if [ -f "$RELEASE_NOTES_FILE" ]; then
    print_warning "Release-Notes existieren bereits: $RELEASE_NOTES_FILE"
else
    print_info "Erstelle Release-Notes Template..."
    cat > "$RELEASE_NOTES_FILE" << EOF
# Release v${NEW_VERSION}

**Veröffentlicht:** $(date +"%d. %B %Y")

## Übersicht

<!-- Kurze Beschreibung der wichtigsten Änderungen -->

## 🎯 Neue Features

<!-- Liste neuer Features -->

## 🔧 Verbesserungen

<!-- Liste von Verbesserungen -->

## 🐛 Bugfixes

<!-- Liste behobener Bugs -->

## 📋 Breaking Changes

<!-- Wenn vorhanden, sonst löschen -->
Keine Breaking Changes - vollständig rückwärtskompatibel mit v${CURRENT_VERSION}

## 🚀 Migration von v${CURRENT_VERSION}

<!-- Migrations-Schritte, falls nötig -->
Keine Aktionen erforderlich - Update funktioniert transparent.

## 🔗 Links

- [CHANGELOG](../CHANGELOG.md)
- [GitHub Release](https://github.com/roimme65/gentoo-updater/releases/tag/v${NEW_VERSION})

---

**Vielen Dank an alle Contributors! 🙏**
EOF
    print_success "Release-Notes Template erstellt: $RELEASE_NOTES_FILE"
    print_warning "Bitte bearbeite die Release-Notes und führe das Skript dann erneut aus"
    
    # Öffne Editor
    if command -v ${EDITOR:-nano} &> /dev/null; then
        ${EDITOR:-nano} "$RELEASE_NOTES_FILE"
    fi
    
    exit 0
fi

# Schritt 3: CHANGELOG.md aktualisieren
print_info "Aktualisiere CHANGELOG.md..."
CHANGELOG_ENTRY="## [${NEW_VERSION}] - $(date +"%Y-%m-%d")

### Siehe
- Detaillierte Release-Notes: [releases/v${NEW_VERSION}.md](releases/v${NEW_VERSION}.md)

---

"

# Füge nach der ersten Zeile mit ## ein
sed -i "/^## \[/i $CHANGELOG_ENTRY" CHANGELOG.md
print_success "CHANGELOG.md aktualisiert"

# Schritt 4: Git commit
print_info "Erstelle Git-Commit..."
git add gentoo-updater.py "$RELEASE_NOTES_FILE" CHANGELOG.md
git commit -m "Release v${NEW_VERSION}

- Bump version to v${NEW_VERSION}
- Add release notes
- Update CHANGELOG"
print_success "Commit erstellt"

# Schritt 5: Git Tag erstellen
print_info "Erstelle Git-Tag v${NEW_VERSION}..."
git tag -a "v${NEW_VERSION}" -m "Version ${NEW_VERSION}"
print_success "Tag erstellt: v${NEW_VERSION}"

# Schritt 6: Push zu GitHub
print_info "Pushe zu GitHub..."
git push origin main
git push origin "v${NEW_VERSION}"
print_success "Gepusht zu GitHub"

# Fertig!
echo ""
print_success "🎉 Release v${NEW_VERSION} wurde erfolgreich erstellt!"
echo ""
print_info "GitHub Actions wird jetzt automatisch:"
echo "  1. ✓ Version validieren"
echo "  2. ✓ Python-Syntax prüfen"
echo "  3. ✓ Release auf GitHub erstellen"
echo "  4. ✓ Assets hochladen"
echo ""
print_info "Verfolge den Workflow: https://github.com/roimme65/gentoo-updater/actions"
echo ""
