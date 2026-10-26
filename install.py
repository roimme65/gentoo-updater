#!/usr/bin/env python3
"""
Gentoo Updater - Installation Script
Installiert gentoo-updater und prüft Abhängigkeiten
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

# Versionsverwaltung - synchronisiert mit gentoo-updater.py (über scripts/create-release.py)
__version__ = "1.4.44"
__author__ = "Roland Imme"
__license__ = "MIT"

# Mindestversion für gentoo-updater.py (argparse.BooleanOptionalAction)
MIN_PYTHON_VERSION = (3, 9)


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


def print_info(msg: str):
    """Gibt eine Info-Nachricht aus"""
    print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {msg}")


def print_success(msg: str):
    """Gibt eine Erfolgs-Nachricht aus"""
    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {msg}")


def print_warning(msg: str):
    """Gibt eine Warn-Nachricht aus"""
    print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {msg}")


def print_error(msg: str):
    """Gibt eine Fehler-Nachricht aus"""
    print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {msg}")


def print_header(title: str):
    """Gibt einen formatierten Header aus"""
    print()
    print(f"{Colors.BOLD}{Colors.OKCYAN}╔════════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}║ {title:^66} ║{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}╚════════════════════════════════════════════════════════════════════╝{Colors.ENDC}")
    print()


def ask_yes_no(prompt: str) -> bool:
    """Fragt ja/nein ab (Standard: nein, auch ohne Terminal)"""
    while True:
        try:
            response = input(f"{prompt} [y/N]: ").strip().lower()
        except EOFError:
            print()
            return False
        if response in ['y', 'yes', 'j', 'ja']:
            return True
        if response in ['n', 'no', 'nein', '']:
            return False
        print("Bitte antworte mit 'y' oder 'n'")


class SystemChecker:
    """Prüft Systemvoraussetzungen"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.optional_missing = []
    
    def check_root_privileges(self) -> bool:
        """Prüft ob das Skript mit Root-Rechten läuft"""
        print_info("Prüfe Root-Rechte...")
        
        if os.geteuid() != 0:
            print_error("Dieses Skript benötigt Root-Rechte!")
            print_info("Bitte mit sudo ausführen: sudo python3 install.py")
            self.errors.append("Keine Root-Rechte")
            return False
        
        print_success("Root-Rechte vorhanden")
        return True
    
    def check_python3(self) -> bool:
        """Prüft ob das python3 aus PATH die Mindestversion erfüllt

        gentoo-updater startet über '#!/usr/bin/env python3', daher zählt dieses
        python3 und nicht der Interpreter, mit dem install.py läuft.
        """
        min_version = '.'.join(map(str, MIN_PYTHON_VERSION))
        print_info(f"Prüfe Python-Version (mindestens {min_version})...")

        try:
            result = subprocess.run(
                ["python3", "-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            print_error("python3 wurde nicht im PATH gefunden!")
            print_info("Installation: emerge --ask dev-lang/python")
            self.errors.append("Python 3 nicht gefunden")
            return False

        if tuple(map(int, version.split('.')[:2])) < MIN_PYTHON_VERSION:
            print_error(f"Python {version} ist zu alt, benötigt wird mindestens {min_version}")
            self.errors.append(f"Python {version} < {min_version}")
            return False

        print_success(f"Python gefunden: {version}")
        return True
    
    def check_gentoo_linux(self) -> bool:
        """Prüft ob auf Gentoo Linux läuft"""
        print_info("Prüfe Gentoo Linux...")
        
        gentoo_release = Path("/etc/gentoo-release")
        
        if not gentoo_release.exists():
            print_warning("Dies scheint nicht Gentoo Linux zu sein!")
            
            # Frage Benutzer (ohne Terminal: abbrechen)
            if ask_yes_no("Trotzdem fortfahren?"):
                self.warnings.append("Nicht auf Gentoo Linux")
                return True
            self.errors.append("Installation auf Nicht-Gentoo-System abgebrochen")
            return False
        else:
            try:
                with open(gentoo_release, 'r') as f:
                    gentoo_info = f.read().strip()
                print_success(f"Gentoo Linux erkannt: {gentoo_info}")
                return True
            except Exception as e:
                print_warning(f"Konnte Gentoo-Info nicht lesen: {e}")
                return True
    
    def check_optional_dependencies(self):
        """Prüft optionale Dependencies"""
        print_info("Prüfe optionale Abhängigkeiten...")
        
        # eix
        if self._command_exists("eix"):
            print_success("eix ist installiert")
        else:
            print_warning("eix ist nicht installiert (empfohlen für schnellere Paketsuchen)")
            print(f"           Installation: emerge --ask app-portage/eix")
            self.optional_missing.append("eix")
        
        # revdep-rebuild
        if self._command_exists("revdep-rebuild"):
            print_success("revdep-rebuild ist installiert")
        else:
            print_warning("gentoolkit ist nicht installiert (empfohlen für revdep-rebuild)")
            print(f"           Installation: emerge --ask app-portage/gentoolkit")
            self.optional_missing.append("gentoolkit")
        
        # mirrorselect
        if self._command_exists("mirrorselect"):
            print_success("mirrorselect ist installiert")
        else:
            print_warning("mirrorselect ist nicht installiert (optional für 'gentoo-updater --use-mirrorselect')")
            print(f"           Installation: emerge --ask app-portage/mirrorselect")
            self.optional_missing.append("mirrorselect")
    
    @staticmethod
    def _command_exists(command: str) -> bool:
        """Prüft ob ein Befehl existiert (ohne externes 'which')"""
        return shutil.which(command) is not None
    
    def run_all_checks(self) -> bool:
        """Führt alle Checks durch"""
        print_header("SYSTEM-PRÜFUNG")
        
        results = [
            self.check_root_privileges(),
            self.check_python3(),
            self.check_gentoo_linux()
        ]
        
        if not all(results):
            print()
            for error in self.errors:
                print_error(error)
            return False
        
        print()
        self.check_optional_dependencies()
        return True


class Installer:
    """Installiert gentoo-updater"""
    
    INSTALL_DIR = "/usr/local/bin"
    SCRIPT_NAME = "gentoo-updater"
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.source_file = self.project_root / "gentoo-updater.py"
        self.dest_file = Path(self.INSTALL_DIR) / self.SCRIPT_NAME
    
    def install(self) -> bool:
        """Installiert das Skript"""
        print_header("INSTALLATION")
        
        # Prüfe ob Quelle existiert
        if not self.source_file.exists():
            print_error(f"Quell-Datei nicht gefunden: {self.source_file}")
            return False
        
        print_info(f"Installiere gentoo-updater v{__version__}...")
        
        try:
            # Stelle sicher dass install_dir existiert
            Path(self.INSTALL_DIR).mkdir(parents=True, exist_ok=True)
            
            # Kopiere Datei
            shutil.copy2(self.source_file, self.dest_file)
            
            # Mache ausführbar
            os.chmod(self.dest_file, 0o755)
            
            print_success(f"Installiert in: {self.dest_file}")
            return True
        
        except PermissionError:
            print_error(f"Keine Berechtigung, in {self.INSTALL_DIR} zu schreiben!")
            print_info("Stelle sicher, dass du sudo verwendest")
            return False
        except Exception as e:
            print_error(f"Installationsfehler: {e}")
            return False
    
    def print_usage_examples(self):
        """Zeigt Usage-Beispiele"""
        print()
        print_info("Verwendungsbeispiele:")
        print()
        examples = [
            ("sudo gentoo-updater", "Vollständiges System-Update"),
            ("sudo gentoo-updater --dry-run", "Test-Modus"),
            ("sudo gentoo-updater --lang de", "Deutsche Sprache"),
            ("sudo gentoo-updater --log-level DEBUG", "Debug-Ausgabe"),
            ("sudo gentoo-updater --only-sync", "Nur Repository-Synchronisation"),
            ("sudo gentoo-updater --skip-cleanup", "Depclean überspringen"),
            ("sudo gentoo-updater --german-mirrors", "Deutsche Mirrors setzen"),
            ("sudo gentoo-updater --use-mirrorselect", "Mirrors interaktiv auswählen"),
            ("sudo gentoo-updater --mirrors 'url1,url2'", "Eigene Mirrors (komma-getrennt)"),
            ("sudo gentoo-updater --repository", "GitHub Repository-Info"),
            ("sudo gentoo-updater --author", "Author und Version"),
            ("sudo gentoo-updater --license", "Lizenz-Info"),
            ("sudo gentoo-updater --help", "Detaillierte Hilfe"),
        ]
        
        for cmd, desc in examples:
            print(f"  {cmd:<50} # {desc}")
        print()
    
    def ask_install_optional_dependencies(self, optional_missing: list) -> bool:
        """Fragt ob optionale Dependencies installiert werden sollen"""
        if not optional_missing:
            return True
        
        print()
        if ask_yes_no("Möchtest du die empfohlenen Pakete installieren?"):
            return self._install_optional_packages(optional_missing)
        return True

    @staticmethod
    def _install_optional_packages(packages: list) -> bool:
        """Installiert optionale Pakete (ein emerge-Aufruf mit einer Rückfrage)"""
        package_map = {
            'eix': 'app-portage/eix',
            'gentoolkit': 'app-portage/gentoolkit',
            'mirrorselect': 'app-portage/mirrorselect'
        }

        portage_pkgs = [package_map[pkg] for pkg in packages if pkg in package_map]
        if not portage_pkgs:
            return True

        print_info(f"Installiere {', '.join(portage_pkgs)}...")
        try:
            subprocess.run(["emerge", "--ask", *portage_pkgs], check=False)
        except Exception as e:
            print_warning(f"Konnte Pakete nicht installieren: {e}")

        return True


def main():
    """Hauptfunktion - Installation/Update von gentoo-updater"""
    # CLI Argument Parser
    parser = argparse.ArgumentParser(
        description='Gentoo Updater - Installation und Update',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  sudo python3 install.py              # Installiere/Update gentoo-updater
  python3 install.py --version         # Zeige aktuelle Version

Hinweis:
  Versionsverwaltung erfolgt ausschließlich über:
  python3 scripts/create-release.py [major|minor|patch]
"""
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Zeige aktuelle Version'
    )
    
    args = parser.parse_args()
    
    try:
        # Versions-Info
        if args.version:
            print_header("VERSION INFO")
            print(f"gentoo-updater: v{__version__}")
            print(f"Author: {__author__}")
            print(f"License: {__license__}")
            print()
            return
        
        # Standard: Installation/Update
        print_header("GENTOO UPDATER INSTALLATION/UPDATE")
        
        # System-Checks
        checker = SystemChecker()
        if not checker.run_all_checks():
            sys.exit(1)
        
        # Installation/Update
        installer = Installer()
        if not installer.install():
            sys.exit(1)
        
        # Abschluss
        print_header("INSTALLATION ABGESCHLOSSEN")
        print_success("gentoo-updater wurde erfolgreich installiert/aktualisiert!")
        
        installer.print_usage_examples()
        
        # Optionale Dependencies
        if checker.optional_missing:
            installer.ask_install_optional_dependencies(checker.optional_missing)
        
        # Finale Info
        print()
        print_info("Du kannst gentoo-updater jetzt starten mit:")
        print(f"  {Colors.BOLD}sudo gentoo-updater{Colors.ENDC}")
        print()
        print_info("Für neue Release via:")
        print(f"  {Colors.BOLD}python3 scripts/create-release.py [major|minor|patch]{Colors.ENDC}")
        print()
        
    except KeyboardInterrupt:
        print()
        print_warning("Installation abgebrochen")
        sys.exit(130)
    except Exception as e:
        print()
        print_error(f"Unerwarteter Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
