# Stack checklist: cli

Stack-specific deep-dive items. Subagents pull from here when `app_class = cli`. Generic focus-area checklists are in `agents/security-auditor.md`; this file lists patterns that **only** make sense for a command-line tool, script, or daemon with no GUI.

## Frameworks covered

Bash/POSIX shell, Python (argparse/click/typer), Node (commander/yargs/oclif), Go (cobra/flag), Rust (clap), .NET (`System.CommandLine`), Ruby (thor), PowerShell, Makefiles, systemd units, cron jobs, CI scripts.

## The one thing to get right

A CLI runs with **the caller's privileges on a shared machine**, so the questions are: does it leak secrets to other local users, does it let a caller execute something unintended, and does it trust the filesystem it operates on. If the tool is ever run as root or in CI with credentials, every one of these escalates.

## Framework-specific issues

### Shell scripts

- **Unquoted variable expansion** — `rm -rf $DIR` with an empty or space-containing `DIR`. `set -u` plus quoting; `"${DIR:?}"` for destructive paths.
- **No `set -euo pipefail`** — a failed step continues and the script proceeds on bad state.
- **`eval` on anything derived from input, a file, or `curl` output.**
- **`curl … | bash` / `wget -O- | sh`** — remote code execution by design; if unavoidable, verify a pinned checksum or signature first, and never over plain HTTP.
- **Word-splitting on `ls`/`find` output** instead of `find -print0 | xargs -0` or `while IFS= read -r -d ''`.
- **Predictable temp files** — `/tmp/myapp.$$` or a fixed name → symlink attack / TOCTOU. Use `mktemp -d`.
- **`PATH` not pinned** while running privileged, or a relative/`.`-containing `PATH` → binary hijack.
- **Secrets passed as arguments** — visible in `ps`, `/proc/*/cmdline`, and shell history.
- **`trap` missing** — temp files and lockfiles left behind, or a partial state on `SIGINT`.
- **`sudo` inside the script** with a wide command, or a `NOPASSWD` sudoers snippet the installer adds.

### Python

- **`subprocess` with `shell=True`** and any interpolated value → command injection. Pass a list.
- **`os.system` / `os.popen`** — same problem, no safe form.
- **`pickle.load` / `yaml.load` without `SafeLoader`** on a config or cache file an attacker may write.
- **`tempfile.mktemp`** (deprecated, racy) instead of `NamedTemporaryFile`/`mkstemp`.
- **`shutil.unpack_archive` / `tarfile.extractall`** without member filtering → path traversal (use `filter='data'` on 3.12+, else validate each member).
- **`input()`/env values into `eval`, `exec`, or a format string** (`f"{user}"` into SQL or a shell).
- **`requests` with `verify=False`** or a monkeypatched session.
- **`os.chmod(…, 0o777)`** or files created before `umask` is considered.

### Node

- **`child_process.exec` / `execSync` with interpolation** → injection; use `execFile`/`spawn` with an argument array.
- **`require()` of a path from config or argv** → arbitrary module load.
- **`JSON.parse` into a deep-merge helper** → prototype pollution reaching later logic.
- **`postinstall` scripts** in the package that fetch or execute remote content.
- **Reading config from `process.env` and echoing it** in verbose/debug output.

### Go / Rust / .NET

- **`exec.Command("sh", "-c", cmd)`** — reintroduces the shell; pass argv directly.
- **`os.OpenFile` with `0666`** for a credential cache; and missing `O_NOFOLLOW` where symlinks matter.
- **`filepath.Join` on untrusted input without `filepath.Clean` + prefix check** → traversal.
- **Rust `std::process::Command` with `.arg(format!(…))`** containing user data destined for a shell wrapper.
- **.NET `Process.Start` with a single command string** instead of `ArgumentList`.

## Cross-cutting for this class

- **Secrets on the command line** — the cardinal sin of CLIs. `--token=…` is world-visible via `ps` on most systems and lands in `~/.bash_history`. Accept secrets via env var, a mode-`0600` file, or stdin, and document it.
- **Secrets in the environment for child processes** — a subprocess inherits everything; scrub before spawning third-party tools.
- **Credential cache file permissions** — `~/.config/tool/credentials` must be `0600` and its directory `0700`. Check the create path, not just the docs.
- **Config file trust** — a config that can set an executable path, a plugin directory, or a pre/post hook is a code-execution vector when it lives in a repo (`.tool.yml` committed by someone else). Prefer explicit opt-in for project-local config.
- **Output injection** — writing untrusted text to a terminal without stripping ANSI/control sequences (title-setting and bracketed-paste sequences can be abused); and CSV/formula injection when emitting `.csv`.
- **TOCTOU and symlinks** — `if os.path.exists(p): open(p, "w")` on a shared directory. Use `O_EXCL`/`O_NOFOLLOW` or operate on a file descriptor.
- **Archive extraction** — Zip Slip (`../`), absolute paths, symlink and hardlink members, and decompression bombs.
- **Privilege handling** — if it ever runs as root: does it drop privileges before touching user-owned paths? Does it `chown` a file to the invoking user safely?
- **setuid/setgid binaries** — any at all is a major finding; check `PATH`, env (`LD_PRELOAD`, `IFS`), and argv handling.
- **Lockfile and PID file placement** — a world-writable `/tmp/app.pid` lets a local user cause a signal to an arbitrary PID.
- **Update/self-update** — signature or checksum verified before replacing the binary; and the binary's own directory not user-writable.
- **CI usage** — secrets echoed by `set -x`, printed in error paths, or written to an artifact/log that is retained.
- **Signal handling for daemons** — clean shutdown that does not leave a half-written state file or an unreleased lock.

## Common false positives in cli

- `shell=True` / `exec` where every interpolated value is a literal or a validated enum from the tool's own code.
- "Hardcoded credential" in a fixture, an example invocation in `--help`, a test, or `README`.
- World-readable files that are genuinely public output (generated reports, build artifacts).
- Predictable temp paths inside a per-run `mktemp -d` directory.
- Missing TLS verification behind an explicit `--insecure` flag that defaults to off and is documented.
- `eval` in shell completion scripts generated by the framework (`clap`, `cobra`, `click`) — that is how completion works.
- Running as root when the tool's whole purpose is system administration — note the assumption instead.
