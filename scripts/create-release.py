#!/usr/bin/env python3
"""
Gentoo Updater - Automatische Release-Erstellung
Erhöht die Versionsnummer, erstellt Release-Notes, committet, taggt und pusht.
GitHub Release und Discussion werden anschließend von den GitHub Actions erstellt
(.github/workflows/release.yml und create-discussion.yml).
"""

import sys
import re
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Tuple, List

GITHUB_REPO_URL = 'https://github.com/roimme65/gentoo-updater'
RELEASE_BRANCH = 'main'

GERMAN_MONTHS = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli',
                 'August', 'September', 'Oktober', 'November', 'Dezember']

# Farben
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_info(msg: str):
    print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {msg}")

def print_success(msg: str):
    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {msg}")

def print_warning(msg: str):
    print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {msg}")

def print_error(msg: str):
    print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {msg}")

def german_date(date: datetime) -> str:
    """Datum unabhängig von der System-Locale, z.B. '10. April 2026'"""
    return f"{date.day}. {GERMAN_MONTHS[date.month - 1]} {date.year}"

class VersionManager:
    """Verwaltet Versionsnummern im Projekt"""

    VERSION_PATTERNS = [
        # gentoo-updater.py - __version__ Variable (zentral)
        {
            'file': 'gentoo-updater.py',
            'pattern': r'(__version__\s*=\s*")(\d+\.\d+\.\d+)(")',
            'replacement': r'\g<1>{version}\g<3>'
        },
        # install.py - __version__ Variable
        {
            'file': 'install.py',
            'pattern': r'(__version__\s*=\s*")(\d+\.\d+\.\d+)(")',
            'replacement': r'\g<1>{version}\g<3>'
        },
    ]

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.current_version = self.get_current_version()

    def get_current_version(self) -> str:
        """Extrahiert aktuelle Version aus __version__ in gentoo-updater.py"""
        py_file = self.project_root / 'gentoo-updater.py'

        with open(py_file, 'r') as f:
            content = f.read()

        # Suche nach __version__ Variable (zentral)
        match = re.search(r'__version__\s*=\s*"(\d+\.\d+\.\d+)"', content)
        if match:
            return match.group(1)

        print_error("Konnte aktuelle Version nicht ermitteln")
        sys.exit(1)

    def bump_version(self, bump_type: str) -> str:
        """Erhöht Versionsnummer"""
        major, minor, patch = map(int, self.current_version.split('.'))

        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        elif bump_type == 'patch':
            patch += 1
        else:
            raise ValueError(f"Unbekannter Bump-Typ: {bump_type}")

        return f"{major}.{minor}.{patch}"

    def update_all_versions(self, new_version: str) -> List[str]:
        """Aktualisiert alle Versionsnummern im Projekt

        Returns:
            Liste der geänderten Dateien (relativ zum Projekt)
        """
        print_info(f"Aktualisiere Versionen zu v{new_version}...")
        changed = []

        for pattern_info in self.VERSION_PATTERNS:
            file_path = self.project_root / pattern_info['file']

            if not file_path.exists():
                print_warning(f"Datei nicht gefunden: {file_path}")
                continue

            with open(file_path, 'r') as f:
                content = f.read()

            # Ersetze mit Pattern
            new_content = re.sub(
                pattern_info['pattern'],
                pattern_info['replacement'].format(version=new_version),
                content
            )

            if new_content != content:
                with open(file_path, 'w') as f:
                    f.write(new_content)
                print_success(f"✓ {file_path.name} aktualisiert")
                changed.append(pattern_info['file'])
            else:
                print_warning(f"Keine Änderungen in {file_path.name}")

        return changed

