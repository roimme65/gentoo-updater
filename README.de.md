# Gentoo System Updater

**Sprachen:** 🇬🇧 [English](README.md) | 🇩🇪 [Deutsch](README.de.md)

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
- 🌐 **Internetverbindungs-Prüfung** (automatisch vor Update-Start)
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

### 🆕 v1.4.0 Erweiterte Parameter
- 🎛️ **--log-level** (DEBUG/INFO/WARNING/ERROR)
- ⏭️ **--skip-*** Optionen (sync, update, eix, cleanup, revdep)
- 🎯 **--only-*** Optionen (nur bestimmte Schritte ausführen)
- 📦 **--max-packages N** (veraltet, ohne Wirkung)
- ⏱️ **--timeout SECONDS** (emerge-Timeout setzen)
- 🔄 **--retry-count N** (Wiederholungen bei Sync-Fehler)
- 🛠️ **--auto-autounmask / --no-auto-autounmask** (automatische Autounmask-Recovery + Retry ein/aus)
- 🔔 **--notification-webhook URL** (Benachrichtigungen)
- ⚙️ **--parallel-jobs N** (Job-Anzahl überschreiben)
- 🌍 **Umgebungsvariablen** (GENTOO_UPDATER_*)

## Voraussetzungen

- Gentoo Linux
- Python 3.6+
- Root/sudo-Rechte
- Optional: `eix` für schnellere Paket-Suche
- Optional: `gentoolkit` für `revdep-rebuild`

## Installation

### Methode 1: Automatische Installation (Empfohlen)

```bash
git clone https://github.com/roimme65/gentoo-updater.git
cd gentoo-updater
sudo python3 install.py
```

### Methode 2: Manuelle Installation

```bash
# Skript herunterladen
git clone https://github.com/roimme65/gentoo-updater.git
cd gentoo-updater

# Ausführbar machen
chmod +x gentoo-updater.py

# Nach /usr/local/bin kopieren (optional)
sudo cp gentoo-updater.py /usr/local/bin/gentoo-updater
```

### Methode 3: PyPI (Kommt in v1.5.x)

```bash
pip install gentoo-updater
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

### Erweiterte Parameter (v1.4.0+)

```bash
# Log-Level setzen
sudo gentoo-updater --log-level DEBUG

# Bestimmte Schritte überspringen
sudo gentoo-updater --skip-cleanup --skip-revdep

# Nur bestimmte Schritte ausführen
sudo gentoo-updater --only-sync      # Nur Repository-Sync
sudo gentoo-updater --only-update    # Nur System-Update

# Timeout je Befehl setzen
sudo gentoo-updater --timeout 3600

# Sync bei Fehler bis zu 3-mal wiederholen
sudo gentoo-updater --retry-count 3

# Job-Anzahl überschreiben
sudo gentoo-updater --parallel-jobs 8

# Webhook-Benachrichtigung (JSON per POST)
sudo gentoo-updater --notification-webhook "https://example.com/webhook"

# Blockierte Pakete automatisch mit Backtracking auflösen
sudo gentoo-updater --resolve-blocks --backtrack 20
```

### Umgebungsvariablen (v1.4.0+)

```bash
# Dry-Run via Umgebungsvariable
GENTOO_UPDATER_DRY_RUN=true sudo gentoo-updater

# Debug-Logging
GENTOO_UPDATER_LOG_LEVEL=DEBUG sudo gentoo-updater

# Timeout setzen
GENTOO_UPDATER_TIMEOUT=3600 sudo gentoo-updater

# Automatisches Retry
GENTOO_UPDATER_RETRY_COUNT=3 sudo gentoo-updater

# Job-Anzahl überschreiben
GENTOO_UPDATER_PARALLEL_JOBS=4 sudo gentoo-updater
# Internetverbindungs-Pr\u00fcfung \u00fcberspringen
GENTOO_UPDATER_SKIP_INTERNET_CHECK=true sudo gentoo-updater

# Blockierte Pakete automatisch aufl\u00f6sen
GENTOO_UPDATER_RESOLVE_BLOCKS=true sudo gentoo-updater

