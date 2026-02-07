#!/bin/bash
#
# Gentoo Updater - Automatische Release-Erstellung
#
# Verwendung: ./scripts/create-release.sh [major|minor|patch] [--auto]
#
# Beispiel: ./scripts/create-release.sh patch
#   → Bumpt 1.2.2 zu 1.2.3 (mit Editor)
# Beispiel: ./scripts/create-release.sh patch --auto
#   → Vollautomatisch ohne Editor
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

# Parse Argumente
BUMP_TYPE="patch"
AUTO_MODE=false

for arg in "$@"; do
    case $arg in
        --auto)
            AUTO_MODE=true
            ;;
        major|minor|patch)
            BUMP_TYPE=$arg
            ;;
        *)
            print_error "Ungültiges Argument: $arg"
            echo "Verwendung: $0 [major|minor|patch] [--auto]"
            exit 1
            ;;
    esac
done

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
esac

NEW_VERSION="${NEW_MAJOR}.${NEW_MINOR}.${NEW_PATCH}"
print_info "Neue Version: v$NEW_VERSION (${BUMP_TYPE} bump)"

# Frage Nutzer um Bestätigung (außer im Auto-Mode)
if [ "$AUTO_MODE" = false ]; then
    read -p "$(echo -e ${YELLOW}Möchtest du mit dem Release v$NEW_VERSION fortfahren? [y/N] ${NC})" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Release abgebrochen"
        exit 0
    fi
else
    print_info "Auto-Mode: Fahre automatisch fort mit v$NEW_VERSION"
fi

# Schritt 1: Version in gentoo-updater.py aktualisieren
print_info "Aktualisiere Version in gentoo-updater.py..."
sed -i "s/version='Gentoo Updater v[0-9.]*'/version='Gentoo Updater v$NEW_VERSION'/" gentoo-updater.py
print_success "Version aktualisiert: v$NEW_VERSION"

# Schritt 2: Release-Notes erstellen
RELEASE_NOTES_FILE="releases/v${NEW_VERSION}.md"

