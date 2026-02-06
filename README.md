# Gentoo System Updater

Ein automatisches Update-Skript für Gentoo Linux, das den gesamten Update-Prozess vereinfacht und automatisiert.

## Features

### 🚀 Performance & Optimierung
- ⚡ **Parallele Kompilierung** mit automatischer CPU-Erkennung (`--jobs` und `--load-average`)
- 📊 **Intelligente Update-Erkennung** - Kernel-Module nur bei Bedarf neu bauen
- 💾 **Speicherplatz-Prüfung** vor Updates
- 🔄 **Automatisches Retry** bei Manifest-Fehlern

### 📦 Update-Funktionen
- 🔄 **Repository-Synchronisation** (`emerge --sync`)
- 📚 **eix-Datenbank Update** (optional)
- 📦 **System-Update** (vollständiges `@world` Update)
- 🔧 **Intelligente Kernel-Modul-Neucompilierung** (NVIDIA, VirtualBox, etc.)
- 🧹 **Automatisches Cleanup** (`emerge --depclean`)
- 🔧 **Dependency-Reparatur** (`revdep-rebuild`)

### 🛡️ Sicherheit & Zuverlässigkeit
- 💾 **Automatische Backups** wichtiger Konfigurationsdateien
- 🔍 **Blockierte Pakete Prüfung** vor Updates
- ⚠️ **Kritische Paket-Warnung** (gcc, glibc, Python)
- 📝 **Vollständiges Logging-System** mit JSON-Export
- 🎯 **Robuste Fehlerbehandlung** mit detaillierten Logs

### 📊 Monitoring & Reports
- 📈 **Update-Zusammenfassung** mit Statistiken
- 🌍 **Mirror-Logging** - Zeigt alle konfigurierten Gentoo Mirrors & primären Mirror
- 📧 **E-Mail-Benachrichtigungen** (optional)
- 📁 **Automatische Log-Rotation**
- 🎨 **Farbige Ausgabe** mit klarer Struktur

### ⚙️ Konfiguration
- 📄 **JSON-Konfigurationsdatei** für individuelle Anpassungen
- 🔧 **Flexible emerge-Optionen**
- ⚡ **Dry-Run Modus** zum Testen

## Voraussetzungen

- Gentoo Linux
- Python 3.6+
- Root/sudo-Rechte
- Optional: `eix` für schnellere Paket-Suche
- Optional: `gentoolkit` für `revdep-rebuild`

## Installation

### Methode 1: Automatische Installation

```bash
git clone https://github.com/yourusername/gentoo-updater.git
cd gentoo-updater
sudo ./install.sh
```

### Methode 2: Manuelle Installation

```bash
# Skript herunterladen
git clone https://github.com/yourusername/gentoo-updater.git
cd gentoo-updater

# Ausführbar machen
chmod +x gentoo-updater.py

# Nach /usr/local/bin kopieren (optional)
sudo cp gentoo-updater.py /usr/local/bin/gentoo-updater
```

## Verwendung

### Vollständiges System-Update

```bash
sudo gentoo-updater
```

### Konfiguration erstellen

Beim ersten Mal Default-Konfiguration erstellen:

```bash
sudo gentoo-updater --create-config
```

Dies erstellt `/etc/gentoo-updater.conf` mit folgenden Optionen:
- **emerge_jobs**: Anzahl paralleler Jobs (auto = CPU-Kerne)
- **emerge_load_average**: Maximale System-Last
- **enable_backups**: Automatische Backups aktivieren
- **backup_dir**: Verzeichnis für Backups
- **enable_notifications**: E-Mail-Benachrichtigungen
- **notification_email**: E-Mail-Adresse
- **min_free_space_gb**: Mindest-Speicherplatz
- **auto_depclean**: Automatisches depclean
- **auto_revdep_rebuild**: Automatisches revdep-rebuild
- **critical_packages**: Liste kritischer Pakete
- **log_retention_days**: Log-Aufbewahrung in Tagen

Beispiel-Config: siehe [gentoo-updater.conf.example](gentoo-updater.conf.example)

### Dry-Run (zeigt was gemacht würde)

```bash
sudo gentoo-updater --dry-run
```

### Ausführliche Ausgabe

```bash
sudo gentoo-updater --verbose
```

### Kernel-Module neu kompilieren

Nützlich nach einem manuellen Kernel-Update oder wenn Module fehlen:

```bash
sudo gentoo-updater --rebuild-modules
```

Dies baut alle externen Kernel-Module neu:
- NVIDIA-Treiber (`nvidia-drivers`)
- VirtualBox-Module (`virtualbox-modules`)
- ZFS-Module
- Weitere externe Module

### Eigene Konfigurationsdatei verwenden

```bash
sudo gentoo-updater --config /path/to/my-config.conf
```

### Hilfe anzeigen

