#!/usr/bin/python3 -I
"""Restricted Debian 13 KDE transaction engine; installed root-owned, never setuid."""
import contextlib
import fcntl
import functools
import hashlib
import json
import os
import shlex
import subprocess
from pathlib import Path
import sys
import time

TARGETS = (
    "kde-plasma-desktop", "kwin-wayland", "plasma-workspace",
    "xwayland", "xdg-desktop-portal-kde", "polkit-kde-agent-1", "kscreen",
)
JOURNAL = Path("/var/lib/udm/operations")
POLICY = Path("/usr/sbin/policy-rc.d")
RECOVERY = ("Inspect this operation and /var/log/apt/term.log and /var/log/dpkg.log. "
            "Run dpkg --audit as administrator. After reviewing its output, an administrator "
            "may need dpkg --configure -a or apt-get --fix-broken install. "
            "These can change packages or services; UDM does not run them automatically. "
            "If an interrupted UDM operation left /usr/sbin/policy-rc.d, inspect and remove only the UDM guard after recovery. "
            "There is no automatic rollback. Restore the disposable VM snapshot if appropriate.")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(plan):
    return hashlib.sha256(canonical(plan)).hexdigest()


def debian13():
    fields = dict(line.split("=", 1) for line in Path("/etc/os-release").read_text().splitlines()
                  if "=" in line)
    if fields.get("ID", "").strip('"') != "debian" or fields.get("VERSION_ID", "").strip('"') != "13":
        raise RuntimeError("Only Debian 13 is supported")


@functools.cache
def apt_modules():
    import apt
    import apt_pkg
    apt_pkg.init_config()
    apt_pkg.init_system()
    apt_pkg.config.set("APT::Get::AllowUnauthenticated", "false")
    apt_pkg.config.set("Acquire::AllowInsecureRepositories", "false")
    return apt, apt_pkg


def checked_origin(version):
    origins = [dict(origin=o.origin, label=o.label, archive=o.archive,
                    site=o.site, component=o.component, trusted=o.trusted)
               for o in version.origins if o.site]
    if not origins or any(not o["trusted"] or o["origin"] != "Debian" or
                          o["site"] not in ("deb.debian.org", "security.debian.org") or
                          o["archive"] not in ("stable", "stable-updates", "stable-security",
                                               "trixie", "trixie-updates", "trixie-security")
                          for o in origins):
        raise RuntimeError(f"Unapproved package origin: {version.package.name}")
    return origins


def resolve(cache):
    if cache.broken_count or cache.dpkg_journal_dirty:
        raise RuntimeError("Package database has broken dependencies or interrupted state; administrator recovery required")
    # Avoid the desktop metapackage's recommended display manager and optional applications.
    for name in TARGETS:
        if name not in cache or cache[name].candidate is None:
            raise RuntimeError(f"No candidate for {name}; refresh trusted Debian metadata separately")
        cache[name].mark_install(auto_fix=True, auto_inst=True, from_user=True)
    changes = []
    for package in sorted(cache.get_changes(), key=lambda p: p.name):
        if package.marked_delete or package.installed is not None:
            raise RuntimeError(f"Removal, reinstall or upgrade forbidden: {package.name}")
        if package.name.split(":")[0] in {"sddm", "gdm3", "lightdm", "xdm", "lxdm", "slim", "nodm", "wdm"}:
            raise RuntimeError(f"Display-manager installation forbidden: {package.name}")
        candidate = package.candidate
        if candidate is None:
            raise RuntimeError(f"Missing candidate: {package.name}")
        if "x-display-manager" in candidate.provides:
            raise RuntimeError(f"Display-manager provider forbidden: {package.name}")
        changes.append(dict(name=package.name, architecture=candidate.architecture,
                            version=candidate.version, download_bytes=candidate.size,
                            installed_bytes=candidate.installed_size,
                            origins=checked_origin(candidate),
                            dependencies=[dict(type=d.rawtype, expression=d.rawstr)
                                          for d in candidate.get_dependencies("PreDepends", "Depends", "Conflicts", "Breaks", "Replaces")]))
    if cache.broken_count:
        raise RuntimeError("Dependency resolution failed")
    return changes