# Funktion: Generiere automatische Release-Notes aus Git-Commits
generate_auto_release_notes() {
    local prev_version="v${CURRENT_VERSION}"
    local new_version="v${NEW_VERSION}"
    
    print_info "Analysiere Commits seit $prev_version..."
    
    # Hole Commits seit letztem Tag
    local commits
    commits=$(git log ${prev_version}..HEAD --pretty=format:"%s" 2>/dev/null || echo "")
    
    # Kategorisiere Commits
    local features=""
    local improvements=""
    local bugfixes=""
    local other=""
    
    while IFS= read -r commit; do
        [[ -z "$commit" ]] && continue
        
        if [[ "$commit" =~ ^(feat|feature|add|✨) ]] || [[ "$commit" =~ [Nn]ew[[:space:]][Ff]eature ]]; then
            features="${features}- ${commit}\n"
        elif [[ "$commit" =~ ^(fix|bug|🐛) ]]; then
            bugfixes="${bugfixes}- ${commit}\n"
        elif [[ "$commit" =~ ^(improve|enhance|update|refactor|🔧|⚡) ]]; then
            improvements="${improvements}- ${commit}\n"
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

**Veröffentlicht:** $(date +"%-d. %B %Y" 2>/dev/null || date +"%d. %B %Y")

## Übersicht

Release v${NEW_VERSION} mit Updates seit v${CURRENT_VERSION}.

## 🎯 Neue Features

$(echo -e "$features")

## 🔧 Verbesserungen

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
        generate_auto_release_notes
        print_success "Release-Notes automatisch generiert"
    else
        print_info "Erstelle Release-Notes Template..."
        cat > "$RELEASE_NOTES_FILE" << 'EOF'
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

Keine Breaking Changes - vollständig rückwärtskompatibel mit v${CURRENT_VERSION}

## 🚀 Migration von v${CURRENT_VERSION}

Keine Aktionen erforderlich - Update funktioniert transparent.

## 🔗 Links

- [CHANGELOG](../CHANGELOG.md)
- [GitHub Release](https://github.com/roimme65/gentoo-updater/releases/tag/v${NEW_VERSION})

---

**Vielen Dank an alle Contributors! 🙏**
EOF
        # Ersetze Variablen im Template
        sed -i "s/\${NEW_VERSION}/${NEW_VERSION}/g" "$RELEASE_NOTES_FILE"
        sed -i "s/\${CURRENT_VERSION}/${CURRENT_VERSION}/g" "$RELEASE_NOTES_FILE"
        sed -i "s/\$(date +\"%d. %B %Y\")/$(date +"%d. %B %Y")/g" "$RELEASE_NOTES_FILE"
        
        print_success "Release-Notes Template erstellt: $RELEASE_NOTES_FILE"
        print_warning "Bitte bearbeite die Release-Notes und führe das Skript dann erneut aus"
        
        # Öffne Editor
        if command -v ${EDITOR:-nano} &> /dev/null; then
            ${EDITOR:-nano} "$RELEASE_NOTES_FILE"
        fi
        
        exit 0
    fi
fi

# Schritt 3: CHANGELOG.md aktualisieren
print_info "Aktualisiere CHANGELOG.md..."

# Temporäre Datei mit neuem Eintrag
{
    cat << EOFCHG
## [${NEW_VERSION}] - $(date +"%Y-%m-%d")

### Siehe
- Detaillierte Release-Notes: [releases/v${NEW_VERSION}.md](releases/v${NEW_VERSION}.md)

---

EOFCHG
    cat CHANGELOG.md
} > CHANGELOG.md.new
mv CHANGELOG.md.new CHANGELOG.md

print_success "CHANGELOG.md aktualisiert"

# Schritt 4: Git commit
print_info "Erstelle Git-Commit..."
git add gentoo-updater.py "$RELEASE_NOTES_FILE" CHANGELOG.md
git commit -m "v${NEW_VERSION} - Release

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

# Watte kurz, damit GitHub den Tag registriert
sleep 2

# Erstelle Release mit gh CLI
if command -v gh &> /dev/null; then
    if gh release create "v${NEW_VERSION}" \
        --title "v${NEW_VERSION} - Gentoo System Updater" \
        --notes-file "$RELEASE_NOTES_FILE" \
        gentoo-updater.py \
        gentoo-updater.conf.example; then
        print_success "GitHub Release erstellt: https://github.com/roimme65/gentoo-updater/releases/tag/v${NEW_VERSION}"
    else
        print_warning "GitHub Release konnte nicht erstellt werden. Prüfe gh CLI Authentifizierung."
        print_info "Alternativ: GitHub Actions erstellt das Release automatisch."
    fi
else
    print_warning "gh CLI nicht installiert. GitHub Actions erstellt das Release automatisch."
fi

# Schritt 8: Erstelle GitHub Discussion für neues Release
print_info "Erstelle GitHub Discussion für neues Release..."

if command -v gh &> /dev/null; then
    # Lese Release-Notes für die Diskussion
    release_notes_content=$(cat "$RELEASE_NOTES_FILE" 2>/dev/null || echo "")
    
    # Kurze Zusammenfassung aus Release-Notes extrahieren
    discussion_body="🎉 **v${NEW_VERSION} ist jetzt verfügbar!**

## Release-Informationen

Bitte benutzt diesen Thread um v${NEW_VERSION} zu diskutieren.

📖 **Release-Notes:** https://github.com/roimme65/gentoo-updater/releases/tag/v${NEW_VERSION}

## Feedback & Fragen

- 🐛 **Bugs gefunden?** → [Issue erstellen](https://github.com/roimme65/gentoo-updater/issues/new?template=bug_report.md)
- 💡 **Neue Features?** → [Feature Request](https://github.com/roimme65/gentoo-updater/issues/new?template=feature_request.md)
- ❓ **Fragen?** → Antwortet hier in der Diskussion

**Vielen Dank für eure Unterstützung!** 🙏"
    
    # Versuche Discussion zu erstellen mit Fehlerausgabe
    discussion_output=$(gh discussion create \
        --title "v${NEW_VERSION} - Release Discussion" \
        --body "$discussion_body" \
        --category "Announcements" \
        2>&1)
    discussion_exit_code=$?
    
    if [ $discussion_exit_code -eq 0 ]; then
        print_success "GitHub Discussion erstellt: https://github.com/roimme65/gentoo-updater/discussions"
    else
        print_warning "GitHub Discussion konnte nicht erstellt werden (optional)."
        if [[ "$discussion_output" == *"not found"* ]] || [[ "$discussion_output" == *"404"* ]]; then
            print_info "→ Kategorie 'Announcements' nicht gefunden. Erstelle ohne Kategorie..."
            gh discussion create \
                --title "v${NEW_VERSION} - Release Discussion" \
                --body "$discussion_body" \
                2>/dev/null && print_success "GitHub Discussion erstellt: https://github.com/roimme65/gentoo-updater/discussions"
        fi
        print_info "Du kannst die Diskussion auch manuell erstellen: https://github.com/roimme65/gentoo-updater/discussions/new"
    fi
else
    print_warning "gh CLI nicht installiert. Discussion kann nicht automatisch erstellt werden."
fi

# Fertig!
echo ""
print_success "🎉 Release v${NEW_VERSION} wurde erfolgreich erstellt!"
echo ""
print_info "Das Release ist verfügbar unter:"
echo "  https://github.com/roimme65/gentoo-updater/releases/tag/v${NEW_VERSION}"
echo ""
print_info "Diskussions-Thread:"
echo "  https://github.com/roimme65/gentoo-updater/discussions"
echo ""
