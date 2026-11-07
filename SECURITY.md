# Security Policy

**Languages:** 🇬🇧 [English](SECURITY.md) | 🇩🇪 [Deutsch](SECURITY.de.md)

## Supported Versions

The following versions of the Gentoo System Updater receive security updates:

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| 2.2.x   | :white_check_mark: | Current stable version (contains security fixes, see [SECURITY_SCAN.md](SECURITY_SCAN.md)) |
| 2.0.x – 2.1.x | :x:          | Please update to 2.2.x |
| < 2.0   | :x:                | End of life |

Security fixes are only released for the latest minor version.

## Security Considerations

### Root Privileges
The Gentoo Updater requires root privileges (sudo) for system updates. This is necessary because `emerge` performs system-level changes.

**Recommended Security Measures:**
- Review the code before execution
- Use the `--dry-run` mode for testing
- Regularly review log files
- Always use the latest version

### Cron Jobs
When setting up cron jobs, they execute with root privileges:
- Ensure only authorized users can modify cron jobs
- Logs are written to `/var/log/`
- Regularly review executed updates
- Kernel updates must be performed manually
- Configuration updates require manual merging

### Data Processing
- The tool stores no sensitive data
- Log files and JSON summaries in `/var/log/gentoo-updater/` (directory mode `0750` from v2.2.0)
- Backups of `/etc/portage` and the world file in `/var/backups/gentoo-updater/` (mode `0700` from v2.2.0)
- All emerge operations are displayed in real-time
- Network communication:
  - Portage sync and distfile/binary package downloads (emerge)
  - Internet check before start: TCP connection to public DNS servers / gentoo.org, no data sent (`--skip-internet-check` disables it)
  - Optional webhook (`--notification-webhook`, http/https only): host name, status and counters
  - Optional e-mail via the local `mail` command (address is validated from v2.2.0)

### System Integrity
- The tool only calls standard Gentoo tools (`emerge`, `eix-update`, `revdep-rebuild`, `eselect`, `etc-update`, `mirrorselect`, plus `find`, `uname`, `mail`); no shell is used
- Files outside Portage are only changed in these cases:
  - `make.conf` / `repos.conf/zz-gentoo-updater.conf`: only with `--german-mirrors`, `--mirrors` or `--use-mirrorselect` (backup of `make.conf` is created)
  - `/etc/portage/package.*`: autounmask recovery (enabled by default, disable with `--no-auto-autounmask`)
  - Files in `/etc`: only with `--etc-update-mode auto` (overwrites local changes)
- Suggested `package.use` lines for blocked packages are only printed, never written (from v2.2.0)
- Configuration file: `/etc/gentoo-updater.conf` (recommended mode `0600`)
- Automatic backups before updates
- Complete audit logging
- All actions are displayed and can be monitored
- Exit codes enable error monitoring
- Kernel updates are NOT automated (security feature)
- Environment variable validation (from v1.4.0)

### Gentoo-Specific Security
- **Kernel Updates**: Only detected, never automatically performed
- **Configuration Updates**: Interactive by default; applied automatically only with `--etc-update-mode auto`
- **USE Flag Changes**: Can trigger recompilation
- **depclean**: May rarely mark important packages for removal
- **revdep-rebuild**: Only repairs broken dependencies
- **Mirrors**: Displayed on every run; changed only on explicit request (from v2.0.0)
- **Blocked packages**: Missing USE flags are suggested, not applied (from v2.2.0)

## Reporting a Vulnerability

If you discover a security vulnerability in the Gentoo System Updater, please report it:

### Contact
- **GitHub Security Advisories**: For critical security issues (recommended)
- **GitHub Issues**: For non-critical issues only (never for exploitable vulnerabilities)

The latest security scan is documented in [SECURITY_SCAN.md](SECURITY_SCAN.md).

### What to Expect
1. **Acknowledgment**: Within 48 hours of reporting
2. **Assessment**: Severity and impact analysis within 5 business days
3. **Updates**: Regular status updates during remediation
4. **Fix**: 
   - Critical issues: Patch within 7 days
   - Moderate issues: Patch in next release
   - Low severity: Documented and scheduled

### Information for Your Report
Please include:
- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Potential impact
- Suggested solution (if available)
- Gentoo-specific information (profile, USE flags, etc.)

### Responsible Disclosure
We ask for:
- No public disclosure before a fix is available
- Time for patch development and testing
- Coordinated publication of security information

Thank you for supporting the security of this project!
