# Gentoo Updater Project Board

Welcome to the **Gentoo Updater Development Board**! This project tracks the development, features, and releases of the automated update system for Gentoo Linux.

## 📊 Project Overview

This project board manages:
- 🐛 **Bug Reports** - Issues and fixes
- 🚀 **Features** - New functionality and enhancements
- 📋 **Tasks** - Development work and maintenance
- ✅ **Completed** - Released features and fixes
- 🔄 **In Progress** - Active development

## 📈 Current Status

- **Latest Version**: v1.4.0 (February 2026)
- **Status**: Stable & Production Ready
- **Python**: 3.6+ compatible
- **Target**: Gentoo Linux systems

## 🎯 Key Features (v1.4.0)

### Core Functionality
- ⚡ Parallel compilation with automatic CPU detection
- 📦 Automated @world updates with safety checks
- 🔄 Repository synchronization (emerge --sync)
- 🧹 Automatic cleanup (emerge --depclean)
- 🔧 Dependency repair (revdep-rebuild)

### Advanced Features
- 🎛️ **Advanced Parameters** (from v1.4.0):
  - `--log-level DEBUG|INFO|WARNING|ERROR`
  - `--skip-*` options (sync, update, eix, cleanup, revdep)
  - `--only-*` options (execute specific steps)
  - `--max-packages N` (limit updates)
  - `--timeout SECONDS`
  - `--retry-count N`
  - `--notification-webhook URL`
  - `--parallel-jobs N`

### Safety & Reliability
- 💾 Automatic configuration backups
- 🔍 Blocked packages detection
- ⚠️ Critical package warnings (gcc, glibc, Python)
- 🎯 Kernel update detection (manual only)
- 🌍 Mirror logging
- 📝 Full audit logging
- 📧 Email notifications (optional)

## 📌 Development Workflow

### Board Views
- **Table View** - Overview of all tasks and issues
- **Timeline View** - Progress tracking and deadlines
- **Board View** - Kanban-style workflow

### Status Categories
- 📋 **To Do** - Planned work
- 🔨 **In Progress** - Active development
- ✅ **Done** - Completed
- 📦 **Backlog** - Future considerations
- 👀 **Review** - Pending review
- 🚀 **Released** - Published versions

## 🔗 Quick Links

- 📖 [Main Repository](https://github.com/roimme65/gentoo-updater)
- 🇬🇧 [English Documentation](https://github.com/roimme65/gentoo-updater/blob/main/README.md)
- 🇩🇪 [Deutsch Dokumentation](https://github.com/roimme65/gentoo-updater/blob/main/README.de.md)
- 🐛 [Issue Tracker](https://github.com/roimme65/gentoo-updater/issues)
- 🔐 [Security Policy](https://github.com/roimme65/gentoo-updater/blob/main/SECURITY.md)
- 📋 [Changelog](https://github.com/roimme65/gentoo-updater/blob/main/CHANGELOG.md)

## 🚀 Getting Started

### Installation
```bash
git clone https://github.com/roimme65/gentoo-updater.git
cd gentoo-updater
sudo ./install.sh
```

### Basic Usage
```bash
# Full system update (dry-run first!)
sudo gentoo-updater --dry-run

# Execute with debug output
sudo gentoo-updater --log-level DEBUG

# Limit updates to 50 packages
sudo gentoo-updater --max-packages 50
```

## 📝 Contribution Guidelines

We welcome contributions! Please:
1. Check existing issues first
2. Create a new issue describing your proposal
3. Submit a pull request with clear descriptions
4. Follow our code style and conventions
5. Ensure all tests pass

## 📊 Project Statistics

- **Versions**: 14+ releases
- **Languages**: Python 3.6+
- **License**: GPL-3.0
- **Platform**: Gentoo Linux (all architectures)

## ❓ Need Help?

- 📖 Check [FAQ](https://github.com/roimme65/gentoo-updater#faq)
- 💬 Ask in [Discussions](https://github.com/roimme65/gentoo-updater/discussions)
- 🐛 Report bugs via [Issues](https://github.com/roimme65/gentoo-updater/issues)
- 🔒 Security issues: [Security Advisory](https://github.com/roimme65/gentoo-updater/security)

## 📄 License

This project is licensed under the **GPL-3.0 License** - see [LICENSE](https://github.com/roimme65/gentoo-updater/blob/main/LICENSE) file for details.

---

**Last Updated**: February 6, 2026  
**Maintained by**: [@roimme65](https://github.com/roimme65)

---

### 📌 Project Board

Visit the [Project Board](https://github.com/users/roimme65/projects/8) to track development progress, view upcoming tasks, and see recently completed features.
