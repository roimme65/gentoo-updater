#!/usr/bin/env python3
"""
Gentoo System Updater
Automatisches Update-Skript für Gentoo Linux
"""

__version__ = "1.4.38"
__author__ = "Roland Imme"
__license__ = "MIT"

import subprocess
import sys
import os
import argparse
import shutil
import time
import json
import re
import locale
import socket
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import logging


# ========================
# Internationalisierung (i18n)
# ========================

def detect_system_language() -> str:
    """Detektiert die Systemsprache aus den Locale-Einstellungen"""
    try:
        system_locale = locale.getlocale()[0]
        if system_locale and system_locale.startswith('de'):
            return 'de'
    except:
        pass
    return 'en'


CURRENT_LANGUAGE = detect_system_language()

# ========================
# Emoji-Support Erkennung
# ========================

def detect_emoji_support() -> bool:
    """Prüft ob das Terminal Emojis unterstützt"""
    try:
        # Schreibe ein Emoji und lese es zurück
        import subprocess
        result = subprocess.run(
            ['printf', '🇩🇪'],
            capture_output=True,
            text=True
        )
        # Wenn das Emoji korrekt ausgegeben wird, unterstützt das Terminal Emojis
        return len(result.stdout) > 0
    except:
        # Im Fehlerfall vorsichtig sein und ASCII verwenden
        return False

SUPPORTS_EMOJI = detect_emoji_support()

# Emoji-Symbole mit ASCII-Fallbacks
SYMBOLS = {
    'germany': ('🇩🇪', '[DE]') if SUPPORTS_EMOJI else ('[DE]', '[DE]'),
    'checkmark': ('✓', '[OK]') if SUPPORTS_EMOJI else ('[OK]', '[OK]'),
    'warning': ('⚠', '[WARN]') if SUPPORTS_EMOJI else ('[WARN]', '[WARN]'),
    'error': ('✗', '[ERR]') if SUPPORTS_EMOJI else ('[ERR]', '[ERR]'),
    'info': ('ℹ', '[INFO]') if SUPPORTS_EMOJI else ('[INFO]', '[INFO]'),
    'fast': ('🥇', '[#1]') if SUPPORTS_EMOJI else ('[#1]', '[#1]'),
    'clock': ('⏱', '[TIME]') if SUPPORTS_EMOJI else ('[TIME]', '[TIME]'),
    'sync': ('🔄', '[SYNC]') if SUPPORTS_EMOJI else ('[SYNC]', '[SYNC]'),
    'package': ('📦', '[PKG]') if SUPPORTS_EMOJI else ('[PKG]', '[PKG]'),
    'skip': ('⏭', '[SKIP]') if SUPPORTS_EMOJI else ('[SKIP]', '[SKIP]'),
}

def symbol(key: str) -> str:
    """Gibt das richtige Symbol zurück (Emoji oder ASCII)"""
    if SUPPORTS_EMOJI:
        return SYMBOLS[key][0]
    else:
        return SYMBOLS[key][1]

TRANSLATIONS = {
    'ROOT_ERROR': {
        'de': 'Dieses Skript benötigt Root-Rechte.',
        'en': 'This script requires root privileges.'
    },
    'ROOT_INFO': {
        'de': 'Bitte mit sudo ausführen: sudo gentoo-updater',
        'en': 'Please run with sudo: sudo gentoo-updater'
    },
    'INTERNET_CHECK_ERROR': {
        'de': 'Keine Internetverbindung verfügbar!',
        'en': 'No internet connection available!'
    },
    'INTERNET_CHECK_INFO': {
        'de': 'Dieses Skript benötigt eine aktive Internetverbindung für Repository-Synchronisation und Paket-Downloads.',
        'en': 'This script requires an active internet connection for repository synchronization and package downloads.'
    },
    'DISK_SPACE_INFO': {
        'de': 'Freier Speicherplatz: {free_gb:.2f} GB',
        'en': 'Free disk space: {free_gb:.2f} GB'
    },
    'DISK_SPACE_ERROR': {
        'de': 'Nicht genug Speicherplatz! Mindestens {min_space} GB erforderlich.',
        'en': 'Not enough disk space! At least {min_space} GB required.'
    },
    'BACKUP_SUCCESS': {
        'de': 'Backup erstellt: {path}',
        'en': 'Backup created: {path}'
    },
    'BACKUP_FAILED': {
        'de': 'Backup fehlgeschlagen: {error}',
        'en': 'Backup failed: {error}'
    },
    'OLD_BACKUP_DELETED': {
        'de': 'Altes Backup gelöscht: {name}',
        'en': 'Old backup deleted: {name}'
    },
    'BLOCKED_PACKAGES_FOUND': {
        'de': 'Blockierte Pakete gefunden!',
        'en': 'Blocked packages found!'
    },
    'BLOCKED_INFO': {
        'de': 'Bitte lösen Sie die Blockierungen manuell auf.',
        'en': 'Please resolve the blocking packages manually.'
    },
    'CRITICAL_PACKAGES_WARNING': {
        'de': 'ACHTUNG: Kritische Pakete werden aktualisiert!',
        'en': 'WARNING: Critical packages will be updated!'
    },
    'CRITICAL_UPDATES_REQUIRED': {
        'de': 'Diese Updates können System-Neustarts oder Rebuilds erfordern.',
        'en': 'These updates may require system restarts or rebuilds.'
    },
    'EIX_NOT_INSTALLED': {
        'de': 'eix ist nicht installiert, überspringe...',
        'en': 'eix is not installed, skipping...'
    },
    'NO_UPDATES': {
        'de': 'Keine Updates verfügbar - System ist aktuell!',
        'en': 'No updates available - system is up to date!'
    },
    'UPDATES_AVAILABLE': {
        'de': 'Updates verfügbar:',
        'en': 'Updates available:'
    },
    'SYSTEM_UPDATE_FAILED': {
        'de': 'System-Update fehlgeschlagen',
        'en': 'System update failed'
    },
    'KERNEL_UPDATE_DETECTED': {
        'de': 'Kernel-Update erkannt! Module werden nach dem Update neu gebaut.',
        'en': 'Kernel update detected! Modules will be rebuilt after the update.'
    },
    'CHECK_KERNEL_MODULES': {
        'de': 'Prüfe Kernel-Module Status...',
        'en': 'Checking kernel module status...'
    },
    'MODULES_STATUS': {
        'de': 'Laufender Kernel ({running}) != Installierter Kernel ({installed})',
        'en': 'Running kernel ({running}) != installed kernel ({installed})'
    },
    'NO_EXTERNAL_MODULES': {
        'de': 'Keine externen Kernel-Module gefunden (oder bereits aktuell)',
        'en': 'No external kernel modules found (or already up to date)'
    },
    'MODULES_REBUILD_SUCCESS': {
        'de': 'Alle Kernel-Module erfolgreich neu gebaut',
        'en': 'All kernel modules successfully rebuilt'
    },
    'MODULES_REBUILD_TIP': {
        'de': 'Tipp: Nach einem Neustart werden die neuen Module verwendet',
        'en': 'Tip: The new modules will be used after a restart'
    },
    'DEPCLEAN_SKIPPED': {
        'de': 'Depclean übersprungen (in Config deaktiviert)',
        'en': 'Depclean skipped (disabled in config)'
    },
    'REVDEP_SKIPPED': {
        'de': 'revdep-rebuild übersprungen (in Config deaktiviert)',
        'en': 'revdep-rebuild skipped (disabled in config)'
    },
    'CONFIG_UPDATES_FOUND': {
        'de': 'Konfigurations-Updates gefunden!',
        'en': 'Configuration updates found!'
    },
    'CONFIG_NO_UPDATES': {
        'de': 'Keine Konfigurations-Updates ausstehend',
        'en': 'No configuration updates pending'
    },
    'UPDATE_INTERRUPTED': {
        'de': 'Update durch Benutzer abgebrochen',
        'en': 'Update interrupted by user'
    },
    'UNEXPECTED_ERROR': {
        'de': 'Unerwarteter Fehler: {error}',
        'en': 'Unexpected error: {error}'
    },
    'REVDEP_NOT_FOUND': {
        'de': 'revdep-rebuild nicht gefunden (gentoolkit installieren?)',
        'en': 'revdep-rebuild not found (install gentoolkit?)'
    },
    'CONFIG_CHECK_FAILED': {
        'de': 'Konfigurations-Prüfung fehlgeschlagen: {error}',
        'en': 'Configuration check failed: {error}'
    },
    'KERNEL_CHECK_FAILED': {
        'de': 'Kernel-Prüfung fehlgeschlagen: {error}',
        'en': 'Kernel check failed: {error}'
    },
    'KERNEL_LIST_INFO': {
        'de': 'Kernel-Updates müssen manuell durchgeführt werden!',
        'en': 'Kernel updates must be performed manually!'
    },
    'KERNEL_UPDATE_STEPS': {
        'de': 'Schritte für Kernel-Update:',
        'en': 'Steps for kernel update:'
    },
    'CONFIG_LOAD_WARNING': {
        'de': '[WARNING] Konnte Config nicht laden: {error}',
        'en': '[WARNING] Could not load config: {error}'
    },
    'CONFIG_SAVE_SUCCESS': {
        'de': '[SUCCESS] Default-Konfiguration gespeichert: {path}',
        'en': '[SUCCESS] Default configuration saved: {path}'
    },
    'CONFIG_SAVE_ERROR': {
        'de': '[ERROR] Konnte Config nicht speichern: {error}',
        'en': '[ERROR] Could not save config: {error}'
    },
    'SYNC_MIRROR_INFO': {
        'de': 'Konfigurierte Gentoo Mirrors:',
        'en': 'Configured Gentoo Mirrors:'
    },
    'SYNC_PRIMARY_MIRROR': {
        'de': 'Primärer Mirror: {mirror}',
        'en': 'Primary mirror: {mirror}'
    },
    'NO_MIRRORS': {
        'de': 'Keine Gentoo Mirrors konfiguriert!',
        'en': 'No Gentoo mirrors configured!'
    },
    'COMMAND_NOT_FOUND': {
        'de': 'Befehl nicht gefunden: {cmd}',
        'en': 'Command not found: {cmd}'
    },
    'RUN_COMMAND_ERROR': {
        'de': 'Fehler bei {desc}: {error}',
        'en': 'Error in {desc}: {error}'
    },
    'DRY_RUN_MSG': {
        'de': 'DRY-RUN: Würde ausführen: {cmd}',
        'en': 'DRY-RUN: Would execute: {cmd}'
    },
    'COMMAND_EXEC_TIMEOUT': {
        'de': '⏱️  Timeout: {timeout} Sekunden',
        'en': '⏱️  Timeout: {timeout} seconds'
    },
    'RETRY_COUNT_MSG': {
        'de': '🔄 Retry-Count: {count}',
        'en': '🔄 Retry-Count: {count}'
    },
    'MAX_PACKAGES_MSG': {
        'de': '📦 Max Packages: {max}',
        'en': '📦 Max Packages: {max}'
    },
    'UPDATE_SKIPPED': {
        'de': '⏭️  Überspringe Repository-Synchronisation (--skip-sync)',
        'en': '⏭️  Skipping repository synchronisation (--skip-sync)'
    },
    'EIX_SKIPPED': {
        'de': '⏭️  Überspringe eix Update (--skip-eix)',
        'en': '⏭️  Skipping eix update (--skip-eix)'
    },
    'SYNC_FAILED': {
        'de': 'Repository-Synchronisation fehlgeschlagen nach 2 Versuchen',
        'en': 'Repository synchronisation failed after 2 attempts'
    },
    'MODULES_CURRENT': {
        'de': 'Kernel-Module sind aktuell - keine Neucompilierung nötig',
        'en': 'Kernel modules are up to date - no rebuild needed'
    },
    'MODULES_MANUAL_CHECK': {
        'de': 'Bitte Kernel-Updates und Konfigurations-Änderungen manuell prüfen',
        'en': 'Please check kernel updates and configuration changes manually'
    },
    'NOTIFICATION_SENT': {
        'de': 'Benachrichtigung gesendet an {email}',
        'en': 'Notification sent to {email}'
    },
    'NOTIFICATION_ERROR': {
        'de': 'Konnte Benachrichtigung nicht senden: {error}',
        'en': 'Could not send notification: {error}'
    },
    'SUMMARY_TITLE': {
        'de': 'UPDATE-ZUSAMMENFASSUNG',
        'en': 'UPDATE SUMMARY'
    },
    'DISK_CHECK_FAILED': {
        'de': 'Konnte Speicherplatz nicht prüfen: {error}',
        'en': 'Could not check disk space: {error}'
    },
    'QUARANTINE_CLEANUP': {
        'de': 'Räume auf: {path}',
        'en': 'Cleaning up: {path}'
    },
    'QUARANTINE_DELETED': {
        'de': 'Quarantine-Verzeichnis gelöscht',
        'en': 'Quarantine directory deleted'
    },
    'MANIFEST_FILE_NOT_FOUND': {
        'de': 'make.conf nicht gefunden: {path}',
        'en': 'make.conf not found: {path}'
    },
    'SYNC_RETRY': {
        'de': 'Sync fehlgeschlagen - räume auf und versuche erneut...',
        'en': 'Sync failed - cleaning up and retrying...'
    },
    'MODULE_ANALYSIS': {
        'de': 'Analysiere zu aktualisierende Pakete...',
        'en': 'Analyzing packages to update...'
    },
    'MODULES_AFTER_UPDATE': {
        'de': 'Module müssen für den neuen Kernel neu gebaut werden',
        'en': 'Modules need to be rebuilt for the new kernel'
    },
    'MODULES_CURRENT_KERNEL': {
        'de': 'Laufender Kernel ist aktuell - Module müssen nicht neu gebaut werden',
        'en': 'Running kernel is up to date - modules do not need to be rebuilt'
    },
    'PERFORMANCE_INFO': {
        'de': 'Performance: {jobs} parallele Jobs, Load Average: {load}',
        'en': 'Performance: {jobs} parallel jobs, Load Average: {load}'
    },
    'PACKAGE_LIMIT': {
        'de': 'Anzahl zu aktualisierender Pakete auf {max} begrenzt',
        'en': 'Limiting packages to update to {max}'
    },
    'MIRRORSELECT_AVAILABLE': {
        'de': '✓ mirrorselect für deutsche Mirror-Auswahl verfügbar',
        'en': '✓ mirrorselect for German mirror selection available'
    },
    'MIRRORSELECT_NOT_INSTALLED': {
        'de': '⚠ mirrorselect ist nicht installiert',
        'en': '⚠ mirrorselect is not installed'
    },
    'MIRRORSELECT_INSTALL_TIP': {
        'de': '  Tipp: sudo emerge -a app-portage/mirrorselect',
        'en': '  Tip: sudo emerge -a app-portage/mirrorselect'
    },
    'MIRRORSELECT_BENEFIT': {
        'de': '  Dies ermöglicht automatische Auswahl des schnellsten deutschen Mirrors',
        'en': '  This enables automatic selection of the fastest German mirrors'
    },
}


