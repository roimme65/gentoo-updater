# 🔒 Security Scan Report - gentoo-updater

**Scan Date:** 2026-11-07
**Version scanned:** v2.1.0 + unreleased changes (USE flag suggestions for blocked packages)
**Repository:** `gentoo-updater` (Public)
**Status:** ✅ **No high-severity issues** – R1–R3 fixed, 1 low-risk recommendation open (R4)

---

## Summary

| Category | Status | Risk | Notes |
|----------|--------|------|-------|
| Secrets/Credentials | ✅ PASS | 🟢 LOW | No hardcoded secrets, no tokens/keys in tracked files |
| Code Execution | ✅ PASS | 🟢 LOW | No `eval`/`exec`/`shell=True`/`os.system`; all subprocess calls use argument lists |
| Dependencies | ✅ PASS | 🟢 LOW | Python standard library only |
| Input Validation | ✅ PASS | 🟢 LOW | Webhook URL scheme checked; e-mail address validated (R2, fixed) |
| Privilege Model | ✅ PASS | 🟢 LOW | Root check before any file is written |
| File System | ✅ PASS | 🟢 LOW | Log dir `0750`, backup dir `0700` (R3, fixed) |
| Output to user | ✅ PASS | 🟢 LOW | Suggested `package.use` commands only with valid PMS names (R1, fixed) |
| CI/CD Workflows | ✅ PASS | 🟢 LOW | Minimal permissions, no script injection; actions pinned by tag (R4) |

**Bandit:** 0 high, 2 medium (both expected/false positive), 36 low.

---

## 🔧 Bandit Results

```
Tool:            Bandit 1.9.4
Python:          3.14.10
Files:           gentoo-updater.py, install.py, scripts/create-release.py
Lines of code:   3,249 (Bandit LOC)
Skipped (nosec): 1  (B310 webhook urlopen – scheme validated, see below)

Severity High:    0 ✅
Severity Medium:  2
Severity Low:    36
```

| Test | Count | Severity | Verdict |
|------|-------|----------|---------|
| B603 subprocess without shell | 17 | Low | ✅ False positive – argument lists, no shell |
| B607 partial executable path | 14 | Low | ✅ Expected – `emerge`, `eselect`, `find`, `mail`, `mirrorselect`, `etc-update`, `uname` from root's `PATH` |
| B404 import subprocess | 3 | Low | ✅ Required for Portage integration |
| B110 try/except/pass | 2 | Low | ℹ️ Non-critical paths (see below) |
| B108 hardcoded tmp directory | 1 | Medium | ✅ False positive |
| B103 chmod 0o755 | 1 | Medium | ✅ Expected |

**B108 – `gentoo-updater.py:727`** (`find_build_log`): `/var/tmp` is only the default for
`PORTAGE_TMPDIR` to locate an existing `build.log`, which is then **read** (last 64 KiB). Nothing is
created or written there, so the usual tmp-file race conditions do not apply.

**B103 – `install.py:241`**: `chmod 0o755` on the installed command in `/usr/local/bin`. This is the
standard permission for system executables; the file contains no secrets.

**B110 – `gentoo-updater.py:40`** (language detection, bare `except:`) and **`:2303`**
(`eselect python list` hint, `except Exception: pass`). Both only affect informational output.
The bare `except:` also swallows `KeyboardInterrupt`; `except Exception:` would be cleaner.

---

## Manual Review

### 1. Secrets & Credentials ✅
- No API keys, tokens, passwords or private keys in tracked files (pattern search for
  `ghp_`, `github_pat_`, `AKIA…`, `BEGIN … PRIVATE KEY`).
- `gentoo-updater.conf.example` contains no secrets.
- The webhook URL (which may contain a token) is only printed when it is invalid or in dry-run mode.

### 2. Code Execution ✅
- No `eval()`, `exec()`, `os.system()`, `os.popen()`, `pickle`, `yaml.load`.
- No `shell=True`. All 17 `subprocess.run`/`Popen` calls pass argument lists; the only
  variable parts are package atoms from Portage output, config values from the root-owned config
  file, or CLI options of the root user.

### 3. Network ✅
- Webhook (`send_webhook`): only `http://`/`https://` accepted (prevents `file://` etc.),
  10 s timeout, payload contains host name, status and counters only.
- Internet check: plain TCP connects to public DNS servers / gentoo.org, no data sent.

### 4. Privilege Model ✅
- `main()` checks `os.geteuid() == 0` before `/var/log/gentoo-updater` is created.
- Autounmask recovery writes only to `/etc/portage` (`CONFIG_PROTECT_MASK=/etc/portage`), not a global
  `etc-update --automode -3`.
