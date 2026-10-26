# Gentoo System Updater

**Languages:** 🇬🇧 [English](README.md) | 🇩🇪 [Deutsch](README.de.md)

Automated update solution for Gentoo Linux that simplifies and automates the entire system update process.

## Features

### 🚀 Performance & Optimization
- ⚡ **Parallel Compilation** with automatic CPU detection (`--jobs` and `--load-average`)
- 📊 **Intelligent Update Detection** - Rebuild kernel modules only when needed
- 💾 **Disk Space Check** before updates
- 🔄 **Automatic Retry** on manifest errors

### 📦 Update Functions
- 🔄 **Repository Synchronisation** (`emerge --sync`)
- 📚 **eix Database Update** (optional)
- 📦 **System Update** (full `@world` update)
- 🔧 **Intelligent Kernel Module Recompilation** (NVIDIA, VirtualBox, etc.)
- 🧹 **Automatic Cleanup** (`emerge --depclean`)
- 🔧 **Dependency Repair** (`revdep-rebuild`)

### 🛡️ Security & Reliability
- 💾 **Automatic Backups** of important configuration files
- 🔍 **Blocked Packages Check** before updates
- ⚠️ **Critical Package Warning** (gcc, glibc, Python)
- 🌐 **Internet Connection Check** (automatic, before starting updates)
- 📝 **Full Logging System** with JSON export
- 🎯 **Robust Error Handling** with detailed logs

### 📊 Monitoring & Reports
- 📈 **Update Summary** with statistics
- 🌍 **Mirror Logging** - Shows all configured Gentoo mirrors & primary mirror
- 📧 **Email Notifications** (optional)
- 📁 **Automatic Log Rotation**
- 🎨 **Colored Output** with clear structure

### ⚙️ Configuration
- 📄 **JSON Configuration File** for customization
- 🔧 **Flexible emerge Options**
- ⚡ **Dry-Run Mode** for testing

### 🆕 v1.4.0 Advanced Parameters
- 🎛️ **--log-level** (DEBUG/INFO/WARNING/ERROR)
- ⏭️ **--skip-*** options (sync, update, eix, cleanup, revdep, internet-check)
- 🎯 **--only-*** options (execute specific steps only)
- 📦 **--max-packages N** (deprecated, ignored)
- ⏱️ **--timeout SECONDS** (set emerge timeout)
- 🔄 **--retry-count N** (retries on sync failure)
- 🛠️ **--auto-autounmask / --no-auto-autounmask** (toggle automatic autounmask recovery + retry)
- 🔔 **--notification-webhook URL** (send notifications)
- ⚙️ **--parallel-jobs N** (override job count)
- 🚫 **--resolve-blocks** (automatically resolve blocked packages with backtracking)
- 📊 **--backtrack N** (set backtrack level, default: 20)
- 🌍 **Environment Variables** (GENTOO_UPDATER_*)

## Requirements

- Gentoo Linux
- Python 3.6+
- Root/sudo privileges
- Optional: `eix` for faster package searches
- Optional: `gentoolkit` for `revdep-rebuild`

## Installation

### Method 1: Automatic Installation (Recommended)

```bash
git clone https://github.com/roimme65/gentoo-updater.git
cd gentoo-updater
sudo python3 install.py
```

### Method 2: Manual Installation

```bash
# Download script
git clone https://github.com/roimme65/gentoo-updater.git
cd gentoo-updater

# Make executable
chmod +x gentoo-updater.py

# Copy to /usr/local/bin (optional)
sudo cp gentoo-updater.py /usr/local/bin/gentoo-updater
```

### Method 3: PyPI (Coming in v1.5.x)

```bash
pip install gentoo-updater
```

## Usage

### Full System Update

```bash
sudo gentoo-updater
```

### Create Configuration

On first run, create default configuration:

```bash
sudo gentoo-updater --create-config
```

