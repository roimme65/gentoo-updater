# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [1.0.0] - 2026-01-01

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
