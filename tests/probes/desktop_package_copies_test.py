"""Small isolated regression cases; no old fixture/build/cache is removed."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from desktop_package_copies import PackageCopies


class PackageCopyLifetime(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="confectory-copy-lifetime-")
        self.root = Path(self.directory.name)
        self.source = self.root / "original"
        self.source.mkdir()
        (self.source / "binary").write_bytes(bytes(range(256)) * 1024)
        self.digest = hashlib.sha256((self.source / "binary").read_bytes()).hexdigest()

    def tearDown(self):
        self.assertEqual(self.digest, hashlib.sha256((self.source / "binary").read_bytes()).hexdigest())
        self.directory.cleanup()

    def preserve_evidence(self, owner):
        for name in ["evidence.json", "packaged-login.png", "packaged-host.log",
                     "owned-data/profile", "owned checkout/.confectory/editor-home/settings",
                     "owned checkout/examples/editor-home/project.cpack", "Windows result/binary"]:
            p = owner.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(name.encode())
        return {p: p.read_bytes() for p in owner.root.rglob("*") if p.is_file()}

    def assert_preserved(self, owner, evidence):
        self.assertTrue(owner.root.exists())
        self.assertTrue(all(p.read_bytes() == data for p, data in evidence.items()))
        report = json.loads((owner.root / "copy-cleanup.json").read_text())
        self.assertTrue(report["cleanupSucceeded"])
        self.assertTrue(all(c["removed"] and not Path(c["path"]).exists() for c in report["copies"]))
        return report

    def test_success_removes_only_created_copies(self):
        with PackageCopies(self.root) as owner:
            evidence = self.preserve_evidence(owner)
            for relative in sorted(owner.allowed):
                shutil.copytree(self.source, owner.create(relative), dirs_exist_ok=True)
        self.assertTrue(self.assert_preserved(owner, evidence)["operationSucceeded"])

    def test_assertion_and_mid_copy_exception_preserve_evidence(self):
        for failure, count in [(AssertionError, 2), (OSError, 1), (RuntimeError, 0)]:
            with self.subTest(failure=failure.__name__), self.assertRaises(failure):
                with PackageCopies(self.root) as owner:
                    evidence = self.preserve_evidence(owner)
                    for relative in sorted(owner.allowed)[:count]:
                        (owner.create(relative) / "partial").write_bytes(b"partial copy")
                    raise failure("isolated probe failure")
            report = self.assert_preserved(owner, evidence)
            self.assertFalse(report["operationSucceeded"])
            self.assertEqual(report["operationErrorType"], failure.__name__)

    def test_repeated_hardlink_and_reused_runtime_do_not_accumulate_copies(self):
        original_links = (self.source / "binary").stat().st_nlink
        for _ in range(3):
            with PackageCopies(self.root) as owner:
                evidence = self.preserve_evidence(owner)
                # External reuse is deliberately never registered with owner.
                reused_runtime = self.source
                target = owner.create("owned checkout/Builds/Windows-x64")
                shutil.copytree(self.source, target, copy_function=os.link, dirs_exist_ok=True)
                self.assertEqual((target / "binary").stat().st_ino, (reused_runtime / "binary").stat().st_ino)
            self.assert_preserved(owner, evidence)
            self.assertEqual((self.source / "binary").stat().st_nlink, original_links)
        self.assertFalse(any(self.root.glob("confectory-desktop-package-*/runtime only")))
        self.assertFalse(any(self.root.glob("confectory-desktop-package-*/owned checkout/Builds/Windows-x64")))

    def test_cannot_adopt_existing_or_unapproved_paths(self):
        with PackageCopies(self.root) as owner:
            existing = owner.root / "runtime only"
            shutil.copytree(self.source, existing)
            with self.assertRaises(FileExistsError):
                owner.create("runtime only")
            with self.assertRaises(ValueError):
                owner.create("../original")
        self.assertTrue((existing / "binary").exists())

    def test_active_process_defers_cleanup_until_waited(self):
        with PackageCopies(self.root) as owner:
            target = owner.create("runtime only")
            process = subprocess.Popen([sys.executable, "-c", "import time;time.sleep(30)"])
            owner.watch(process)
            try:
                with self.assertRaisesRegex(RuntimeError, "still using"):
                    owner.close()
                self.assertTrue(target.exists())
            finally:
                process.terminate()
                process.wait(timeout=10)
            owner.close()
            owner.close()  # A completed cleanup never adopts a replacement.
            target.mkdir()
        self.assertTrue(target.exists())

    def test_replaced_target_or_parent_is_not_followed(self):
        for replace_parent in [False, True]:
            with self.subTest(parent=replace_parent):
                with self.assertRaises(RuntimeError):
                    with PackageCopies(self.root) as owner:
                        target = owner.create("owned checkout/Builds/Windows-x64")
                        replaced = target.parent if replace_parent else target
                        replaced.rename(replaced.with_name(replaced.name + "-retained"))
                        replaced.symlink_to(self.source, target_is_directory=True)
                self.assertTrue(replaced.is_symlink())
                report = json.loads((owner.root / "copy-cleanup.json").read_text())
                self.assertFalse(report["cleanupSucceeded"])

    def test_leaf_symlink_is_removed_without_touching_external_target(self):
        with PackageCopies(self.root) as owner:
            target = owner.create("runtime only")
            (target / "outside").symlink_to(self.source, target_is_directory=True)
        self.assertFalse(target.exists())
        self.assertTrue((self.source / "binary").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
