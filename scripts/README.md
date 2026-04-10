# Release Scripts

## create-release.py

Automatisiert den kompletten Release-Prozess für den Gentoo Updater.

### Features

✨ **Vollautomatisch:**
- Version-Bumping (major, minor, patch)
- **Automatische Release-Notes aus Git-Commits** (mit `--auto`)
- **Intelligente Commit-Kategorisierung** (Features, Bugfixes, Security, Docs, Improvements)
- CHANGELOG-Update
- Git-Commit und Tag
- Push zu GitHub
- **Direktes GitHub Release erstellen** (via `gh` CLI)
- **GitHub Discussion** wird automatisch via GitHub Action erstellt

### Verwendung

#### 🚀 Vollautomatischer Modus (empfohlen)

```bash
# Patch Release (1.2.3 → 1.2.4) - Bugfixes
python scripts/create-release.py patch --auto

# Minor Release (1.2.3 → 1.3.0) - Neue Features
python scripts/create-release.py minor --auto

# Major Release (1.2.3 → 2.0.0) - Breaking Changes
python scripts/create-release.py major --auto
```

**Das war's!** Ein Befehl macht alles:
- ✅ Analysiert Commits seit letztem Release
- ✅ Generiert Release-Notes automatisch
- ✅ Updated Version + CHANGELOG
- ✅ Erstellt Commit, Tag & Release
- ✅ Alles auf GitHub

#### 📝 Interaktiver Modus (mit Bestätigung)

```bash
# Ohne --auto wird vor dem Fortfahren eine Bestätigung abgefragt
python scripts/create-release.py patch
```

#### ⏭ GitHub-Integration überspringen

```bash
python scripts/create-release.py patch --auto --skip-github
```

### 🏷️ Commit-Message Kategorisierung

Das Skript kategorisiert Commits automatisch für die Release-Notes:

| Kategorie | Prefixes |
|-----------|----------|
| ✨ Neue Features | `feat:`, `feature:`, `add:`, `✨`, `🆕` |
| 🐛 Bugfixes | `fix:`, `bugfix:`, `bug:`, `🐛`, `🔧` |
| ⚡ Verbesserungen | `improve:`, `perf:`, `refactor:`, `⚡` |
| 🔐 Security | `sec:`, `security:`, `🔐` |
| 📝 Dokumentation | `docs:`, `doc:`, `readme:`, `📝` |
| 📋 Andere | alles Weitere (außer Release-Commits) |

### Workflow

**Ein-Befehl-Release:**
```bash
# 1. Normale Änderungen committen
git add -A
git commit -m "feat: Add Python update handling"
git push

# 2. Release erstellen
python scripts/create-release.py patch --auto

# ✅ Fertig! Release ist live auf GitHub
```

### Was passiert automatisch?

1. ✓ Aktuelle Version aus `gentoo-updater.py` auslesen
2. ✓ Versionsnummer in `gentoo-updater.py` und `install.py` erhöhen
3. ✓ Git-Commits seit letztem Tag analysieren und kategorisieren
4. ✓ Release-Notes in `releases/vX.Y.Z.md` schreiben
5. ✓ `CHANGELOG.md` aktualisieren
6. ✓ Git-Commit (`vX.Y.Z - Release`) erstellen
7. ✓ Git-Tag `vX.Y.Z` erstellen
8. ✓ Commits und Tag zu GitHub pushen
9. ✓ **GitHub Release** direkt via `gh` CLI erstellen
10. ✓ **GitHub Discussion** via GitHub Action (`.github/workflows/create-discussion.yml`) erstellen

### Voraussetzungen

✅ **Python 3** installiert  
✅ **Git muss sauber sein** (keine uncommitted changes)  
✅ **Auf main Branch**  
✅ **SSH-Key für GitHub** konfiguriert  
✅ **gh CLI installiert und authentifiziert** (für direktes GitHub Release)

### Sicherheit

- Im interaktiven Modus: Bestätigung vor dem Release
- Zeigt aktuelle und neue Version vor Ausführung an

### Troubleshooting

**"Konnte aktuelle Version nicht ermitteln"**
```bash
# Stelle sicher dass __version__ in gentoo-updater.py vorhanden ist
grep '__version__' gentoo-updater.py
```

**"Tag-Erstellung fehlgeschlagen"**
```bash
# Tag existiert möglicherweise bereits
git tag -l | grep vX.Y.Z
git tag -d vX.Y.Z  # Tag lokal löschen falls nötig
```

**"Push zu GitHub fehlgeschlagen"**
```bash
# SSH-Key prüfen
ssh -T git@github.com
```

**"gh CLI nicht installiert"**
- GitHub Release wird dann übersprungen
- Release kann manuell auf github.com erstellt werden
- Alternativ: `emerge dev-util/github-cli` und `gh auth login`

### Integration mit GitHub Actions

Das Skript triggert via Tag-Push automatisch:
- `create-discussion.yml` – erstellt eine GitHub Discussion zum Release

Kein manueller GitHub-Zugriff mehr nötig! 🎉
