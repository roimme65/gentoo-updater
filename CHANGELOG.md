## v1.4.44 (2026-04-10)
- Release

## v1.4.43 (2026-04-10)
- Release

## v1.4.42 (2026-02-28)
- Release

## v1.4.41 (2026-02-21)
- Release

## v1.4.40 (2026-02-21)

- Neu: **--resolve-blocks** Parameter f\u00fcr automatische Aufl\u00f6sung blockierter Pakete
- Neu: **--backtrack N** Parameter zur Kontrolle der Backtrack-Stufe (Standard: 20)
- Neu: Umgebungsvariablen `GENTOO_UPDATER_RESOLVE_BLOCKS` und `GENTOO_UPDATER_BACKTRACK`
- Verbesserung: Verbesserte `check_blocked_packages()` Funktion mit auto-resolve Logik
- Verbesserung: emerge-Befehl nutzt --backtrack bei blockierten Paketen automatisch
- Doku: README und README.de aktualisiert mit neuen Parametern
## v1.4.39 (2026-02-16)
- Release

## v1.4.38 (2026-02-16)
- Release

## Unreleased (2026-02-16)
- Neu: CLI-Toggle `--auto-autounmask` / `--no-auto-autounmask` hinzugefügt
- Neu: Automatische Recovery bei Portage-Autounmask-Fehlern (`--autounmask-write` + Config-Merge + emerge-Retry)
- Doku: README und README.de um kurzen Hinweis zum neuen Toggle ergänzt

## v1.4.36 (2026-02-15)
- Release

## v1.4.35 (2026-02-15)
- Release

## v1.4.34 (2026-02-15)
- Release

## v1.4.33 (2026-02-15)
- Release

## v1.4.32 (2026-02-15)
- Release

## v1.4.31 (2026-02-08)
- Release

## v1.4.30 (2026-02-08)
- Release

## v1.4.29 (2026-02-08)
- Release

## v1.4.28 (2026-02-08)
- Release

## v1.4.27 (2026-02-08)
- Release

## v1.4.26 (2026-02-08)
- Release

## v1.4.25 (2026-02-07)
- Release

## v1.4.24 (2026-02-07)
- Release

## v1.4.23 (2026-02-07)
- Release

## v1.4.22 (2026-02-07)
- Release

## v1.4.21 (2026-02-07)
- Release

## v1.4.20 (2026-02-07)
- Release

## v1.4.19 (2026-02-07)
- Release

## v1.4.18 (2026-02-07)
- Release

## v1.4.17 (2026-02-07)
- Release

## v1.4.16 (2026-02-07)
- Release

## v1.4.15 (2026-02-07)
- Release

## v1.4.14 (2026-02-07)
- Release

## v1.4.13 (2026-02-07)
- Release

## v1.4.12 (2026-02-07)
- Release

## v1.4.11 (2026-02-07)
- Release

## v1.4.10 (2026-02-07)
- Release

## v1.4.9 (2026-02-07)
- Release

## v1.4.8 (2026-02-07)
- Release

## v1.4.7 (2026-02-07)
- Release

## v1.4.6 (2026-02-07)
- Release

## v1.4.5 (2026-02-07)
- Release

## [1.4.4] - 2026-02-07

### Siehe
- Detaillierte Release-Notes: [releases/v1.4.4.md](releases/v1.4.4.md)

---

## [1.4.3] - 2026-02-07

### Siehe
- Detaillierte Release-Notes: [releases/v1.4.3.md](releases/v1.4.3.md)

---

## [1.4.1] - 2026-02-07

### Siehe
- Detaillierte Release-Notes: [releases/v1.4.1.md](releases/v1.4.1.md)

---

## [1.3.4] - 2026-02-06

### Siehe
- Detaillierte Release-Notes: [releases/v1.3.4.md](releases/v1.3.4.md)

---

## [1.3.3] - 2026-02-06

### Siehe
- Detaillierte Release-Notes: [releases/v1.3.3.md](releases/v1.3.3.md)

---

## [1.3.2] - 2026-01-31

### Siehe
- Detaillierte Release-Notes: [releases/v1.3.2.md](releases/v1.3.2.md)

---

## [1.3.1] - 2026-01-29

### Siehe
- Detaillierte Release-Notes: [releases/v1.3.1.md](releases/v1.3.1.md)

---

## [1.3.0] - 2026-01-27

### Siehe
- Detaillierte Release-Notes: [releases/v1.3.0.md](releases/v1.3.0.md)

---

## [1.2.4] - 2026-01-27

### Siehe
- Detaillierte Release-Notes: [releases/v1.2.4.md](releases/v1.2.4.md)

---

## [1.2.3] - 2026-01-27

### Siehe
- Detaillierte Release-Notes: [releases/v1.2.3.md](releases/v1.2.3.md)

---

# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [1.2.2] - 2026-01-27

