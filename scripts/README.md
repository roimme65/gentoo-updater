# Release Scripts

## create-release.sh

Automatisiert den kompletten Release-Prozess für den Gentoo Updater.

### Features

✨ **Vollautomatisch:**
- Version-Bumping (major, minor, patch)
- **Automatische Release-Notes aus Git-Commits** (mit `--auto`)
- **Intelligente Commit-Kategorisierung** (Features, Bugfixes, Improvements)
- CHANGELOG-Update
- Git-Commit und Tag
- Push zu GitHub
- **Direktes GitHub Release erstellen** (via gh CLI)

### Verwendung

#### 🚀 Vollautomatischer Modus (empfohlen)

```bash
# Patch Release (1.2.3 → 1.2.4) - Bugfixes
./scripts/create-release.sh patch --auto

# Minor Release (1.2.3 → 1.3.0) - Neue Features
./scripts/create-release.sh minor --auto

# Major Release (1.2.3 → 2.0.0) - Breaking Changes
./scripts/create-release.sh major --auto
```

**Das war's!** Ein Befehl macht alles:
- ✅ Analysiert Commits seit letztem Release
- ✅ Generiert Release-Notes automatisch
- ✅ Updated Version + CHANGELOG
- ✅ Erstellt Commit, Tag & Release
- ✅ Alles auf GitHub

#### 📝 Interaktiver Modus (mit Editor)

```bash
# Ohne --auto öffnet sich der Editor
./scripts/create-release.sh patch
```

# Ohne --auto öffnet sich der Editor
./scripts/create-release.sh patch

# → Editor öffnet sich für manuelle Release-Notes
# → Speichern und Skript nochmal ausführen
./scripts/create-release.sh patch
```

### 🏷️ Commit-Message Kategorisierung

Das Skript kategorisiert deine Commits automatisch für die Release-Notes:

**Features:**
- `feat:`, `feature:`, `add:`, `✨`
- Beispiel: `feat: Add automatic backup rotation`

**Bugfixes:**
- `fix:`, `bug:`, `🐛`
- Beispiel: `fix: Resolve dependency calculation bug`

**Improvements:**
- `improve:`, `enhance:`, `update:`, `refactor:`, `🔧`, `⚡`
- Beispiel: `improve: Better error messages`

### Workflow (Auto-Mode)

**Ein-Befehl-Release:**

### Workflow (Auto-Mode)

**Ein-Befehl-Release:**
```bash
# 1. Normale Änderungen committen
git add -A
git commit -m "improve: Better documentation"
git push

# 2. Release erstellen
./scripts/create-release.sh patch --auto

# ✅ Fertig! Release ist live auf GitHub
```

### Workflow (Interaktiv)

1. **Erster Aufruf:**
   - Erstellt Release-Notes Template
   - Öffnet Editor zum Bearbeiten
   - Speichern und beenden

2. **Zweiter Aufruf:**
   - Liest bearbeitete Release-Notes
   - Erstellt Release automatisch

### Was passiert automatisch?

1. ✓ Version in `gewerden generiert (auto) oder Template erstellt (interaktiv)
3. ✓ Git-Commits seit letztem Release werden analysiert
4. ✓ Commits werden kategorisiert (Features/Bugfixes/Improvements)
5. ✓ `CHANGELOG.md` wird aktualisiert
6. ✓ Git-Commit wird erstellt
7. ✓ Git-Tag `vX.Y.Z` wird erstellt
8. ✓ Alles wird zu GitHub gepusht
9. ✓ **GitHub Release wird direkt erstellt** (mit gh CLI)
10. ✓ Assets werden hochgeladen (gentoo-updater.py, gentoo-updater.conf.example)

### Voraussetzungen

✅ **Git muss sauber sein** (keine uncommitted changes)  
✅ **Auf main Branch**  
✅ **SSH-Key für GitHub** konfiguriert
✅ **gh CLI installiert und authentifiziert** (für direktes Release)lt
6. ✓ Alles wird zu GitHub gepusht
7. ✓ GitHub Actions erstellt automatisch das Release mit Assets

### Sicherheit

- Fragt vor dem Release nach Bestätigung
- Prüft Git-Status vor Änderungen
- Validiert Branch (nur main erlaubt)
- Zeigt neue Version vor Bestätigung

### Troubleshooting

**"Git-Arbeitsverzeichnis nicht sauber"**
```bash
git status
# Committe oder stashe alle Änderungen
```

**"Nicht auf main Branch"**
```bash
git checkout main
```

**"Release-Notes existieren bereits"**
- Das ist OK, beim zweiten Aufruf werden sie verwendet
- Bearbeite die Datei manuell falls nötig

### Integration mit GitHub Actions

Das Skript triggert automatisch den `release.yml` Workflow, der:
- Version validiert
- Python-Syntax prüft
- GitHub Release erstellt
- Assets hochlädt

Kein manueller GitHub-Zugriff mehr nötig! 🎉
