# Gentoo System Updater

Ein automatisches Update-Skript für Gentoo Linux, das den gesamten Update-Prozess vereinfacht und automatisiert.

## Features

- 🔄 **Repository-Synchronisation** (`emerge --sync`) mit automatischem Retry bei Manifest-Fehlern
- 📚 **eix-Datenbank Update** (falls eix installiert ist)
- 📦 **System-Update** (vollständiges `@world` Update mit deep und newuse)
- 🔧 **Automatische Kernel-Modul-Neucompilierung** (NVIDIA, VirtualBox, etc.)
  - Erkennt Kernel-Updates automatisch
  - Baut externe Module neu mit `@module-rebuild`
  - Prüft auch nachträglich auf veraltete Module
- 🧹 **Automatisches Cleanup** (`emerge --depclean`)
- 🔧 **Dependency-Reparatur** (`revdep-rebuild`)
- 🐧 **Kernel-Update-Prüfung**
- ⚙️ **Konfigurations-Update-Prüfung** (._cfg Dateien)
- 🎨 **Farbige Ausgabe** mit klarer Struktur
- ⚡ **Dry-Run Modus** zum Testen
- 🛡️ **Robuste Fehlerbehandlung** mit Quarantine-Cleanup

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

### Hilfe anzeigen

```bash
gentoo-updater --help
```

## Was macht das Skript?

Das Skript führt folgende Schritte automatisch aus:

1. **Repository-Synchronisation**
   - `emerge --sync` zum Aktualisieren des Portage-Trees

2. **eix-Update**
   - `eix-update` zur Aktualisierung der eix-Datenbank (falls installiert)

3. **Update-Prüfung**
   - Prüft ob Updates verfügbar sind
   - Zeigt eine Liste aller zu aktualisierenden Pakete

4. **System-Update**
   - `emerge --update --deep --newuse --with-bdeps=y @world`
   - Aktualisiert alle installierten Pakete
   - Erkennt automatisch Kernel-Updates

5. **Kernel-Module neu kompilieren** (nur bei Kernel-Update oder veralteten Modulen)
   - `emerge @module-rebuild`
   - Baut NVIDIA, VirtualBox und andere externe Module neu
   - Prüft Kernel-Version-Mismatch

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
  --version           Zeige Version (aktuell: v1.1.0)
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
```

### "Manifest verification failed"

Das Skript behebt dies automatisch durch:
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

### Testen ohne Änderungen
```bash
sudo gentoo-updater --dry-run
```

## Lizenz

MIT License - Siehe LICENSE Datei

## Beiträge

Beiträge sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## Changelog

### v1.1.0 (2025-01-10)
- ✨ Automatische Kernel-Modul-Neucompilierung
- ✨ Neue Option: `--rebuild-modules`
- 🔧 Automatisches Manifest-Quarantine-Cleanup
- 🔧 Retry-Mechanismus bei Sync-Fehlern
- 📊 Intelligente Erkennung von Kernel-Updates
- 📊 Prüfung auf veraltete Module auch ohne Update

### v1.0.0 (2025-01-01)
- 🎉 Initiales Release
- Basis Update-Funktionalität

## Autor

Erstellt für Gentoo Linux Benutzer

## Siehe auch

- [Gentoo Wiki - Updating Gentoo](https://wiki.gentoo.org/wiki/Handbook:AMD64/Working/Portage#Updating_Gentoo)
- [Gentoo Wiki - eix](https://wiki.gentoo.org/wiki/Eix)
- [Gentoo Wiki - gentoolkit](https://wiki.gentoo.org/wiki/Gentoolkit)