def _(key: str, **kwargs) -> str:
    """
    Übersetzungs-Helper Funktion (Gettext-ähnlich)
    
    Args:
        key: Übersetzungs-Key im TRANSLATIONS Dictionary
        **kwargs: Platzhalter für Format-Strings
        
    Returns:
        Übersetzter Text in CURRENT_LANGUAGE oder 'en' fallback
    """
    if key not in TRANSLATIONS:
        return key  # Rückfall auf Key selbst wenn nicht gefunden
    
    translation = TRANSLATIONS[key].get(CURRENT_LANGUAGE, TRANSLATIONS[key].get('en', key))
    
    # Format-String mit kwargs ersetzen
    if kwargs:
        try:
            return translation.format(**kwargs)
        except KeyError as e:
            return f"[TRANSLATION_ERROR: {key} missing parameter {e}]"
    
    return translation


# ========================
# Hilfe-Texte für Parameter (Deutsch/Englisch)
# ========================

HELP_TEXTS = {
    'verbose': {
        'de': 'Ausführliche Ausgabe',
        'en': 'Verbose output'
    },
    'dry_run': {
        'de': 'Zeige nur was gemacht würde, ohne es auszuführen',
        'en': 'Show what would be done without actually performing the update'
    },
    'rebuild_modules': {
        'de': 'Erzwingt Neucompilierung der Kernel-Module',
        'en': 'Force rebuild of kernel modules'
    },
    'create_config': {
        'de': 'Erstellt Default-Konfigurationsdatei',
        'en': 'Create a default configuration file'
    },
    'config': {
        'de': 'Pfad zur Konfigurationsdatei',
        'en': 'Path to the configuration file'
    },
    'log_level': {
        'de': 'Logging-Stufe (Standard: INFO)',
        'en': 'Logging level (default: INFO)'
    },
    'skip_sync': {
        'de': 'Überspringe Repository-Synchronisation',
        'en': 'Skip repository synchronisation'
    },
    'skip_update': {
        'de': 'Überspringe System-Update (@world)',
        'en': 'Skip system update (@world)'
    },
    'skip_eix': {
        'de': 'Überspringe eix-Datenbank-Update',
        'en': 'Skip eix database update'
    },
    'skip_cleanup': {
        'de': 'Überspringe depclean',
        'en': 'Skip depclean'
    },
    'skip_revdep': {
        'de': 'Überspringe revdep-rebuild',
        'en': 'Skip revdep-rebuild'
    },
    'skip_internet_check': {
        'de': 'Überspringe Internetverbindungs-Prüfung (nützlich für Offline-Tests)',
        'en': 'Skip internet connection check (useful for offline tests)'
    },
    'only_sync': {
        'de': 'Führe nur Repository-Synchronisation durch',
        'en': 'Execute only repository synchronisation'
    },
    'only_update': {
        'de': 'Führe nur System-Update (@world) durch',
        'en': 'Execute only system update (@world)'
    },
    'only_cleanup': {
        'de': 'Führe nur depclean durch',
        'en': 'Execute only depclean'
    },
    'max_packages': {
        'de': 'Begrenze Anzahl der zu aktualisierenden Pakete',
        'en': 'Limit number of packages to update'
    },
    'timeout': {
        'de': 'Timeout in Sekunden für emerge-Operationen',
        'en': 'Timeout in seconds for emerge operations'
    },
    'retry_count': {
        'de': 'Anzahl der Wiederholungsversuche bei Fehler (Standard: 1)',
        'en': 'Number of retries on failure (default: 1)'
    },
    'notification_webhook': {
        'de': 'Sende Abschluss-Benachrichtigung an Webhook-URL',
        'en': 'Send completion notification to webhook URL'
    },
    'parallel_jobs': {
        'de': 'Überschreibe emerge --jobs Einstellung',
        'en': 'Override emerge --jobs setting'
    },
    'lang': {
        'de': 'Sprache (de/en, Standard: automatische Erkennung aus System-Locale)',
        'en': 'Language (de/en, default: auto-detect from system locale)'
    },
    'mirrors': {
        'de': 'Benutzerdefinierte Gentoo Mirrors (durch Komma getrennt)',
        'en': 'Custom Gentoo mirrors (comma-separated URLs)'
    },
    'use_mirrorselect': {
        'de': 'Nutze mirrorselect für automatische Auswahl des schnellsten Mirrors',
        'en': 'Use mirrorselect for automatic selection of fastest mirror'
    },
    'etc_update_mode': {
        'de': 'Modus für Konfigurationsdateien-Updates (Standard: interaktiv)',
        'en': 'Mode for configuration file updates (default: interactive)'
    },
    'auto_autounmask': {
        'de': 'Aktiviere automatische Portage-Autounmask-Recovery (--autounmask-write + Config-Merge + Retry)',
        'en': 'Enable automatic Portage autounmask recovery (--autounmask-write + config merge + retry)'
    },
    'repository': {
        'de': 'Zeige GitHub-Repository-Informationen',
        'en': 'Show GitHub repository information'
    },
    'support': {
        'de': 'Zeige Support- und Issue-Template-Links',
        'en': 'Show support and issue template links'
    },
    'author': {
        'de': 'Zeige Autor- und Versions-Informationen',
        'en': 'Show author and version information'
    },
    'license': {
        'de': 'Zeige Lizenz-Informationen',
        'en': 'Show license information'
    }
}


def get_help_text(key: str) -> str:
    """
    Gibt Hilfe-Text basierend auf aktueller Sprache zurück
    
    Args:
        key: Key im HELP_TEXTS Dictionary
        
    Returns:
        Hilfe-Text in CURRENT_LANGUAGE oder Englisch als Fallback
    """
    if key not in HELP_TEXTS:
        return key
    return HELP_TEXTS[key].get(CURRENT_LANGUAGE, HELP_TEXTS[key].get('en', key))


# ========================
# GitHub Integration
# ========================

GITHUB_REPO = 'https://github.com/imme-php/gentoo-updater'
GITHUB_ISSUES = 'https://github.com/imme-php/gentoo-updater/issues'
GITHUB_DISCUSSIONS = 'https://github.com/imme-php/gentoo-updater/discussions'
GITHUB_ISSUE_TEMPLATE_BUG = 'https://github.com/imme-php/gentoo-updater/issues/new?template=bug_report.md'
GITHUB_ISSUE_TEMPLATE_FEATURE = 'https://github.com/imme-php/gentoo-updater/issues/new?template=feature_request.md'

# ========================
# German Mirrors (Default)
# ========================

# Deutsche und europäische Gentoo Mirrors - DISTFILES (Quellcode-Downloads)
# Nach Geschwindigkeit/Zuverlässigkeit sortiert (RWTH Aachen ist bei Geschwindigkeit #1)
DEFAULT_GERMAN_MIRRORS_DISTFILES = [
    'https://ftp.halifax.rwth-aachen.de/gentoo/',           # 🥇 RWTH Aachen - sehr schnell
    'https://mirror.init7.net/gentoo/',                      # Init7 - Schweiz
    'http://linux.rz.ruhr-uni-bochum.de/download/gentoo-mirror/', # Ruhr-Uni Bochum
]