```bash
gentoo-updater --help
```

## 🤖 Automatische Release-Erstellung (für Entwickler)

Das Projekt verwendet ein vollautomatisches Release-System für schnelle und konsistente Versionierung.

### Vollautomatischer Workflow

```bash
# 1. Normale Änderungen committen
git add -A
git commit -m "improve: Better error handling"
git push

# 2. Release erstellen (vollautomatisch!)
./scripts/create-release.sh patch --auto
```

Das war's! Der Befehl macht **automatisch**:
- ✅ Version erhöhen (patch/minor/major)
- ✅ Release-Notes aus Git-Commits generieren
- ✅ CHANGELOG.md aktualisieren
- ✅ Git-Commit und Tag erstellen
- ✅ Zu GitHub pushen
- ✅ GitHub Release mit Assets erstellen

### Release-Typen

```bash
# Patch Release (1.2.3 → 1.2.4) - Bugfixes
./scripts/create-release.sh patch --auto

# Minor Release (1.2.3 → 1.3.0) - Neue Features
./scripts/create-release.sh minor --auto

# Major Release (1.2.3 → 2.0.0) - Breaking Changes
./scripts/create-release.sh major --auto
```

### Interaktiver Modus (mit Editor)

Wenn du die Release-Notes manuell bearbeiten möchtest:

```bash
# Ohne --auto Flag öffnet sich der Editor
./scripts/create-release.sh patch

# → Editor öffnet sich zum Bearbeiten der Release-Notes
# → Nach dem Speichern: Skript nochmal ausführen
./scripts/create-release.sh patch
```

### Commit-Message Kategorisierung

Das Skript kategorisiert deine Commits automatisch:

- **Features**: `feat:`, `feature:`, `add:`, `✨`, "New Feature"
- **Bugfixes**: `fix:`, `bug:`, `🐛`
- **Improvements**: `improve:`, `enhance:`, `update:`, `🔧`, `⚡`

**Beispiele:**
```bash
git commit -m "feat: Add automatic backup rotation"
git commit -m "fix: Resolve dependency calculation bug"
git commit -m "improve: Better error messages"
git commit -m "🐛 fix: Handle missing config gracefully"
```

### GitHub Actions Integration

Nach dem Push wird automatisch:
- ✓ Python-Syntax validiert
- ✓ Code-Qualität geprüft
- ✓ Release auf GitHub erstellt
- ✓ Assets hochgeladen

**Workflow überwachen:** https://github.com/roimme65/gentoo-updater/actions

### Detaillierte Dokumentation

Mehr Details findest du in:
- [scripts/README.md](scripts/README.md) - Release-Skript Dokumentation
- [.github/WORKFLOWS.md](.github/WORKFLOWS.md) - GitHub Actions Details
- [CHANGELOG.md](CHANGELOG.md) - Vollständige Änderungshistorie

## Was macht das Skript?

Das Skript führt folgende Schritte automatisch aus:

1. **Repository-Synchronisation**
   - Zeigt alle konfigurierten Gentoo Mirrors aus `/etc/portage/make.conf`
   - Loggt primären Mirror in die Log-Datei
   - `emerge --sync` zum Aktualisieren des Portage-Trees

2. **eix-Update**
   - `eix-update` zur Aktualisierung der eix-Datenbank (falls installiert)

3. **Update-Prüfung**
   - Prüft ob Updates verfügbar sind
   - Zeigt eine Liste aller zu aktualisierenden Pakete
create-config] 
                      [--config CONFIG] [--version]

Gentoo System Updater - Automatisiert System-Updates

optional arguments:
  -h, --help            Zeige diese Hilfe
  -v, --verbose         Ausführliche Ausgabe
  -n, --dry-run         Zeige nur was gemacht würde, ohne es auszuführen
  --rebuild-modules     Erzwingt Neucompilierung der Kernel-Module (ohne System-Update)
  --create-config       Erstellt Default-Konfigurationsdatei
  --config CONFIG       Pfad zur Konfigurationsdatei (Standard: /etc/gentoo-updater.conf)
  --version             Zeige Version (aktuell: v1.2.0ect kernel show)
   - **Wird NICHT ausgeführt** wenn Kernel schon aktuell ist!

6. **Cleanup**
   - `emerge --depclean` entfernt nicht mehr benötigte Pakete

7. **Dependency-Reparatur**
   - `revdep-rebuild` repariert kaputte Abhängigkeiten (falls gentoolkit installiert)

8. **Kernel-Prüfung**
   - Zeigt verfügbare Kernel-Versionen an
   - Gibt Hinweise für manuelle Kernel-Updates

9. **Konfigurations-Prüfung**
   - Sucht nach ._cfg Dateien
   - Weist auf notwendige Konfigurations-Updates hin

## Optionen

