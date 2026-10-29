"""Checks the approval boundary without starting a VM or installing packages."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('vm_runner', Path(__file__).with_name('run.py'))
vm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vm)


class Review(unittest.TestCase):
    def test_binds_source_plan_snapshot_and_files(self):
        with tempfile.TemporaryDirectory() as directory:
            vm.STATE = root = Path(directory)
            plan = {'install': [{'name': 'fixed', 'version': '1'}]}
            digest = vm.hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            vm.write(root / 'baseline.json', {'review': {'plan': plan, 'digest': digest}})
            for name in ('guest.qcow2', 'source.iso', 'seed.iso', 'uuid'):
                (root / name).write_text(name)
            manifest = dict(source_revision='a' * 40, plan_digest=digest, snapshot_name='reviewed', snapshot_restore_verified=True,
                            files={name: vm.sha(root / name) for name in
                                   ('guest.qcow2', 'source.iso', 'seed.iso', 'uuid', 'baseline.json')})
            vm.write(root / 'review.json', manifest)
            approved = vm.sha(root / 'review.json')
            vm.validate_review(manifest, approved, digest, 'a' * 40)
            for review, transaction, source in (('', digest, 'a' * 40),
                                                (approved, '0' * 64, 'a' * 40),
                                                (approved, digest, 'b' * 40)):
                with self.assertRaises(ValueError):
                    vm.validate_review(manifest, review, transaction, source)
            (root / 'guest.qcow2').write_text('changed')
            with self.assertRaises(ValueError):
                vm.validate_review(manifest, approved, digest, 'a' * 40)

    def test_rejects_rehashed_manifest_with_changed_transaction(self):
        # The helper digest must still match the actual complete plan in baseline.json.
        with tempfile.TemporaryDirectory() as directory:
            vm.STATE = root = Path(directory)
            vm.write(root / 'baseline.json', {'review': {'plan': {}, 'digest': '0' * 64}})
            for name in ('guest.qcow2', 'source.iso', 'seed.iso', 'uuid'):
                (root / name).write_text(name)
            manifest = dict(source_revision='s', plan_digest='0' * 64, snapshot_name='reviewed', snapshot_restore_verified=True,
                            files={name: vm.sha(root / name) for name in
                                   ('guest.qcow2', 'source.iso', 'seed.iso', 'uuid', 'baseline.json')})
            vm.write(root / 'review.json', manifest)
            with self.assertRaises(ValueError):
                vm.validate_review(manifest, vm.sha(root / 'review.json'), '0' * 64, 's')


class Sessions(unittest.TestCase):
    def test_logind_user_manager_does_not_count_as_graphical_session(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        spec = importlib.util.spec_from_file_location('vm_guest', Path(__file__).with_name('guest.py'))
        guest = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guest)

        def command(*args):
            if args[:2] == ('systemctl', 'is-active'):
                output = 'active'
            elif args[0] == 'pgrep' or args[:2] == ('systemctl', 'show'):
                output = '42'
            elif args[:2] == ('loginctl', 'list-sessions'):
                output = '2 desktop manager\n1 desktop seat0\n'
            else:
                kind = 'unspecified' if args[2] == '2' else 'x11'
                output = f'Name=desktop\nActive=yes\nRemote=no\nType={kind}\n'
            return SimpleNamespace(stdout=output)

        with patch.object(guest, 'run', side_effect=command), patch.object(guest, 'identity', return_value={'pid': 42}), patch.object(guest, 'Path') as path:
            path.return_value.exists.return_value = True
            path.return_value.glob.return_value = []
            path.return_value.read_text.return_value = 'baseline'
            self.assertEqual(guest.baseline()['sessions'], ['1'])


class Acceleration(unittest.TestCase):
    def test_requires_a_successful_kvm_probe(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        with patch.object(vm.os, 'access', return_value=False):
            self.assertEqual(vm.acceleration()['selected'], 'tcg')
        for code, selected in ((0, 'kvm'), (1, 'tcg')):
            with patch.object(vm.os, 'access', return_value=True), patch.object(vm.subprocess, 'run', return_value=SimpleNamespace(returncode=code, stderr='probe evidence')):
                measured = vm.acceleration()
                self.assertEqual(measured['selected'], selected)
                self.assertEqual(measured['probe_returncode'], code)


class Source(unittest.TestCase):
    def test_rejects_abbreviated_or_mistyped_source_before_provisioning(self):
        from unittest.mock import patch
        for source in ('8566addd', 'g' * 40, ''):
            with patch.object(vm, 'prepare') as prepare, patch('sys.argv', ['run.py', 'prepare', '--source', source]):
                with self.assertRaises(ValueError):
                    vm.main()
                prepare.assert_not_called()


class CpuModel(unittest.TestCase):
    def test_kvm_uses_fixed_migration_model_instead_of_host_passthrough(self):
        from unittest.mock import patch
        old_state = vm.STATE
        try:
            with tempfile.TemporaryDirectory() as directory:
                vm.STATE = Path(directory)
                (vm.STATE / 'uuid').write_text('9226415a-9a66-4157-89a1-ae8e5b3b6546')
                for acceleration, cpu in (('kvm', vm.KVM_CPU), ('tcg', 'max')):
                    with patch.object(vm, 'acceleration', return_value={'selected': acceleration}), patch.object(vm.subprocess, 'Popen') as popen, patch.object(vm.subprocess, 'check_output', return_value='QEMU test version'):
                        instance = vm.VM()
                        command = popen.call_args.args[0]
                        self.assertEqual(command[command.index('-cpu') + 1], cpu)
                        self.assertNotEqual(cpu, 'host')
                        instance.log.close()
        finally:
            vm.STATE = old_state


class Interruption(unittest.TestCase):
    def test_ignores_planning_audit_and_unrelated_processes(self):
        from unittest.mock import patch
        spec = importlib.util.spec_from_file_location('vm_guest', Path(__file__).with_name('guest.py'))
        guest = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guest)
        digest = 'a' * 64
        with tempfile.TemporaryDirectory() as directory:
            comm = Path(directory) / '42' / 'comm'
            comm.parent.mkdir()
            comm.write_text('dpkg\n')
            cmd = comm.parent / 'cmdline'
            for phase, args, group, expected in (
                ('installing', b'dpkg\0--audit\0', 7, False),
                ('planned', b'dpkg\0--unpack\0pkg.deb\0', 7, False),
                ('installing', b'dpkg\0--unpack\0pkg.deb\0', 8, False),
                ('installing', b'dpkg\0--unpack\0pkg.deb\0', 7, True),
            ):
                cmd.write_bytes(args)
                with patch.object(guest, 'records', return_value=[dict(digest=digest, phase=phase)]), patch.object(guest.Path, 'glob', return_value=[comm]), patch.object(guest.os, 'getpgid', return_value=group):
                    self.assertEqual(bool(guest.installing_dpkg(digest, 7)), expected)


if __name__ == '__main__':
    unittest.main()