### Siehe
- Detaillierte Release-Notes: [releases/v1.2.2.md](releases/v1.2.2.md)

---

## [1.2.0] - 2025-01-27

### Hinzugefügt
- ⚡ **Performance-Optimierung**: Parallele Kompilierung mit automatischer CPU-Erkennung
  - `--jobs` und `--load-average` werden automatisch gesetzt
  - Konfigurierbar über Config-Datei
  - Bis zu 50% schnellere Updates bei Multi-Core-Systemen
- 📄 **Konfigurationssystem**: JSON-basierte Konfigurationsdatei
  - Neue Option `--create-config` erstellt `/etc/gentoo-updater.conf`
  - Neue Option `--config` für eigene Konfigurationsdatei
  - Alle wichtigen Parameter konfigurierbar
  - Beispiel-Config: `gentoo-updater.conf.example`
- 💾 **Automatisches Backup-System**
  - Sichert wichtige Konfigurationsdateien vor jedem Update
  - Backup-Location: `/var/backups/gentoo-updater/`
  - Automatische Bereinigung alter Backups
- 📝 **Vollständiges Logging-System**
  - Strukturierte Logs: `/var/log/gentoo-updater/update-YYYYMMDD-HHMMSS.log`
  - JSON-Export für maschinelle Verarbeitung
  - Automatische Log-Rotation
  - Exception-Logging mit Stack-Traces
- 📊 **Update-Zusammenfassung**
  - Detaillierte Statistiken nach jedem Update
  - Anzahl aktualisierter/entfernter Pakete
  - Kernel- und Modul-Status
  - Fehler- und Warnungs-Übersicht
- 🔍 **Intelligente Prüfungen**
  - Speicherplatz-Check vor Updates (konfigurierbar)
  - Blockierte-Pakete-Erkennung vor Updates
  - Kritische-Pakete-Warnungen (gcc, glibc, Python)
- 📧 **E-Mail-Benachrichtigungen** (optional)
  - Benachrichtigung nach Update-Abschluss
  - Status-Meldung und Zusammenfassung
  - Konfigurierbar über Config-Datei

### Verbessert
- 🔧 `run_command()` gibt jetzt auch Output zurück
- 🔧 Besseres Exception-Handling mit vollständigem Logging
- 🔧 Strukturierte Fehler- und Warnungs-Sammlung
- 🔧 `check_updates()` gibt pretend-Output zurück
- 🔧 `update_system()` nutzt Performance-Optionen
- 🔧 Alle Methoden integriert mit Logging-System
- 🔧 Finally-Blöcke für garantierte Zusammenfassung

### Intern
- 🏗️ Neue Klasse `Config` für Konfigurationsverwaltung
- 🏗️ Erweiterte Imports: `json`, `re`, `pathlib`, `logging`
- 🏗️ Stats-Dictionary für Update-Statistiken
- 🏗️ Neue Hilfsmethoden:
  - `setup_logging()`
  - `check_disk_space()`
  - `backup_important_files()`
  - `cleanup_old_backups()`
  - `check_blocked_packages()`
  - `detect_critical_updates()`
  - `extract_package_list()`
  - `print_summary()`
  - `save_summary_json()`
  - `send_notification()`
- 🏗️ Type Hints verbessert (`Tuple` statt `tuple`)
- 🏗️ Version auf v1.2.0 erhöht

---

## [1.1.2] - 2025-01-10

### Behoben
- 🐛 **KRITISCH: Kernel-Mismatch-Erkennung war fehlerhaft**
  - Problem: eselect kernel show Output falsch geparst
  - Lösung: Robustere String-Parsing-Logik
  - Effekt: Kernel-Mismatch wird jetzt korrekt erkannt

---

## [1.1.1] - 2025-01-10

### Behoben
- 🐛 **KRITISCH: Kernel-Module wurden bei jedem Update neu gebaut**
  - Problem: `check_kernel_module_mismatch()` nutzte zu aggressive Prüfung
  - Lösung: Nur Kernel-Version-Mismatch als Kriterium (uname -r vs eselect kernel show)
  - Effekt: Module werden NICHT mehr unnötig bei jedem Update neu kompiliert
- 🔧 **Optimierte Kernel-Versions-Prüfung**
  - Bereinigt eselect Output korrekt
  - Zuverlässigere Kernel-Versions-Erkennung
  - Bessere String-Vergleiche

### Versionsangabe
- Version: v1.1.1 (Patch-Release)

---

## [1.1.0] - 2025-01-10

### Hinzugefügt
- ✨ **Automatische Kernel-Modul-Neucompilierung**
  - Erkennt Kernel-Updates während des System-Updates automatisch
  - Baut externe Module (NVIDIA, VirtualBox, ZFS, etc.) automatisch neu mit `@module-rebuild`
  - Neue Methode `check_kernel_module_mismatch()` prüft auch nachträglich auf veraltete Module
  - Vergleicht laufenden Kernel mit installiertem Kernel
