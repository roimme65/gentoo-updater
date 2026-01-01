# Gentoo System Updater

Ein automatisches Update-Skript für Gentoo Linux, das den gesamten Update-Prozess vereinfacht und automatisiert.

## Features

- 🔄 **Repository-Synchronisation** (`emerge --sync`)
- 📚 **eix-Datenbank Update** (falls eix installiert ist)
- 📦 **System-Update** (vollständiges `@world` Update mit deep und newuse)
- 🧹 **Automatisches Cleanup** (`emerge --depclean`)
- 🔧 **Dependency-Reparatur** (`revdep-rebuild`)
- 🐧 **Kernel-Update-Prüfung**
- ⚙️ **Konfigurations-Update-Prüfung** (._cfg Dateien)
- 🎨 **Farbige Ausgabe** mit klarer Struktur
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

### Dry-Run (zeigt was gemacht würde)

```bash
sudo gentoo-updater --dry-run
```

### Ausführliche Ausgabe

```bash
sudo gentoo-updater --verbose
```

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

5. **Cleanup**
   - `emerge --depclean` entfernt nicht mehr benötigte Pakete

6. **Dependency-Reparatur**
   - `revdep-rebuild` repariert kaputte Abhängigkeiten (falls gentoolkit installiert)

7. **Kernel-Prüfung**
   - Zeigt verfügbare Kernel-Versionen an
   - Gibt Hinweise für manuelle Kernel-Updates

8. **Konfigurations-Prüfung**
   - Sucht nach ._cfg Dateien
   - Weist auf notwendige Konfigurations-Updates hin

## Optionen

```
usage: gentoo-updater [-h] [-v] [-n] [--version]

Gentoo System Updater - Automatisiert System-Updates

optional arguments:
  -h, --help     Zeige diese Hilfe
  -v, --verbose  Ausführliche Ausgabe
  -n, --dry-run  Zeige nur was gemacht würde, ohne es auszuführen
  --version      Zeige Version
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

- Kernel-Updates müssen manuell durchgeführt werden
- Konfigurations-Änderungen mit `dispatch-conf` oder `etc-update` prüfen
- Bei wichtigen Updates: System neu starten

## Fehlerbehebung

### "Dieses Skript benötigt Root-Rechte"

```bash
sudo gentoo-updater
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
- **Kernel-Updates** sind manuell (nicht automatisiert)
- **Konfigurations-Updates** erfordern `dispatch-conf` oder `etc-update`
- **Kompilierung** kann lange dauern (abhängig von Hardware und USE-Flags)
- **USE-Flag-Änderungen** können Neukompilierung erfordern

## Lizenz

MIT License - Siehe LICENSE Datei

## Beiträge

Beiträge sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## Autor

Erstellt für Gentoo Linux Benutzer

## Siehe auch

- [Gentoo Wiki - Updating Gentoo](https://wiki.gentoo.org/wiki/Handbook:AMD64/Working/Portage#Updating_Gentoo)
- [Gentoo Wiki - eix](https://wiki.gentoo.org/wiki/Eix)
- [Gentoo Wiki - gentoolkit](https://wiki.gentoo.org/wiki/Gentoolkit)
