# Sicherheitsrichtlinie

**Sprachen:** 🇬🇧 [English](SECURITY.md) | 🇩🇪 [Deutsch](SECURITY.de.md)

## Unterstützte Versionen

Die folgenden Versionen des Gentoo System Updaters erhalten Sicherheitsupdates:

| Version | Unterstützt        | Status |
| ------- | ------------------ | ------ |
| 2.2.x   | :white_check_mark: | Aktuelle stabile Version (enthält Sicherheitsfixes, siehe [SECURITY_SCAN.md](SECURITY_SCAN.md)) |
| 2.0.x – 2.1.x | :x:          | Bitte auf 2.2.x aktualisieren |
| < 2.0   | :x:                | Lebensende erreicht |

Sicherheitsfixes werden nur für die jeweils neueste Minor-Version veröffentlicht.

## Sicherheitsüberlegungen

### Root-Rechte
Der Gentoo Updater benötigt Root-Rechte (sudo) für System-Updates. Dies ist erforderlich, da `emerge` Systemänderungen vornimmt.

**Empfohlene Sicherheitsmaßnahmen:**
- Überprüfen Sie den Code vor der Ausführung
- Verwenden Sie den `--dry-run` Modus zum Testen
- Prüfen Sie die Log-Dateien regelmäßig
- Verwenden Sie immer die neueste Version

### Cronjobs
Wenn Sie Cronjobs einrichten, werden diese mit Root-Rechten ausgeführt:
- Stellen Sie sicher, dass nur autorisierte Benutzer Cronjobs ändern können
- Logs werden nach `/var/log/` geschrieben
- Überprüfen Sie regelmäßig die ausgeführten Updates
- Kernel-Updates müssen manuell durchgeführt werden
- Konfigurations-Updates erfordern manuelle Zusammenführung

### Datenverarbeitung
- Das Tool speichert keine sensiblen Daten
- Log-Dateien und JSON-Zusammenfassungen in `/var/log/gentoo-updater/` (Verzeichnis `0750` ab v2.2.0)
- Backups von `/etc/portage` und der world-Datei in `/var/backups/gentoo-updater/` (`0700` ab v2.2.0)
- Alle emerge-Operationen werden in Echtzeit angezeigt
- Netzwerkkommunikation:
  - Portage-Sync sowie Download von Distfiles/Binärpaketen (emerge)
  - Internet-Check vor dem Start: TCP-Verbindung zu öffentlichen DNS-Servern / gentoo.org, es werden keine Daten gesendet (abschaltbar mit `--skip-internet-check`)
  - Optionaler Webhook (`--notification-webhook`, nur http/https): Hostname, Status und Zähler
  - Optionale E-Mail über den lokalen `mail`-Befehl (Adresse wird ab v2.2.0 geprüft)

### Systemintegrität
- Das Tool ruft nur Gentoo-Standardwerkzeuge auf (`emerge`, `eix-update`, `revdep-rebuild`, `eselect`, `etc-update`, `mirrorselect`, dazu `find`, `uname`, `mail`); es wird keine Shell verwendet
- Dateien außerhalb von Portage werden nur in diesen Fällen geändert:
  - `make.conf` / `repos.conf/zz-gentoo-updater.conf`: nur mit `--german-mirrors`, `--mirrors` oder `--use-mirrorselect` (Sicherung von `make.conf` wird angelegt)
  - `/etc/portage/package.*`: Autounmask-Recovery (standardmäßig aktiv, abschaltbar mit `--no-auto-autounmask`)
  - Dateien in `/etc`: nur mit `--etc-update-mode auto` (überschreibt eigene Anpassungen)
- Vorgeschlagene `package.use`-Zeilen bei blockierten Paketen werden nur angezeigt, nie geschrieben (ab v2.2.0)
- Konfigurationsdatei: `/etc/gentoo-updater.conf` (empfohlen: Rechte `0600`)
- Automatische Backups vor Updates
- Vollständiges Audit-Logging
- Alle Aktionen werden angezeigt und können überwacht werden
- Exit-Codes ermöglichen Fehlerüberwachung
- Kernel-Updates werden NICHT automatisiert (Sicherheitsfeature)
- Validierung von Umgebungsvariablen (ab v1.4.0)

### Gentoo-spezifische Sicherheit
- **Kernel-Updates**: Werden nur erkannt, niemals automatisch durchgeführt
- **Konfigurations-Updates**: Standardmäßig interaktiv; automatisch nur mit `--etc-update-mode auto`
- **USE-Flag-Änderungen**: Können Neukompilierung auslösen
- **depclean**: Kann in seltenen Fällen wichtige Pakete markieren
- **revdep-rebuild**: Repariert nur kaputte Abhängigkeiten
- **Mirrors**: Werden bei jedem Lauf angezeigt, aber nur auf ausdrücklichen Wunsch geändert (ab v2.0.0)
- **Blockierte Pakete**: Fehlende USE-Flags werden vorgeschlagen, nicht gesetzt (ab v2.2.0)

## Sicherheitslücken melden

Wenn Sie eine Sicherheitslücke im Gentoo System Updater entdecken, melden Sie diese bitte:

### Kontakt
- **GitHub Security Advisories**: Für kritische Sicherheitsprobleme (empfohlen)
- **GitHub Issues**: Nur für nicht-kritische Probleme (nie für ausnutzbare Sicherheitslücken)

Der aktuelle Security-Scan ist in [SECURITY_SCAN.md](SECURITY_SCAN.md) dokumentiert.

### Was Sie erwarten können
1. **Bestätigung**: Innerhalb von 48 Stunden nach Meldung
2. **Bewertung**: Analyse der Schwere und Auswirkung innerhalb von 5 Werktagen
3. **Updates**: Regelmäßige Statusupdates während der Bearbeitung
4. **Fix**: 
   - Kritische Probleme: Patch innerhalb von 7 Tagen
   - Moderate Probleme: Patch im nächsten Release
   - Geringe Probleme: Wird dokumentiert und geplant

### Informationen für Ihre Meldung
Bitte fügen Sie hinzu:
- Beschreibung der Sicherheitslücke
- Schritte zur Reproduktion
- Betroffene Versionen
- Mögliche Auswirkungen
- Vorgeschlagene Lösung (falls vorhanden)
- Gentoo-spezifische Informationen (Profile, USE-Flags, etc.)

### Verantwortungsvolle Offenlegung
Wir bitten um:
- Keine öffentliche Bekanntgabe vor einem Fix
- Zeit für Entwicklung und Testing eines Patches
- Koordinierte Veröffentlichung von Sicherheitsinformationen

Vielen Dank für Ihre Unterstützung bei der Sicherheit dieses Projekts!
