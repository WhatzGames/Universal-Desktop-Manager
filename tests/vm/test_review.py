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
            manifest = dict(source_revision='a' * 40, plan_digest=digest, snapshot_name='reviewed',
                            files={name: vm.sha(root / name) for name in
                                   ('guest.qcow2', 'source.iso', 'seed.iso', 'uuid', 'baseline.json')})
            vm.write(root / 'review.json', manifest)
            approved = vm.sha(root / 'review.json')
            vm.validate_review(manifest, approved, digest, 'a' * 40)
            for review, transaction, source in (('', digest, 'a' * 40),
                                                (approved, '0' * 64, 'a' * 40),
                                                (approved, digest, 'b' * 40)):
                with self.assertRaises(AssertionError):
                    vm.validate_review(manifest, review, transaction, source)
            (root / 'guest.qcow2').write_text('changed')
            with self.assertRaises(AssertionError):
                vm.validate_review(manifest, approved, digest, 'a' * 40)

    def test_rejects_rehashed_manifest_with_changed_transaction(self):
        # The helper digest must still match the actual complete plan in baseline.json.
        with tempfile.TemporaryDirectory() as directory:
            vm.STATE = root = Path(directory)
            vm.write(root / 'baseline.json', {'review': {'plan': {}, 'digest': '0' * 64}})
            manifest = dict(source_revision='s', plan_digest='0' * 64, snapshot_name='reviewed',
                            files={'baseline.json': vm.sha(root / 'baseline.json')})
            vm.write(root / 'review.json', manifest)
            with self.assertRaises(AssertionError):
                vm.validate_review(manifest, vm.sha(root / 'review.json'), '0' * 64, 's')


if __name__ == '__main__':
    unittest.main()
