#!/usr/bin/env python3
"""
Gentoo System Updater
Automatisches Update-Skript für Gentoo Linux
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime
from typing import Optional, List


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


class GentooUpdater:
    """Hauptklasse für Gentoo System-Updates"""
    
    def __init__(self, verbose: bool = False, dry_run: bool = False):
        self.verbose = verbose
        self.dry_run = dry_run
        self.log_file = f"/var/log/gentoo-updater-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        
    def print_section(self, message: str):
        """Gibt einen formatierten Abschnitts-Header aus"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")
        
    def print_info(self, message: str):
        """Gibt eine Info-Nachricht aus"""
        print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {message}")
        
    def print_success(self, message: str):
        """Gibt eine Erfolgs-Nachricht aus"""
        print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {message}")
        
    def print_warning(self, message: str):
        """Gibt eine Warn-Nachricht aus"""
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {message}")
        
    def print_error(self, message: str):
        """Gibt eine Fehler-Nachricht aus"""
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {message}")
        
    def check_root_privileges(self):
        """Prüft, ob das Skript mit Root-Rechten läuft"""
        if os.geteuid() != 0:
            self.print_error("Dieses Skript benötigt Root-Rechte.")
            self.print_info("Bitte mit sudo ausführen: sudo gentoo-updater")
            sys.exit(1)
            
    def run_command(self, command: List[str], description: str, 
                    allow_fail: bool = False) -> bool:
        """
        Führt einen Befehl aus und gibt den Status zurück
        
        Args:
            command: Befehlsliste
            description: Beschreibung für Log
            allow_fail: Wenn True, wird bei Fehler nicht abgebrochen
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        self.print_info(f"{description}...")
        
        if self.dry_run:
            self.print_warning(f"DRY-RUN: Würde ausführen: {' '.join(command)}")
            return True
            
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Echtzeit-Ausgabe
            for line in process.stdout:
                print(line, end='')
                
            process.wait()
            
            if process.returncode == 0:
                self.print_success(f"{description} erfolgreich abgeschlossen")
                return True
            else:
                self.print_error(f"{description} fehlgeschlagen (Exit Code: {process.returncode})")
                if not allow_fail:
                    sys.exit(1)
                return False
                
        except FileNotFoundError:
            self.print_error(f"Befehl nicht gefunden: {command[0]}")
            if not allow_fail:
                sys.exit(1)
            return False
        except Exception as e:
            self.print_error(f"Fehler bei {description}: {str(e)}")
            if not allow_fail:
                sys.exit(1)
            return False
            
    def sync_repositories(self):
        """Synchronisiert die Portage-Repositories"""
        self.print_section("SCHRITT 1: Repository-Synchronisation")
        return self.run_command(
            ["emerge", "--sync"],
            "Synchronisiere Portage-Repositories"
        )
        
    def update_eix(self):
        """Aktualisiert die eix-Datenbank"""
        self.print_section("SCHRITT 2: eix-Datenbank aktualisieren")
        
        # Prüfe ob eix installiert ist
        try:
            subprocess.run(["which", "eix"], check=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            self.print_warning("eix ist nicht installiert, überspringe...")
            return True
            
        return self.run_command(
            ["eix-update"],
            "Aktualisiere eix-Datenbank"
        )
        
    def check_updates(self) -> bool:
        """Prüft ob Updates verfügbar sind"""
        self.print_section("SCHRITT 3: Prüfe verfügbare Updates")
        
        try:
            result = subprocess.run(
                ["emerge", "--update", "--deep", "--newuse", 
                 "--pretend", "@world"],
                capture_output=True,
                text=True
            )
            
            if "Total: 0 packages" in result.stdout:
                self.print_success("Keine Updates verfügbar - System ist aktuell!")
                return False
            else:
                self.print_info("Updates verfügbar:")
                print(result.stdout)
                return True
                
        except Exception as e:
            self.print_error(f"Fehler beim Prüfen der Updates: {str(e)}")
            return False
            
    def update_system(self):
        """Aktualisiert das gesamte System"""
        self.print_section("SCHRITT 4: System-Update")
        return self.run_command(
            ["emerge", "--update", "--deep", "--newuse", 
             "--with-bdeps=y", "@world"],
            "Aktualisiere System-Pakete"
        )
        
    def depclean(self):
        """Entfernt nicht mehr benötigte Pakete"""
        self.print_section("SCHRITT 5: Bereinige verwaiste Pakete")
        return self.run_command(
            ["emerge", "--depclean", "--ask=n"],
            "Entferne nicht mehr benötigte Pakete",
            allow_fail=True
        )
        
    def revdep_rebuild(self):
        """Baut Pakete mit kaputten Abhängigkeiten neu"""
        self.print_section("SCHRITT 6: Prüfe und repariere Abhängigkeiten")
        
        # Prüfe ob revdep-rebuild verfügbar ist
        try:
            subprocess.run(["which", "revdep-rebuild"], check=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            self.print_warning("revdep-rebuild nicht gefunden (gentoolkit installieren?)")
            return True
            
        return self.run_command(
            ["revdep-rebuild"],
            "Repariere kaputte Abhängigkeiten",
            allow_fail=True
        )
        
    def check_kernel_updates(self):
        """Prüft ob Kernel-Updates verfügbar sind"""
        self.print_section("SCHRITT 7: Kernel-Update-Prüfung")
        
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
        self.print_section("SCHRITT 8: Konfigurationsdateien prüfen")
        
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
            
    def run_full_update(self):
        """Führt ein komplettes System-Update durch"""
        start_time = datetime.now()
        
        print(f"{Colors.BOLD}{Colors.OKCYAN}")
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║           GENTOO SYSTEM UPDATER                                    ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        self.check_root_privileges()
        
        # Schritt 1: Sync
        self.sync_repositories()
        
        # Schritt 2: eix-update
        self.update_eix()
        
        # Schritt 3: Prüfe Updates
        has_updates = self.check_updates()
        
        if not has_updates and not self.dry_run:
            self.check_config_updates()
            end_time = datetime.now()
            duration = end_time - start_time
            self.print_section("Update abgeschlossen")
            self.print_success(f"Gesamtdauer: {duration}")
            return
            
        # Schritt 4: System-Update
        self.update_system()
        
        # Schritt 5: Depclean
        self.depclean()
        
        # Schritt 6: revdep-rebuild
        self.revdep_rebuild()
        
        # Schritt 7: Kernel-Check
        self.check_kernel_updates()
        
        # Schritt 8: Config-Check
        self.check_config_updates()
        
        # Zusammenfassung
        end_time = datetime.now()
        duration = end_time - start_time
        
        self.print_section("Update abgeschlossen")
        self.print_success(f"Gesamtdauer: {duration}")
        self.print_info("Bitte Kernel-Updates und Konfigurations-Änderungen manuell prüfen")
        

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(
        description='Gentoo System Updater - Automatisiert System-Updates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  sudo gentoo-updater              # Vollständiges System-Update
  sudo gentoo-updater --dry-run    # Zeige was gemacht würde
  sudo gentoo-updater --verbose    # Ausführliche Ausgabe
        """
    )
    
    parser.add_argument('-v', '--verbose', 
                       action='store_true',
                       help='Ausführliche Ausgabe')
    parser.add_argument('-n', '--dry-run',
                       action='store_true', 
                       help='Zeige nur was gemacht würde, ohne es auszuführen')
    parser.add_argument('--version',
                       action='version',
                       version='Gentoo Updater v1.0.0')
    
    args = parser.parse_args()
    
    try:
        updater = GentooUpdater(verbose=args.verbose, dry_run=args.dry_run)
        updater.run_full_update()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Update durch Benutzer abgebrochen{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.FAIL}Unerwarteter Fehler: {str(e)}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
