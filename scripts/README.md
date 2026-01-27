# Release Scripts

## create-release.sh

Automatisiert den kompletten Release-Prozess für den Gentoo Updater.

### Features

✨ **Vollautomatisch:**
- Version-Bumping (major, minor, patch)
- Release-Notes-Template-Generierung
- CHANGELOG-Update
- Git-Commit und Tag
- Push zu GitHub
- Triggert automatisch GitHub Actions für Release-Erstellung

### Verwendung

#### Patch Release (1.2.1 → 1.2.2)
```bash
./scripts/create-release.sh patch
```

#### Minor Release (1.2.1 → 1.3.0)
```bash
./scripts/create-release.sh minor
```

#### Major Release (1.2.1 → 2.0.0)
```bash
./scripts/create-release.sh major
```

### Workflow

1. **Beim ersten Aufruf:**
   - Erstellt Release-Notes Template
   - Öffnet Editor zum Bearbeiten
   - Beende das Skript

2. **Beim zweiten Aufruf:**
   - Liest vollständige Release-Notes
   - Aktualisiert Version überall
   - Erstellt Commit und Tag
   - Pusht zu GitHub
   - GitHub Actions erstellt automatisch das Release

### Voraussetzungen

✅ **Git muss sauber sein** (keine uncommitted changes)  
✅ **Auf main Branch**  
✅ **SSH-Key für GitHub** konfiguriert

### Beispiel

```bash
# 1. Patch Release starten
./scripts/create-release.sh patch

# → Öffnet Editor für Release-Notes
# → Bearbeite die Notes und speichere

# 2. Skript erneut ausführen
./scripts/create-release.sh patch

# → Erstellt Release v1.2.2
# → Pusht zu GitHub
# → GitHub Actions erstellt automatisch das Release

# ✅ Fertig!
```

### Was passiert automatisch?

1. ✓ Version in `gentoo-updater.py` wird aktualisiert
2. ✓ Release-Notes in `releases/vX.Y.Z.md` werden erstellt/verwendet
3. ✓ `CHANGELOG.md` wird aktualisiert
4. ✓ Git-Commit wird erstellt
5. ✓ Git-Tag `vX.Y.Z` wird erstellt
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