class ReleaseManager:
    """Verwaltet Release-Prozess"""

    # Commit-Präfixe (Conventional Commits, optional mit Scope und "!")
    CATEGORY_PATTERNS = [
        ('features', r'^(feat|feature|add)(\(.+?\))?!?:|^(✨|🆕)'),
        ('fixes', r'^(fix|bugfix|bug)(\(.+?\))?!?:|^(🐛|🔧)'),
        ('improvements', r'^(improve|perf|refactor)(\(.+?\))?!?:|^⚡'),
        ('security', r'^(sec|security)(\(.+?\))?!?:|^🔐'),
        ('docs', r'^(docs|doc|readme|documentation)(\(.+?\))?!?:|^📝'),
    ]

    def __init__(self, project_root: Path, new_version: str, auto_mode: bool = False):
        self.project_root = project_root
        self.new_version = new_version
        self.tag = f'v{new_version}'
        self.auto_mode = auto_mode
        self.release_dir = project_root / 'releases'

    def run_command(self, cmd: List[str], description: str = "") -> Tuple[bool, str]:
        """Führt Shell-Befehl aus"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.returncode != 0:
                return False, result.stderr.strip() or result.stdout.strip()
            return True, result.stdout
        except Exception as e:
            return False, str(e)

    def check_preconditions(self) -> bool:
        """Prüft, ob ein Release sicher erstellt werden kann

        - Arbeitsverzeichnis sauber (sonst landen fremde Änderungen im Release-Commit)
        - auf dem Release-Branch
        - Tag existiert weder lokal noch auf GitHub
        - lokaler Branch ist nicht hinter origin
        """
        print_info("Prüfe Voraussetzungen...")
        ok = True

        success, status = self.run_command(['git', 'status', '--porcelain'])
        if not success:
            print_error(f"git status fehlgeschlagen: {status}")
            return False
        if status.strip():
            print_error("Arbeitsverzeichnis enthält nicht committete Änderungen:")
            print(status.rstrip())
            print_info("Bitte zuerst committen oder stashen - sie würden sonst im Release-Commit landen")
            ok = False

        success, branch = self.run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        branch = branch.strip()
        if not success or branch != RELEASE_BRANCH:
            print_error(f"Releases nur von '{RELEASE_BRANCH}' (aktuell: '{branch}')")
            ok = False

        success, _ = self.run_command(['git', 'rev-parse', '--verify', '--quiet', f'refs/tags/{self.tag}'])
        if success:
            print_error(f"Tag {self.tag} existiert bereits lokal")
            ok = False

        success, remote_tags = self.run_command(['git', 'ls-remote', '--tags', 'origin', f'refs/tags/{self.tag}'])
        if not success:
            print_error(f"Konnte origin nicht abfragen: {remote_tags}")
            ok = False
        elif remote_tags.strip():
            print_error(f"Tag {self.tag} existiert bereits auf origin")
            ok = False

        success, fetch_msg = self.run_command(['git', 'fetch', 'origin', RELEASE_BRANCH])
        if success:
            success, behind = self.run_command(['git', 'rev-list', '--count', f'HEAD..origin/{RELEASE_BRANCH}'])
            if success and behind.strip() not in ('', '0'):
                print_error(f"Lokaler Branch ist {behind.strip()} Commit(s) hinter origin/{RELEASE_BRANCH} - bitte zuerst pullen")
                ok = False
        else:
            print_warning(f"git fetch fehlgeschlagen ({fetch_msg}) - überspringe Prüfung auf neuere Commits")

        if ok:
            print_success("Voraussetzungen erfüllt")
        return ok

    def get_commits_since_last_tag(self) -> List[dict]:
        """Liest Commits seit dem letzten Tag (ohne Commit-Body)"""
        success, last_tag_output = self.run_command(['git', 'tag', '--list', 'v*', '--sort=-version:refname'])

        if success and last_tag_output.strip():
            last_version = last_tag_output.strip().split('\n')[0]
            print_info(f"Letzter Tag: {last_version}")
            log_range = f'{last_version}..HEAD'
        else:
            print_info("Kein vorheriger Tag gefunden, verwende alle Commits")
            log_range = 'HEAD'

        # Felder mit \x1f, Commits mit \x1e getrennt - robust gegen "|" und Zeilenumbrüche
        success, commits_output = self.run_command(
            ['git', 'log', log_range, '--pretty=format:%h%x1f%s%x1f%an%x1f%ad%x1e', '--date=short']
        )
        if not success:
            return []

        commits = []
        for record in commits_output.split('\x1e'):
            fields = record.strip().split('\x1f')
            if len(fields) == 4:
                commits.append(dict(zip(['hash', 'subject', 'author', 'date'], fields)))
        return commits

    def generate_release_notes(self) -> str:
        """Generiert Release-Notes aus Git-Commits und dem Unreleased-Abschnitt des CHANGELOG"""
        print_info("Generiere Release-Notes aus Git-Commits...")

        notes = f"# Release v{self.new_version}\n\n"
        notes += f"**Veröffentlicht:** {german_date(datetime.now())}\n"

        commits = self.get_commits_since_last_tag()
        notes += f"**Commits:** {len(commits)}\n\n"
        print_info(f"Gefundene Commits: {len(commits)}")

        # Einträge aus "## Unreleased" im CHANGELOG übernehmen
        unreleased = self.get_unreleased_changelog_entries()
        if unreleased:
            notes += "## 📋 Änderungen\n" + unreleased.strip() + "\n\n"

        categories = {name: [] for name, _ in self.CATEGORY_PATTERNS}
        other = []
        for commit in commits:
            subject = commit['subject']
            entry = f"{subject} ({commit['hash']})"
            for name, pattern in self.CATEGORY_PATTERNS:
                if re.match(pattern, subject, re.IGNORECASE):
                    categories[name].append(entry)
                    break
            else:
                # Release-Commits ("vX.Y.Z - Release") nicht aufführen
                if not re.match(r'^v\d+\.\d+\.\d+ - Release$', subject):
                    other.append(entry)

        sections = [
            ('features', "## ✨ Neue Features"),
            ('security', "## 🔐 Security"),
            ('fixes', "## 🐛 Bugfixes"),
            ('improvements', "## ⚡ Verbesserungen"),
            ('docs', "## 📝 Dokumentation"),
        ]
        for name, title in sections:
            if categories[name]:
                notes += title + "\n" + "".join(f"- {e}\n" for e in categories[name]) + "\n"
        if other:
            notes += "## 🔀 Andere Commits\n" + "".join(f"- {e}\n" for e in other) + "\n"

        if not commits and not unreleased:
            notes += "*Keine Änderungen dokumentiert*\n"

        return notes

    def get_unreleased_changelog_entries(self) -> str:
        """Gibt den Inhalt des obersten '## Unreleased'-Abschnitts im CHANGELOG zurück"""
        changelog = self.project_root / 'CHANGELOG.md'
        if not changelog.exists():
            return ""
        content = changelog.read_text()
        match = re.match(r'\s*## Unreleased[^\n]*\n(.*?)(?=^## |\Z)', content, re.DOTALL | re.MULTILINE)
        return match.group(1) if match else ""

    def create_release_file(self) -> str:
        """Erstellt Release-Notizen Datei

        Returns:
            Pfad relativ zum Projekt
        """
        self.release_dir.mkdir(exist_ok=True)
        release_file = self.release_dir / f"{self.tag}.md"

        notes = self.generate_release_notes()

        with open(release_file, 'w') as f:
            f.write(notes)

        print_success(f"Release-Notes erstellt: {release_file}")
        return str(release_file.relative_to(self.project_root))

    def update_changelog(self) -> bool:
        """Aktualisiert CHANGELOG.md

        Steht oben ein '## Unreleased'-Abschnitt, wird er zur neuen Version umbenannt.
        Sonst wird ein Eintrag ohne Details ergänzt.
        """
        changelog = self.project_root / 'CHANGELOG.md'

        if not changelog.exists():
            print_warning("CHANGELOG.md nicht gefunden")
            return False

        header = f"## {self.tag} ({datetime.now().strftime('%Y-%m-%d')})"
        content = changelog.read_text()

        # Nur ein Unreleased-Abschnitt ganz oben zählt (ältere bleiben unverändert)
        new_content, count = re.subn(r'\A(\s*)## Unreleased[^\n]*', lambda m: m.group(1) + header, content)
        if count:
            print_success(f"CHANGELOG.md: 'Unreleased' → {self.tag}")
        else:
            new_content = f"{header}\n- Release\n\n" + content
            print_warning("Kein 'Unreleased'-Abschnitt im CHANGELOG - füge Eintrag ohne Details hinzu")

        changelog.write_text(new_content)
        return True

    def commit_changes(self, files: List[str]) -> bool:
        """Committed nur die vom Release geänderten Dateien"""
        print_info("Committe Änderungen...")

        success, msg = self.run_command(['git', 'add', '--', *files])
        if not success:
            print_error(f"Git add fehlgeschlagen: {msg}")
            return False

        commit_msg = f"{self.tag} - Release"
        success, msg = self.run_command(['git', 'commit', '-m', commit_msg])

        if not success:
            print_error(f"Commit fehlgeschlagen: {msg}")
            return False

        print_success(f"Committed: {commit_msg}")
        return True

    def create_git_tag(self) -> bool:
        """Erstellt Git Tag"""
        print_info("Erstelle Git Tag...")

        success, msg = self.run_command(
            ['git', 'tag', '-a', self.tag, '-m', f"Release {self.tag}"]
        )

        if success:
            print_success(f"Tag erstellt: {self.tag}")
            return True
        print_error(f"Tag-Erstellung fehlgeschlagen: {msg}")
        return False

    def push_to_github(self) -> bool:
        """Pusht Commit und Tag zu GitHub (der Tag löst die Release-Workflows aus)"""
        print_info("Pushe zu GitHub...")

        success, msg = self.run_command(['git', 'push', 'origin', RELEASE_BRANCH])
        if not success:
            print_error(f"Push fehlgeschlagen: {msg}")
            return False
        print_success("Commits gepusht")

        success, msg = self.run_command(['git', 'push', 'origin', self.tag])
        if not success:
            print_error(f"Tag-Push fehlgeschlagen: {msg}")
            return False
        print_success("Tag gepusht")
        return True

def main():
    parser = argparse.ArgumentParser(
        description='Erstellt automatisch neue Releases für Gentoo Updater',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python scripts/create-release.py patch          # Interaktives Release (1.2.2 → 1.2.3)
  python scripts/create-release.py minor --auto   # Auto (1.2.2 → 1.3.0)
  python scripts/create-release.py major --auto   # Auto (1.2.2 → 2.0.0)
  python scripts/create-release.py patch --no-push  # Nur lokal committen und taggen

Ablauf:
  1. Prüft: sauberes Arbeitsverzeichnis, Branch main, Tag noch frei, nicht hinter origin
  2. Erhöht die Version in gentoo-updater.py und install.py
  3. Erstellt releases/vX.Y.Z.md und benennt '## Unreleased' im CHANGELOG um
  4. Committet, taggt und pusht
  5. GitHub Actions erstellen Release (release.yml) und Discussion (create-discussion.yml)
        """
    )

    parser.add_argument(
        'bump_type',
        choices=['major', 'minor', 'patch'],
        help='Art der Versionsbumping'
    )

    parser.add_argument(
        '--auto',
        action='store_true',
        help='Vollautomatisches Release ohne Bestätigungen'
    )

    parser.add_argument(
        '--no-push',
        action='store_true',
        help='Nur lokal committen und taggen, nicht pushen'
    )

    parser.add_argument(
        '--skip-github',
        action='store_true',
        help='Veraltet, ohne Wirkung (Release und Discussion erstellen die GitHub Actions)'
    )

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent

    # Banner
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          GENTOO UPDATER - RELEASE MANAGER (Python)                 ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

    # Initialisiere Version Manager
    version_manager = VersionManager(project_root)
    print_info(f"Aktuelle Version: v{version_manager.current_version}")

    # Bump Version
    new_version = version_manager.bump_version(args.bump_type)
    print_info(f"Neue Version: v{new_version} ({args.bump_type} bump)")

    release_manager = ReleaseManager(project_root, new_version, args.auto)

    # Voraussetzungen prüfen, bevor irgendetwas geändert wird
    if not release_manager.check_preconditions():
        print_error("Release abgebrochen - es wurde nichts verändert")
        sys.exit(1)

    # Bestätigung (wenn nicht auto)
    if not args.auto:
        try:
            response = input(f"\n{Colors.WARNING}Fortfahren mit Release v{new_version}? [y/N]: {Colors.ENDC}")
        except EOFError:
            response = ''
        if response.strip().lower() not in ('y', 'yes', 'j', 'ja'):
            print_warning("Release abgebrochen")
            sys.exit(0)
    else:
        print_info("Auto-Mode: Fahre automatisch fort...")

    # Aktualisiere alle Versionsnummern
    changed_files = version_manager.update_all_versions(new_version)

    # Release-Notes vor dem CHANGELOG-Update erzeugen (liest den Unreleased-Abschnitt)
    changed_files.append(release_manager.create_release_file())
    if release_manager.update_changelog():
        changed_files.append('CHANGELOG.md')

    # Git Workflow
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}=== Git Workflow ==={Colors.ENDC}\n")

    if not release_manager.commit_changes(changed_files):
        print_error("Commit fehlgeschlagen - kein Tag erstellt. Änderungen prüfen mit: git status")
        sys.exit(1)

    if not release_manager.create_git_tag():
        sys.exit(1)

    if args.no_push:
        print_warning(f"--no-push: Bitte später pushen mit: git push origin {RELEASE_BRANCH} && git push origin v{new_version}")
    elif not release_manager.push_to_github():
        print_error("Push zu GitHub fehlgeschlagen")
        sys.exit(1)

    # Summary
    print(f"\n{Colors.BOLD}{Colors.OKGREEN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print(f"║ {f'RELEASE v{new_version} ERFOLGREICH ERSTELLT':^66} ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

    if not args.no_push:
        print_info("GitHub Actions erstellen jetzt Release und Discussion:")
        print_info(f"  Workflows:  {GITHUB_REPO_URL}/actions")
        print_info(f"  Release:    {GITHUB_REPO_URL}/releases/tag/v{new_version}")
        print_info(f"  Discussion: {GITHUB_REPO_URL}/discussions")

if __name__ == '__main__':
    main()
