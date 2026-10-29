"""The push gate must reject accidental triggers before any VM is scheduled."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('approval', Path(__file__).with_name('approval.py'))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class Approval(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(Path('.ci/debian13-approval.example.json').read_text())
        self.record['approved'] = True
        self.event = dict(ref=gate.BRANCH, before='a' * 40, after='b' * 40,
                          created=False, deleted=False, forced=False, sender={'login': 'WhatzGames'})
        self.commit = dict(sha='b' * 40, author={'login': 'WhatzGames'}, committer={'login': 'WhatzGames'},
                           commit=dict(verification={'verified': True},
                                       message='Approve Debian 13 VM ' + self.record['review_sha256'] + '\n\nCo-authored-by: test'))

    def validate(self, **changes):
        args = dict(event=self.event, record=self.record, commit=self.commit, parent='a' * 40,
                    changes='A\t' + gate.APPROVAL, previous=None, actor='WhatzGames', owner='WhatzGames', attempt='1')
        args.update(changes)
        return gate.validate(**args)

    def test_exact_signed_approval_produces_only_bound_inputs(self):
        result = self.validate()
        self.assertEqual(result['source_revision'], self.record['source_revision'])
        self.assertEqual(result['approval_commit'], 'b' * 40)
        self.assertEqual(result['software_only'], 'true')

    def test_unrelated_pushes_force_creation_and_multiple_commits_are_rejected(self):
        for key, value in [('ref', 'refs/heads/main'), ('created', True), ('deleted', True),
                           ('forced', True), ('before', '0' * 40)]:
            event = {**self.event, key: value}
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.validate(event=event)
        for change in ('M\tREADME.md', 'M\t' + gate.APPROVAL + '\nM\tREADME.md', 'D\t' + gate.APPROVAL):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.validate(changes=change)
        with self.assertRaises(ValueError):
            self.validate(parent='c' * 40)

    def test_unsigned_wrong_owner_title_rerun_and_repeat_are_rejected(self):
        commit = copy.deepcopy(self.commit)
        commit['commit']['verification']['verified'] = False
        for change in (dict(commit=commit), dict(actor='someone-else'), dict(attempt='2'),
                       dict(previous=dict(self.record))):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.validate(**change)
        commit = copy.deepcopy(self.commit)
        commit['commit']['message'] = 'Ordinary documentation update'
        with self.assertRaises(ValueError):
            self.validate(commit=commit)

    def test_placeholder_missing_and_changed_digest_fields_are_rejected(self):
        for key, value in [('approved', False), ('source_revision', 'short'), ('review_run', True),
                           ('review_sha256', ''), ('plan_digest', 'x' * 64), ('software_only', 'true')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.validate(record={**self.record, key: value})
        with self.assertRaises(ValueError):
            self.validate(record={**self.record, 'extra': 'field'})
        self.assertEqual(self.validate(previous={**self.record, 'approved': False})['approval_commit'], 'b' * 40)

    def test_actual_review_manifest_and_run_must_match_before_vm_outputs(self):
        manifest = Path('docs/development/validation/v0.2-vm/tcg-review.json').read_bytes()
        run = dict(conclusion='success', head_sha=self.record['source_revision'],
                   head_repository={'full_name': 'WhatzGames/Universal-Desktop-Manager'},
                   event='push', head_branch='ci/debian13-snapshot-vm', path='.github/workflows/debian-vm-tcg.yml')
        gate.check_review(self.record, run, manifest, 'WhatzGames/Universal-Desktop-Manager')
        for key, value in [('conclusion', 'failure'), ('head_sha', 'c' * 40), ('path', 'other.yml')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                gate.check_review(self.record, {**run, key: value}, manifest, 'WhatzGames/Universal-Desktop-Manager')
        with self.assertRaises(ValueError):
            gate.check_review(self.record, run, manifest + b' ', 'WhatzGames/Universal-Desktop-Manager')
        with self.assertRaises(ValueError):
            gate.check_review({**self.record, 'plan_digest': '0' * 64}, run, manifest, 'WhatzGames/Universal-Desktop-Manager')


if __name__ == '__main__':
    unittest.main()
