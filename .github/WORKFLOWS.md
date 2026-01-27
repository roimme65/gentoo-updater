# GitHub Actions Workflows

Dieses Repository nutzt GitHub Actions für automatisierte Tests, Validierung und Releases.

## Workflows

### 1. 🚀 Release (`release.yml`)
**Trigger:** Push von Version-Tags (`v*.*.*`)  
**Environment:** `production`

**Was passiert:**
- ✅ Validiert Python-Syntax
- ✅ Prüft Version-Übereinstimmung (Tag vs. Script)
- ✅ Verifiziert Release-Notes
- ✅ Erstellt GitHub Release automatisch
- ✅ Lädt Assets hoch (gentoo-updater.py, config-example)

**Verwendung:**
```bash
git tag -a v1.2.1 -m "Version 1.2.1"
git push --tags
# → Automatisches Release wird erstellt
```

### 2. 🧪 Tests (`test.yml`)
**Trigger:** Push zu `main`/`develop`, Pull Requests  
**Environment:** `development`

**Was passiert:**
- ✅ Python-Syntax-Check (3.11 und 3.12)
- ✅ Code-Qualitäts-Prüfung
- ✅ Dokumentations-Validierung
- ✅ Config-File-Validierung (JSON)

### 3. 🔍 Pull Request Check (`pr-check.yml`)
**Trigger:** Pull Requests zu `main`  
**Environment:** `staging`

**Was passiert:**
- ✅ PR-Titel-Format-Check (Conventional Commits)
- ✅ Breaking-Changes-Erkennung
- ✅ CHANGELOG-Update-Check
- ✅ Automatischer Kommentar bei erfolgreichen Checks

## Environments

### Production
- **Branches:** Nur Tags `v*.*.*`
- **Schutz:** Aktiviert
- **Verwendung:** Automatische Releases

### Staging
- **Branches:** Pull Requests
- **Schutz:** Optional
- **Verwendung:** Pre-Release-Tests

### Development
- **Branches:** Alle Branches
- **Schutz:** Keine
- **Verwendung:** Entwicklungs-Tests

## Einrichtung der Environments

### Über GitHub Web Interface:

1. Gehe zu **Settings** → **Environments**
2. Erstelle folgende Environments:

#### Production Environment
```
Name: production
Deployment branches: Tags matching v*
Protection rules:
  - ✅ Required reviewers: 1 (optional)
  - ✅ Wait timer: 0 minutes
```

#### Staging Environment
```
Name: staging
Deployment branches: All branches
Protection rules: None
```

#### Development Environment
```
Name: development
Deployment branches: All branches
Protection rules: None
```

## Workflow-Status Badges

Füge diese Badges zu deinem README.md hinzu:

```markdown
[![Release](https://github.com/roimme65/gentoo-updater/actions/workflows/release.yml/badge.svg)](https://github.com/roimme65/gentoo-updater/actions/workflows/release.yml)
[![Tests](https://github.com/roimme65/gentoo-updater/actions/workflows/test.yml/badge.svg)](https://github.com/roimme65/gentoo-updater/actions/workflows/test.yml)
```

## Secrets

Aktuell werden nur automatische GitHub-Tokens verwendet:
- `GITHUB_TOKEN` - Automatisch bereitgestellt

**Optional (für zukünftige Features):**
- `EMAIL_TOKEN` - Für E-Mail-Benachrichtigungen
- `DEPLOY_KEY` - Für externe Deployments

## Best Practices

### Release-Prozess:
1. **Entwicklung** auf Feature-Branch
2. **Pull Request** zu `main` → Tests laufen automatisch
3. **Merge** → Tests auf `main`
4. **Tag erstellen** → Automatisches Release
5. **Fertig!** 🎉

### Versionierung:
- Folge [Semantic Versioning](https://semver.org/)
- Format: `vMAJOR.MINOR.PATCH` (z.B. `v1.2.0`)
- Erstelle immer Release-Notes: `releases/v1.2.0.md`

### Commit Messages:
- Nutze [Conventional Commits](https://www.conventionalcommits.org/)
- Format: `type: description`
- Typen: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`

## Troubleshooting

### "Version mismatch" Fehler
- Stelle sicher, dass die Version in `gentoo-updater.py` mit dem Git-Tag übereinstimmt

### "Release notes missing" Fehler
- Erstelle `releases/v{VERSION}.md` vor dem Tag-Push

### Environment nicht gefunden
- Environments müssen in GitHub Settings manuell erstellt werden

## Weitere Informationen

- [GitHub Actions Dokumentation](https://docs.github.com/en/actions)
- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
