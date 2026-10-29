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
    return subprocess.run(args, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=check, timeout=3600)


def identity(pid):
    # /proc comm can contain spaces and parentheses; starttime is field 22.
    return dict(pid=int(pid), start=Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19])


def baseline():
    assert Path('/var/lib/udm-ci-provisioned').exists()
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
        if fields.get('Name') == 'desktop' and fields.get('Active') == 'yes':
            assert fields['Type'] == 'x11' and fields['Remote'] == 'no'
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


def evidence():
    logs = {}
    for path in ('/var/log/dpkg.log', '/var/log/apt/term.log', '/var/log/apt/history.log'):
        p = Path(path)
        if p.exists():
            logs[path] = p.read_text(errors='replace')
    return dict(records=records(), native_logs=logs, inventory=run('dpkg-query', '-W').stdout,
                audit=run('dpkg', '--audit', check=False).stdout,
                baseline=baseline(), screenshot=screenshot())


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
                    for proc in Path('/proc').glob('[0-9]*/comm'):
                        try:
                            if proc.read_text().strip() == 'dpkg':
                                observed.append(int(proc.parent.name))
                        except FileNotFoundError:
                            pass
                    if observed:
                        # Kill the native package process during its real operation.
                        for pid in observed:
                            os.kill(pid, signal.SIGSTOP)
                        os.killpg(process.pid, signal.SIGKILL)
                        for pid in observed:
                            try:
                                os.kill(pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        break
                    time.sleep(0.01)
                assert observed, 'No native dpkg operation observed; interruption not tested'
                process.wait(timeout=30)
                assert any(r['phase'] in ('installing', 'verifying') for r in records())
                retry = install(approved)
                assert retry.returncode != 0 and 'Interrupted operation' in retry.stderr
                failed = retry
            else:
                failed = install(approved)
            result = evidence()
            result.update(returncode=failed.returncode, stdout=failed.stdout, stderr=failed.stderr)
            if operation == 'verification-failure':
                assert failed.returncode == 0
                # Corrupt only the disposable guest's installed launcher, then verify honestly.
                Path('/usr/bin/startplasma-wayland').chmod(0o644)
                verification = json.loads(run('/usr/local/bin/udm-app', 'packages', 'verify').stdout)
                assert not verification['ready'] and not verification['launcher_executable']
                result['verification'] = verification
            else:
                assert failed.returncode != 0
                assert result['records'], 'Native failure did not reach the helper journal'
                if operation != 'interruption':
                    assert result['records'][-1]['phase'] == 'failed'
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
    main()
