# Beiträge / Contributing

Vielen Dank, dass du zu Gentoo Updater beitragen möchtest! Hier sind die Guidelines für einen reibungslosen Beitrag.

## 🇩🇪 Deutsche Richtlinien

### Commit-Messages Format

Damit deine Commits automatisch in die Release-Notes aufgenommen werden, verwende folgendes Format:

```
<Typ>: <Beschreibung>
```

#### Typen

- **feat:** Neue Features/Funktionalität
  ```bash
  git commit -m "feat: Add Internet Connection Check"
  git commit -m "feat: Add Bilingual Help Text Support"
  ```

- **fix:** Bugfixes
  ```bash
  git commit -m "fix: Fix parameter documentation"
  git commit -m "fix: Correct version detection"
  ```

- **improve:** Verbesserungen und Refactoring
  ```bash
  git commit -m "improve: Optimize mirror selection"
  git commit -m "refactor: Simplify error handling"
  ```

- **sec:** Security-Fixes
  ```bash
  git commit -m "sec: Add GPG signature verification"
  ```

- **docs:** Dokumentation
  ```bash
  git commit -m "docs: Update README with new parameters"
  git commit -m "docs: Add troubleshooting section"
  ```

- **perf:** Performance-Verbesserungen
  ```bash
  git commit -m "perf: Reduce emerge time by 20%"
  ```

### Beispiel-Workflow

```bash
# 1. Feature entwickeln
# ... Dateien bearbeiten ...

# 2. Änderungen testen
python3 -m py_compile gentoo-updater.py
python3 gentoo-updater.py --help

# 3. Mit aussagekräftiger Commit-Message committen
git add -A
git commit -m "feat: Add new update feature"

# 4. Zu deinem Fork pushen
git push origin feature-branch

# 5. Pull Request erstellen
```

### Release-Prozess

Releases werden automatisch mit `create-release.py` erstellt und parsed die Commits automatisch:

```bash
# Patch-Version erhöhen (1.4.31 → 1.4.32)
python3 scripts/create-release.py patch --auto

# Minor-Version erhöhen (1.4.31 → 1.5.0)
python3 scripts/create-release.py minor --auto

# Major-Version erhöhen (1.4.31 → 2.0.0)
python3 scripts/create-release.py major --auto
```

Das Skript wird automatisch:
- ✅ Version in allen Dateien erhöhen
- ✅ Release-Datei mit auto-generierten Notes erstellen
- ✅ CHANGELOG.md aktualisieren
- ✅ Git-Commit und Tag erstellen
- ✅ Zu GitHub pushen
- ✅ GitHub Release erstellen

---

## 🇬🇧 English Guidelines

### Commit Message Format

Use the following format for commits to be automatically included in release notes:

```
<Type>: <Description>
```

#### Types

- **feat:** New features
  ```bash
  git commit -m "feat: Add Internet Connection Check"
  ```

- **fix:** Bug fixes
  ```bash
  git commit -m "fix: Fix parameter documentation"
  ```

- **improve:** Improvements and refactoring
  ```bash
  git commit -m "improve: Optimize mirror selection"
  ```

- **sec:** Security fixes
  ```bash
  git commit -m "sec: Add GPG signature verification"
  ```

- **docs:** Documentation
  ```bash
  git commit -m "docs: Update README with new parameters"
  ```

- **perf:** Performance improvements
  ```bash
  git commit -m "perf: Reduce emerge time by 20%"
  ```

### Example Workflow

```bash
# 1. Develop feature
# ... edit files ...

# 2. Test changes
python3 -m py_compile gentoo-updater.py
python3 gentoo-updater.py --help

# 3. Commit with descriptive message
git add -A
git commit -m "feat: Add new update feature"

# 4. Push to your fork
git push origin feature-branch

# 5. Create Pull Request
```

### Release Process

Releases are automatically created with `create-release.py` which automatically parses commits:

```bash
# Bump patch version (1.4.31 → 1.4.32)
python3 scripts/create-release.py patch --auto

# Bump minor version (1.4.31 → 1.5.0)
python3 scripts/create-release.py minor --auto

# Bump major version (1.4.31 → 2.0.0)
python3 scripts/create-release.py major --auto
```

The script will automatically:
- ✅ Bump version in all files
- ✅ Create release file with auto-generated notes
- ✅ Update CHANGELOG.md
- ✅ Create git commit and tag
- ✅ Push to GitHub
- ✅ Create GitHub release

---

## Auto-Generated Release Notes Format

Release notes are automatically categorized:

### ✨ New Features
```
- feat: Your feature description (abc1234)
```

### 🐛 Bug Fixes
```
- fix: Your bugfix description (def5678)
```

### ⚡ Improvements
```
- improve: Your improvement description (ghi9012)
```

### 🔐 Security
```
- sec: Your security fix description (jkl3456)
```

### 📝 Documentation
```
- docs: Your documentation update (mno7890)
```

### 📋 Other Changes
```
- Your other commit description (pqr1234)
```

---

## Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/roimme65/gentoo-updater/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/roimme65/gentoo-updater/discussions)
- 📧 **Contact:** Create an issue or discussion

Danke / Thank you! 🙏
