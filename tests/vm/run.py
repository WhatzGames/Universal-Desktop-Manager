#!/usr/bin/env python3
"""QEMU snapshot preparation and explicit digest-bound acceptance runner."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time
import urllib.request
import uuid

ROOT = Path('/source')
STATE = Path('/state')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def rpc(path, command, arguments=None, qmp=False):
    with socket.socket(socket.AF_UNIX) as sock:
        sock.settimeout(120)
        sock.connect(str(path))
        stream = sock.makefile('rwb')
        if qmp:
            json.loads(stream.readline())
            stream.write(b'{"execute":"qmp_capabilities"}\n')
            stream.flush()
            while 'return' not in json.loads(stream.readline()):
                pass
        stream.write(json.dumps(dict(execute=command, arguments=arguments or {})).encode() + b'\n')
        stream.flush()
        while True:
            response = json.loads(stream.readline())
            if 'error' in response:
                raise RuntimeError(response['error'])
            if 'return' in response:
                return response['return']


def acceleration():
    if not os.access('/dev/kvm', os.R_OK | os.W_OK):
        return dict(selected='tcg', reason='No accessible KVM device inside tooling container')
    try:
        probe = subprocess.run(['qemu-system-x86_64', '-machine', 'q35,accel=kvm',
                                '-cpu', 'host', '-m', '128', '-nodefaults', '-display', 'none',
                                '-S', '-qmp', 'stdio'], text=True, capture_output=True, timeout=15,
                               input='{"execute":"qmp_capabilities"}\n{"execute":"quit"}\n')
        return dict(selected='kvm' if probe.returncode == 0 else 'tcg',
                    probe_returncode=probe.returncode, probe_stderr=probe.stderr)
    except subprocess.TimeoutExpired:
        return dict(selected='tcg', reason='KVM initialization probe timed out')


class VM:
    def __init__(self, restore=False):
        self.log = (STATE / 'serial.log').open('ab')
        self.acceleration = acceleration()
        self.accel = self.acceleration['selected']
        command = ['qemu-system-x86_64', '-machine', f'q35,accel={self.accel}',
                   '-cpu', 'host' if self.accel == 'kvm' else 'max', '-m', '4096', '-smp', '2',
                   '-uuid', (STATE / 'uuid').read_text().strip(),
                   '-drive', f'file={STATE}/guest.qcow2,if=virtio,format=qcow2',
                   '-drive', f'file={STATE}/seed.iso,media=cdrom,readonly=on',
                   '-drive', f'file={STATE}/source.iso,media=cdrom,readonly=on',
                   '-device', 'virtio-vga', '-display', 'none',
                   '-netdev', 'user,id=net0', '-device', 'virtio-net-pci,netdev=net0,id=nic0',
                   '-device', 'virtio-serial', '-chardev', f'socket,path={STATE}/qga.sock,server=on,wait=off,id=qga0',
                   '-device', 'virtserialport,chardev=qga0,name=org.qemu.guest_agent.0',
                   '-qmp', f'unix:{STATE}/qmp.sock,server=on,wait=off', '-serial', 'stdio']
        if restore:
            command += ['-loadvm', 'reviewed']
        self.process = subprocess.Popen(command, stdout=self.log, stderr=subprocess.STDOUT)
        execution = dict(acceleration=self.acceleration, host_architecture=os.uname().machine,
                         qemu_version=subprocess.check_output(['qemu-system-x86_64', '--version'], text=True),
                         started_unix=time.time(), restore=restore)
        write(STATE / 'execution.json', execution)
        print(json.dumps(execution), flush=True)

    def qmp(self, command, **args):
        return rpc(STATE / 'qmp.sock', command, args, qmp=True)

    def guest(self, operation, *args, timeout=3600):
        pid = rpc(STATE / 'qga.sock', 'guest-exec', dict(
            path='/usr/bin/python3', arg=['/source/tests/vm/guest.py', operation, *args],
            **{'capture-output': True}))['pid']
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            result = rpc(STATE / 'qga.sock', 'guest-exec-status', dict(pid=pid))
            if result['exited']:
                out = base64.b64decode(result.get('out-data', '')).decode()
                err = base64.b64decode(result.get('err-data', '')).decode()
                (STATE / f'{operation}-stdout.log').write_text(out)
                (STATE / f'{operation}-stderr.log').write_text(err)
                assert not result.get('out-truncated') and not result.get('err-truncated'), 'QGA output truncated'
                if result.get('exitcode') != 0:
                    write(STATE / f'{operation}-failure.json', json.loads(out) if out else {'stderr': err})
                    raise RuntimeError(f'{operation} failed: {err[-4000:]}')
                return json.loads(out)
            time.sleep(2)
        raise TimeoutError(operation)

    def ready(self, timeout):
        deadline = time.monotonic() + timeout
        last = ''
        while time.monotonic() < deadline:
            assert self.process.poll() is None, 'QEMU exited; inspect serial.log'
            try:
                return self.guest('capture', timeout=120)
            except (OSError, ValueError, RuntimeError, AssertionError) as error:
                last = str(error)
            time.sleep(5)
        raise TimeoutError(f'Guest desktop not ready: {last}')

    def close(self):
        if self.process.poll() is None:
            try:
                self.qmp('quit')
            finally:
                self.process.wait(timeout=30)
        self.log.close()


def export(name, result):
    result = dict(result)
    if 'screenshot' in result:
        (STATE / f'{name}.png').write_bytes(base64.b64decode(result.pop('screenshot')))
    for filename, content in result.pop('files', {}).items():
        destination = STATE / 'plasma' / filename
        assert destination.name == filename and '/' not in filename
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(base64.b64decode(content))
    write(STATE / f'{name}.json', result)
    return result


def validate_review(manifest, expected_manifest, expected_plan, expected_source):
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    require(sha(STATE / 'review.json') == expected_manifest, 'Review manifest differs')
    require(manifest['source_revision'] == expected_source, 'Source revision differs')
    require(manifest['plan_digest'] == expected_plan, 'Transaction digest differs')
    require(manifest['snapshot_name'] == 'reviewed', 'Snapshot name differs')
    required = {'guest.qcow2', 'source.iso', 'seed.iso', 'uuid', 'baseline.json'}
    require(set(manifest['files']) == required, 'Snapshot file inventory differs')
    for name, digest in manifest['files'].items():
        require(sha(STATE / name) == digest, f'{name} differs')
    review = json.loads((STATE / 'baseline.json').read_text())['review']
    actual = hashlib.sha256(json.dumps(review['plan'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    require(actual == review['digest'] == expected_plan, 'Complete transaction differs')


def prepare(args):
    STATE.mkdir(exist_ok=True)
    assert not (STATE / 'guest.qcow2').exists(), 'Use a fresh state directory'
    started = time.monotonic()
    image = 'debian-13-generic-amd64.qcow2'
    url = 'https://cloud.debian.org/images/cloud/trixie/latest/'
    urllib.request.urlretrieve(url + 'SHA512SUMS', STATE / 'SHA512SUMS')
    sums = (STATE / 'SHA512SUMS').read_text()
    expected = [line.split()[0] for line in sums.splitlines() if line.split()[-1].lstrip('*') == image]
    assert len(expected) == 1, 'Missing Debian image checksum'
    urllib.request.urlretrieve(url + image, STATE / 'base.qcow2')
    h = hashlib.sha512()
    with (STATE / 'base.qcow2').open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    assert h.hexdigest() == expected[0], 'Debian image checksum mismatch'
    subprocess.run(['qemu-img', 'convert', '-O', 'qcow2', str(STATE / 'base.qcow2'), str(STATE / 'guest.qcow2')], check=True)
    subprocess.run(['qemu-img', 'resize', str(STATE / 'guest.qcow2'), '24G'], check=True)
    (STATE / 'base.qcow2').unlink()
    (STATE / 'uuid').write_text(str(uuid.uuid4()))
    seed = STATE / 'seed'
    seed.mkdir()
    (seed / 'meta-data').write_text('instance-id: udm-' + (STATE / 'uuid').read_text() + '\nlocal-hostname: udm-ci\n')
    script = base64.b64encode((ROOT / 'tests/vm/provision.sh').read_bytes()).decode()
    (seed / 'user-data').write_text('#cloud-config\nssh_pwauth: false\ndisable_root: true\n'
        'users: []\nssh_genkeytypes: []\nwrite_files:\n  - path: /root/udm-provision.sh\n    permissions: "0700"\n'
        f'    encoding: b64\n    content: {script}\n'
        'runcmd:\n  - [sh, /root/udm-provision.sh]\n')
    subprocess.run(['genisoimage', '-quiet', '-output', str(STATE / 'seed.iso'), '-volid', 'cidata', '-joliet', '-rock', str(seed)], check=True)
    source = STATE / 'source'
    source.mkdir()
    for name in ('tests', 'packaging'):
        shutil.copytree(ROOT / name, source / name)
    shutil.copyfile(ROOT / 'target/debug/udm-app', source / 'udm-app')
    subprocess.run(['genisoimage', '-quiet', '-output', str(STATE / 'source.iso'), '-volid', 'UDMSOURCE', '-joliet', '-rock', str(source)], check=True)
    vm = VM()
    try:
        baseline = export('baseline', vm.ready(args.timeout))
        assert not baseline['dpkg_audit'].strip()
        export('denial', vm.guest('denial'))
        # Internal snapshot includes RAM, so original PID/starttime/session survive the gate.
        saved = vm.qmp('human-monitor-command', **{'command-line': 'savevm reviewed'})
        assert not saved.strip(), saved
    finally:
        vm.close()
    snapshot_info = subprocess.check_output(['qemu-img', 'snapshot', '-l', str(STATE / 'guest.qcow2')], text=True)
    assert 'reviewed' in snapshot_info
    (STATE / 'snapshots.txt').write_text(snapshot_info)
    manifest = dict(qemu_sha256=sha('/usr/bin/qemu-system-x86_64'),
                    qemu_version=subprocess.check_output(['qemu-system-x86_64', '--version'], text=True),
                    host_architecture=os.uname().machine, schema_version=1, source_revision=args.source, plan_digest=baseline['review']['digest'],
                    snapshot_name='reviewed', uuid=(STATE / 'uuid').read_text(), image_url=url + image,
                    image_sha512=expected[0], acceleration=vm.accel, acceleration_probe=vm.acceleration, prepare_seconds=time.monotonic() - started,
                    files={name: sha(STATE / name) for name in ('guest.qcow2', 'source.iso', 'seed.iso', 'uuid', 'baseline.json')})
    write(STATE / 'review.json', manifest)
    print(json.dumps(dict(review_sha256=sha(STATE / 'review.json'), **manifest), indent=2))


def accept(args):
    manifest = json.loads((STATE / 'review.json').read_text())
    validate_review(manifest, args.review_sha256, args.plan_digest, args.source)
    if manifest['qemu_sha256'] != sha('/usr/bin/qemu-system-x86_64') or manifest['host_architecture'] != os.uname().machine:
        raise ValueError('Snapshot requires the reviewed QEMU binary and host architecture')
    actual_accel = acceleration()['selected']
    if manifest['acceleration'] != actual_accel:
        raise ValueError('Snapshot acceleration differs; prepare and review again')
    # Never mutate the approved disk: each destructive case gets an independent copy.
    original = STATE / 'guest.qcow2'
    reviewed = STATE / 'reviewed.qcow2'
    original.rename(reviewed)
    outcomes = []
    try:
        baseline = json.loads((STATE / 'baseline.json').read_text())
        for case in ('stale', 'download-failure', 'dpkg-failure', 'interruption',
                     'verification-failure', 'install'):
            shutil.copyfile(reviewed, original)
            vm = VM(restore=True)
            try:
                before = vm.ready(180)
                assert before['baseline'] == baseline['baseline'], 'Running desktop identity changed'
                assert before['review'] == baseline['review'], 'Guest transaction state changed'
                result = export(case, vm.guest(case, args.plan_digest))
                assert result['baseline'] == baseline['baseline'], 'Original desktop/session changed'
                if case == 'install':
                    assert result['returncode'] == 0 and result['verification']['ready']
                    assert not result['verification']['session_started']
                    assert len(result['records']) == 1 and result['records'][0]['phase'] == 'ready'
                    assert result['records'][0]['digest'] == args.plan_digest
                    plasma = export('plasma', vm.guest('plasma'))
                    assert plasma['returncode'] == 0 and plasma['baseline'] == baseline['baseline']
                outcomes.append(dict(case=case, passed=True, recovery='Restore reviewed VM RAM/disk snapshot'))
                write(STATE / 'acceptance.json', dict(complete=False, outcomes=outcomes))
            finally:
                vm.close()
        # Verify administrator snapshot recovery after the final destructive case too.
        shutil.copyfile(reviewed, original)
        vm = VM(restore=True)
        try:
            recovered = export('recovered', vm.ready(180))
            assert recovered['baseline'] == baseline['baseline']
            assert recovered['review'] == baseline['review']
            assert recovered['inventory'] == baseline['inventory']
        finally:
            vm.close()
        write(STATE / 'acceptance.json', dict(complete=True, outcomes=outcomes,
              recovery='Reviewed snapshot restored; original inventory/session/process identities match',
              limits='No native package repair, physical GPU/input or session migration tested'))
    finally:
        original.unlink(missing_ok=True)
        reviewed.rename(original)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare', 'accept'])
    parser.add_argument('--source', required=True)
    parser.add_argument('--timeout', type=int, default=3600)
    parser.add_argument('--review-sha256')
    parser.add_argument('--plan-digest')
    args = parser.parse_args()
    if len(args.source) != 40 or any(c not in '0123456789abcdef' for c in args.source):
        raise ValueError('A full exact 40-character source commit SHA is required')
    if args.stage == 'accept':
        assert args.review_sha256 and args.plan_digest, 'Explicit reviewed digests required'
        accept(args)
    else:
        prepare(args)


if __name__ == '__main__':
    main()
