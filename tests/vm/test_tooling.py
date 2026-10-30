"""Provenance and freshness boundaries without downloading or running images."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('tooling', Path(__file__).with_name('tooling.py'))
tooling = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tooling)


class Tooling(unittest.TestCase):
    def setUp(self):
        self.repository = 'WhatzGames/Universal-Desktop-Manager'
        self.run = dict(id=42, run_attempt=2, head_sha='a' * 40, conclusion='success',
                        path=tooling.WORKFLOW, event='workflow_dispatch',
                        head_repository={'full_name': self.repository})
        self.metadata = dict(schema_version=1, run_id=42, run_attempt=2,
                             source_revision='a' * 40, platform='linux/amd64',
                             dockerfile_sha256='b' * 64, image_id='sha256:' + 'c' * 64,
                             archive_sha256='d' * 64)

    def validate(self, metadata=None, run=None, reviewed=None):
        tooling.validate(metadata or self.metadata, run or self.run, self.repository, 'b' * 64, reviewed)

    def test_accepts_current_producer_and_exact_reviewed_image(self):
        self.validate()
        self.validate(reviewed={'tooling_image': self.metadata})

    def test_latest_image_change_or_old_manifest_requires_fresh_review(self):
        for reviewed in ({}, {'tooling_image': {**self.metadata, 'archive_sha256': 'e' * 64}}):
            with self.assertRaisesRegex(ValueError, 'changed since review'):
                self.validate(reviewed=reviewed)

    def test_rejects_wrong_source_recipe_attempt_architecture_and_hashes(self):
        for key, value in [('run_id', 43), ('run_attempt', 1), ('source_revision', 'e' * 40),
                           ('dockerfile_sha256', 'e' * 64), ('platform', 'linux/arm64'),
                           ('image_id', 'latest'), ('archive_sha256', None)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.validate(metadata={**self.metadata, key: value})

    def test_rejects_failed_foreign_or_pull_request_producers(self):
        for key, value in [('conclusion', 'failure'), ('path', 'other.yml'),
                           ('event', 'pull_request'), ('head_repository', {'full_name': 'other/repo'})]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.validate(run={**self.run, key: value})


if __name__ == '__main__':
    unittest.main()
