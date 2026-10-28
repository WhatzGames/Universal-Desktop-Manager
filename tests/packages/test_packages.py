"""Safety contract tests; no APT calls or privileged host changes."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace as NS
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
from contextlib import nullcontext

spec = importlib.util.spec_from_file_location("packages", Path(__file__).parents[2] / "packaging/debian/udm_packages.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def package(name="example", installed=None, deleted=False, origin="Debian", site="deb.debian.org", trusted=True):
    version = NS(version="1.0", architecture="amd64", size=10, installed_size=20,
                 origins=[NS(origin=origin, label="Debian", archive="trixie", site=site,
                             component="main", trusted=trusted)], get_dependencies=lambda *args: [], provides=[])
    value = NS(name=name, candidate=version, installed=installed, marked_delete=deleted,
               mark_install=lambda **kwargs: None)
    version.package = value
    return value


class Cache(dict):
    broken_count = 0
    dpkg_journal_dirty = False

    def __init__(self, changes=None):
        super().__init__((name, package(name)) for name in m.TARGETS)
        self.changes = changes if changes is not None else [package()]

    def get_changes(self):
        return self.changes


class Packages(unittest.TestCase):
    def test_polkit_policy_is_restricted_and_does_not_cache_authorization(self):
        policy = Path(__file__).parents[2] / "packaging/polkit/org.whatzgames.udm.install.policy"
        action = ET.parse(policy).getroot().find("action")
        self.assertEqual(action.attrib["id"], "org.whatzgames.udm.install")
        self.assertEqual(action.findtext("defaults/allow_any"), "no")
        self.assertEqual(action.findtext("defaults/allow_inactive"), "no")
        self.assertEqual(action.findtext("defaults/allow_active"), "auth_admin")
        self.assertEqual(action.findtext("annotate"), "/usr/libexec/udm-packages")

    def test_dependency_plan_has_versions_origins_and_estimates(self):
        changes = m.resolve(Cache())
        self.assertEqual(changes[0]["version"], "1.0")
        self.assertEqual(changes[0]["download_bytes"], 10)
        self.assertTrue(changes[0]["origins"][0]["trusted"])

    def test_removal_upgrade_display_manager_and_untrusted_origin_rejected(self):
        for change in (package(deleted=True), package(installed=True), package("sddm"),
                       package("gdm3:amd64"), package(origin="Other"), package(trusted=False),
                       package(site="unknown.example")):
            with self.subTest(change=change.name), self.assertRaises(RuntimeError):
                m.resolve(Cache([change]))

    def test_broken_or_missing_candidate_rejected(self):
        cache = Cache()
        cache.broken_count = 1
        with self.assertRaises(RuntimeError):
            m.resolve(cache)
        cache.broken_count = 0
        cache[m.TARGETS[0]].candidate = None
        with self.assertRaises(RuntimeError):
            m.resolve(cache)

    def test_digest_stable_and_changes_with_review(self):
        self.assertEqual(m.digest({"a": 1, "b": 2}), m.digest({"b": 2, "a": 1}))
        self.assertNotEqual(m.digest({"a": 1}), m.digest({"a": 2}))

    def test_no_arbitrary_command_or_path(self):
        for args in (["shell", "id"], ["plan", "extra"], ["install", "--help"], ["install", "/tmp/file"]):
            with self.subTest(args=args), self.assertRaises(RuntimeError):
                m.main(args)

    def test_install_requires_authorization(self):
        with patch.object(m.os, "geteuid", return_value=1000), self.assertRaises(RuntimeError):
            m.install("a" * 64)

    def test_service_guard_preserves_existing_policy_and_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = Path(directory) / "policy"
            with patch.object(m, "POLICY", policy):
                policy.write_text("administrator policy")
                with self.assertRaises(FileExistsError), m.service_guard():
                    self.fail("must not enter")
                self.assertEqual(policy.read_text(), "administrator policy")
                policy.unlink()
                policy.symlink_to("missing")
                with self.assertRaises(FileExistsError), m.service_guard():
                    self.fail("must not enter")
                self.assertTrue(policy.is_symlink())

    def test_service_guard_cleanup_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = Path(directory) / "policy"
            with patch.object(m, "POLICY", policy):
                with self.assertRaisesRegex(RuntimeError, "injected"), m.service_guard():
                    self.assertIn("exit 101", policy.read_text())
                    raise RuntimeError("injected")
                self.assertFalse(policy.exists())

    def run_install(self, directory, plan, commit=None, reviewed=None, ready=True):
        cache = NS(commit=commit or (lambda **kwargs: True))
        modules = (NS(), NS(SystemLock=nullcontext))
        with (patch.object(m, "JOURNAL", Path(directory)),
              patch.object(m, "POLICY", Path(directory) / "policy"),
              patch.object(m.os, "geteuid", return_value=0),
              patch.dict(m.os.environ, {"PKEXEC_UID": "1000"}),
              patch.object(m, "apt_modules", return_value=modules),
              patch.object(m, "plan_transaction", return_value=(cache, plan)),
              patch.object(m.os, "statvfs", return_value=NS(f_bavail=10000000, f_frsize=4096)),
              patch.object(m, "verify", return_value={"ready": ready})):
            return m.install(reviewed or m.digest(plan))

    def test_changed_plan_rejected_before_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "changed since review"):
                self.run_install(directory, {}, reviewed="a" * 64,
                                 commit=lambda: self.fail("must not commit"))
            self.assertEqual(list(Path(directory).glob("*.json")), [])

    def test_commit_failure_is_durable_and_guard_removed(self):
        def fail(**kwargs):
            raise RuntimeError("injected dpkg failure")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "injected"):
                self.run_install(directory, {"additional_disk_bytes": 0, "download_bytes": 0}, commit=fail)
            record = json.loads(next(Path(directory).glob("*.json")).read_text())
            self.assertEqual(record["phase"], "failed")
            self.assertIn("no automatic rollback", record["recovery"])
            self.assertFalse((Path(directory) / "policy").exists())

    def test_success_and_verification_failure_are_distinct(self):
        for ready in (True, False):
            with self.subTest(ready=ready), tempfile.TemporaryDirectory() as directory:
                if ready:
                    result = self.run_install(directory, {"additional_disk_bytes": 0, "download_bytes": 0})
                    self.assertEqual(result["phase"], "ready")
                else:
                    with self.assertRaisesRegex(RuntimeError, "verification failed"):
                        self.run_install(directory, {"additional_disk_bytes": 0, "download_bytes": 0}, ready=False)
                record = json.loads(next(Path(directory).glob("*.json")).read_text())
                self.assertEqual(record["phase"], "ready" if ready else "failed")

    def test_interrupted_operation_blocks_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "prior.json").write_text('{"phase":"installing"}')
            with self.assertRaisesRegex(RuntimeError, "Interrupted operation"):
                self.run_install(directory, {}, commit=lambda: self.fail("must not commit"))

    def test_debian_wrapped_launcher_and_optional_type(self):
        fields = {"Name": "Plasma (Wayland)", "Exec": "/usr/lib/x86_64-linux-gnu/libexec/plasma-dbus-run-session-if-needed /usr/bin/startplasma-wayland"}
        with patch.object(m.os, "access", return_value=True):
            self.assertTrue(m.session_matches(fields, Path("/usr/bin/startplasma-wayland")))
            fields["Hidden"] = "true"
            self.assertFalse(m.session_matches(fields, Path("/usr/bin/startplasma-wayland")))
        fields = {"Name": "Plasma", "Exec": "/bin/sh /usr/bin/startplasma-wayland"}
        self.assertFalse(m.session_matches(fields, Path("/usr/bin/startplasma-wayland")))

    def test_journal_atomic_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            m.durable_write(path, {"phase": "installing"})
            m.durable_write(path, {"phase": "failed"})
            self.assertEqual(json.loads(path.read_text()), {"phase": "failed"})
            self.assertFalse(path.with_suffix(".tmp").exists())


if __name__ == "__main__":
    unittest.main()
