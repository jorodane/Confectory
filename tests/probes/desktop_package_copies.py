"""Lifetime of the two disposable copies made by desktop_package.py.

The fixture root, evidence, profiles and generated/original packages are retained.
Only explicitly created copy directories can be removed by this owner.
"""
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile


class PackageCopies:
    allowed = frozenset({"runtime only", "owned checkout/Builds/Windows-x64"})

    def __init__(self, directory=None):
        self.root = Path(tempfile.mkdtemp(prefix="confectory-desktop-package-", dir=directory))
        self.root_identity = self._identity(self.root)
        self.copies = []
        self.processes = []

    @staticmethod
    def _identity(path):
        info = path.lstat()
        if not stat.S_ISDIR(info.st_mode):
            raise RuntimeError(f"Copy directory was replaced or linked: {path}")
        return info.st_dev, info.st_ino, info.st_uid

    def _root_unchanged(self):
        if any(p.is_symlink() for p in [self.root, *self.root.parents]):
            raise RuntimeError("Fixture root has a linked ancestor")
        if self._identity(self.root) != self.root_identity:
            raise RuntimeError("Fixture root was replaced")

    def create(self, relative):
        if relative not in self.allowed:
            raise ValueError("Not a disposable package copy path")
        self._root_unchanged()
        target = self.root / relative
        parent = self.root
        parents = []
        for part in Path(relative).parts[:-1]:
            parent = parent / part
            parent.mkdir(exist_ok=True)
            parents.append((parent, self._identity(parent)))
        # No existing directory, reused runtime or original can be adopted.
        target.mkdir()
        self.copies.append({"path": target, "identity": self._identity(target),
                            "parents": parents, "removed": False})
        return target

    def watch(self, process):
        self.processes.append(process)

    def close(self):
        self._root_unchanged()
        if any(p.poll() is None for p in self.processes):
            raise RuntimeError("A package process is still using the copies")
        pending = [copy for copy in self.copies if not copy["removed"]]
        # Validate all ownership before removing anything. Never follow a new
        # parent link or delete a replacement at the old path.
        for copy in pending:
            if any(self._identity(p) != identity for p, identity in copy["parents"]):
                raise RuntimeError("A copy parent was replaced")
            if self._identity(copy["path"]) != copy["identity"]:
                raise RuntimeError("A copy directory was replaced")
        if pending and not shutil.rmtree.avoids_symlink_attacks:
            raise RuntimeError("Safe directory-relative removal is unavailable")
        for copy in pending:
            target = copy["path"]
            parent_fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                shutil.rmtree(target.name, dir_fd=parent_fd)
            finally:
                os.close(parent_fd)
            copy["removed"] = True

    def __enter__(self):
        return self

    def __exit__(self, error_type, error, traceback):
        cleanup_error = None
        try:
            self.close()
        except Exception as failure:
            cleanup_error = failure
        # Never follow a replaced root just to write the cleanup report.
        self._root_unchanged()
        report = {"operationSucceeded": error_type is None,
                  "operationErrorType": error_type.__name__ if error_type else None,
                  "cleanupSucceeded": cleanup_error is None,
                  "cleanupErrorType": type(cleanup_error).__name__ if cleanup_error else None,
                  "copies": [{"path": str(c["path"]), "removed": c["removed"]} for c in self.copies],
                  "fixtureRootRetained": str(self.root)}
        with (self.root / "copy-cleanup.json").open("x") as evidence:
            evidence.write(json.dumps(report, indent=2) + "\n")
        if cleanup_error:
            raise cleanup_error from error
        return False
