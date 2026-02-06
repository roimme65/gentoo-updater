# Security Policy

**Languages:** 🇬🇧 [English](SECURITY.md) | 🇩🇪 [Deutsch](SECURITY.de.md)

## Supported Versions

The following versions of the Gentoo System Updater receive security updates:

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| 1.4.x   | :white_check_mark: | Current stable version |
| 1.3.x   | :white_check_mark: | Supported until 30.06.2026 |
| 1.2.x   | :white_check_mark: | Supported until 31.03.2026 |
| 1.1.x   | :x:                | End of life |
| < 1.1   | :x:                | Development versions |

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
- Log files contain package information and system output (from v1.2.0)
- JSON export of update statistics (from v1.2.0, no sensitive data)
- Automatic backups of configuration files (from v1.2.0)
- No network communication except to Portage repositories
- All emerge operations are displayed in real-time
- Email notifications optional (from v1.2.0)
- Advanced parameters and dry-run testing (from v1.4.0)

### System Integrity
- The tool only executes official emerge commands
- No modification of system files outside Portage control
- Configuration file support (from v1.2.0): `/etc/gentoo-updater.conf`
- Automatic backups before updates (from v1.2.0)
- Complete audit logging (from v1.2.0)
- All actions are displayed and can be monitored
- Exit codes enable error monitoring
- Kernel updates are NOT automated (security feature)
- Environment variable validation (from v1.4.0)

### Gentoo-Specific Security
- **Kernel Updates**: Only detected, never automatically performed
- **Configuration Updates**: Detected but not automatically applied
- **USE Flag Changes**: Can trigger recompilation
- **depclean**: May rarely mark important packages for removal
- **revdep-rebuild**: Only repairs broken dependencies
- **Mirror Logging**: Displays all configured Gentoo mirrors (from v1.3.0)

## Reporting a Vulnerability

If you discover a security vulnerability in the Gentoo System Updater, please report it:

### Contact
- **GitHub Security Advisories**: For critical security issues (recommended)
- **GitHub Issues**: For non-critical issues only

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