- 🛡️ **Robuste Fehlerbehandlung für Manifest-Fehler**
  - Neue Methode `cleanup_manifest_quarantine()` räumt beschädigte Dateien auf
  - Automatischer Retry-Mechanismus bei Repository-Sync-Fehlern
  - Löst das häufige "Manifest verification failed" Problem automatisch
- 🎯 **Neue Command-Line Option: `--rebuild-modules`**
  - Ermöglicht isolierte Neucompilierung von Kernel-Modulen
  - Nützlich nach manuellen Kernel-Updates
  - Separate Funktion `run_modules_only()` für schnellen Modul-Rebuild
- 🔄 **Intelligente Update-Erkennung**
  - Analysiert `emerge --pretend` Output auf Kernel-Updates
  - Gibt Warnungen bei erkannten Kernel-Updates aus

### Geändert
- 🔧 `sync_repositories()` unterstützt jetzt Retry-Parameter
- 🔧 `update_system()` gibt jetzt Tuple zurück: `(success, kernel_updated)`
- 🔧 `rebuild_kernel_modules()` unterstützt `force`-Parameter
- 📊 Schrittnummerierung angepasst (jetzt 9 Schritte statt 8)
- 📚 Versionsnummer auf v1.1.0 erhöht

### Imports
- Hinzugefügt: `shutil` (für Verzeichnis-Operationen)
- Hinzugefügt: `time` (für Retry-Delays)

### Dokumentation
- 📝 README.md umfassend aktualisiert mit neuen Features
- 📝 Neue Beispiele für `--rebuild-modules` Option
- 📝 Fehlerbehebungs-Sektion erweitert
- 📝 Häufige Anwendungsfälle hinzugefügt

### Technische Details
- Python 3.6+ Kompatibilität beibehalten
- Type Hints für `update_system()` Return-Wert: `tuple[bool, bool]`
- Robustere Fehlerbehandlung mit `allow_fail=True` bei kritischen Operationen

### Verwendung
```bash
# Vollständiges Update (inkl. automatischem Modul-Rebuild)
sudo gentoo-updater

# Nur Kernel-Module neu bauen (nach manuellem Kernel-Update)
sudo gentoo-updater --rebuild-modules

# Test-Modus
sudo gentoo-updater --dry-run
```

### Vorteile
- ✅ Kein manuelles `emerge @module-rebuild` mehr nach Kernel-Updates
- ✅ Automatische Erkennung veralteter NVIDIA/VirtualBox-Module
- ✅ Zuverlässigerer Sync durch Manifest-Error-Handling
- ✅ Flexiblere Verwendung durch `--rebuild-modules` Option

---

## [1.0.0] - 2025-01-01

### Hinzugefügt
- 🚀 **Initiales Release des Gentoo System Updaters**
- ✨ Python-basierter Auto-Updater mit detaillierter Statusanzeige
- 📊 Echtzeit-Fortschrittsanzeige mit ANSI-Farbcodierung
- 🔄 Kompletter Update-Zyklus:
  - `emerge --sync` - Repository-Synchronisation
  - `eix-update` - eix-Datenbank aktualisieren (falls installiert)
  - `emerge --update --deep --newuse @world` - System-Update
  - `emerge --depclean` - Unnötige Pakete entfernen
  - `revdep-rebuild` - Abhängigkeiten reparieren (falls gentoolkit installiert)
- 🐧 Kernel-Update-Prüfung mit manuellen Anweisungen
- ⚙️ Konfigurations-Update-Prüfung (._cfg Dateien)
- 🧪 Dry-Run Modus zum Testen ohne Systemänderungen
- 🔒 Root-Rechte-Prüfung
- 📥 **Installations-Script** (`install.py`):
  - Automatische Installation und Einrichtung
  - Symlink-Erstellung nach `/usr/local/bin`
  - Prüfung optionaler Abhängigkeiten (eix, gentoolkit)
  - Optionale Installation empfohlener Pakete
  - Lokale Versionsverwaltung mit `--bump {major|minor|patch}`
- 📖 Vollständige Dokumentation mit Beispielen
- 🎯 Kompatibilität mit Gentoo Linux

### Technische Details
- Python 3.6+ kompatibel
- Nur Standard-Bibliotheken (keine externen Abhängigkeiten)
- Exit-Codes für Automatisierung
- Saubere Fehlerbehandlung
- STRG+C Interrupt-Unterstützung

### Verwendung
```bash
# Installation
sudo python3 install.py

# Version lokal aktualisieren
python3 install.py --bump patch

# Vollständiges Update
sudo gentoo-updater

# Test-Modus
sudo gentoo-updater --dry-run

# Ausführliche Ausgabe
sudo gentoo-updater --verbose
```

### Lizenz
- MIT License hinzugefügt
- Open Source und frei verwendbar

[1.0.0]: https://github.com/roimme65/gentoo-updater/releases/tag/v1.0.0