This creates `/etc/gentoo-updater.conf` with options:
- **emerge_jobs**: Number of parallel jobs (auto = CPU cores)
- **emerge_load_average**: Maximum system load
- **enable_backups**: Enable automatic backups
- **backup_dir**: Backup directory
- **enable_notifications**: Enable email notifications
- **notification_email**: Email address
- **min_free_space_gb**: Minimum free space required
- **auto_depclean**: Enable automatic depclean
- **auto_revdep_rebuild**: Enable automatic revdep-rebuild
- **critical_packages**: List of critical packages
- **log_retention_days**: Log retention in days

Example config: see [gentoo-updater.conf.example](gentoo-updater.conf.example)

### Dry-Run Mode

```bash
sudo gentoo-updater --dry-run
```

### Verbose Output

```bash
sudo gentoo-updater --verbose
```

### Advanced Parameters (v1.4.0+)

```bash
# Log level control
sudo gentoo-updater --log-level DEBUG

# Skip specific steps
sudo gentoo-updater --skip-cleanup --skip-revdep

# Skip internet connection check (useful for offline systems)
sudo gentoo-updater --skip-internet-check

# Execute only specific steps
sudo gentoo-updater --only-sync      # Only repository sync
sudo gentoo-updater --only-update    # Only system update

# Set timeout per command
sudo gentoo-updater --timeout 3600

# Retry sync up to 3 times on failure
sudo gentoo-updater --retry-count 3

# Override parallel jobs
sudo gentoo-updater --parallel-jobs 8

# Send webhook notification (JSON via POST)
sudo gentoo-updater --notification-webhook "https://example.com/webhook"

# Automatically resolve blocked packages with backtracking
sudo gentoo-updater --resolve-blocks --backtrack 20
```

### Environment Variables (v1.4.0+)

```bash
# Enable dry-run via environment variable
GENTOO_UPDATER_DRY_RUN=true sudo gentoo-updater

# Debug logging
GENTOO_UPDATER_LOG_LEVEL=DEBUG sudo gentoo-updater

# Set timeout
GENTOO_UPDATER_TIMEOUT=3600 sudo gentoo-updater

# Enable retry
GENTOO_UPDATER_RETRY_COUNT=3 sudo gentoo-updater

# Override parallel jobs
GENTOO_UPDATER_PARALLEL_JOBS=4 sudo gentoo-updater

# Skip internet connection check
GENTOO_UPDATER_SKIP_INTERNET_CHECK=true sudo gentoo-updater

# Automatically resolve blocked packages
GENTOO_UPDATER_RESOLVE_BLOCKS=true sudo gentoo-updater

# Set backtrack level
GENTOO_UPDATER_BACKTRACK=25 sudo gentoo-updater
```

### Kernel Module Recompilation

Recompile kernel modules (useful after manual kernel update):

```bash
sudo gentoo-updater --rebuild-modules
```

This rebuilds external kernel modules:
- NVIDIA drivers (`nvidia-drivers`)
- VirtualBox modules (`virtualbox-modules`)
- ZFS modules
- Other external modules

### Custom Configuration File

```bash
sudo gentoo-updater --config /path/to/my-config.conf
```

### Show Help

```bash
gentoo-updater --help
```

## What the Script Does

The script automatically executes these steps:

1. **Repository Synchronisation**
   - Reads GENTOO_MIRRORS from `/etc/portage/make.conf`
   - Displays all configured mirrors
   - Runs `emerge --sync` to update the Portage tree

2. **eix Database Update**
   - Runs `eix-update` to update eix database (if installed)

3. **Update Check**
   - Checks for available updates
   - Shows list of packages to update

4. **System Update**
   - Runs `emerge @world --update --deep --newuse`
   - Monitors for critical package updates
   - Only rebuilds kernel modules if kernel was updated

5. **Cleanup**
   - Runs `emerge --depclean` to remove unused packages

6. **Dependency Repair**
   - Runs `revdep-rebuild` to fix broken dependencies (if gentoolkit installed)

7. **Kernel Check**
   - Shows available kernel versions
   - Provides hints for manual kernel updates

8. **Configuration Check**
   - Searches for ._cfg files
   - Alerts about pending configuration updates

## Logs & Backups

