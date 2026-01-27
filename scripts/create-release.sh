#!/bin/bash
#
# Gentoo Updater - Automatische Release-Erstellung
#
# Verwendung: ./scripts/create-release.sh [major|minor|patch] [--auto]
#
# Beispiel: ./scripts/create-release.sh patch
#   → Bumpt 1.2.1 zu 1.2.2
# Beispiel: ./scripts/create-release.sh patch --auto
#   → Automatisch ohne Editor
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

# Parse Argumente
BUMP_TYPE=${1:-patch}
AUTO_MODE=false

if [[ "$2" == "--auto" ]] || [[ "$1" == "--auto" ]]; then
    AUTO_MODE=true
    if [[ "$1" == "--auto" ]]; then
        BUMP_TYPE="patch"
    fi
fi

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
        print_error "Ungültig (außer im Auto-Mode)
if [ "$AUTO_MODE" = false ]; then
    read -p "$(echo -e ${YELLOW}Möchtest du mit dem Release v$NEW_VERSION fortfahren? [y/N] ${NC})" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Release abgebrochen"
        exit 0
    fi
else
    print_info "Auto-Mode: Fahre automatisch fort mit v$NEW_VERSION"N="${NEW_MAJOR}.${NEW_MINOR}.${NEW_PATCH}"
print_info "Neue Version: v$NEW_VERSION ($BUMP_TYPE bump)"

# Frage Nutzer um Bestätigung
read -p "$(echo -e ${YELLOW}Möchtest du mit dem Release v$NEW_VERSION fortfahren? [y/N] ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Release abgebrochen"
    exit 0
fi

# Schritt 1: Version in gentoo-updater.py aktualisieren
print_info "Aktualisiere Veerstellen oder generieren
RELEASE_NOTES_FILE="releases/v${NEW_VERSION}.md"

# Funktion: Generiere automatische Release-Notes aus Git-Commits
generate_auto_release_notes() {
    local prev_version="v${CURRENT_VERSION}"
    local new_version="v${NEW_VERSION}"
    
    print_info "Analysiere Commits seit $prev_version..."
    
    # Hole Commits seit letztem Tag
    local commits=$(git log ${prev_version}..HEAD --pretty=format:"%s" 2>/dev/null || echo "")
    
    # Kategorisiere Commits
    local features=""
    local improvements=""
    local bugfixes=""
    local other=""
    
    while IFS= read -r commit; do
        [[ -z "$commit" ]] && continue
        
        if [[ "$commit" =~ ^(feat|feature|add|\+|✨) ]] || [[ "$commit" =~ [Nn]ew\ [Ff]eature ]]; then
            features="${features}- ${commit#*: }\n"
        elif [[ "$commit" =~ ^(fix|bug|🐛) ]]; then
            bugfixes="${bugfixes}- ${commit#*: }\n"
        elif [[ "$commit" =~ ^(improve|enhance|update|refactor|🔧|⚡) ]]; then
            improvements="${improvements}- ${commit#*: }\n"
        else
            other="${other}- ${commit}\n"
        fi
    done <<< "$commits"
    
    # Wenn keine kategorisierten Commits, nutze "other"
    if [[ -z "$features" && -z "$bugfixes" && -z "$improvements" ]]; then
        improvements="$other"
    fi
    
    # Default Werte wenn leer
    [[ -z "$features" ]] && features="Keine neuen Features in diesem Release\n"
    [[ -z "$improvements" ]] && improvements="Kleinere Verbesserungen und Dokumentationsupdates\n"
    [[ -z "$bugfixes" ]] && bugfixes="Keine Bugfixes in diesem Release\n"
    
    # Erstelle Release-Notes
    cat > "$RELEASE_NOTES_FILE" << EOF
# Release v${NEW_VERSION}

**Veröffentlicht:** $(date +"%-d. %B %Y")

## Übersicht
    print_success "Release-Notes Template erstellt: $RELEASE_NOTES_FILE"
        print_warning "Bitte bearbeite die Release-Notes und führe das Skript dann erneut aus"
        
        # Öffne Editor
        if command -v ${EDITOR:-nano} &> /dev/null; then
            ${EDITOR:-nano} "$RELEASE_NOTES_FILE"
        fi
        
        exit 0
    fi
$(echo -e "$improvements")

## 🐛 Bugfixes

$(echo -e "$bugfixes")

## 📋 Breaking Changes

Keine Breaking Changes - vollständig rückwärtskompatibel mit v${CURRENT_VERSION}

## 🚀 Migration von v${CURRENT_VERSION}

Keine Aktionen erforderlich - Update funktioniert transparent.

## 🔗 Links

- [CHANGELOG](../CHANGELOG.md)
- [GitHub Release](https://github.com/roimme65/gentoo-updater/releases/tag/v${NEW_VERSION})

---

**Vielen Dank an alle Contributors! 🙏**
EOF
}

if [ -f "$RELEASE_NOTES_FILE" ]; then
    print_warning "Release-Notes existieren bereits: $RELEASE_NOTES_FILE"
else
    if [ "$AUTO_MODE" = true ]; then
        print_info "Generiere automatische Release-Notes..."
        generate_auto_release_notes
        print_success "Release-Notes automatisch generiert: $RELEASE_NOTES_FILE"
    else
        print_info "Erstelle Release-Notes Template..."
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

# Schritt 7: Erstelle GitHub Release
print_info "Erstelle GitHub Release..."

# Warte kurz, damit GitHub den Tag registriert
sleep 2

# Erstelle Release mit gh CLI
if command -v gh &> /dev/null; then
    gh release create "v${NEW_VERSION}" \
        --title "v${NEW_VERSION} - Gentoo System Updater" \
        --notes-file "$RELEASE_NOTES_FILE" \
        gentoo-updater.py \
        gentoo-updater.conf.example
    
    if [ $? -eq 0 ]; then
        print_success "GitHub Release erstellt: https://github.com/roimme65/gentoo-updater/releases/tag/v${NEW_VERSION}"
    else
        print_warning "GitHub Release konnte nicht erstellt werden. Prüfe gh CLI Authentifizierung."
        print_info "Alternativ: GitHub Actions erstellt das Release automatisch."
    fi
else
    print_warning "gh CLI nicht installiert. GitHub Actions erstellt das Release automatisch."
fi

# Fertig!
echo ""
print_success "🎉 Release v${NEW_VERSION} wurde erfolgreich erstellt!"
echo ""
print_info "Das Release ist verfügbar unter:"
echo "  https://github.com/roimme65/gentoo-updater/releases/tag/v${NEW_VERSION}"
echo ""
