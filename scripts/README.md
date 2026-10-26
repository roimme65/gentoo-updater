# Release Scripts

## create-release.py

Automatisiert den Release-Prozess für den Gentoo Updater. Das Skript erhöht die Version, erstellt Release-Notes, committet, taggt und pusht. GitHub Release und Discussion erstellen danach die GitHub Actions.

### Verwendung

```bash
# Patch Release (1.2.3 → 1.2.4) - Bugfixes
python scripts/create-release.py patch --auto

# Minor Release (1.2.3 → 1.3.0) - Neue Features
python scripts/create-release.py minor --auto

# Major Release (1.2.3 → 2.0.0) - Breaking Changes
python scripts/create-release.py major --auto

# Interaktiv (Bestätigung vor dem Fortfahren)
python scripts/create-release.py patch

# Nur lokal committen und taggen, später selbst pushen
python scripts/create-release.py patch --no-push
```

### Workflow

```bash
# 1. Änderungen committen, CHANGELOG unter "## Unreleased" pflegen
git commit -am "feat: Add Python update handling"
git push

# 2. Release erstellen
python scripts/create-release.py patch --auto
```

### Was passiert?

1. **Prüfungen** – bevor irgendetwas geändert wird:
   - Arbeitsverzeichnis ist sauber (sonst würden fremde Änderungen im Release-Commit landen)
   - aktueller Branch ist `main`
   - Tag `vX.Y.Z` existiert weder lokal noch auf GitHub
   - lokaler Branch ist nicht hinter `origin/main`
2. Versionsnummer in `gentoo-updater.py` und `install.py` erhöhen
3. `releases/vX.Y.Z.md` schreiben: Einträge aus `## Unreleased` im CHANGELOG plus kategorisierte Commits seit dem letzten Tag
4. `## Unreleased` im `CHANGELOG.md` in `## vX.Y.Z (Datum)` umbenennen (gibt es keinen Abschnitt, wird ein Eintrag ohne Details angelegt)
5. Commit `vX.Y.Z - Release` mit genau diesen Dateien, danach Tag `vX.Y.Z`
6. Commit und Tag zu GitHub pushen

Schlägt ein Schritt fehl, bricht das Skript ab. Ohne erfolgreichen Commit wird kein Tag erstellt.

### GitHub Actions (durch den Tag-Push ausgelöst)

| Workflow | Aufgabe |
|----------|---------|
| `release.yml` | prüft die Version in `gentoo-updater.py`/`install.py` gegen den Tag, erstellt das GitHub Release mit `releases/vX.Y.Z.md` und hängt die Dateien an |
| `create-discussion.yml` | erstellt die Discussion „Release vX.Y.Z“ in der Kategorie *Announcements* (übersprungen, falls bereits vorhanden) |

### 🏷️ Commit-Message Kategorisierung

Präfixe nach Conventional Commits, optional mit Scope (`feat(sync):`) und `!` für Breaking Changes:

| Kategorie | Prefixes |
|-----------|----------|
| ✨ Neue Features | `feat:`, `feature:`, `add:`, `✨`, `🆕` |
| 🐛 Bugfixes | `fix:`, `bugfix:`, `bug:`, `🐛`, `🔧` |
| ⚡ Verbesserungen | `improve:`, `perf:`, `refactor:`, `⚡` |
| 🔐 Security | `sec:`, `security:`, `🔐` |
| 📝 Dokumentation | `docs:`, `doc:`, `readme:`, `📝` |
| 🔀 Andere Commits | alles Weitere (außer `vX.Y.Z - Release`) |

### Voraussetzungen

- Python 3.9+
- Git mit SSH-Zugriff auf GitHub (`ssh -T git@github.com`)
- Die `gh` CLI wird **nicht** mehr benötigt

### Troubleshooting

**„Arbeitsverzeichnis enthält nicht committete Änderungen“**
```bash
git status            # Änderungen committen oder
git stash             # vorübergehend beiseitelegen
```

**„Tag vX.Y.Z existiert bereits“**
```bash
git tag -l 'vX.Y.Z'
git tag -d vX.Y.Z     # nur lokal löschen, wenn er nie gepusht wurde
```

**„Push zu GitHub fehlgeschlagen“** – Commit und Tag sind lokal vorhanden:
```bash
ssh -T git@github.com
git push origin main && git push origin vX.Y.Z
```