### Logs
The script automatically creates detailed logs:
- Log file: `/var/log/gentoo-updater/update-YYYYMMDD-HHMMSS.log`
- JSON summary: `/var/log/gentoo-updater/update-YYYYMMDD-HHMMSS.json`
- Real-time output to terminal
- Automatic log rotation (default: 30 days)

### Backups
Before each update, these files are backed up:
- `/etc/portage/make.conf`
- `/etc/portage/package.use`
- `/etc/portage/package.accept_keywords`
- `/var/lib/portage/world`

Backup directory: `/var/backups/gentoo-updater/YYYYMMDD-HHMMSS/`

### Update Summary
After each update:
- 🌍 All configured Gentoo mirrors
- 🌍 Primary mirror (first available)
- Number of updated packages
- Number of removed packages
- Kernel update status
- Module rebuild status
- Errors and warnings
- Total duration
## 🇩🇪 German Mirrors & Security

### German Mirrors (optional)

By default Gentoo Updater modifies **neither `make.conf` nor `repos.conf`** – the configured mirrors are only displayed.
With `--german-mirrors` (or `GENTOO_UPDATER_GERMAN_MIRRORS=true`) the following German/European mirrors are set:

- Distfiles: `GENTOO_MIRRORS` in `/etc/portage/make.conf` (backup: `make.conf.gentoo-updater.bak`)
- Portage tree: separate file `/etc/portage/repos.conf/zz-gentoo-updater.conf` with `sync-uri = rsync://rsync.de.gentoo.org/gentoo-portage` – only if `sync-type = rsync`. Delete the file to revert.

Custom distfile mirrors: `--mirrors URL1,URL2` or `GENTOO_UPDATER_MIRRORS`.

**Distfiles (Source Code):**
| Rank | Server | Location | Speed |
|------|--------|----------|-------|
| 🥇 | RWTH Aachen (ftp.halifax.rwth-aachen.de) | Aachen, Germany | ⚡⚡⚡ Very Fast |
| 🥈 | Init7 (mirror.init7.net) | Switzerland | ⚡⚡ Fast |
| 🥉 | Ruhr University Bochum | Bochum, Germany | ⚡ Stable |

**Portage Repository (Rsync):**
- 🔄 Fallback: rsync.gentoo.org (Official)

### verify-sig Security

🔐 **GPG Signature Verification Automatically Enabled:**

The script automatically enables the `verify-sig` USE flag for maximum security:

```bash
# verify-sig enabled in make.conf
USE="... verify-sig"

# Emerge will verify all distfiles:
- Manifests with OpenPGP signatures
- All packages validated against Gentoo keys
- Tampering detected immediately
```

### Code Security Audit

🔍 **Security Scan Report:** [SECURITY_SCAN.md](SECURITY_SCAN.md)

Detailed security audit of the gentoo-updater source code:
- ✅ No hardcoded secrets or credentials
- ✅ Safe subprocess patterns (no shell injection)
- ✅ Standard library only (no external dependencies)
- ✅ Comprehensive input validation
- ✅ Full Bandit security scanner results

**In Production?** Check [SECURITY_SCAN.md](SECURITY_SCAN.md) for deployment recommendations.

**Customize Configuration:**

```bash
# make.conf - Distfiles Mirror
nano /etc/portage/make.conf
GENTOO_MIRRORS="https://ftp.halifax.rwth-aachen.de/gentoo/ ..."

# repos.conf - Portage Tree Mirror
nano /etc/portage/repos.conf/gentoo.conf
sync-uri = rsync://rsync.gentoo.org/gentoo-portage
```

### mirrorselect Integration

**Automatic Interactive Mirror Selection:**

With `--use-mirrorselect` Gentoo Updater runs the interactive `mirrorselect` selection and applies the result:

```bash
# Installation (if not already installed)
sudo emerge -a app-portage/mirrorselect

# Select and apply mirrors interactively
sudo gentoo-updater --use-mirrorselect
```

**Manual Mirror Selection:**

```bash
# Select Distfiles interactively (ncurses UI)
sudo mirrorselect -i -o

# Select Rsync mirror interactively
sudo mirrorselect -i -r
```
## Troubleshooting