```
usage: gentoo-updater [-h] [-v] [-n] [--rebuild-modules] [--version]

Gentoo System Updater - Automatisiert System-Updates

optional arguments:
  -h, --help          Zeige diese Hilfe
  -v, --verbose       Ausführliche Ausgabe
  -n, --dry-run       Zeige nur was gemacht würde, ohne es auszuführen
  --rebuild-modules   Erzwingt Neucompilierung der Kernel-Module (ohne System-Update)
  --version           Zeige Version (aktuell: v1.1.2)
```

## Sicherheit

- Das Skript benötigt Root-Rechte (sudo)
- Es prüft automatisch ob es mit entsprechenden Rechten läuft
- Dry-Run Modus ermöglicht sicheres Testen
- Fehler führen zu kontrolliertem Abbruch

## Empfehlungen

### Vor dem ersten Update

```bash
# eix installieren (empfohlen für schnellere Suche)
sudo emerge --ask app-portage/eix

# gentoolkit installieren (für revdep-rebuild)
sudo emerge --ask app-portage/gentoolkit
```

### Regelmäßige Updates

```bash
# Tägliches Update via cron (z.B. nachts)
# /etc/cron.daily/gentoo-updater
#!/bin/bash
/usr/local/bin/gentoo-updater >> /var/log/gentoo-updater.log 2>&1
```

### Nach dem Update

- **Kernel-Updates** müssen manuell kompiliert werden:
  ```bash
  eselect kernel set <nummer>
  cd /usr/src/linux
  make oldconfig && make && make modules_install && make install
  grub-mkconfig -o /boot/grub/grub.cfg
  ```
  **Aber:** Module werden automatisch neu gebaut!
  
- **Konfigurations-Änderungen** mit `dispatch-conf` oder `etc-update` prüfen
- Bei Kernel- oder wichtigen Updates: **System neu starten**
- Nach Neustart mit neuem Kernel laufen die neu kompilierten Module automatisch

## Fehlerbehebung

### "Dieses Skript benötigt Root-Rechte"

```bash
sudo gentoo-updater
``` & Backups

### Logs
Das Skript erstellt automatisch detaillierte Logs:
- Log-Datei: `/var/log/gentoo-updater/update-YYYYMMDD-HHMMSS.log`
- JSON-Summary: `/var/log/gentoo-updater/update-YYYYMMDD-HHMMSS.json`
- Echtzeit-Ausgabe im Terminal
- Automatische Log-Rotation (Standard: 30 Tage)

### Backups
Vor jedem Update werden automatisch gesichert:
- `/etc/portage/make.conf`
- `/etc/portage/package.use`
- `/etc/portage/package.accept_keywords`
- `/var/lib/portage/world`

Backup-Speicherort: `/var/backups/gentoo-updater/YYYYMMDD-HHMMSS/`

### Update-Summary
Nach jedem Update:
- 🌍 Alle konfigurierten Gentoo Mirrors
- 🌍 Primärer Mirror (der erste verfügbare)
- Anzahl aktualisierter Pakete
- Anzahl entfernter Pakete
- Kernel-Update Status
- Modul-Rebuild Status
- Fehler und Warnungen
- Gesamt-Dauerisch durch:
1. Löschen des Quarantine-Verzeichnisses
2. Automatischer Retry des Syncs

Falls es dennoch fehlschlägt:
```bash
sudo rm -rf /var/db/repos/gentoo/.tmp-unverified-download-quarantine
sudo emerge --sync
```

### Kernel-Module fehlen nach Kernel-Update

```bash
sudo gentoo-updater --rebuild-modules
```

### eix nicht gefunden

```bash
sudo emerge --ask app-portage/eix
```

### revdep-rebuild nicht gefunden

```bash
sudo emerge --ask app-portage/gentoolkit
```

## Logs

Das Skript erstellt automatisch Logs:
- Zeitstempel: `/var/log/gentoo-updater-YYYYMMDD-HHMMSS.log`
- Echtzeit-Ausgabe im Terminal

## Unterschiede zu anderen Distributionen

Gentoo erfordert mehr manuelle Schritte als andere Distributionen:
- **Kernel-Kompilierung** ist manuell (nicht automatisiert)
  - ✅ Aber: Kernel-Module werden automatisch neu gebaut!
- **Konfigurations-Updates** erfordern `dispatch-conf` oder `etc-update`
- **Kompilierung** kann lange dauern (abhängig von Hardware und USE-Flags)
- **USE-Flag-Änderungen** können Neukompilierung erfordern

## Häufige Anwendungsfälle

### Komplettes Wochenend-Update
```bash
sudo gentoo-updater
# Warten bis fertig...
# Kernel-Updates und Configs prüfen
# System neu starten
```

