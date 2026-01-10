# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

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
- 📥 **Installations-Script** (`install.sh`):
  - Automatische Installation und Einrichtung
  - Symlink-Erstellung nach `/usr/local/bin`
  - Prüfung optionaler Abhängigkeiten (eix, gentoolkit)
  - Optionale Installation empfohlener Pakete
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
sudo ./install.sh

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