# Backtrack-Stufe setzen
GENTOO_UPDATER_BACKTRACK=25 sudo gentoo-updater```

### Kernel-Module neu kompilieren

Nützlich nach einem manuellen Kernel-Update:

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

## Was macht das Skript?

Das Skript führt folgende Schritte automatisch aus:

1. **Repository-Synchronisation**
   - Liest GENTOO_MIRRORS aus `/etc/portage/make.conf`
   - Zeigt alle konfigurierten Mirrors an
   - Führt `emerge --sync` aus

2. **eix-Update**
   - Führt `eix-update` aus (falls installiert)

3. **Update-Prüfung**
   - Prüft ob Updates verfügbar sind
   - Zeigt eine Liste aller zu aktualisierenden Pakete

4. **System-Update**
   - Führt `emerge @world --update --deep --newuse` aus
   - Warnt vor kritischen Paket-Updates
   - Baut Kernel-Module nur dann neu, wenn Kernel aktualisiert wurde

5. **Cleanup**
   - Führt `emerge --depclean` aus

6. **Dependency-Reparatur**
   - Führt `revdep-rebuild` aus (falls gentoolkit installiert)

7. **Kernel-Prüfung**
   - Zeigt verfügbare Kernel-Versionen
   - Gibt Hinweise für manuelle Kernel-Updates

8. **Konfigurations-Prüfung**
   - Sucht nach ._cfg Dateien
   - Warnt vor ausstehenden Konfigurations-Updates

## Logs & Backups

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

### Update-Zusammenfassung
Nach jedem Update:
- 🌍 Alle konfigurierten Gentoo Mirrors
- 🌍 Primärer Mirror (der erste verfügbare)
- Anzahl aktualisierter Pakete
- Anzahl entfernter Pakete
- Kernel-Update Status
- Modul-Rebuild Status
- Fehler und Warnungen
- Gesamt-Dauer

## 🇩🇪 Deutsche Mirrors & Sicherheit

### Deutsche Mirrors (optional)

Standardmäßig verändert Gentoo-Updater **weder `make.conf` noch `repos.conf`** – die vorhandenen Mirrors werden nur angezeigt.
Mit `--german-mirrors` (oder `GENTOO_UPDATER_GERMAN_MIRRORS=true`) werden die folgenden deutschen/europäischen Mirrors gesetzt:

- Distfiles: `GENTOO_MIRRORS` in `/etc/portage/make.conf` (Sicherung: `make.conf.gentoo-updater.bak`)
- Portage-Tree: eigene Datei `/etc/portage/repos.conf/zz-gentoo-updater.conf` mit `sync-uri = rsync://rsync.de.gentoo.org/gentoo-portage` – nur bei `sync-type = rsync`. Zum Zurücksetzen die Datei löschen.

Eigene Distfile-Mirrors: `--mirrors URL1,URL2` bzw. `GENTOO_UPDATER_MIRRORS`.

**Distfiles (Quellcode):**
| Rang | Server | Ort | Geschwindigkeit |
|------|--------|-----|-----------------|
| 🥇 | RWTH Aachen (ftp.halifax.rwth-aachen.de) | Aachen, Germany | ⚡⚡⚡ Sehr schnell |
| 🥈 | Init7 (mirror.init7.net) | Schweiz | ⚡⚡ Schnell |
| 🥉 | Ruhr-Universität Bochum | Bochum, Germany | ⚡ Stabil |

**Portage-Repository (Rsync):**
- 🔄 Fallback: rsync.gentoo.org (Official)

### verify-sig Security

🔐 **GPG-Signaturverifikation automatisch aktiviert:**

Das Skript aktiviert automatisch das `verify-sig` USE-Flag, was folgende Sicherheit bietet:

```bash
# verify-sig ist in make.conf aktiviert
USE="... verify-sig"

# Bei emerge werden alle Distfiles verprüft:
- Manifests mit OpenPGP-Signaturen
- Alle Pakete gegen Gentoo-Keys validiert
- Manipulation wird sofort erkannt
```

### Code-Sicherheits-Audit

🔍 **Sicherheitsbericht:** [SECURITY_SCAN.md](SECURITY_SCAN.md)

Detailliertes Sicherheits-Audit des gentoo-updater Quellcodes:
- ✅ Keine hardcodierten Geheimnisse oder Anmeldedaten
- ✅ Sichere subprocess-Muster (kein Shell-Injection)
- ✅ Nur Python-Standardbibliothek (keine externen Abhängigkeiten)
- ✅ Umfassende Eingabevalidierung
- ✅ Vollständige Bandit Security-Scanner-Ergebnisse

**In Produktion?** Schaue [SECURITY_SCAN.md](SECURITY_SCAN.md) für Deployment-Empfehlungen an.

**Konfiguration anpassen:**

```bash
# make.conf - Distfiles Mirror
nano /etc/portage/make.conf
GENTOO_MIRRORS="https://ftp.halifax.rwth-aachen.de/gentoo/ https://mirror.init7.net/gentoo/ http://linux.rz.ruhr-uni-bochum.de/download/gentoo-mirror/"

# repos.conf - Portage-Tree Mirror
nano /etc/portage/repos.conf/gentoo.conf
# German Portage Repository Mirrors
# Primary: rsync.de.gentoo.org (German Official Mirror)

[DEFAULT]
main-repo = gentoo

[gentoo]
location = /var/db/repos/gentoo
sync-type = rsync
sync-uri = rsync://rsync.de.gentoo.org/gentoo-portage
priority = 50
```

