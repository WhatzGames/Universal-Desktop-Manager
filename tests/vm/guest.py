#!/usr/bin/python3
"""Fixed acceptance operations inside a disposable VM; no UI-provided commands."""
import base64
import glob
import hashlib
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import time


def run(*args, check=True):
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False, timeout=3600)
    if check and result.returncode != 0:
        raise RuntimeError(f'{args[0]} exited {result.returncode}: {result.stdout} {result.stderr}')
    return result


def identity(pid):
    # /proc comm can contain spaces and parentheses; starttime is field 22.
    return dict(pid=int(pid), start=Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19])


def baseline():
    assert Path('/var/lib/udm-ci-provisioned').exists()
    assert not list(Path('/etc/ssh').glob('ssh_host_*')), 'Unexpected guest SSH keys'
    assert run('systemctl', 'is-active', 'lightdm').stdout.strip() == 'active'
    processes = {}
    for name in ('xfce4-session', 'xfwm4', 'xfdesktop', 'xfce4-panel'):
        processes[name] = [identity(p) for p in run('pgrep', '-u', 'desktop', '-x', name).stdout.split()]
        assert processes[name], name
    dm = run('systemctl', 'show', 'lightdm', '-p', 'MainPID', '--value').stdout.strip()
    sessions = run('loginctl', 'list-sessions', '--no-legend', '--no-pager').stdout
    active = []
    for line in sessions.splitlines():
        sid = line.split()[0]
        fields = dict(line.split('=', 1) for line in run('loginctl', 'show-session', sid,
                      '-p', 'Name', '-p', 'Active', '-p', 'Type', '-p', 'Remote').stdout.splitlines())
        # logind also reports the per-user manager; only a local X11 session qualifies.
        if (fields.get('Name') == 'desktop' and fields.get('Active') == 'yes'
                and fields.get('Type') == 'x11' and fields.get('Remote') == 'no'):
            active.append(sid)
    assert active, sessions
    return dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                machine_id=Path('/etc/machine-id').read_text().strip(),
                processes=processes, display_manager=identity(dm), sessions=active,
                dm_config=Path('/etc/X11/default-display-manager').read_text())


def screenshot():
    run('runuser', '-u', 'desktop', '--', 'env', 'DISPLAY=:0',
        'XAUTHORITY=/home/desktop/.Xauthority', 'import', '-window', 'root', '/tmp/original-desktop.png')
    return base64.b64encode(Path('/tmp/original-desktop.png').read_bytes()).decode()


def plan():
    return json.loads(run('runuser', '-u', 'desktop', '--', '/usr/local/bin/udm-app', 'packages', 'plan').stdout)


def capture():
    return dict(baseline=baseline(), review=plan(),
                inventory=run('dpkg-query', '-W').stdout, screenshot=screenshot(),
                os_release=Path('/etc/os-release').read_text(),
                cpu_vulnerabilities={p.name: p.read_text().strip() for p in
                                     Path('/sys/devices/system/cpu/vulnerabilities').glob('*') if p.is_file()},
                image_repositories=Path('/var/lib/udm-ci/image-debian.sources').read_text(),
                reviewed_repositories=Path('/etc/apt/sources.list.d/debian.sources').read_text(),
                dpkg_audit=run('dpkg', '--audit').stdout)


def authorize(digest):
    assert len(digest) == 64 and all(c in '0123456789abcdef' for c in digest)
    # CI's reviewed administrator authorization is limited to this helper + exact digest.
    rule = '''polkit.addRule(function(action, subject) {
      if (action.id === "org.whatzgames.udm.install" && subject.user === "desktop" &&
          action.lookup("program") === "/usr/libexec/udm-packages" &&
          action.lookup("command_line") === "/usr/libexec/udm-packages install %s")
        return polkit.Result.YES;
    });\n''' % digest
    Path('/etc/polkit-1/rules.d/00-udm-ci.rules').write_text(rule)
    time.sleep(3)


def install(digest):
    return run('runuser', '-u', 'desktop', '--', '/usr/local/bin/udm-app',
               'packages', 'install', digest, check=False)


def records():
    return [json.loads(Path(p).read_text()) for p in glob.glob('/var/lib/udm/operations/*.json')]


def process_ancestors(pid, root):
    lineage = []
    while pid > 1 and pid not in lineage:
        lineage.append(pid)
        if pid == root:
            return lineage
        pid = int(Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[1])
    return []


def installing_dpkg(digest, root):
    # Planning also runs dpkg --audit; interrupt only this approved native mutation.
    if not any(r['digest'] == digest and r['phase'] == 'installing' for r in records()):
        return []
    found = []
    for proc in Path('/proc').glob('[0-9]*/comm'):
        try:
            pid = int(proc.parent.name)
            args = (proc.parent / 'cmdline').read_bytes().split(b'\0')
            if (proc.read_text().strip() == 'dpkg' and
                    any(arg in (b'--unpack', b'--configure', b'--triggers-only', b'--install', b'-i') for arg in args)):
                lineage = process_ancestors(pid, root)
                if lineage:
                    found.append(dict(pid=pid, ancestors=lineage[1:], command=[a.decode(errors='replace') for a in args if a]))
        except (FileNotFoundError, ProcessLookupError):
            pass
    return found


def evidence():
    logs = {}
    for path in ('/var/log/dpkg.log', '/var/log/apt/term.log', '/var/log/apt/history.log'):
        p = Path(path)
        if p.exists():
            logs[path] = p.read_text(errors='replace')
    continuity = {}
    try:
        continuity.update(baseline=baseline(), screenshot=screenshot())
    except Exception as error:
        continuity['continuity_error'] = str(error)
    return dict(records=records(), native_logs=logs,
                polkit_journal=run('journalctl', '-u', 'polkit.service', '--no-pager', check=False).stdout,
                service_guard=Path('/usr/sbin/policy-rc.d').read_text() if Path('/usr/sbin/policy-rc.d').exists() else None,
                inventory=run('dpkg-query', '-W').stdout,
                audit=run('dpkg', '--audit', check=False).stdout,
                **continuity)