- `--etc-update-mode auto` overwrites local changes in `/etc` – documented, opt-in only.
- Mirror settings are only changed on explicit request (`--german-mirrors`, `--mirrors`,
  `--use-mirrorselect`); a backup of `make.conf` is written first.

### 5. CI/CD Workflows ✅
- `pr-check.yml`: PR title passed via `env:` instead of `${{ }}` inside the script (no script injection).
- Workflow-level `permissions:` are minimal (`contents: read`, write only where needed).
- No `pull_request_target`.

---

## ⚠️ Recommendations

### R1 – Validate names in suggested `package.use` commands (new feature) ✅ FIXED
`suggest_use_fixes()` prints ready-to-run commands such as
`echo "dev-qt/qttools designer" >> /etc/portage/package.use/qttools`, which the user runs as root.
Package and flag names come from the emerge slot-conflict output, i.e. from ebuilds of the
configured repositories – including third-party overlays (e.g. GURU). A malicious ebuild could put
shell metacharacters into a USE dependency.

**Fix:** `parse_conflict_use_requirements()` only accepts package names matching
`PACKAGE_NAME_PATTERN` (`^[A-Za-z0-9_][A-Za-z0-9+_.-]*/[A-Za-z0-9_][A-Za-z0-9+_-]*$`) and flags matching
`USE_FLAG_PATTERN` (`^[A-Za-z0-9][A-Za-z0-9+_@.-]*$`, PMS 3.1); anything else is dropped.
Verified with crafted input (`evil/pkg$(id)`, ``bad`id` ``, `-$(rm)`): none of it is suggested.

### R2 – E-mail address passed to `mail` without validation ✅ FIXED
`send_notification()` runs `['mail', '-s', subject, email]`. An address starting with `-`
would be interpreted as an option of `mail` (argument injection). The value comes from the
root-owned config file, so exploitation requires root access anyway.

**Fix:** `send_notification()` checks the address against `EMAIL_PATTERN` (no leading `-`, no
whitespace, `local@domain.tld`) and sends no mail with a warning otherwise.

### R3 – Logs and backups are world-readable ✅ FIXED
`/var/log/gentoo-updater/` and `/var/backups/gentoo-updater/` are created with mode `0755`,
files with `0644`. Backups contain `/etc/portage` and the world file, logs contain the package list.
Not secret on most systems, but it reveals installed software and versions to local users.

**Fix:** on every run the updater sets `/var/log/gentoo-updater` to `0750` and the backup directory
(`backup_dir`, default `/var/backups/gentoo-updater`) to `0700` via `restrict_permissions()`.
Existing installations are corrected on the next run.

### R4 – GitHub Actions pinned by tag 🟢 LOW
Actions are referenced by tag (`actions/checkout@v4`, `softprops/action-gh-release@v2`, …).
A compromised tag of a third-party action would run in the release job with `contents: write`.

**Recommendation:** pin at least `softprops/action-gh-release` to a full commit SHA.

### Note – Timeouts
Commands started via `run_command()` honour `--timeout`. The default is **no timeout**, and a few
helper calls (`emerge --pretend @world`, `eselect`, `find`, `mail`) run without one. This is a
robustness issue rather than a security issue: a hanging command blocks the update run.

---

## Corrections to the previous report (2026-02-15)

The previous report contained statements that do not match the code:

| Previous statement | Actual state |
|--------------------|--------------|
| "Timeouts enforced on all subprocess calls" | Optional (`--timeout`), several helper calls without timeout |
| "Email addresses validated before use" | Was not validated – fixed now (R2) |
| "Logging implementation uses dedicated filtering for sensitive data" | No filtering exists; nothing sensitive is logged by design |
| "Bare except fixed in next version" | Still present at `gentoo-updater.py:40` |

---

## 📋 Deployment Checklist

- [ ] `chmod 600 /etc/gentoo-updater.conf` (currently created as `0644`)
- [ ] Use `--dry-run` first after upgrading the updater
- [ ] Set `--timeout` when running from cron/systemd timers
- [ ] Review suggested `package.use` lines before applying them

---

## 📝 Scan Metadata

- **Methods:** Bandit 1.9.4 (automated), manual review of all subprocess/network/file operations,
  secret pattern search over tracked files, GitHub workflow review, check of file permissions on
  a live system
- **Files:** `gentoo-updater.py` (3,223 lines), `install.py` (389), `scripts/create-release.py` (525),
  `.github/workflows/*.yml`
- **Dependencies:** none outside the Python standard library (no `pip-audit` needed)
- **Next recommended scan:** 2027-02 (quarterly) or after larger features

---

## 📧 Security Reporting

Please report vulnerabilities **privately** via GitHub Security Advisory:
https://github.com/roimme65/gentoo-updater/security – do **not** open public issues.