def file_state(paths):
    result = {}
    for path in paths:
        p = Path(path)
        if p.is_symlink():
            result[path] = dict(link=str(p.readlink()),
                                content=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
        elif p.is_file():
            result[path] = hashlib.sha256(p.read_bytes()).hexdigest()
        else:
            result[path] = None
    return result


def plan_transaction():
    debian13()
    apt, apt_pkg = apt_modules()
    apt_pkg.config.set("APT::Install-Recommends", "false")
    apt_pkg.config.set("APT::Install-Suggests", "false")
    cache = apt.Cache()
    changes = resolve(cache)
    audit = dpkg_audit()
    if not audit["clean"]:
        raise RuntimeError(f"dpkg requires administrator review: {audit['output']}")
    state_paths = ["/var/lib/dpkg/status", "/etc/apt/preferences", "/etc/apt/apt.conf", "/etc/apt/sources.list",
                   "/etc/X11/default-display-manager", "/etc/systemd/system/display-manager.service"]
    for directory in ("/etc/apt/sources.list.d", "/etc/apt/preferences.d", "/etc/apt/apt.conf.d", "/var/lib/apt/lists"):
        state_paths.extend(str(p) for p in sorted(Path(directory).glob("*")) if p.is_file() and p.name != "lock")
    plan = dict(schema_version=1, target="kde-plasma-wayland", distribution="debian-13",
                install=changes, remove=[], upgrade=[], download_bytes=sum(p["download_bytes"] for p in changes),
                additional_disk_bytes=sum(p["installed_bytes"] for p in changes),
                state=file_state(state_paths),
                restart="No session activation. Service starts/restarts denied by temporary policy-rc.d. "
                        "Maintainer scripts are privileged; VM validation is required. Reboot requirement checked after install.")
    return cache, plan


def session_matches(fields, launcher):
    if (fields.get("Type", "Application") != "Application" or
            fields.get("Hidden", "false") == "true" or not fields.get("Name")):
        return False
    command = shlex.split(fields.get("Exec", ""))
    direct = command in (["startplasma-wayland"], [str(launcher)])
    wrapped = (len(command) == 2 and command[1] == str(launcher) and
               Path(command[0]).name == "plasma-dbus-run-session-if-needed" and
               command[0].startswith("/usr/lib/") and
               os.access(command[0], os.X_OK))
    return direct or wrapped


def dpkg_audit():
    audit = subprocess.run(["/usr/bin/dpkg", "--audit"], capture_output=True, text=True,
                           check=False, timeout=30)
    output = audit.stdout + audit.stderr
    return dict(clean=audit.returncode == 0 and not output.strip(), output=output)


def verify():
    debian13()
    apt, _ = apt_modules()
    cache = apt.Cache()
    missing = [name for name in TARGETS if name not in cache or cache[name].installed is None]
    launcher = Path("/usr/bin/startplasma-wayland")
    entries = []
    for path in Path("/usr/share/wayland-sessions").glob("*.desktop"):
        fields = {}
        section = None
        for line in path.read_text().splitlines():
            if line.startswith("["):
                section = line
            elif section == "[Desktop Entry]" and "=" in line:
                key, value = line.split("=", 1)
                fields[key] = value
        if session_matches(fields, launcher):
            entries.append(str(path))
    audit = dpkg_audit()
    clean = audit["clean"]
    return dict(packages_missing=missing, dpkg_audit_clean=clean,
                dpkg_audit=audit["output"], launcher=str(launcher),
                launcher_executable=launcher.is_file() and os.access(launcher, os.X_OK),
                session_entries=entries, reboot_required=Path("/var/run/reboot-required").exists(),
                ready=clean and not missing and launcher.is_file() and os.access(launcher, os.X_OK) and bool(entries),
                graphics_readiness="unverified", session_started=False, live_switch_capable=False)


def durable_write(path, value):
    temporary = path.with_suffix(".tmp")
    with open(temporary, "x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


@contextlib.contextmanager
def service_guard():
    # Never replace a host administrator's existing policy (including a dangling symlink).
    fd = os.open(POLICY, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o755)
    try:
        os.write(fd, b"#!/bin/sh\n# UDM temporary service-start guard; see /var/lib/udm/operations\nexit 101\n")
        os.fsync(fd)
        os.close(fd)
        fd = None
        yield
    finally:
        if fd is not None:
            os.close(fd)
        POLICY.unlink()


def install(reviewed_digest):
    if len(reviewed_digest) != 64 or any(c not in "0123456789abcdef" for c in reviewed_digest):
        raise RuntimeError("Expected the SHA-256 digest of the reviewed transaction")
    if os.geteuid() != 0 or not os.environ.get("PKEXEC_UID", "").isdigit():
        raise RuntimeError("Installation must be authorized through the installed Polkit helper")
    # pkexec supplies the authenticated caller and a sanitized environment. No paths or commands from UI.
    JOURNAL.mkdir(parents=True, exist_ok=True, mode=0o700)
    with open(JOURNAL / "lock", "a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for prior in JOURNAL.glob("*.json"):
            if json.loads(prior.read_text()).get("phase") in ("installing", "verifying"):
                raise RuntimeError(f"Interrupted operation {prior.name}; {RECOVERY}")
        apt, apt_pkg = apt_modules()
        # Hold APT's system lock across re-resolution, download and dpkg commit.
        with apt_pkg.SystemLock():
            cache, plan = plan_transaction()
            if digest(plan) != reviewed_digest:
                raise RuntimeError("Transaction changed since review; simulate and review again")
            operation = dict(id=f"{time.time_ns()}-{reviewed_digest[:12]}", plan=plan,
                             digest=reviewed_digest, caller_uid=int(os.environ["PKEXEC_UID"]),
                             phase="authorized", recovery=RECOVERY)
            path = JOURNAL / (operation["id"] + ".json")
            durable_write(path, operation)
            original_dm = file_state(["/etc/X11/default-display-manager",
                                      "/etc/systemd/system/display-manager.service"])
            try:
                for location, required in (("/", plan["additional_disk_bytes"]),
                                           ("/var/cache/apt/archives", plan["download_bytes"])):
                    space = os.statvfs(location)
                    if space.f_bavail * space.f_frsize < required:
                        raise RuntimeError(f"Insufficient free space at {location}")
                with service_guard():
                    operation["phase"] = "installing"
                    durable_write(path, operation)
                    os.environ["DEBIAN_FRONTEND"] = "noninteractive"
                    os.environ["NEEDRESTART_MODE"] = "l"
                    # python-apt calls native Acquire and dpkg, never a UI-supplied shell.
                    if not cache.commit(allow_unauthenticated=False):
                        raise RuntimeError("APT commit did not report success")
                    operation["phase"] = "verifying"
                    durable_write(path, operation)
                    operation["verification"] = verify()
                    if file_state(list(original_dm)) != original_dm:
                        raise RuntimeError("Display-manager configuration changed; administrator review required")
                    if not operation["verification"]["ready"]:
                        raise RuntimeError("Package commit succeeded but KDE verification failed")
                operation["phase"] = "ready"
            except Exception as error:
                operation["phase"] = "failed"
                operation["error"] = str(error)
                durable_write(path, operation)
                raise
            durable_write(path, operation)
            return operation


def main(args):
    if args == ["plan"]:
        _, plan = plan_transaction()
        return dict(digest=digest(plan), plan=plan)
    if args == ["verify"]:
        return verify()
    if len(args) == 2 and args[0] == "install":
        return install(args[1])
    raise RuntimeError("Usage: udm-packages plan | verify | install REVIEWED_SHA256")


if __name__ == "__main__":
    try:
        print(json.dumps(main(sys.argv[1:]), indent=2))
    except Exception as error:
        print(json.dumps(dict(error=str(error), recovery=RECOVERY)), file=sys.stderr)
        sys.exit(1)
