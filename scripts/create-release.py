#!/usr/bin/env python3
"""
Gentoo Updater - Automatische Release-Erstellung
Erstellt neue Releases, aktualisiert Versionsnummern und verwaltet GitHub Integration
"""

import os
import sys
import re
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Optional

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
    
    def update_all_versions(self, new_version: str):
        """Aktualisiert alle Versionsnummern im Projekt"""
        print_info(f"Aktualisiere Versionen zu v{new_version}...")
        
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
            else:
                print_warning(f"Keine Änderungen in {file_path.name}")

class ReleaseManager:
    """Verwaltet Release-Prozess"""
    
    def __init__(self, project_root: Path, new_version: str, auto_mode: bool = False):
        self.project_root = project_root
        self.new_version = new_version
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
                return False, result.stderr
            return True, result.stdout
        except Exception as e:
            return False, str(e)
    
    def generate_release_notes(self) -> str:
        """Generiert Release-Notes aus Git-Commits"""
        print_info("Generiere Release-Notes...")
        
        # Hole letzten Tag
        success, last_tag = self.run_command(['git', 'tag', '--list', '-n0', '--sort=-version:refname'], "Get last tag")
        
        if success and last_tag.strip():
            last_version = last_tag.strip().split('\n')[0]
        else:
            last_version = 'HEAD'
        
        # Hole Commits seit letztem Tag
        success, commits = self.run_command(['git', 'log', f'{last_version}..HEAD', '--pretty=format:%s'], "Get commits")
        
        if not success or not commits.strip():
            return f"Release v{self.new_version}"
        
        # Kategorisiere Commits
        features = []
        fixes = []
        improvements = []
        other = []
        
        for commit in commits.strip().split('\n'):
            if not commit:
                continue
            
            if commit.lower().startswith(('feat:', 'feature:', 'add:', '✨')):
                features.append(commit)
            elif commit.lower().startswith(('fix:', 'bug:', '🐛')):
                fixes.append(commit)
            elif commit.lower().startswith(('improve:', 'perf:', '⚡')):
                improvements.append(commit)
            else:
                other.append(commit)
        
        # Baue Release-Notes
        notes = f"# Release v{self.new_version}\n\n"
        
        if features:
            notes += "## ✨ Neue Features\n"
            for f in features:
                notes += f"- {f}\n"
            notes += "\n"
        
        if fixes:
            notes += "## 🐛 Bugfixes\n"
            for fix in fixes:
                notes += f"- {fix}\n"
            notes += "\n"
        
        if improvements:
            notes += "## ⚡ Verbesserungen\n"
            for imp in improvements:
                notes += f"- {imp}\n"
            notes += "\n"
        
        if other:
            notes += "## 📝 Andere Änderungen\n"
            for o in other:
                notes += f"- {o}\n"
            notes += "\n"
        
        notes += f"**Veröffentlicht:** {datetime.now().strftime('%d. %B %Y')}\n"
        
        return notes
    
    def create_release_file(self) -> Path:
        """Erstellt Release-Notizen Datei"""
        self.release_dir.mkdir(exist_ok=True)
        release_file = self.release_dir / f"v{self.new_version}.md"
        
        notes = self.generate_release_notes()
        
        with open(release_file, 'w') as f:
            f.write(notes)
        
        print_success(f"Release-Notes erstellt: {release_file}")
        return release_file
    
    def update_changelog(self):
        """Aktualisiert CHANGELOG.md"""
        changelog = self.project_root / 'CHANGELOG.md'
        
        if not changelog.exists():
            print_warning("CHANGELOG.md nicht gefunden")
            return
        
        entry = f"## v{self.new_version} ({datetime.now().strftime('%Y-%m-%d')})\n"
        entry += "- Release\n\n"
        
        with open(changelog, 'r') as f:
            content = f.read()
        
        with open(changelog, 'w') as f:
            f.write(entry + content)
        
        print_success("CHANGELOG.md aktualisiert")
    
    def commit_changes(self):
        """Committed alle Änderungen"""
        print_info("Committe Änderungen...")
        
        success, msg = self.run_command(['git', 'add', '-A'], "Stage changes")
        if not success:
            print_error(f"Git add fehlgeschlagen: {msg}")
            return False
        
        commit_msg = f"v{self.new_version} - Release"
        success, msg = self.run_command(['git', 'commit', '-m', commit_msg], "Commit")
        
        if not success:
            print_warning("Nichts zu committen")
            return False
        
        print_success(f"Committed: {commit_msg}")
        return True
    
    def create_git_tag(self):
        """Erstellt Git Tag"""
        print_info("Erstelle Git Tag...")
        
        tag_msg = f"Release v{self.new_version}"
        success, msg = self.run_command(
            ['git', 'tag', '-a', f'v{self.new_version}', '-m', tag_msg],
            "Create tag"
        )
        
        if success:
            print_success(f"Tag erstellt: v{self.new_version}")
            return True
        else:
            print_error(f"Tag-Erstellung fehlgeschlagen: {msg}")
            return False
    
    def push_to_github(self):
        """Pusht zu GitHub"""
        print_info("Pushe zu GitHub...")
        
        # Push commits
        success, msg = self.run_command(['git', 'push', 'origin', 'main'], "Push commits")
        if not success:
            print_error(f"Push fehlgeschlagen: {msg}")
            return False
        
        print_success("Commits gepusht")
        
        # Push tags
        success, msg = self.run_command(['git', 'push', 'origin', f'v{self.new_version}'], "Push tag")
        if not success:
            print_warning(f"Tag-Push fehlgeschlagen: {msg}")
            return False
        
        print_success("Tags gepusht")
        return True
    
    def create_github_release(self):
        """Erstellt GitHub Release"""
        print_info("Erstelle GitHub Release...")
        
        # Prüfe ob gh installiert ist
        try:
            subprocess.run(['which', 'gh'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print_warning("gh CLI nicht installiert - überspringe GitHub Release")
            return False
        
        release_file = self.project_root / 'releases' / f"v{self.new_version}.md"
        
        if release_file.exists():
            with open(release_file, 'r') as f:
                body = f.read()
        else:
            body = f"Release v{self.new_version}"
        
        # Schreibe Body in temporäre Datei für gh (robuster als inline)
        try:
            cmd = [
                'gh', 'release', 'create',
                f'v{self.new_version}',
                f'--title', f'v{self.new_version} - Release',
                f'--notes-file', '-'
            ]
            
            result = subprocess.run(
                cmd,
                input=body,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print_success(f"GitHub Release erstellt: v{self.new_version}")
                return True
            else:
                # Fallback: ohne Notes-Datei
                cmd_simple = [
                    'gh', 'release', 'create',
                    f'v{self.new_version}',
                    f'--title', f'v{self.new_version} - Release'
                ]
                
                result = subprocess.run(cmd_simple, capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    print_success(f"GitHub Release erstellt (ohne Notes): v{self.new_version}")
                    return True
                else:
                    print_warning(f"GitHub Release-Erstellung fehlgeschlagen")
                    return False
        except Exception as e:
            print_warning(f"GitHub Release-Fehler: {e}")
            return False
    
    def create_github_discussion(self):
        """GitHub Discussion wird via GitHub Action erstellt (automatisch)"""
        print_info("GitHub Discussions...")
        
        print_success("✅ GitHub Action erstellt Discussion automatisch!")
        print_info(f"→ Workflow: .github/workflows/create-discussion.yml")
        print_info(f"→ Wird bei neuen Tags automatisch ausgelöst")
        print_info(f"   https://github.com/imme-php/gentoo-updater/discussions")
        
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
        '--skip-github',
        action='store_true',
        help='Überspringe GitHub Release und Discussion'
    )
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    
    # Banner
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          GENTOO UPDATER - RELEASE MANAGER (Python)               ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    # Initialisiere Version Manager
    version_manager = VersionManager(project_root)
    print_info(f"Aktuelle Version: v{version_manager.current_version}")
    
    # Bump Version
    new_version = version_manager.bump_version(args.bump_type)
    print_info(f"Neue Version: v{new_version} ({args.bump_type} bump)")
    
    # Bestätigung (wenn nicht auto)
    if not args.auto:
        response = input(f"\n{Colors.YELLOW}Fortfahren mit Release v{new_version}? [y/N]: {Colors.ENDC}")
        if response.lower() != 'y':
            print_warning("Release abgebrochen")
            sys.exit(0)
    else:
        print_info("Auto-Mode: Fahre automatisch fort...")
    
    # Aktualisiere alle Versionsnummern
    version_manager.update_all_versions(new_version)
    
    # Release Manager
    release_manager = ReleaseManager(project_root, new_version, args.auto)
    
    # Erstelle Release-Datei
    release_manager.create_release_file()
    
    # Aktualisiere CHANGELOG
    release_manager.update_changelog()
    
    # Git Workflow
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}=== Git Workflow ==={Colors.ENDC}\n")
    
    if not release_manager.commit_changes():
        print_warning("Commit fehlgeschlagen, fahre fort...")
    
    if not release_manager.create_git_tag():
        print_error("Tag-Erstellung fehlgeschlagen")
        sys.exit(1)
    
    if not release_manager.push_to_github():
        print_error("Push zu GitHub fehlgeschlagen")
        sys.exit(1)
    
    # GitHub Release
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}=== GitHub Integration ==={Colors.ENDC}\n")
    
    if not args.skip_github:
        release_manager.create_github_release()
        release_manager.create_github_discussion()
    else:
        print_warning("GitHub-Integration übersprungen")
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.OKGREEN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print(f"║          RELEASE v{new_version} ERFOLGREICH ERSTELLT                        ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    print_success(f"Release v{new_version} ist bereit!")
    print_info(f"GitHub: https://github.com/imme-php/gentoo-updater/releases/tag/v{new_version}")

if __name__ == '__main__':
    main()