# Deutsche und europäische Gentoo Mirrors - RSYNC (Portage-Tree Sync)
# Für emaint sync -a oder emerge --sync
# Nach Geschwindigkeit/Zuverlässigkeit sortiert
DEFAULT_GERMAN_MIRRORS_RSYNC = [
    'rsync://rsync.de.gentoo.org/gentoo-portage',           # 🇩🇪 Deutschland (Offiziell)
    'rsync://ftp.halifax.rwth-aachen.de/gentoo-portage',    # 🥇 RWTH Aachen - sehr schnell
    'rsync://mirror.init7.net/gentoo-portage',              # 🇨🇭 Init7 - Schweiz
    'rsync://rsync.gentoo.org/gentoo-portage',              # Official Gentoo - Fallback
]

# Unified list (für Kompatibilität und einfache Verwendung - hauptsächlich Distfiles)
DEFAULT_GERMAN_MIRRORS = DEFAULT_GERMAN_MIRRORS_DISTFILES

CUSTOM_MIRRORS = None  # Will be set from CLI arguments or env vars


class Colors:
    """ANSI Farb-Codes für Terminal-Ausgabe"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def check_internet_connection() -> bool:
    """
    Prüft ob eine Internetverbindung verfügbar ist.
    Versucht DNS-Lookups für mehrere bekannte Server.
    
    Returns:
        bool: True wenn Internetverbindung verfügbar ist, False sonst
    """
    # Mehrere Hosts zum Testen
    test_hosts = [
        ('8.8.8.8', 53),           # Google DNS
        ('1.1.1.1', 53),           # Cloudflare DNS
        ('9.9.9.9', 53),           # Quad9 DNS
        ('gentoo.org', 80),        # Gentoo.org HTTP
    ]
    
    for host, port in test_hosts:
        try:
            # Versucht Verbindung zu öffnen (Timeout: 3 Sekunden)
            socket.create_connection((host, port), timeout=3)
            return True
        except (socket.timeout, socket.error, OSError):
            # Host nicht erreichbar, versuche nächsten
            continue
    
    # Kein Host war erreichbar
    return False


def translate(key: str, **kwargs) -> str:
    """Übersetzt einen Text basierend auf der Systemsprache"""
    try:
        text = TRANSLATIONS[key].get(CURRENT_LANGUAGE, TRANSLATIONS[key].get('en', ''))
        if kwargs:
            return text.format(**kwargs)
        return text
    except (KeyError, ValueError):
        return f"[TRANSLATION MISSING: {key}]"


class Config:
    """Konfigurationsverwaltung für den Updater"""
    
    DEFAULT_CONFIG = {
        'emerge_jobs': 'auto',  # auto = CPU-Kerne, oder z.B. '4'
        'emerge_load_average': 'auto',  # auto = CPU-Kerne, oder z.B. '4.0'
        'enable_backups': True,
        'backup_dir': '/var/backups/gentoo-updater',
        'enable_notifications': False,
        'notification_email': '',
        'min_free_space_gb': 5,
        'auto_depclean': True,
        'auto_revdep_rebuild': True,
        'critical_packages': ['sys-devel/gcc', 'sys-libs/glibc', 'dev-lang/python'],
        'log_retention_days': 30
    }
    
    def __init__(self, config_file: str = '/etc/gentoo-updater.conf'):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Lädt Konfiguration aus Datei oder verwendet Defaults"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge mit Defaults
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(user_config)
                    return config
            except Exception as e:
                print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {_('CONFIG_LOAD_WARNING', error=e)}")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save_default_config(self):
        """Speichert Default-Konfiguration in Datei"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2)
            print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {_('CONFIG_SAVE_SUCCESS', path=self.config_file)}")
        except Exception as e:
            print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {_('CONFIG_SAVE_ERROR', error=e)}")
    
    def get(self, key: str, default=None):
        """Gibt Konfigurationswert zurück"""
        return self.config.get(key, default)
    
    def get_emerge_jobs(self) -> int:
        """Berechnet optimale Job-Anzahl"""
        jobs = self.config['emerge_jobs']
        if jobs == 'auto':
            return os.cpu_count() or 1
        return int(jobs)
    
    def get_load_average(self) -> float:
        """Berechnet optimale Load Average"""
        load = self.config['emerge_load_average']
        if load == 'auto':
            return float(os.cpu_count() or 1)
        return float(load)