### mirrorselect Integration

**Automatische interaktive Mirror-Auswahl:**

Mit `--use-mirrorselect` startet Gentoo-Updater die interaktive Auswahl von `mirrorselect` und übernimmt das Ergebnis:

```bash
# Installation (falls nicht vorhanden)
sudo emerge -a app-portage/mirrorselect

# Mirrors interaktiv auswählen und setzen
sudo gentoo-updater --use-mirrorselect
```

**Manuelle Mirror-Auswahl:**

```bash
# Distfiles interaktiv auswählen (ncurses UI)
sudo mirrorselect -i -o

# Rsync-Mirror interaktiv auswählen
sudo mirrorselect -i -r
```

## Fehlerbehebung

### "Das Skript benötigt Root-Rechte"

```bash
sudo gentoo-updater
```

### Manifest-Quarantine Fehler

Das Skript behandelt diese automatisch durch:
1. Löschen des Quarantine-Verzeichnisses
2. Automatisches Retry

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

## FAQ

**F: Warum werden meine Kernel-Module nicht neu gebaut?**

A: Das ist normal und richtig! Module werden neu gebaut nur wenn:
- ✅ Ein Kernel-Update während des System-Updates stattfand, ODER
- ✅ Laufender Kernel ≠ Installierter Kernel (nach manueller Kernel-Kompilierung)

Module werden NICHT neu gebaut wenn:
- ❌ Der Kernel schon für die aktuelle Version kompiliert ist

Warum? Damit das Update schneller geht! (5-10 Minuten schneller)

**F: Wie erzwinge ich ein Module-Rebuild?**

A: Nutze die --rebuild-modules Option:
```bash
sudo gentoo-updater --rebuild-modules
```

**F: Wie schnell ist das Update?**

A: Das hängt vom Update-Umfang ab:
- **Ohne Kernel-Update**: 5-10 Minuten (Module NICHT neu kompiliert)
- **Mit Kernel-Update**: 15-25 Minuten (Module werden neu kompiliert)

**F: Was ist wenn ich den Kernel manuell aktualisiere?**

A: Nach manuellem Kernel-Build:
```bash
eselect kernel set <nummer>
cd /usr/src/linux
make oldconfig && make && make modules_install && make install
grub-mkconfig -o /boot/grub/grub.cfg

# Dann:
sudo gentoo-updater --rebuild-modules
```

Das Skript erkennt den Kernel-Mismatch automatisch.

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

### Schnelles Modul-Rebuild nach manueller Kernel-Update
```bash
# Nach manuellem Kernel-Build:
sudo gentoo-updater --rebuild-modules
sudo reboot
```

### Testen ohne Änderungen
```bash
sudo gentoo-updater --dry-run
```

## Lizenz

MIT License - Siehe LICENSE Datei

## Beiträge

Beiträge sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## Changelog

### Neueste Releases

- [v1.4.37](releases/v1.4.37.md) - Auto-Autounmask-Recovery (2026-02-16) ⭐ **NEUESTE**
- [v1.4.36](releases/v1.4.36.md) - Security-Scan-Dokumentation aktualisiert (2026-02-15)
- [v1.4.35](releases/v1.4.35.md) - Sichtbare Internetverbindungs-Prüfung beim Start (2026-02-15)
- [v1.4.24](releases/v1.4.24.md) - Deutsche Mirrors und verify-sig Integration (2026-02-07)
- [v1.4.0](releases/v1.4.0.md) - Erweiterte CLI-Parameter (2026-02-06)
- [v1.3.3](releases/v1.3.3.md) - Mirror-Logging (2026-02-06)

Für die vollständige Historie siehe [CHANGELOG.md](CHANGELOG.md) und das [releases-Verzeichnis](releases/README.md).

## Siehe auch

- [Gentoo Wiki - Updating Gentoo](https://wiki.gentoo.org/wiki/Handbook:AMD64/Working/Portage#Updating_Gentoo)
- [Gentoo Wiki - eix](https://wiki.gentoo.org/wiki/Eix)
- [Gentoo Wiki - gentoolkit](https://wiki.gentoo.org/wiki/Gentoolkit)
- [GitHub Repository](https://github.com/roimme65/gentoo-updater)
- [Release Notes](https://github.com/roimme65/gentoo-updater/releases)
