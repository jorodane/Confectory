"""Linux-only actual EditorHome host lifecycle; no Chromium, account or user project.

Run with REPO BUILD_REPORT. The test is a child subreaper so the pre-fix
failure cannot leave an orphan worker with the container's PID 1.
"""
import ctypes
import os
import signal
import sys
import time
from pathlib import Path

assert sys.platform.startswith("linux")
libc = ctypes.CDLL(None, use_errno=True)
if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
    raise OSError(ctypes.get_errno(), "Cannot own test descendants")

import v666_workspace_finder_fixture as f


def processes():
    result = {}
    for path in Path("/proc").iterdir():
        if not path.name.isdigit():
            continue
        try:
            raw = (path / "stat").read_text()
            end = raw.rfind(")")
            fields = raw[end + 2:].split()
            result[int(path.name)] = (raw[raw.index("(") + 1:end], fields[0], int(fields[1]))
        except (OSError, ValueError, IndexError):
            pass
    return result


def descendants(parent):
    table = processes()
    ids = {parent}
    while True:
        more = {pid for pid, row in table.items() if row[2] in ids} - ids
        if not more:
            break
        ids.update(more)
    return {pid: table[pid] for pid in ids if pid != parent and pid in table}


try:
    f.start(0)
    view = f.mount()
    workers = descendants(f.host.pid)
    assert any(name == "dotnet" and state != "Z" for name, state, _ in workers.values()), workers
    assert f.raw({"op": "dispose", "view": view["view"]}).get("ok")
    assert f.host.poll() is None
    assert any(pid in descendants(f.host.pid) for pid in workers), workers
    print("PASS view disposal retains live host and owned read worker", flush=True)
    # HostLoop's normal console cancel path runs owner/session cleanup.
    f.host.send_signal(signal.SIGINT)
    assert f.host.wait(timeout=20) == 0
    now = processes()
    remaining = {pid: now[pid] for pid in workers if pid in now}
    assert not remaining, ("Worker not reaped by exiting host", remaining)
    print("PASS graceful host shutdown reaped all observed child workers", flush=True)
finally:
    f.stop()
    # Reap only descendants adopted by this disposable test, including the
    # expected pre-fix zombie. Never signal an unrelated process.
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            pid, _ = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            break
        if pid == 0:
            time.sleep(.05)
    print("evidence", f.root, flush=True)