### "Script requires root privileges"

```bash
sudo gentoo-updater
```

### Manifest quarantine errors

The script automatically handles manifest errors by:
1. Deleting the quarantine directory
2. Automatic retry of sync

If problems persist:

```bash
sudo rm -rf /var/db/repos/gentoo/.tmp-unverified-download-quarantine
sudo emerge --sync
```

### Missing kernel modules after kernel update

```bash
sudo gentoo-updater --rebuild-modules
```

### eix not found

```bash
sudo emerge --ask app-portage/eix
```

### revdep-rebuild not found

```bash
sudo emerge --ask app-portage/gentoolkit
```

## FAQ

**Q: Why are kernel modules not rebuilt?**

A: This is normal and correct! Modules are rebuilt only when:
- ✅ A kernel update occurred during system update, OR
- ✅ Running kernel ≠ Installed kernel (after manual kernel compilation)

Modules are NOT rebuilt when:
- ❌ Kernel is already compiled for current version

Why? To make updates faster! (5-10 minutes faster)

**Q: How do I force module rebuild?**

A: Use `--rebuild-modules` option:
```bash
sudo gentoo-updater --rebuild-modules
```

**Q: How long does an update take?**

A: Depends on update scope:
- **Without kernel update**: 5-10 minutes (modules NOT recompiled)
- **With kernel update**: 15-25 minutes (NVIDIA/VirtualBox modules recompiled)

**Q: What if I manually update the kernel?**

A: After manual kernel build:
```bash
eselect kernel set <number>
cd /usr/src/linux
make oldconfig && make && make modules_install && make install
grub-mkconfig -o /boot/grub/grub.cfg

# Then:
sudo gentoo-updater --rebuild-modules
```

The script automatically detects kernel mismatch and rebuilds modules.

## Differences from Other Distributions

Gentoo requires more manual steps than other distributions:
- **Kernel Compilation** is manual (not automated)
  - ✅ But: Kernel modules are automatically rebuilt!
- **Configuration Updates** require `dispatch-conf` or `etc-update`
- **Compilation** can take a long time (depends on hardware and USE flags)
- **USE flag changes** may require recompilation

## Common Use Cases

### Complete Weekend Update
```bash
sudo gentoo-updater
# Wait for completion...
# Check kernel updates and configs
# Reboot system
```

### Quick Module Rebuild After Manual Kernel Update
```bash
# After manual kernel build:
sudo gentoo-updater --rebuild-modules
sudo reboot
```

### Testing Without Changes
```bash
sudo gentoo-updater --dry-run
```

## License

MIT License - See LICENSE file

## Contributing

Contributions are welcome! Please create a pull request or open an issue.

## Changelog

### Latest Releases

- [v1.4.37](releases/v1.4.37.md) - Auto Autounmask Recovery (2026-02-16) ⭐ **LATEST**
- [v1.4.36](releases/v1.4.36.md) - Security scan documentation update (2026-02-15)
- [v1.4.35](releases/v1.4.35.md) - Startup internet connection check message (2026-02-15)
- [v1.4.24](releases/v1.4.24.md) - German mirrors and verify-sig integration (2026-02-07)
- [v1.4.0](releases/v1.4.0.md) - Advanced CLI parameters (2026-02-06)
- [v1.3.3](releases/v1.3.3.md) - Mirror logging (2026-02-06)

For complete history, see [CHANGELOG.md](CHANGELOG.md) and the [releases folder](releases/README.md).

## Author

Created for Gentoo Linux users

## See Also

- [Gentoo Wiki - Updating Gentoo](https://wiki.gentoo.org/wiki/Handbook:AMD64/Working/Portage#Updating_Gentoo)
- [Gentoo Wiki - eix](https://wiki.gentoo.org/wiki/Eix)
- [Gentoo Wiki - gentoolkit](https://wiki.gentoo.org/wiki/Gentoolkit)
- [GitHub Repository](https://github.com/roimme65/gentoo-updater)
- [Release Notes](https://github.com/roimme65/gentoo-updater/releases)
