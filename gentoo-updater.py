#!/usr/bin/env python3
"""
Gentoo System Updater
Automatisches Update-Skript für Gentoo Linux
"""

import subprocess
import sys
import os
import argparse
import shutil
import time
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import logging


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
                print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} Konnte Config nicht laden: {e}")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save_default_config(self):
        """Speichert Default-Konfiguration in Datei"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2)
            print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} Default-Konfiguration gespeichert: {self.config_file}")
        except Exception as e:
            print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Konnte Config nicht speichern: {e}")
    
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
                 rebuild_modules: bool = False, config: Optional[Config] = None):
        self.verbose = verbose
        self.dry_run = dry_run
        self.rebuild_modules = rebuild_modules
        self.config = config or Config()
        
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
            'warnings': []
        }
    
    def setup_logging(self):
        """Konfiguriert das Logging-System"""
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
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
            self.print_error("Dieses Skript benötigt Root-Rechte.")
            self.print_info("Bitte mit sudo ausführen: sudo gentoo-updater")
            sys.exit(1)
    
    def check_disk_space(self) -> bool:
        """Prüft ob genügend Festplattenspeicher verfügbar ist"""
        min_space_gb = self.config.get('min_free_space_gb', 5)
        
        try:
            stat = shutil.disk_usage('/usr')
            free_gb = stat.free / (1024**3)
            
            self.print_info(f"Freier Speicherplatz: {free_gb:.2f} GB")
            
            if free_gb < min_space_gb:
                self.print_error(f"Nicht genug Speicherplatz! Mindestens {min_space_gb} GB erforderlich.")
                return False
            return True
        except Exception as e:
            self.print_warning(f"Konnte Speicherplatz nicht prüfen: {e}")
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
            
            self.print_success(f"Backup erstellt: {backup_path}")
            self.cleanup_old_backups(backup_dir)
            
        except Exception as e:
            self.print_warning(f"Backup fehlgeschlagen: {e}")
    
    def cleanup_old_backups(self, backup_dir: Path):
        """Löscht alte Backups"""
        retention_days = self.config.get('log_retention_days', 30)
        cutoff_time = time.time() - (retention_days * 86400)
        
        try:
            for item in backup_dir.iterdir():
                if item.is_dir() and item.stat().st_mtime < cutoff_time:
                    shutil.rmtree(item)
                    self.print_info(f"Altes Backup gelöscht: {item.name}")
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
                self.print_error("Blockierte Pakete gefunden!")
                print(result.stdout)
                self.print_info("Bitte lösen Sie die Blockierungen manuell auf.")
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
            self.print_warning("ACHTUNG: Kritische Pakete werden aktualisiert!")
            for pkg in found_critical:
                self.print_warning(f"  - {pkg}")
            self.print_info("Diese Updates können System-Neustarts oder Rebuilds erfordern.")
        
        return found_critical
    
    def cleanup_manifest_quarantine(self):
        """Räumt beschädigte Manifest-Dateien auf"""
        quarantine_dir = "/var/db/repos/gentoo/.tmp-unverified-download-quarantine"
        
        if os.path.exists(quarantine_dir):
            self.print_info(f"Räume auf: {quarantine_dir}")
            try:
                shutil.rmtree(quarantine_dir)
                self.print_success("Quarantine-Verzeichnis gelöscht")
            except Exception as e:
                self.print_warning(f"Konnte Quarantine nicht löschen: {str(e)}")
            
    def run_command(self, command: List[str], description: str, 
                    allow_fail: bool = False, capture_output: bool = False) -> Tuple[bool, str]:
        """
        Führt einen Befehl aus und gibt den Status zurück
        
        Args:
            command: Befehlsliste
            description: Beschreibung für Log
            allow_fail: Wenn True, wird bei Fehler nicht abgebrochen
            capture_output: Wenn True, wird Output zurückgegeben statt gedruckt
            
        Returns:
            Tuple (success, output): True bei Erfolg, False bei Fehler und Output
        """
        self.print_info(f"{description}...")
        self.logger.debug(f"Führe aus: {' '.join(command)}")
        
        if self.dry_run:
            self.print_warning(f"DRY-RUN: Würde ausführen: {' '.join(command)}")
            return True, ""
            
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True
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
                    bufsize=1
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
            self.print_error(f"Befehl nicht gefunden: {command[0]}")
            if not allow_fail:
                sys.exit(1)
            return False, ""
        except Exception as e:
            self.print_error(f"Fehler bei {description}: {str(e)}")
            self.logger.exception("Exception Details:")
            if not allow_fail:
                sys.exit(1)
            return False, str(e)
            
    def sync_repositories(self, retry: int = 1) -> bool:
        """Synchronisiert die Portage-Repositories
        
        Args:
            retry: Anzahl der Wiederholungsversuche bei Manifest-Fehler
        """
        self.print_section(f"SCHRITT 1: Repository-Synchronisation (Versuch {retry}/2)")
        
        success, _ = self.run_command(
            ["emerge", "--sync"],
            "Synchronisiere Portage-Repositories",
            allow_fail=True
        )
        
        # Bei Fehler: Quarantine aufräumen und nochmal versuchen
        if not success and retry < 2:
            self.print_warning("Sync fehlgeschlagen - räume auf und versuche erneut...")
            self.cleanup_manifest_quarantine()
            
            # Warte kurz, bevor Retry
            time.sleep(2)
            
            return self.sync_repositories(retry=2)
        
        return success
        
    def update_eix(self) -> bool:
        """Aktualisiert die eix-Datenbank"""
        self.print_section("SCHRITT 2: eix-Datenbank aktualisieren")
        
        # Prüfe ob eix installiert ist
        try:
            subprocess.run(["which", "eix"], check=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            self.print_warning("eix ist nicht installiert, überspringe...")
            return True
            
        success, _ = self.run_command(
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
                self.print_success("Keine Updates verfügbar - System ist aktuell!")
                return False, ""
            else:
                self.print_info("Updates verfügbar:")
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
            
    def update_system(self) -> Tuple[bool, bool]:
        """Aktualisiert das gesamte System
        
        Returns:
            Tuple (success, kernel_updated): Erfolg und ob Kernel aktualisiert wurde
        """
        self.print_section("SCHRITT 4: System-Update")
        
        # Prüfe welche Pakete aktualisiert werden (mit --pretend)
        self.print_info("Analysiere zu aktualisierende Pakete...")
        try:
            result = subprocess.run(
                ["emerge", "--update", "--deep", "--newuse", 
                 "--with-bdeps=y", "--pretend", "@world"],
                capture_output=True,
                text=True
            )
            kernel_updated = "sys-kernel/" in result.stdout and "-sources" in result.stdout
            if kernel_updated:
                self.print_warning("Kernel-Update erkannt! Module werden nach dem Update neu gebaut.")
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
        
        self.print_info(f"Performance: {jobs} parallele Jobs, Load Average: {load_avg}")
        
        # Führe das eigentliche Update durch
        success, _ = self.run_command(
            emerge_cmd,
            "Aktualisiere System-Pakete"
        )
        
        return success, kernel_updated
        
    def check_kernel_module_mismatch(self) -> bool:
        """Prüft, ob Kernel-Module für den aktuellen Kernel fehlen oder veraltet sind
        
        WICHTIG: Nur True zurückgeben wenn wirklich Kernel-Mismatch erkannt wird!
        Nicht bei jedem Update die Module neu bauen!
        
        Returns:
            True wenn Module neu gebaut werden müssen, sonst False
        """
        self.print_info("Prüfe Kernel-Module Status...")
        
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
                    self.print_warning(f"Laufender Kernel ({running_kernel}) != Installierter Kernel ({selected_kernel})")
                    self.print_info("Module müssen für den neuen Kernel neu gebaut werden")
                    return True
                else:
                    self.print_success("Laufender Kernel ist aktuell - Module müssen nicht neu gebaut werden")
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
        
        self.print_info("Überprüfe externe Kernel-Module...")
        
        # Prüfe ob @module-rebuild Set Pakete enthält
        try:
            result = subprocess.run(
                ["emerge", "--pretend", "@module-rebuild"],
                capture_output=True,
                text=True
            )
            
            if "Total: 0 packages" in result.stdout:
                self.print_success("Keine externen Kernel-Module gefunden (oder bereits aktuell)")
                return True
            else:
                self.print_info("Folgende Module werden neu gebaut:")
                print(result.stdout)
        except Exception as e:
            self.print_warning(f"Konnte Module nicht prüfen: {str(e)}")
        
        # Baue Module neu
        success, _ = self.run_command(
            ["emerge", "@module-rebuild"],
            "Kompiliere Kernel-Module neu",
            allow_fail=True
        )
        
        if success:
            self.stats['modules_rebuilt'] = True
            self.print_success("Alle Kernel-Module erfolgreich neu gebaut")
            self.print_info("Tipp: Nach einem Neustart werden die neuen Module verwendet")
        
        return success
    
    def depclean(self) -> bool:
        """Entfernt nicht mehr benötigte Pakete"""
        if not self.config.get('auto_depclean', True):
            self.print_info("Depclean übersprungen (in Config deaktiviert)")
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
            success, _ = self.run_command(
                ["emerge", "--depclean", "--ask=n"],
                "Entferne nicht mehr benötigte Pakete",
                allow_fail=True
            )
        
        return success
        
    def revdep_rebuild(self) -> bool:
        """Baut Pakete mit kaputten Abhängigkeiten neu"""
        if not self.config.get('auto_revdep_rebuild', True):
            self.print_info("revdep-rebuild übersprungen (in Config deaktiviert)")
            return True
        
        self.print_section("SCHRITT 7: Prüfe und repariere Abhängigkeiten")
        
        # Prüfe ob revdep-rebuild verfügbar ist
        try:
            subprocess.run(["which", "revdep-rebuild"], check=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            self.print_warning("revdep-rebuild nicht gefunden (gentoolkit installieren?)")
            return True
            
        success, _ = self.run_command(
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
            self.print_warning("Kernel-Updates müssen manuell durchgeführt werden!")
            self.print_info("Schritte für Kernel-Update:")
            print("  1. eselect kernel list")
            print("  2. eselect kernel set <nummer>")
            print("  3. cd /usr/src/linux")
            print("  4. make oldconfig")
            print("  5. make && make modules_install")
            print("  6. make install")
            print("  7. grub-mkconfig -o /boot/grub/grub.cfg")
            
        except Exception as e:
            self.print_warning(f"Kernel-Prüfung fehlgeschlagen: {str(e)}")
            
    def check_config_updates(self):
        """Prüft auf Konfigurations-Updates"""
        self.print_section("SCHRITT 9: Konfigurationsdateien prüfen")
        
        try:
            # Suche nach ._cfg Dateien
            result = subprocess.run(
                ["find", "/etc", "-name", "._cfg*"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                self.print_warning("Konfigurations-Updates gefunden!")
                self.print_info("Bitte mit dispatch-conf oder etc-update zusammenführen:")
                print(result.stdout)
            else:
                self.print_success("Keine Konfigurations-Updates ausstehend")
                
        except Exception as e:
            self.print_warning(f"Konfigurations-Prüfung fehlgeschlagen: {str(e)}")
    
    def print_summary(self, duration):
        """Gibt eine Zusammenfassung des Updates aus"""
        self.print_section("UPDATE-ZUSAMMENFASSUNG")
        
        print(f"{Colors.BOLD}Dauer:{Colors.ENDC} {duration}")
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
            print(f"{Colors.WARNING}⚠ Kernel wurde aktualisiert{Colors.ENDC}")
            print()
        
        if self.stats['modules_rebuilt']:
            print(f"{Colors.OKGREEN}✓ Kernel-Module neu gebaut{Colors.ENDC}")
            print()
        
        if self.stats['warnings']:
            print(f"{Colors.WARNING}Warnungen ({len(self.stats['warnings'])}):{Colors.ENDC}")
            for warn in self.stats['warnings'][:5]:
                print(f"  ⚠ {warn}")
            print()
        
        if self.stats['errors']:
            print(f"{Colors.FAIL}Fehler ({len(self.stats['errors'])}):{Colors.ENDC}")
            for err in self.stats['errors']:
                print(f"  ✗ {err}")
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
        print("║           GENTOO SYSTEM UPDATER                                    ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        try:
            self.check_root_privileges()
            
            # Prüfe Festplattenspeicher
            if not self.check_disk_space():
                sys.exit(1)
            
            # Erstelle Backup
            self.backup_important_files()
            
            # Vorbereitung: Räume Manifest-Fehler auf
            self.cleanup_manifest_quarantine()
            
            # Schritt 1: Sync
            if not self.sync_repositories():
                self.print_error("Repository-Synchronisation fehlgeschlagen nach 2 Versuchen")
                update_success = False
                sys.exit(1)
            
            # Schritt 2: eix-update
            self.update_eix()
            
            # Schritt 3: Prüfe Updates
            has_updates, pretend_output = self.check_updates()
            
            if not has_updates and not self.dry_run:
                self.check_config_updates()
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
            
            # Schritt 9: Config-Check
            self.check_config_updates()
            
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
    parser = argparse.ArgumentParser(
        description='Gentoo System Updater - Automatisiert System-Updates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  sudo gentoo-updater                    # Vollständiges System-Update
  sudo gentoo-updater --dry-run          # Zeige was gemacht würde
  sudo gentoo-updater --verbose          # Ausführliche Ausgabe
  sudo gentoo-updater --create-config    # Erstelle Default-Config
        """
    )
    
    parser.add_argument('-v', '--verbose', 
                       action='store_true',
                       help='Ausführliche Ausgabe')
    parser.add_argument('-n', '--dry-run',
                       action='store_true', 
                       help='Zeige nur was gemacht würde, ohne es auszuführen')
    parser.add_argument('--rebuild-modules',
                       action='store_true',
                       help='Erzwingt Neucompilierung der Kernel-Module')
    parser.add_argument('--create-config',
                       action='store_true',
                       help='Erstellt Default-Konfigurationsdatei')
    parser.add_argument('--config',
                       type=str,
                       default='/etc/gentoo-updater.conf',
                       help='Pfad zur Konfigurationsdatei')
    parser.add_argument('--version',
                       action='version',
                       version='Gentoo Updater v1.2.1')
    
    args = parser.parse_args()
    
    # Config erstellen wenn gewünscht
    if args.create_config:
        config = Config(args.config)
        config.save_default_config()
        sys.exit(0)
    
    try:
        config = Config(args.config)
        updater = GentooUpdater(
            verbose=args.verbose, 
            dry_run=args.dry_run,
            rebuild_modules=args.rebuild_modules,
            config=config
        )
        
        # Wenn nur Module neu gebaut werden sollen
        if args.rebuild_modules:
            updater.run_modules_only()
        else:
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