class GentooUpdater:
    """Hauptklasse für Gentoo System-Updates"""
    
    def __init__(self, verbose: bool = False, dry_run: bool = False, 
                 rebuild_modules: bool = False, config: Optional[Config] = None,
                 log_level: str = 'INFO', timeout: Optional[int] = None,
                 retry_count: int = 1, webhook_url: Optional[str] = None,
                 max_packages: Optional[int] = None, custom_mirrors: Optional[List[str]] = None,
                 etc_update_mode: str = 'interactive', auto_autounmask: bool = True):
        self.verbose = verbose
        self.dry_run = dry_run
        self.rebuild_modules = rebuild_modules
        self.config = config or Config()
        self.log_level = log_level
        self.timeout = timeout
        self.retry_count = retry_count
        self.webhook_url = webhook_url
        self.max_packages = max_packages
        self.custom_mirrors = custom_mirrors
        self.etc_update_mode = etc_update_mode  # interactive, auto, oder skip
        self.auto_autounmask = auto_autounmask
        
        # Skip-Flags (werden von main() gesetzt)
        self.skip_sync = False
        self.skip_update = False
        self.skip_eix = False
        self.skip_cleanup = False
        self.skip_revdep = False
        
        # Logging einrichten
        self.log_dir = Path('/var/log/gentoo-updater')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"update-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        
        self.setup_logging()
        
        # Statistiken für Summary
        self.stats = {
            'packages_updated': [],
            'packages_removed': [],
            'kernel_updated': False,
            'modules_rebuilt': False,
            'errors': [],
            'warnings': [],
            'gentoo_mirrors': [],
            'used_mirror': None,
            'retry_count': self.retry_count,
            'timeout': self.timeout,
            'max_packages': self.max_packages
        }
    
    def setup_logging(self):
        """Konfiguriert das Logging-System"""
        # Log-Level konvertieren
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        level = level_map.get(self.log_level, logging.INFO)
        
        # Verbose überschreibt log_level
        if self.verbose:
            level = logging.DEBUG
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('gentoo-updater')
        self.logger.info("=" * 70)
        self.logger.info("Gentoo Updater gestartet")
        self.logger.info(f"Log-Datei: {self.log_file}")
        self.logger.info("=" * 70)
        
    def print_section(self, message: str):
        """Gibt einen formatierten Abschnitts-Header aus"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")
        self.logger.info(message)
        
    def print_info(self, message: str):
        """Gibt eine Info-Nachricht aus"""
        print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {message}")
        self.logger.info(message)
        
    def print_success(self, message: str):
        """Gibt eine Erfolgs-Nachricht aus"""
        print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {message}")
        self.logger.info(f"SUCCESS: {message}")
        
    def print_warning(self, message: str):
        """Gibt eine Warn-Nachricht aus"""
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {message}")
        self.logger.warning(message)
        self.stats['warnings'].append(message)
        
    def print_error(self, message: str):
        """Gibt eine Fehler-Nachricht aus"""
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {message}")
        self.logger.error(message)
        self.stats['errors'].append(message)
        
    def check_root_privileges(self):
        """Prüft, ob das Skript mit Root-Rechten läuft"""
        if os.geteuid() != 0:
            self.print_error(_('ROOT_ERROR'))
            self.print_info(_('ROOT_INFO'))
            sys.exit(1)
    
    def check_disk_space(self) -> bool:
        """Prüft ob genügend Festplattenspeicher verfügbar ist"""
        min_space_gb = self.config.get('min_free_space_gb', 5)
        
        try:
            stat = shutil.disk_usage('/usr')
            free_gb = stat.free / (1024**3)
            
            self.print_info(_('DISK_SPACE_INFO', free_gb=free_gb))
            
            if free_gb < min_space_gb:
                self.print_error(_('DISK_SPACE_ERROR', min_space=min_space_gb))
                return False
            return True
        except Exception as e:
            self.print_warning(_('DISK_CHECK_FAILED', error=e))
            return True
    
    def backup_important_files(self):
        """Erstellt Backup wichtiger Konfigurationsdateien"""
        if not self.config.get('enable_backups', True):
            return
        
        backup_dir = Path(self.config.get('backup_dir', '/var/backups/gentoo-updater'))
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_path = backup_dir / timestamp
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Wichtige Dateien sichern
            important_files = [
                '/etc/portage/make.conf',
                '/etc/portage/package.use',
                '/etc/portage/package.accept_keywords',
                '/var/lib/portage/world'
            ]
            
            for file_path in important_files:
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        shutil.copytree(file_path, backup_path / Path(file_path).name, 
                                       dirs_exist_ok=True)
                    else:
                        shutil.copy2(file_path, backup_path)
            
            self.print_success(_('BACKUP_SUCCESS', path=backup_path))
            self.cleanup_old_backups(backup_dir)
            
        except Exception as e:
            self.print_warning(_('BACKUP_FAILED', error=e))
    
    def cleanup_old_backups(self, backup_dir: Path):
        """Löscht alte Backups"""
        retention_days = self.config.get('log_retention_days', 30)
        cutoff_time = time.time() - (retention_days * 86400)
        
        try:
            for item in backup_dir.iterdir():
                if item.is_dir() and item.stat().st_mtime < cutoff_time:
                    shutil.rmtree(item)
                    self.print_info(_('OLD_BACKUP_DELETED', name=item.name))
        except Exception as e:
            self.print_warning(f"Konnte alte Backups nicht löschen: {e}")
    
    def check_blocked_packages(self) -> bool:
        """Prüft auf blockierte Pakete"""
        self.print_info("Prüfe auf blockierte Pakete...")
        
        try:
            result = subprocess.run(
                ["emerge", "--update", "--deep", "--newuse", "--pretend", "@world"],
                capture_output=True,
                text=True
            )
            
            if "blocked by" in result.stdout.lower() or "blocking" in result.stdout.lower():
                self.print_error(_('BLOCKED_PACKAGES_FOUND'))
                print(result.stdout)
                self.print_info(_('BLOCKED_INFO'))
                return False
            return True
        except Exception as e:
            self.print_warning(f"Konnte Blockierungen nicht prüfen: {e}")
            return True
    
    def detect_critical_updates(self, pretend_output: str) -> List[str]:
        """Erkennt kritische Paket-Updates"""
        critical_packages = self.config.get('critical_packages', [])
        found_critical = []
        
        for pkg in critical_packages:
            if pkg in pretend_output:
                found_critical.append(pkg)
        
        if found_critical:
            self.print_warning(_('CRITICAL_PACKAGES_WARNING'))
            for pkg in found_critical:
                self.print_warning(f"  - {pkg}")
            self.print_info(_('CRITICAL_UPDATES_REQUIRED'))
        
        return found_critical
    
    def cleanup_manifest_quarantine(self):
        """Räumt beschädigte Manifest-Dateien auf"""
        quarantine_dir = "/var/db/repos/gentoo/.tmp-unverified-download-quarantine"
        
        if os.path.exists(quarantine_dir):
            self.print_info(_('QUARANTINE_CLEANUP', path=quarantine_dir))
            try:
                shutil.rmtree(quarantine_dir)
                self.print_success(_('QUARANTINE_DELETED'))
            except Exception as e:
                self.print_warning(f"Konnte Quarantine nicht löschen: {str(e)}")
    
    def get_gentoo_mirrors(self) -> List[str]:
        """Liest die GENTOO_MIRRORS aus /etc/portage/make.conf
        
        Returns:
            Liste der konfigurierten Mirrors
        """
        mirrors = []
        make_conf_path = '/etc/portage/make.conf'
        
        if not os.path.exists(make_conf_path):
            self.print_warning(_('MANIFEST_FILE_NOT_FOUND', path=make_conf_path))
            return mirrors
        
        try:
            with open(make_conf_path, 'r') as f:
                content = f.read()
            
            # Suche nach GENTOO_MIRRORS Variable
            # Berücksichtigt mehrzeilige Definitionen mit Backslash
            import re
            pattern = r'GENTOO_MIRRORS\s*=\s*"([^"]+)"'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            
            if match:
                mirrors_str = match.group(1)
                # Entferne Backslashes und extra Whitespace
                mirrors_str = mirrors_str.replace('\\', ' ').replace('\n', ' ')
                # Teile nach Whitespace und filtere leere Strings
                mirrors = [m.strip() for m in mirrors_str.split() if m.strip()]
                self.stats['gentoo_mirrors'] = mirrors
            else:
                self.print_warning("GENTOO_MIRRORS nicht in make.conf gefunden")
        
        except Exception as e:
            self.print_warning(f"Fehler beim Lesen der Mirrors aus make.conf: {e}")
        
        return mirrors
    
    def auto_select_best_mirror_distfiles(self) -> Optional[List[str]]:
        """Nutzt mirrorselect um die schnellsten deutschen Distfile-Mirror automatisch zu wählen
        
        Befehl: mirrorselect -i -o
        Öffnet eine ncurses-UI zur interaktiven Auswahl deutscher Distfile-Mirror
        
        Returns:
            Liste der schnellsten Mirror URLs oder None wenn mirrorselect nicht verfügbar
        """
        self.print_info("Öffne mirrorselect zur Auswahl deutscher Distfile-Mirror...")
        self.print_info("(Leertaste zum Auswählen, Enter zum Bestätigen)")
        
        try:
            # Prüfe ob mirrorselect installiert ist
            which_result = subprocess.run(
                ["which", "mirrorselect"],
                capture_output=True,
                timeout=5
            )
            
            if which_result.returncode != 0:
                self.print_info("mirrorselect nicht verfügbar - verwende Standard-Mirror")
                return None
            
            # Führe mirrorselect für Distfiles aus: -i (interaktiv), -o (output)
            # Dies öffnet eine ncurses-Liste zur Auswahl deutscher Distfile-Mirror
            result = subprocess.run(
                ["mirrorselect", "-i", "-o"],  # -i = interaktiv mit UI, -o = output format
                timeout=120  # Mehr Zeit für interaktive Auswahl durch Benutzer
            )
            
            if result.returncode == 0:
                # Lese die aktualisierte make.conf
                make_conf_path = '/etc/portage/make.conf'
                if os.path.exists(make_conf_path):
                    with open(make_conf_path, 'r') as f:
                        content = f.read()
                    # Extrahiere GENTOO_MIRRORS
                    pattern = r'GENTOO_MIRRORS\s*=\s*"([^"]+)"'
                    match = re.search(pattern, content)
                    if match:
                        mirrors_str = match.group(1)
                        mirror_urls = [m.strip() for m in mirrors_str.split() if m.strip()]
                        if mirror_urls:
                            self.print_success(f"Mirror ausgewählt: {', '.join(mirror_urls[:2])}...")
                            return mirror_urls
                
            else:
                if result.returncode == 130:  # Ctrl+C
                    self.print_info("Mirror-Auswahl abgebrochen")
                else:
                    self.print_warning(f"mirrorselect fehlgeschlagen (Code: {result.returncode})")
                
        except subprocess.TimeoutExpired:
            self.print_warning("mirrorselect Timeout - verwende Standard-Mirror")
        except Exception as e:
            self.print_warning(f"Fehler bei mirrorselect: {e}")
        
        return None
    
    def auto_select_best_mirror_rsync(self) -> Optional[str]:
        """Nutzt mirrorselect um den schnellsten deutschen Rsync-Mirror automatisch zu wählen
        
        Befehl: mirrorselect -i -r
        Öffnet eine ncurses-UI zur interaktiven Auswahl eines Rsync-Mirror
        
        Returns:
            Schnellster Rsync-Mirror URL oder None wenn mirrorselect nicht verfügbar
        """
        self.print_info("Öffne mirrorselect zur Auswahl des deutschen Rsync-Mirror...")
        self.print_info("(Leertaste zum Auswählen, Enter zum Bestätigen)")
        
        try:
            # Prüfe ob mirrorselect installiert ist
            which_result = subprocess.run(
                ["which", "mirrorselect"],
                capture_output=True,
                timeout=5
            )
            
            if which_result.returncode != 0:
                return None
            
            # Führe mirrorselect für Rsync aus: -i (interaktiv), -r (rsync only)
            result = subprocess.run(
                ["mirrorselect", "-i", "-r"],  # -i = interaktiv, -r = rsync only
                timeout=120
            )
            
            if result.returncode == 0:
                # Lese die aktualisierte make.conf für sync-uri
                repos_conf_path = '/etc/portage/repos.conf/gentoo.conf'
                if os.path.exists(repos_conf_path):
                    with open(repos_conf_path, 'r') as f:
                        content = f.read()
                    # Extrahiere sync-uri
                    match = re.search(r'sync-uri\s*=\s*([^\n]+)', content)
                    if match:
                        mirror_url = match.group(1).strip()
                        if mirror_url:
                            self.print_success(f"Rsync-Mirror ausgewählt: {mirror_url}")
                            return mirror_url
            
            elif result.returncode == 130:  # Ctrl+C
                self.print_info("Rsync-Mirror-Auswahl abgebrochen")
            
        except subprocess.TimeoutExpired:
            self.print_warning("mirrorselect Rsync-Auswahl Timeout")
        except Exception as e:
            self.print_warning(f"Fehler bei mirrorselect Rsync-Auswahl: {e}")
        
        return None
    
    def configure_rsync_mirrors(self):
        """Konfiguriert die deutschen RSYNC Mirror in repos.conf/gentoo.conf
        
        Setzt rsync.de.gentoo.org als primären Mirror mit deutschen Fallbacks
        """
        repos_conf_path = '/etc/portage/repos.conf/gentoo.conf'
        
        if not os.path.exists(repos_conf_path):
            self.print_warning(f"repos.conf nicht gefunden: {repos_conf_path}")
            return
        
        try:
            with open(repos_conf_path, 'r') as f:
                repos_conf_content = f.read()
            
            # Extrahiere aktuellen sync-uri
            current_sync = None
            pattern = r'sync-uri\s*=\s*([^\n]+)'
            match = re.search(pattern, repos_conf_content)
            if match:
                current_sync = match.group(1).strip()
            
            # Baue neue Fallback-Liste (nur primär Mirror, rsync.de.gentoo.org)
            # Portage übernimmt automatisch Fallbacks aus repos.conf wenn dieser Mirror ausfällt
            primary_rsync_mirror = 'rsync://rsync.de.gentoo.org/gentoo-portage'
            
            # Ersetze sync-uri mit deutschem Primary Mirror
            if 'sync-uri' in repos_conf_content:
                # Ersetze existierende sync-uri
                updated_content = re.sub(
                    r'sync-uri\s*=\s*[^\n]+',
                    f'sync-uri = {primary_rsync_mirror}',
                    repos_conf_content
                )
            else:
                # Füge neue Zeile am Ende des [gentoo] Block hinzu
                updated_content = repos_conf_content.rstrip() + f'\nsync-uri = {primary_rsync_mirror}\n'
            
            if updated_content != repos_conf_content:
                # Schreibe mit besseren Fehlerbehandlung
                try:
                    with open(repos_conf_path, 'w') as f:
                        f.write(updated_content)
                    self.print_success(f"repos.conf aktualisiert mit deutschem RSYNC Mirror (rsync.de.gentoo.org)")
                    self.logger.info(f"Primärer RSYNC Mirror: {primary_rsync_mirror}")
                    if current_sync:
                        self.logger.info(f"Alter Mirror: {current_sync}")
                except PermissionError as pe:
                    self.print_warning(f"Keine Berechtigung, repos.conf zu schreiben (Root erforderlich): {pe}")
                except IOError as ie:
                    self.print_warning(f"IO-Fehler beim Schreiben von repos.conf: {ie}")
            else:
                self.logger.info(f"repos.conf ist bereits mit deutschem Mirror konfiguriert")
        
        except PermissionError as pe:
            self.print_warning(f"Keine Berechtigung, repos.conf zu lesen: {pe}")
        except Exception as e:
            self.print_warning(f"Fehler bei repos.conf-Konfiguration: {e}")
            self.logger.exception("Exception Details:")
    
    def log_mirrors_info(self):
        """Loggt die tatsächlich verwendeten Gentoo Mirrors"""
        # Zeige Distfiles Mirror
        self.print_info(_('SYNC_MIRROR_INFO'))
        
        # Prüfe ob custom_mirrors oder defaults verwendet werden
        if self.custom_mirrors and self.custom_mirrors == DEFAULT_GERMAN_MIRRORS_DISTFILES:
            self.print_success(f"{symbol('germany')} Verwende deutsche Gentoo Mirrors als Standard!")
        
        # Gibt GENTOO_MIRRORS aus  
        mirrors = self.get_gentoo_mirrors()
        
        if mirrors:
            for i, mirror in enumerate(mirrors, 1):
                print(f"  {i}. {mirror}")
                self.logger.info(f"Distfile Mirror {i}: {mirror}")
            self.logger.info(f"Insgesamt {len(mirrors)} Distfile-Mirror(s) konfiguriert")
            self.stats['used_mirror'] = mirrors[0]
            self.print_info(_('SYNC_PRIMARY_MIRROR', mirror=mirrors[0]))
        else:
            self.print_warning(_('NO_MIRRORS'))
            
            
    def run_command(self, command: List[str], description: str, 
                    allow_fail: bool = False, capture_output: bool = False,
                    custom_env: Optional[Dict[str, str]] = None) -> Tuple[bool, str]:
        """
        Führt einen Befehl aus und gibt den Status zurück
        
        Args:
            command: Befehlsliste
            description: Beschreibung für Log
            allow_fail: Wenn True, wird bei Fehler nicht abgebrochen
            capture_output: Wenn True, wird Output zurückgegeben statt gedruckt
            custom_env: Zusätzliche oder überschreibende Umgebungsvariablen
            
        Returns:
            Tuple (success, output): True bei Erfolg, False bei Fehler und Output
        """
        self.print_info(f"{description}...")
        self.logger.debug(f"Führe aus: {' '.join(command)}")
        
        if self.dry_run:
            self.print_warning(_('DRY_RUN_MSG', cmd=' '.join(command)))
            return True, ""
        
        # Baue Umgebung auf
        env = os.environ.copy()
        if custom_env:
            env.update(custom_env)
            
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    env=env
                )
                output = result.stdout + result.stderr
                
                if result.returncode == 0:
                    self.print_success(f"{description} erfolgreich abgeschlossen")
                    return True, output
                else:
                    self.print_error(f"{description} fehlgeschlagen (Exit Code: {result.returncode})")
                    if not allow_fail:
                        sys.exit(1)
                    return False, output
            else:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1,
                    env=env
                )
                
                output_lines = []
                # Echtzeit-Ausgabe
                for line in process.stdout:
                    print(line, end='')
                    output_lines.append(line)
                    
                process.wait()
                output = ''.join(output_lines)
                
                if process.returncode == 0:
                    self.print_success(f"{description} erfolgreich abgeschlossen")
                    return True, output
                else:
                    self.print_error(f"{description} fehlgeschlagen (Exit Code: {process.returncode})")
                    if not allow_fail:
                        sys.exit(1)
                    return False, output
                
        except FileNotFoundError:
            self.print_error(_('COMMAND_NOT_FOUND', cmd=command[0]))
            if not allow_fail:
                sys.exit(1)
            return False, ""
        except Exception as e:
            self.print_error(_('RUN_COMMAND_ERROR', desc=description, error=str(e)))
            self.logger.exception("Exception Details:")
            if not allow_fail:
                sys.exit(1)
            return False, str(e)
            
    def sync_repositories(self, retry: int = 1, mirror_index: int = 0) -> bool:
        """Synchronisiert die Portage-Repositories mit Mirror-Fallback
        
        Args:
            retry: Anzahl der Wiederholungsversuche bei Manifest-Fehler
            mirror_index: Index des zu verwendenden German Mirror (0-2)
        """
        self.print_section(f"SCHRITT 1: Repository-Synchronisation (Versuch {retry}/2)")
        
        # Versuche erst, die schnellsten Mirror mit mirrorselect zu wählen (nur beim ersten Versuch)
        # WICHTIG: -i öffnet UI nur wenn Terminal interaktiv ist, sonst automatisch fallback
        best_mirrors_distfiles = None
        best_mirror_rsync = None
        
        if retry == 1 and mirror_index == 0 and not self.custom_mirrors:
            # Versuche Distfiles Mirror auszuwählen
            try:
                best_mirrors_distfiles = self.auto_select_best_mirror_distfiles()
            except (EOFError, KeyboardInterrupt):
                # Benutzer hat abgebrochen - verwende Standard
                self.print_info("Verwende Standard-Mirror statt mirrorselect")
            except Exception:
                pass
        
        # Verwende beste Mirror wenn vorhanden, sonst Fallback
        mirrors_to_use = None
        if best_mirrors_distfiles:
            mirrors_to_use = best_mirrors_distfiles
            self.print_success(f"Verwende automatisch ausgewählte Mirror")
        elif self.custom_mirrors:
            mirrors_to_use = self.custom_mirrors
        else:
            mirrors_to_use = DEFAULT_GERMAN_MIRRORS_DISTFILES
        
        # Logge die konfigurierten Mirrors
        self.log_mirrors_info()
        
        # Aktualisiere make.conf mit Distfiles Mirror
        make_conf_path = '/etc/portage/make.conf'
        if mirrors_to_use and os.path.exists(make_conf_path):
            try:
                with open(make_conf_path, 'r') as f:
                    make_conf_content = f.read()
                
                # Ersetze GENTOO_MIRRORS oder füge sie hinzu
                mirrors_value = ' '.join(mirrors_to_use)
                if 'GENTOO_MIRRORS=' in make_conf_content:
                    # Ersetze existierende GENTOO_MIRRORS
                    updated_content = re.sub(
                        r'GENTOO_MIRRORS\s*=\s*"[^"]*"',
                        f'GENTOO_MIRRORS="{mirrors_value}"',
                        make_conf_content
                    )
                else:
                    # Füge neue Zeile am Ende hinzu
                    updated_content = make_conf_content.rstrip() + f'\n\n# Deutsche Gentoo Mirrors (Distfiles)\nGENTOO_MIRRORS="{mirrors_value}"\n'
                
                if updated_content != make_conf_content:
                    with open(make_conf_path, 'w') as f:
                        f.write(updated_content)
                    self.print_success(f"make.conf aktualisiert mit deutschen Mirrors")
            except Exception as e:
                self.print_warning(f"Konnte make.conf nicht aktualisieren: {e}")
        
        # Aktualisiere repos.conf mit deutschem RSYNC Mirror
        self.configure_rsync_mirrors()
        
        # Verwende Standard-Sync mit repos.conf (Portage-Tree über rsync)
        success, output = self.run_command(
            ["emerge", "--sync"],
            "Synchronisiere Portage-Repositories mit emerge --sync",
            allow_fail=True
        )
        
        # Bei Fehler: Quarantine aufräumen und Retry
        if not success and retry < 2:
            self.print_warning(_('SYNC_RETRY'))
            self.cleanup_manifest_quarantine()
            
            # Warte kurz, bevor Retry
            time.sleep(2)
            
            return self.sync_repositories(retry=2, mirror_index=0)
        
        return success
        
    def update_eix(self) -> bool:
        """Aktualisiert die eix-Datenbank"""
        self.print_section("SCHRITT 2: eix-Datenbank aktualisieren")
        
        # Prüfe ob eix installiert ist
        try:
            subprocess.run(["which", "eix"], check=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            self.print_warning(_('EIX_NOT_INSTALLED'))
            return True
            
        success, output = self.run_command(
            ["eix-update"],
            "Aktualisiere eix-Datenbank"
        )
        return success
        
    def check_updates(self) -> Tuple[bool, str]:
        """Prüft ob Updates verfügbar sind"""
        self.print_section("SCHRITT 3: Prüfe verfügbare Updates")
        
        # Prüfe blockierte Pakete
        if not self.check_blocked_packages():
            sys.exit(1)
        
        try:
            result = subprocess.run(
                ["emerge", "--update", "--deep", "--newuse", 
                 "--pretend", "@world"],
                capture_output=True,
                text=True
            )
            
            if "Total: 0 packages" in result.stdout:
                self.print_success(_('NO_UPDATES'))
                return False, ""
            else:
                self.print_info(_('UPDATES_AVAILABLE'))
                print(result.stdout)
                
                # Prüfe auf kritische Updates
                self.detect_critical_updates(result.stdout)
                
                # Extrahiere Paket-Liste
                self.extract_package_list(result.stdout, 'update')
                
                return True, result.stdout
                
        except Exception as e:
            self.print_error(f"Fehler beim Prüfen der Updates: {str(e)}")
            return False, ""
    
    def extract_package_list(self, output: str, operation: str):
        """Extrahiert Paket-Namen aus emerge-Output"""
        pattern = r'\[ebuild.*?\]\s+([^\s]+)'
        packages = re.findall(pattern, output)
        
        if operation == 'update':
            self.stats['packages_updated'].extend(packages)
        elif operation == 'remove':
            self.stats['packages_removed'].extend(packages)

    def requires_autounmask_recovery(self, output: str) -> bool:
        """Prüft, ob emerge wegen notwendiger autounmask-Änderungen abgebrochen ist"""
        if not output:
            return False

        output_lower = output.lower()
        indicators = [
            "use --autounmask-write to write changes to config files",
            "the following use changes are necessary to proceed",
            "autounmask change(s)",
            "no ebuilds built with use flags to satisfy"
        ]
        return any(indicator in output_lower for indicator in indicators)

    def apply_autounmask_and_update_configs(self, base_emerge_cmd: List[str]) -> bool:
        """Führt autounmask-write aus und merged Konfigurationsänderungen automatisch"""
        self.print_warning("Portage verlangt Konfigurations-/USE-Änderungen. Starte automatische Autounmask-Recovery...")

        # 1) Änderungen automatisch schreiben lassen
        autounmask_flags = [
            "--autounmask=y",
            "--autounmask-write",
            "--autounmask-continue",
            "--ask=n"
        ]
        autounmask_cmd = [base_emerge_cmd[0], *autounmask_flags, *base_emerge_cmd[1:]]

        success, _ = self.run_command(
            autounmask_cmd,
            "Wende autounmask-Änderungen automatisch an",
            allow_fail=True
        )
        if not success:
            self.print_warning("Autounmask-Änderungen konnten nicht automatisch geschrieben werden")
            return False

        # 2) Config-Merge durchführen (bevorzugt etc-update)
        if shutil.which("etc-update"):
            merge_cmd = ["etc-update", "-a"]
            merge_desc = "Übernehme Konfigurationsänderungen mit etc-update -a"
        elif shutil.which("dispatch-conf"):
            merge_cmd = ["dispatch-conf", "--replace-unmodified"]
            merge_desc = "Übernehme Konfigurationsänderungen mit dispatch-conf"
        else:
            self.print_warning("Weder etc-update noch dispatch-conf gefunden - automatische Recovery nicht möglich")
            return False

        success, _ = self.run_command(
            merge_cmd,
            merge_desc,
            allow_fail=True
        )
        if not success:
            self.print_warning("Konfigurations-Merge nach autounmask fehlgeschlagen")
            return False

        self.print_success("Autounmask-Recovery erfolgreich abgeschlossen")
        return True
            
    def update_system(self) -> Tuple[bool, bool]:
        """Aktualisiert das gesamte System
        
        Returns:
            Tuple (success, kernel_updated): Erfolg und ob Kernel aktualisiert wurde
        """
        self.print_section("SCHRITT 4: System-Update")
        
        # Prüfe welche Pakete aktualisiert werden (mit --pretend)
        self.print_info(_('MODULE_ANALYSIS'))
        try:
            result = subprocess.run(
                ["emerge", "--update", "--deep", "--newuse", 
                 "--with-bdeps=y", "--pretend", "@world"],
                capture_output=True,
                text=True
            )
            kernel_updated = "sys-kernel/" in result.stdout and "-sources" in result.stdout
            if kernel_updated:
                self.print_warning(_('KERNEL_UPDATE_DETECTED'))
                self.stats['kernel_updated'] = True
        except:
            kernel_updated = False
        
        # Baue emerge-Befehl mit Performance-Optimierungen
        jobs = self.config.get_emerge_jobs()
        load_avg = self.config.get_load_average()
        
        emerge_cmd = [
            "emerge", 
            "--update", "--deep", "--newuse",
            "--with-bdeps=y",
            f"--jobs={jobs}",
            f"--load-average={load_avg}",
            "@world"
        ]
        
        self.print_info(_('PERFORMANCE_INFO', jobs=jobs, load=load_avg))
        
        # Führe das eigentliche Update durch
        success, output = self.run_command(
            emerge_cmd,
            "Aktualisiere System-Pakete",
            allow_fail=True
        )

        # Wenn notwendige USE/Config-Änderungen fehlen: automatisch anwenden und einmal neu versuchen
        if not success and self.auto_autounmask and self.requires_autounmask_recovery(output):
            recovered = self.apply_autounmask_and_update_configs(emerge_cmd)
            if recovered:
                self.print_info("Starte emerge nach automatischer autounmask-Recovery erneut...")
                success, output = self.run_command(
                    emerge_cmd,
                    "Aktualisiere System-Pakete (Retry nach autounmask)",
                    allow_fail=True
                )
        elif not success and self.requires_autounmask_recovery(output):
            self.print_warning("Autounmask-Recovery erkannt, aber deaktiviert (--no-auto-autounmask)")
        
        return success, kernel_updated
        
    def check_kernel_module_mismatch(self) -> bool:
        """Prüft, ob Kernel-Module für den aktuellen Kernel fehlen oder veraltet sind
        
        WICHTIG: Nur True zurückgeben wenn wirklich Kernel-Mismatch erkannt wird!
        Nicht bei jedem Update die Module neu bauen!
        
        Returns:
            True wenn Module neu gebaut werden müssen, sonst False
        """
        self.print_info(_('CHECK_KERNEL_MODULES'))
        
        try:
            # HAUPTPRÜFUNG: Vergleiche laufenden Kernel mit installiertem Kernel
            # Das ist die einzige zuverlässige Prüfung!
            running_kernel = subprocess.run(
                ["uname", "-r"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Prüfe neuesten installierten Kernel
            eselect_result = subprocess.run(
                ["eselect", "kernel", "show"],
                capture_output=True,
                text=True
            )
            
            if eselect_result.returncode == 0:
                selected_kernel = eselect_result.stdout.strip()
                
                # Entferne "*" und Extra-Zeichen aus eselect Output
                # eselect kernel show gibt zurück: "Current: linux-6.12.63-gentoo-dist"
                selected_kernel = selected_kernel.replace("*", "").strip()
                
                # Extrahiere Kernel-Namen nach dem Doppelpunkt (wenn vorhanden)
                if ":" in selected_kernel:
                    selected_kernel = selected_kernel.split(":")[-1].strip()
                else:
                    # Nehme das letzte nicht-leere Wort
                    words = selected_kernel.split()
                    selected_kernel = words[-1] if words else ""
                
                # Prüfe ob laufender Kernel != installierter Kernel
                if selected_kernel and running_kernel not in selected_kernel:
                    self.print_warning(_('MODULES_STATUS', running=running_kernel, installed=selected_kernel))
                    self.print_info(_('MODULES_AFTER_UPDATE'))
                    return True
                else:
                    self.print_success(_('MODULES_CURRENT_KERNEL'))
                    return False
            
        except Exception as e:
            self.print_warning(f"Konnte Modul-Status nicht prüfen: {str(e)}")
            return False
        
        return False
    
    def rebuild_kernel_modules(self, force: bool = False):
        """Baut externe Kernel-Module neu (NVIDIA, VirtualBox, etc.)
        
        Args:
            force: Wenn True, wird ohne Prüfung neu gebaut
        """
        self.print_section("SCHRITT 5: Kernel-Module neu kompilieren")
        
        self.print_info(_('CHECK_KERNEL_MODULES'))
        
        # Prüfe ob @module-rebuild Set Pakete enthält
        try:
            result = subprocess.run(
                ["emerge", "--pretend", "@module-rebuild"],
                capture_output=True,
                text=True
            )
            
            if "Total: 0 packages" in result.stdout:
                self.print_success(_('NO_EXTERNAL_MODULES'))
                return True
            else:
                self.print_info("Folgende Module werden neu gebaut:")
                print(result.stdout)
        except Exception as e:
            self.print_warning(f"Konnte Module nicht prüfen: {str(e)}")
        
        # Baue Module neu
        success, output = self.run_command(
            ["emerge", "@module-rebuild"],
            "Kompiliere Kernel-Module neu",
            allow_fail=True
        )
        
        if success:
            self.stats['modules_rebuilt'] = True
            self.print_success(_('MODULES_REBUILD_SUCCESS'))
            self.print_info(_('MODULES_REBUILD_TIP'))
        
        return success
    
    def depclean(self) -> bool:
        """Entfernt nicht mehr benötigte Pakete"""
        if not self.config.get('auto_depclean', True):
            self.print_info(_('DEPCLEAN_SKIPPED'))
            return True
        
        self.print_section("SCHRITT 6: Bereinige verwaiste Pakete")
        
        # Erst pretend, um zu sehen was entfernt würde
        success, output = self.run_command(
            ["emerge", "--depclean", "--pretend"],
            "Prüfe zu entfernende Pakete",
            allow_fail=True,
            capture_output=True
        )
        
        if success:
            self.extract_package_list(output, 'remove')
            print(output)
            
            # Jetzt tatsächlich entfernen
            success, output = self.run_command(
                ["emerge", "--depclean", "--ask=n"],
                "Entferne nicht mehr benötigte Pakete",
                allow_fail=True
            )
        
        return success
        
    def revdep_rebuild(self) -> bool:
        """Baut Pakete mit kaputten Abhängigkeiten neu"""
        if not self.config.get('auto_revdep_rebuild', True):
            self.print_info(_('REVDEP_SKIPPED'))
            return True
        
        self.print_section("SCHRITT 7: Prüfe und repariere Abhängigkeiten")
        
        # Prüfe ob revdep-rebuild verfügbar ist
        try:
            subprocess.run(["which", "revdep-rebuild"], check=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            self.print_warning(_('REVDEP_NOT_FOUND'))
            return True
            
        success, output = self.run_command(
            ["revdep-rebuild"],
            "Repariere kaputte Abhängigkeiten",
            allow_fail=True
        )
        return success
        
    def check_kernel_updates(self):
        """Prüft ob Kernel-Updates verfügbar sind"""
        self.print_section("SCHRITT 8: Kernel-Update-Prüfung")
        
        try:
            # Prüfe installierte Kernel-Quellen
            result = subprocess.run(
                ["eselect", "kernel", "list"],
                capture_output=True,
                text=True
            )
            
            self.print_info("Verfügbare Kernel:")
            print(result.stdout)
            
            # Hinweis für manuelles Update
            self.print_warning(_('KERNEL_LIST_INFO'))
            self.print_info(_('KERNEL_UPDATE_STEPS'))
            print("  1. eselect kernel list")
            print("  2. eselect kernel set <nummer>")
            print("  3. cd /usr/src/linux")
            print("  4. make oldconfig")
            print("  5. make && make modules_install")
            print("  6. make install")
            print("  7. grub-mkconfig -o /boot/grub/grub.cfg")
            
        except Exception as e:
            self.print_warning(_('KERNEL_CHECK_FAILED', error=str(e)))
            
    def check_config_updates(self):
        """Prüft auf Konfigurations-Updates (nur Prüfung, keine Aktualisierung)"""
        try:
            # Suche nach ._cfg Dateien
            result = subprocess.run(
                ["find", "/etc", "-name", "._cfg*"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                self.print_warning(_('CONFIG_UPDATES_FOUND'))
                self.print_info("Konfigurationsdateien mit Updates:")
                print(result.stdout)
                return True  # Updates vorhanden
            else:
                return False  # Keine Updates
                
        except Exception as e:
            self.print_warning(_('CONFIG_CHECK_FAILED', error=str(e)))
            return False
    
    def update_config_files(self):
        """Aktualisiert Konfigurationsdateien basierend auf eingestelltem Modus
        
        Modi:
        - interactive: Benutzer wird interaktiv gefragt (standard etc-update UI)
        - auto: Alle Updates werden automatisch angewendet (etc-update -a)
        - skip: Keine Aktualisierung, nur Benachrichtigung
        """
        self.print_section("SCHRITT 9: Konfigurationsdateien aktualisieren")
        
        # Prüfe zuerst ob Updates vorhanden sind
        has_updates = self.check_config_updates()
        
        if not has_updates:
            self.print_success(_('CONFIG_NO_UPDATES'))
            return True
        
        # Verarbeite basierend auf Modus
        if self.etc_update_mode == 'skip':
            self.print_info("Modus: skip - Konfigurationsdateien werden nicht aktualisiert")
            return True
        
        elif self.etc_update_mode == 'auto':
            if self.dry_run:
                self.print_warning("DRY-RUN: Würde etc-update -a ausführen")
                return True
            
            self.print_info("Modus: auto - Aktualisiere alle Konfigurationsdateien automatisch")
            success, output = self.run_command(
                ["etc-update", "-a"],
                "Aktualisiere Konfigurationsdateien automatisch",
                allow_fail=True
            )
            
            if success:
                self.print_success("Alle Konfigurationsdateien wurden automatisch aktualisiert")
            else:
                self.print_warning("Fehler beim automatischen Update von Konfigurationsdateien")
            
            return success
        
        else:  # interactive (default)
            if self.dry_run:
                self.print_warning("DRY-RUN: Würde interaktives etc-update starten")
                return True
            
            self.print_info("Modus: interactive - Starte interaktives etc-update")
            self.print_info("Drücke 'q' zum Beenden, '-' um eine Datei zu überspringen")
            
            try:
                # Starte interaktives etc-update ohne -a Flag (interaktiv)
                subprocess.run(
                    ["etc-update"],
                    check=False
                )
                self.print_success("Interaktives etc-update abgeschlossen")
                return True
            except Exception as e:
                self.print_warning(f"Fehler bei interaktivem etc-update: {e}")
                return False
    
    def print_summary(self, duration):
        """Gibt eine Zusammenfassung des Updates aus"""
        self.print_section("UPDATE-ZUSAMMENFASSUNG")
        
        print(f"{Colors.BOLD}Dauer:{Colors.ENDC} {duration}")
        print()
        
        # Zeige verwendete Mirrors
        if self.stats.get('gentoo_mirrors'):
            print(f"{Colors.OKBLUE}Gentoo Mirrors:{Colors.ENDC}")
            for mirror in self.stats['gentoo_mirrors']:
                print(f"  • {mirror}")
            if self.stats.get('used_mirror'):
                print(f"{Colors.BOLD}Primärer Mirror:{Colors.ENDC} {self.stats['used_mirror']}")
            print()
        
        if self.stats['packages_updated']:
            print(f"{Colors.OKGREEN}Aktualisierte Pakete ({len(self.stats['packages_updated'])}):{Colors.ENDC}")
            for pkg in self.stats['packages_updated'][:10]:  # Zeige erste 10
                print(f"  • {pkg}")
            if len(self.stats['packages_updated']) > 10:
                print(f"  ... und {len(self.stats['packages_updated']) - 10} weitere")
            print()
        
        if self.stats['packages_removed']:
            print(f"{Colors.OKCYAN}Entfernte Pakete ({len(self.stats['packages_removed'])}):{Colors.ENDC}")
            for pkg in self.stats['packages_removed'][:5]:
                print(f"  • {pkg}")
            if len(self.stats['packages_removed']) > 5:
                print(f"  ... und {len(self.stats['packages_removed']) - 5} weitere")
            print()
        
        if self.stats['kernel_updated']:
            print(f"{Colors.WARNING}{symbol('warning')} Kernel wurde aktualisiert{Colors.ENDC}")
            print()
        
        if self.stats['modules_rebuilt']:
            print(f"{Colors.OKGREEN}{symbol('checkmark')} Kernel-Module neu gebaut{Colors.ENDC}")
            print()
        
        if self.stats['warnings']:
            print(f"{Colors.WARNING}Warnungen ({len(self.stats['warnings'])}):{Colors.ENDC}")
            for warn in self.stats['warnings'][:5]:
                print(f"  {symbol('warning')} {warn}")
            print()
        
        if self.stats['errors']:
            print(f"{Colors.FAIL}Fehler ({len(self.stats['errors'])}):{Colors.ENDC}")
            for err in self.stats['errors']:
                print(f"  {symbol('error')} {err}")
            print()
        
        print(f"{Colors.BOLD}Log-Datei:{Colors.ENDC} {self.log_file}")
        print()
        
        # Speichere Summary auch in JSON
        self.save_summary_json(duration)
    
    def save_summary_json(self, duration):
        """Speichert Update-Summary als JSON"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'duration': str(duration),
            'mirrors': self.stats.get('gentoo_mirrors', []),
            'primary_mirror': self.stats.get('used_mirror'),
            'stats': self.stats
        }
        
        summary_file = self.log_file.with_suffix('.json')
        try:
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            self.logger.info(f"Summary gespeichert: {summary_file}")
        except Exception as e:
            self.logger.warning(f"Konnte Summary nicht speichern: {e}")
    
    def send_notification(self, success: bool, duration):
        """Sendet Benachrichtigung über Update-Status"""
        if not self.config.get('enable_notifications', False):
            return
        
        email = self.config.get('notification_email', '')
        if not email:
            return
        
        status = "erfolgreich" if success else "mit Fehlern"
        subject = f"Gentoo Update {status} abgeschlossen"
        
        body = f"""Update-Status: {status}
Dauer: {duration}
Pakete aktualisiert: {len(self.stats['packages_updated'])}
Fehler: {len(self.stats['errors'])}

Details siehe: {self.log_file}
"""
        
        try:
            subprocess.run(
                ['mail', '-s', subject, email],
                input=body,
                text=True,
                check=False
            )
            self.print_info(f"Benachrichtigung gesendet an {email}")
        except Exception as e:
            self.print_warning(f"Konnte Benachrichtigung nicht senden: {e}")
            
    def run_modules_only(self):
        """Baut nur Kernel-Module neu (ohne System-Update)"""
        start_time = datetime.now()
        
        print(f"{Colors.BOLD}{Colors.OKCYAN}")
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║       KERNEL-MODULE NEU KOMPILIEREN                              ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        self.check_root_privileges()
        
        # Prüfe Modul-Status
        needs_rebuild = self.check_kernel_module_mismatch()
        
        if needs_rebuild or self.rebuild_modules:
            self.rebuild_kernel_modules(force=True)
        else:
            self.print_success("Alle Kernel-Module sind bereits aktuell!")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        self.print_section("Modul-Rebuild abgeschlossen")
        self.print_success(f"Gesamtdauer: {duration}")
    
    def run_full_update(self):
        """Führt ein komplettes System-Update durch"""
        start_time = datetime.now()
        update_success = True
        
        print(f"{Colors.BOLD}{Colors.OKCYAN}")
        print("╔════════════════════════════════════════════════════════════════════╗")
        version_text = f"GENTOO SYSTEM UPDATER v{__version__}"
        print(f"║ {version_text:^64} ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        if self.timeout:
            print(f"{Colors.OKCYAN}{symbol('clock')} Timeout: {self.timeout} Sekunden{Colors.ENDC}")
        if self.retry_count > 1:
            print(f"{Colors.OKCYAN}{symbol('sync')} Retry-Count: {self.retry_count}{Colors.ENDC}")
        if self.max_packages:
            print(f"{Colors.OKCYAN}{symbol('package')} Max Packages: {self.max_packages}{Colors.ENDC}")
        
        # Prüfe ob mirrorselect verfügbar ist und informiere Benutzer
        try:
            subprocess.run(["which", "mirrorselect"], check=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
            print(f"{Colors.OKCYAN}{_('MIRRORSELECT_AVAILABLE')}{Colors.ENDC}")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print(f"{Colors.WARNING}{_('MIRRORSELECT_NOT_INSTALLED')}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}{_('MIRRORSELECT_INSTALL_TIP')}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}{_('MIRRORSELECT_BENEFIT')}{Colors.ENDC}\n")
        
        try:
            self.check_root_privileges()
            
            # Prüfe Festplattenspeicher
            if not self.check_disk_space():
                sys.exit(1)
            
            # Erstelle Backup
            self.backup_important_files()
            
            # Vorbereitung: Räume Manifest-Fehler auf
            self.cleanup_manifest_quarantine()
            
            # Schritt 1: Sync (wenn nicht übersprungen)
            if not self.skip_sync:
                if not self.sync_repositories():
                    self.print_error("Repository-Synchronisation fehlgeschlagen nach 2 Versuchen")
                    update_success = False
                    sys.exit(1)
            else:
                print(f"{Colors.WARNING}{symbol('skip')} Skipping repository synchronisation (--skip-sync){Colors.ENDC}")
            
            # Schritt 2: eix-update (wenn nicht übersprungen)
            if not self.skip_eix:
                self.update_eix()
            else:
                print(f"{Colors.WARNING}{symbol('skip')} Skipping eix update (--skip-eix){Colors.ENDC}")
            
            # Schritt 3: Prüfe Updates (nur wenn nicht --skip-update)
            if not self.skip_update:
                has_updates, pretend_output = self.check_updates()
                
                if not has_updates and not self.dry_run:
                    self.update_config_files()
                    end_time = datetime.now()
                    duration = end_time - start_time
                    self.print_summary(duration)
                    self.send_notification(True, duration)
                    return
                
            # Schritt 4: System-Update
            success, kernel_updated = self.update_system()
            if not success:
                self.print_error("System-Update fehlgeschlagen")
                update_success = False
                sys.exit(1)
            
            # Schritt 5: Kernel-Module neu bauen
            # Prüfe ob Module fehlen oder veraltet sind (auch ohne Update)
            needs_module_rebuild = kernel_updated or self.check_kernel_module_mismatch()
            
            if needs_module_rebuild:
                self.rebuild_kernel_modules(force=kernel_updated)
            else:
                self.print_success("Kernel-Module sind aktuell - keine Neucompilierung nötig")
            
            # Schritt 6: Depclean
            self.depclean()
            
            # Schritt 7: revdep-rebuild
            self.revdep_rebuild()
            
            # Schritt 8: Kernel-Check
            self.check_kernel_updates()
            
            # Schritt 9: Config-Update (interaktiv, automatisch oder übersprungen)
            self.update_config_files()
            
        except KeyboardInterrupt:
            self.print_error("Update durch Benutzer abgebrochen")
            update_success = False
            raise
        except Exception as e:
            self.print_error(f"Unerwarteter Fehler: {e}")
            self.logger.exception("Exception Details:")
            update_success = False
            raise
        finally:
            # Zusammenfassung (wird immer ausgeführt)
            end_time = datetime.now()
            duration = end_time - start_time
            
            self.print_summary(duration)
            self.send_notification(update_success, duration)
            
            if update_success:
                self.print_info("Bitte Kernel-Updates und Konfigurations-Änderungen manuell prüfen")
        

def main():
    """Hauptfunktion"""
    # Vorverarbeitung: Prüfe auf --lang Parameter bevor argparser lädt
    # Das erlaubt es, Hilfe-Texte in der richtigen Sprache anzuzeigen
    import sys
    if '--lang' in sys.argv:
        try:
            lang_index = sys.argv.index('--lang')
            if lang_index + 1 < len(sys.argv):
                lang = sys.argv[lang_index + 1]
                if lang in ['de', 'en']:
                    globals()['CURRENT_LANGUAGE'] = lang
        except (ValueError, IndexError):
            pass
    
    # Environment-Variable Support
    env_dry_run = os.getenv('GENTOO_UPDATER_DRY_RUN', 'false').lower() == 'true'
    env_verbose = os.getenv('GENTOO_UPDATER_VERBOSE', 'false').lower() == 'true'
    env_log_level = os.getenv('GENTOO_UPDATER_LOG_LEVEL', 'INFO')
    env_timeout = os.getenv('GENTOO_UPDATER_TIMEOUT')
    env_retry = os.getenv('GENTOO_UPDATER_RETRY_COUNT', '1')
    env_webhook = os.getenv('GENTOO_UPDATER_WEBHOOK')
    env_parallel = os.getenv('GENTOO_UPDATER_PARALLEL_JOBS')
    env_auto_autounmask = os.getenv('GENTOO_UPDATER_AUTO_AUTOUNMASK')
    env_skip_internet_check = os.getenv('GENTOO_UPDATER_SKIP_INTERNET_CHECK', 'false').lower() == 'true'
    
    parser = argparse.ArgumentParser(
        description='Gentoo System Updater - Automatisiert System-Updates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  sudo gentoo-updater                    # Vollständiges System-Update mit deutschen Mirrors
  sudo gentoo-updater --dry-run          # Zeige was gemacht würde
  sudo gentoo-updater --only-sync        # Nur Repository-Sync
  sudo gentoo-updater --skip-cleanup     # Überspringe depclean
  GENTOO_UPDATER_DRY_RUN=true gentoo-updater  # Env-Var für Dry-Run

Deutsche Mirrors:
  Das Skript nutzt standardmäßig deutsche/europäische Mirrors für bessere Geschwindigkeit:
  
  Distfiles (Quellcode):
    - 🥇 RWTH Aachen (https://ftp.halifax.rwth-aachen.de/gentoo/) - sehr schnell
    - Init7 Schweiz (https://mirror.init7.net/gentoo/)
    - Ruhr-Universität Bochum (http://linux.rz.ruhr-uni-bochum.de/download/gentoo-mirror/)
  
  Portage-Tree (RSYNC):
    - 🇩🇪 Deutschland (rsync://rsync.de.gentoo.org/gentoo-portage) - offiziell
    - 🥇 RWTH Aachen (rsync://ftp.halifax.rwth-aachen.de/gentoo-portage) - sehr schnell
    - 🇨🇭 Init7 Schweiz (rsync://mirror.init7.net/gentoo-portage)
    - Official Gentoo (rsync://rsync.gentoo.org/gentoo-portage) - Fallback
  
  Mit mirrorselect interaktiv auswählen:
    sudo emerge -av app-portage/mirrorselect  # Eine einzelne Installation
    gentoo-updater wird mirrorselect automatisch starten wenn verfügbar!
  
  Manuell konfigurieren:
    - Distfiles: /etc/portage/make.conf (GENTOO_MIRRORS)
    - Portage-Tree: /etc/portage/repos.conf/gentoo.conf (sync-uri)

Umgebungsvariablen:
  GENTOO_UPDATER_DRY_RUN=true            # Aktiviere Dry-Run
  GENTOO_UPDATER_VERBOSE=true            # Verbose Logging
  GENTOO_UPDATER_LOG_LEVEL=DEBUG         # Log-Level (DEBUG/INFO/WARNING/ERROR)
  GENTOO_UPDATER_TIMEOUT=3600            # Timeout in Sekunden
  GENTOO_UPDATER_RETRY_COUNT=3           # Wiederholung bei Fehler
  GENTOO_UPDATER_SKIP_INTERNET_CHECK=true # Überspringe Internetverbindungs-Prüfung
  GENTOO_UPDATER_WEBHOOK=URL             # Webhook-URL
  GENTOO_UPDATER_PARALLEL_JOBS=4         # Parallele Jobs
    GENTOO_UPDATER_AUTO_AUTOUNMASK=true    # Automatische autounmask-Recovery
  GENTOO_UPDATER_MIRRORS=URL1,URL2       # Custom Mirror (komma-getrennt)
        """
    )
    
    parser.add_argument('-v', '--verbose', 
                       action='store_true',
                       help=get_help_text('verbose'))
    parser.add_argument('-n', '--dry-run',
                       action='store_true', 
                       help=get_help_text('dry_run'))
    parser.add_argument('--rebuild-modules',
                       action='store_true',
                       help=get_help_text('rebuild_modules'))
    parser.add_argument('--create-config',
                       action='store_true',
                       help=get_help_text('create_config'))
    parser.add_argument('--config',
                       type=str,
                       default='/etc/gentoo-updater.conf',
                       help=get_help_text('config'))
    
    # Parameter für v1.4.2
    parser.add_argument('--log-level',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help=get_help_text('log_level'))
    
    parser.add_argument('--skip-sync',
                       action='store_true',
                       help=get_help_text('skip_sync'))
    parser.add_argument('--skip-update',
                       action='store_true',
                       help=get_help_text('skip_update'))
    parser.add_argument('--skip-eix',
                       action='store_true',
                       help=get_help_text('skip_eix'))
    parser.add_argument('--skip-cleanup',
                       action='store_true',
                       help=get_help_text('skip_cleanup'))
    parser.add_argument('--skip-revdep',
                       action='store_true',
                       help=get_help_text('skip_revdep'))
    
    parser.add_argument('--skip-internet-check',
                       action='store_true',
                       help=get_help_text('skip_internet_check'))
    
    parser.add_argument('--only-sync',
                       action='store_true',
                       help=get_help_text('only_sync'))
    parser.add_argument('--only-update',
                       action='store_true',
                       help=get_help_text('only_update'))
    parser.add_argument('--only-cleanup',
                       action='store_true',
                       help=get_help_text('only_cleanup'))
    
    parser.add_argument('--max-packages',
                       type=int,
                       default=None,
                       help=get_help_text('max_packages'))
    
    parser.add_argument('--timeout',
                       type=int,
                       default=None,
                       help=get_help_text('timeout'))
    
    parser.add_argument('--retry-count',
                       type=int,
                       default=1,
                       help=get_help_text('retry_count'))
    
    parser.add_argument('--notification-webhook',
                       type=str,
                       default=None,
                       help=get_help_text('notification_webhook'))
    
    parser.add_argument('--parallel-jobs',
                       type=int,
                       default=None,
                       help=get_help_text('parallel_jobs'))
    
    parser.add_argument('--lang',
                       choices=['de', 'en'],
                       default=None,
                       help=get_help_text('lang'))
    
    parser.add_argument('--mirrors',
                       type=str,
                       default=None,
                       help=get_help_text('mirrors'))
    
    parser.add_argument('--use-mirrorselect',
                       action='store_true',
                       help=get_help_text('use_mirrorselect'))
    
    parser.add_argument('--etc-update-mode',
                       choices=['interactive', 'auto', 'skip'],
                       default='interactive',
                       help=get_help_text('etc_update_mode'))

    parser.add_argument('--auto-autounmask',
                       action=argparse.BooleanOptionalAction,
                       default=True,
                       help=get_help_text('auto_autounmask'))
    
    parser.add_argument('--repository',
                       action='store_true',
                       help=get_help_text('repository'))
    
    parser.add_argument('--support',
                       action='store_true',
                       help=get_help_text('support'))
    
    parser.add_argument('--author',
                       action='store_true',
                       help=get_help_text('author'))
    
    parser.add_argument('--license',
                       action='store_true',
                       help=get_help_text('license'))
    
    parser.add_argument('--version',
                       action='version',
                       version=f'Gentoo Updater v{__version__}')
    
    args = parser.parse_args()
    
    # Handle --author flag
    if args.author:
        print(f"Gentoo System Updater")
        print(f"Version: {__version__}")
        print(f"Author: {__author__}")
        print(f"License: {__license__}")
        sys.exit(0)
    
    # Handle --license flag
    if args.license:
        print(f"\n{Colors.HEADER}{Colors.BOLD}License Information{Colors.ENDC}")
        print(f"")
        print(f"Gentoo System Updater - {__license__} License")
        print(f"")
        print(f"Copyright (c) 2024 {__author__}")
        print(f"")
        print(f"MIT License text:")
        print(f"Permission is hereby granted, free of charge, to any person obtaining")
        print(f"a copy of this software and associated documentation files (the")
        print(f"'Software'), to deal in the Software without restriction, including")
        print(f"without limitation the rights to use, copy, modify, merge, publish,")
        print(f"distribute, sublicense, and/or sell copies of the Software.")
        print(f"")
        print(f"License file: {Colors.OKCYAN}See LICENSE file in repository{Colors.ENDC}")
        sys.exit(0)
    
    # Handle --repository flag
    if args.repository:
        print(f"\n{Colors.HEADER}{Colors.BOLD}GitHub Repository Information{Colors.ENDC}")
        print(f"  Repository: {GITHUB_REPO}")
        print(f"  Issues: {GITHUB_ISSUES}")
        print(f"  Discussions: {GITHUB_DISCUSSIONS}")
        print()
        sys.exit(0)
    
    # Handle --support flag
    if args.support:
        print(f"\n{Colors.HEADER}{Colors.BOLD}Support & Issue Templates{Colors.ENDC}")
        print(f"\n{Colors.OKGREEN}Report a Bug:{Colors.ENDC}")
        print(f"  {GITHUB_ISSUE_TEMPLATE_BUG}")
        print(f"\n{Colors.OKGREEN}Request a Feature:{Colors.ENDC}")
        print(f"  {GITHUB_ISSUE_TEMPLATE_FEATURE}")
        print(f"\n{Colors.OKGREEN}Discussions:{Colors.ENDC}")
        print(f"  {GITHUB_DISCUSSIONS}")
        print()
        sys.exit(0)
    
    # Language override via --lang parameter
    if args.lang:
        globals()['CURRENT_LANGUAGE'] = args.lang
    
    # Environment-Variablen überschreiben Defaults
    if env_dry_run:
        args.dry_run = True
    if env_verbose:
        args.verbose = True
    if env_log_level:
        args.log_level = env_log_level
    if env_timeout:
        args.timeout = int(env_timeout) if env_timeout else None
    if env_retry:
        args.retry_count = int(env_retry) if env_retry else 1
    if env_webhook:
        args.notification_webhook = env_webhook
    if env_parallel:
        args.parallel_jobs = int(env_parallel) if env_parallel else None
    if env_auto_autounmask is not None:
        args.auto_autounmask = env_auto_autounmask.lower() in ['1', 'true', 'yes', 'on']
    if env_skip_internet_check:
        args.skip_internet_check = True
    
    # ===== KRITISCHE CHECKS: INTERNET-VERBINDUNG =====
    # Prüfe Internet-Verbindung, sofern nicht übersprungen
    skip_internet_check = getattr(args, 'skip_internet_check', False) or env_skip_internet_check
    if not skip_internet_check:
        print(f"\n{Colors.OKCYAN}🌐 Prüfe Internetverbindung...{Colors.ENDC}")
        if not check_internet_connection():
            print(f"{Colors.FAIL}{symbol('error')} {translate('INTERNET_CHECK_ERROR')}{Colors.ENDC}")
            print(f"{Colors.WARNING}{symbol('info')} {translate('INTERNET_CHECK_INFO')}{Colors.ENDC}")
            sys.exit(1)
        print(f"{Colors.OKGREEN}{symbol('checkmark')} Internetverbindung verfügbar{Colors.ENDC}\n")
    
    # Parse custom mirrors if provided (or use German mirrors as default)
    custom_mirrors = None
    env_mirrors = os.getenv('GENTOO_UPDATER_MIRRORS')
    
    if env_mirrors:
        # Umgebungsvariable überschreibt CLI
        custom_mirrors = [m.strip() for m in env_mirrors.split(',') if m.strip()]
    elif args.mirrors:
        # CLI Parameter
        custom_mirrors = [m.strip() for m in args.mirrors.split(',') if m.strip()]
    else:
        # Verwende deutsche Mirrors als Default
        custom_mirrors = DEFAULT_GERMAN_MIRRORS
    
    # Config erstellen wenn gewünscht
    if args.create_config:
        config = Config(args.config)
        config.save_default_config()
        sys.exit(0)
    
    try:
        config = Config(args.config)
        
        # Parallel-Jobs from parameter override config
        if args.parallel_jobs:
            config.config['emerge_jobs'] = args.parallel_jobs
        
        updater = GentooUpdater(
            verbose=args.verbose, 
            dry_run=args.dry_run,
            rebuild_modules=args.rebuild_modules,
            config=config,
            log_level=args.log_level,
            timeout=args.timeout,
            retry_count=args.retry_count,
            webhook_url=args.notification_webhook,
            max_packages=args.max_packages,
            custom_mirrors=custom_mirrors,
            etc_update_mode=args.etc_update_mode,
            auto_autounmask=args.auto_autounmask
        )
        
        # Nur Module neu gebaut werden sollen
        if args.rebuild_modules:
            updater.run_modules_only()
        # Nur spezifische Operationen ausführen (--only-*)
        elif args.only_sync:
            updater.sync_repositories()
        elif args.only_update:
            updater.update_world()
        elif args.only_cleanup:
            updater.depclean()
        # Spezifische Operationen überspringen (--skip-*)
        else:
            updater.skip_sync = args.skip_sync
            updater.skip_update = args.skip_update
            updater.skip_eix = args.skip_eix
            updater.skip_cleanup = args.skip_cleanup
            updater.skip_revdep = args.skip_revdep
            updater.run_full_update()
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Update durch Benutzer abgebrochen{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.FAIL}Unerwarteter Fehler: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
