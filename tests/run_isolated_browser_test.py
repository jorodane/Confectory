"""Linux test supervisor: preserve test arguments/status and reap its descendants.

Usage: python tests/run_isolated_browser_test.py -- python tests/web/TEST.py ...
This does not change product shutdown behavior or touch pre-existing processes.
"""
import ctypes
import json
import os
import signal
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path


def supervise(command):
    if not sys.platform.startswith("linux"):
        raise SystemExit("This supervisor requires Linux child subreaper support.")
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), "Cannot own test descendants")

    child = subprocess.Popen(command, start_new_session=True)
    interrupted = None
    previous = {}
    reaped = Counter()
    signalled = Counter()

    def interrupt(number, _frame):
        nonlocal interrupted
        if interrupted is None:
            interrupted = time.monotonic()
            try:
                child.send_signal(number)
            except ProcessLookupError:
                pass

    for number in (signal.SIGINT, signal.SIGTERM):
        previous[number] = signal.signal(number, interrupt)

    def children():
        path = Path(f"/proc/self/task/{os.getpid()}/children")
        try:
            return {int(value) for value in path.read_text().split()}
        except OSError:
            # Some Linux procfs mounts do not expose task/children. Fall
            # back to exact PPID checks, not executable names.
            result = set()
            for entry in Path("/proc").iterdir():
                if not entry.name.isdigit():
                    continue
                try:
                    stat = (entry / "stat").read_text()
                    fields = stat[stat.rfind(")") + 2:].split()
                    if int(fields[1]) == os.getpid():
                        result.add(int(entry.name))
                except (OSError, ValueError, IndexError):
                    pass
            return result

    def reap():
        # Observe the comm before consuming the wait status. Only this process
        # can wait for its direct children; an unreaped PID cannot be reused.
        while True:
            try:
                status = os.waitid(os.P_ALL, 0, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            except ChildProcessError:
                return False
            if status is None:
                return True
            try:
                name = Path(f"/proc/{status.si_pid}/comm").read_text().strip()
            except OSError:
                name = "unknown"
            os.waitpid(status.si_pid, 0)
            reaped[name] += 1

    try:
        # The test keeps its own normal timeout/error behavior. Only a received
        # cancellation adds a bounded termination sequence for our test child.
        while True:
            try:
                code = child.wait(timeout=.2)
                break
            except subprocess.TimeoutExpired:
                if interrupted is None:
                    continue
                elapsed = time.monotonic() - interrupted
                if elapsed >= 15:
                    child.kill()
                elif elapsed >= 10:
                    child.terminate()

        # Playwright has already had its ordinary browser/context shutdown.
        # Adopted children may need a little more time to flush and exit.
        started = time.monotonic()
        sent_term, sent_kill = set(), set()
        while True:
            if not reap():
                break
            elapsed = time.monotonic() - started
            if elapsed >= 12:
                break
            if elapsed >= 5:
                pending = children()
                number, sent = (signal.SIGKILL, sent_kill) if elapsed >= 9 else (signal.SIGTERM, sent_term)
                for pid in pending - sent:
                    # These are exclusively direct children of this subreaper,
                    # not names, process groups, or a scan of the system.
                    try:
                        os.kill(pid, number)
                        signalled[signal.Signals(number).name] += 1
                    except ProcessLookupError:
                        pass
                    sent.add(pid)
            time.sleep(.05)
        remaining = 0
        if reap():
            remaining = len(children()) or "unobserved"
        print(json.dumps({"testExit": code, "reaped": dict(reaped),
                          "fallbackSignals": dict(signalled), "remaining": remaining}),
              file=sys.stderr, flush=True)
        if remaining:
            return 1
        return code if code >= 0 else 128 - code
    finally:
        for number, handler in previous.items():
            signal.signal(number, handler)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--"]:
        args = args[1:]
    if not args:
        raise SystemExit(__doc__)
    raise SystemExit(supervise(args))