### Schnelles Modul-Rebuild nach Kernel-Update
```bash
# Nach manuellem Kernel-Build:
sudo gentoo-updater --rebuild-modules
sudo reboot
```
2.0 (2025-01-27) - 🚀 Große Optimierung
- ⚡ **Performance-Optimierung**: Parallele Kompilierung mit `--jobs` und `--load-average`
- 📄 **Konfigurationssystem**: JSON-basierte Konfigurationsdatei
- 💾 **Automatische Backups**: Wichtige Konfigurationsdateien werden gesichert
- 📝 **Vollständiges Logging**: Detaillierte Logs mit JSON-Export
- 📊 **Update-Zusammenfassung**: Statistiken und Reports nach Updates
- 🔍 **Intelligente Prüfungen**: 
  - Speicherplatz-Check vor Updates
  - Blockierte Pakete Erkennung
  - Kritische Paket-Warnungen (gcc, glibc, Python)
- 📧 **E-Mail-Benachrichtigungen**: Optional nach Update-Abschluss
- 🛡️ **Verbesserte Fehlerbehandlung**: Exception-Logging, finally-Blöcke
- 🔧 **Neue Optionen**: `--create-config`, `--config`
- 📁 **Log-Rotation**: Automatische Bereinigung alter Logs/Backups

### v1.
### Testen ohne Änderungen
```bash
sudo gentoo-updater --dry-run
```

## ❓ FAQ

### F: Warum werden meine Kernel-Module nicht neu gebaut?
**A:** Das ist normal und richtig! Module werden **nur** neu gebaut wenn:
- ✅ Ein Kernel-Update während des System-Updates stattfand, ODER
- ✅ Laufender Kernel ≠ Installierter Kernel (nach manueller Kernel-Kompilierung)

Module werden **NICHT** neu gebaut wenn:
- ❌ Der Kernel schon für die aktuelle Version kompiliert ist

**Warum?** Damit das Update schneller geht! (5-10 Minuten schneller)

### F: Wie erzwinge ich ein Module-Rebuild?
**A:** Nutze die `--rebuild-modules` Option:
```bash
sudo gentoo-updater --rebuild-modules
```

### F: Wie schnell ist das Update?
**A:** Das hängt vom Update-Umfang ab:
- **Ohne Kernel-Update**: 5-10 Minuten (Module NICHT neu kompiliert)
- **Mit Kernel-Update**: 15-25 Minuten (NVIDIA/VirtualBox Module werden neu kompiliert)

### F: Was ist wenn ich den Kernel manuell aktualisiere?
**A:** Nach manuellem Kernel-Build:
```bash
eselect kernel set <nummer>
cd /usr/src/linux
make oldconfig && make && make modules_install && make install
grub-mkconfig -o /boot/grub/grub.cfg

# Dann:
sudo gentoo-updater --rebuild-modules
```

Das Skript erkennt den Kernel-Mismatch automatisch und baut die Module neu.

## Lizenz

MIT License - Siehe LICENSE Datei

## Beiträge

Beiträge sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## Changelog

### v1.3.3 (2026-02-06) - 🌍 Mirror-Logging
- 🌍 **Neue Funktion:** Mirror-Logging
  - Alle Gentoo Mirrors aus `/etc/portage/make.conf` werden angezeigt
  - Primärer Mirror wird im Log festgehalten
  - Mirrors erscheinen in Konsolen-Ausgabe und JSON-Summary
- 📊 Erweiterte Statistics mit Mirror-Informationen
- 📝 Besseres Logging beim Repository-Sync

### v1.1.2 (2025-01-10) - 🔧 Bug Fix
- 🐛 **KRITISCH FIX:** Kernel-Module wurden bei jedem Update neu gebaut
  - Lösung: Nur bei echtem Kernel-Mismatch neu bauen
  - Effekt: 5-10 Minuten schneller bei Updates ohne Kernel-Change
- 🔧 Optimierte Kernel-Versions-Prüfung mit besserer String-Verarbeitung
- 📚 Dokumentation erweitert mit FAQ-Sektion

### v1.1.0 (2025-01-10)
- ✨ Automatische Kernel-Modul-Neucompilierung
- ✨ Neue Option: `--rebuild-modules`
- 🛡️ Automatisches Manifest-Quarantine-Cleanup
- 🔄 Retry-Mechanismus bei Sync-Fehlern
- 📊 Intelligente Erkennung von Kernel-Updates

### v1.0.0 (2025-01-01)
- 🎉 Initiales Release
- Basis Update-Funktionalität

## Autor

Erstellt für Gentoo Linux Benutzer

## Siehe auch

- [Gentoo Wiki - Updating Gentoo](https://wiki.gentoo.org/wiki/Handbook:AMD64/Working/Portage#Updating_Gentoo)
- [Gentoo Wiki - eix](https://wiki.gentoo.org/wiki/Eix)
- [Gentoo Wiki - gentoolkit](https://wiki.gentoo.org/wiki/Gentoolkit)