def main():
    operation = sys.argv[1]
    if operation == 'capture':
        result = capture()
    elif operation == 'denial':
        review = plan()
        before = run('dpkg-query', '-W').stdout
        denied = install(review['digest'])
        assert denied.returncode != 0 and not records(), denied.stdout + denied.stderr
        assert before == run('dpkg-query', '-W').stdout
        result = dict(returncode=denied.returncode, stdout=denied.stdout, stderr=denied.stderr,
                      baseline=baseline(), inventory_unchanged=True)
    elif operation == 'stale':
        before = run('dpkg-query', '-W').stdout
        stale = '0' * 64
        authorize(stale)
        try:
            rejected = install(stale)
        finally:
            Path('/etc/polkit-1/rules.d/00-udm-ci.rules').unlink()
        assert rejected.returncode != 0 and not records()
        assert before == run('dpkg-query', '-W').stdout
        assert 'changed since review' in rejected.stderr
        result = dict(returncode=rejected.returncode, stderr=rejected.stderr,
                      inventory_unchanged=True, baseline=baseline())
    elif operation in ('download-failure', 'dpkg-failure', 'interruption', 'verification-failure'):
        approved = sys.argv[2]
        assert plan()['digest'] == approved
        authorize(approved)
        try:
            if operation == 'dpkg-failure':
                Path('/run/udm-ci-dpkg-fail').touch()
            if operation == 'verification-failure':
                Path('/run/udm-ci-verification-fail').touch()
            if operation == 'download-failure':
                # No repository/config changes: use a separate network namespace with no uplink.
                # pkexec remains real, while APT's download fails honestly.
                command = ['unshare', '--net', 'runuser', '-u', 'desktop', '--',
                           '/usr/local/bin/udm-app', 'packages', 'install', approved]
                failed = run(*command, check=False)
            elif operation == 'interruption':
                process = subprocess.Popen(['runuser', '-u', 'desktop', '--', '/usr/local/bin/udm-app',
                                           'packages', 'install', approved],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                          start_new_session=True)
                deadline = time.monotonic() + 1800
                observed = []
                while time.monotonic() < deadline and process.poll() is None:
                    observed = installing_dpkg(approved, process.pid)
                    if observed:
                        # Kill the native package process during its real operation.
                        for native in observed:
                            os.kill(native['pid'], signal.SIGSTOP)
                        # Native APT/dpkg can change process groups; kill the exact parent chain.
                        for native in observed:
                            for pid in reversed(native['ancestors']):
                                try:
                                    os.kill(pid, signal.SIGKILL)
                                except ProcessLookupError:
                                    pass
                        for native in observed:
                            try:
                                os.kill(native['pid'], signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        break
                    time.sleep(0.01)
                assert observed, 'No journaled mutating dpkg operation observed; interruption not tested'
                process.wait(timeout=30)
                assert any(r['digest'] == approved and r['phase'] == 'installing' for r in records()), 'Interrupted native operation lost its installing journal'
                retry = install(approved)
                assert retry.returncode != 0 and 'Interrupted operation' in retry.stderr
                failed = retry
            else:
                failed = install(approved)
            result = evidence()
            if operation == 'interruption':
                result['interrupted_dpkg'] = observed
            result.update(returncode=failed.returncode, stdout=failed.stdout, stderr=failed.stderr)
            assert failed.returncode != 0
            assert result['records'], 'Native failure did not reach the helper journal'
            if operation != 'interruption':
                assert result['records'][-1]['phase'] == 'failed'
            if operation == 'verification-failure':
                verification = result['records'][-1]['verification']
                assert not verification['ready'] and not verification['launcher_executable']
                assert verification['dpkg_audit_clean']
                assert 'Package commit succeeded but KDE verification failed' in failed.stderr
                result['verification'] = verification
        finally:
            Path('/etc/polkit-1/rules.d/00-udm-ci.rules').unlink(missing_ok=True)
    elif operation == 'install':
        approved = sys.argv[2]
        assert plan()['digest'] == approved, 'Review is stale'
        authorize(approved)
        try:
            installed = install(approved)
        finally:
            Path('/etc/polkit-1/rules.d/00-udm-ci.rules').unlink()
        result = evidence()
        result.update(returncode=installed.returncode, stdout=installed.stdout, stderr=installed.stderr)
        verification = json.loads(run('/usr/local/bin/udm-app', 'packages', 'verify').stdout)
        result['verification'] = verification
    elif operation == 'plasma':
        out = Path('/tmp/plasma-artifacts')
        out.mkdir(exist_ok=True)
        run('chown', 'plasma-check:plasma-check', str(out))
        smoke = run('runuser', '-u', 'plasma-check', '--', 'dbus-run-session', '--',
                    '/usr/bin/python3', '/source/tests/plasma/smoke.py', check=False)
        result = dict(returncode=smoke.returncode, stdout=smoke.stdout, stderr=smoke.stderr,
                      baseline=baseline(), files={p.name: base64.b64encode(p.read_bytes()).decode()
                                                 for p in out.iterdir() if p.is_file()})
    else:
        raise ValueError(operation)
    print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Retain native evidence even when an acceptance assertion fails.
        try:
            failure = evidence()
        except Exception as capture_error:
            failure = dict(capture_error=str(capture_error))
        print(json.dumps(dict(harness_error=str(error), evidence=failure)))
        sys.exit(1)
