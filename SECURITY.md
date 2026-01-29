# Security Policy

## Supported Versions

Die folgenden Versionen des Gentoo System Updaters werden mit Sicherheitsupdates unterstützt:

| Version | Unterstützt        | Status |
| ------- | ------------------ | ------ |
| 1.2.x   | :white_check_mark: | Aktuelle stabile Version |
| 1.1.x   | :white_check_mark: | Unterstützt bis 30.06.2026 |
| 1.0.x   | :x:                | Nicht mehr unterstützt |
| < 1.0   | :x:                | Entwicklungsversionen |

## Sicherheitsüberlegungen

### Root-Rechte
Der Gentoo Updater benötigt Root-Rechte (sudo) für System-Updates. Dies ist erforderlich, da `emerge` Systemänderungen vornimmt.

**Empfohlene Sicherheitsmaßnahmen:**
- Überprüfen Sie den Code vor der Ausführung
- Verwenden Sie den `--dry-run` Modus zum Testen
- Prüfen Sie die Log-Dateien regelmäßig
- Verwenden Sie die neueste Version

### Cronjobs
Wenn Sie Cronjobs einrichten, werden diese mit Root-Rechten ausgeführt:
- Stellen Sie sicher, dass nur autorisierte Benutzer Cronjobs ändern können
- Logs werden nach `/var/log/` geschrieben
- Überprüfen Sie regelmäßig die ausgeführten Updates
- Kernel-Updates müssen manuell durchgeführt werden
- Konfigurations-Updates erfordern manuelle Zusammenführung

### Datenverarbeitung
- Das Tool speichert keine sensiblen Daten
- Log-Dateien enthalten Paketinformationen und Systemausgaben (ab v1.2.0)
- JSON-Export von Update-Statistiken (ab v1.2.0, keine sensiblen Daten)
- Automatische Backups von Konfigurationsdateien (ab v1.2.0)
- Keine Netzwerkkommunikation außer Portage-Repositories
- Alle emerge-Operationen werden in Echtzeit angezeigt
- E-Mail-Benachrichtigungen optional (ab v1.2.0)

### Systemintegrität
- Das Tool führt nur offizielle emerge-Befehle aus
- Keine Modifikation von Systemdateien außerhalb des Portage-Sys
- Konfigurationsdatei-Support (ab v1.2.0): `/etc/gentoo-updater.conf`
- Automatische Backups vor Updates (ab v1.2.0)
- Vollständiges Audit-Logging (ab v1.2.0)tems
- Alle Aktionen werden angezeigt und können überwacht werden
- Exit-Codes ermöglichen Fehlerüberwachung
- Kernel-Updates werden NICHT automatisiert (Sicherheitsfeature)

### Gentoo-spezifische Sicherheit
- **Kernel-Updates**: Werden nur geprüft, niemals automatisch durchgeführt
- **Konfigurations-Updates**: Werden erkannt, aber nicht automatisch angewendet
- **USE-Flag-Änderungen**: Können Neukompilierung auslösen
- **depclean**: Kann in seltenen Fällen wichtige Pakete markieren
- **revdep-rebuild**: Repariert nur kaputte Abhängigkeiten

## Reporting a Vulnerability

Wenn Sie eine Sicherheitslücke im Gentoo System Updater entdecken, melden Sie diese bitte:

### Kontakt
- **GitHub Issues**: https://github.com/roimme65/gentoo-updater/issues (für nicht-kritische Probleme)
- **GitHub Security Advisories**: Für kritische Sicherheitsprobleme (empfohlen)

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
