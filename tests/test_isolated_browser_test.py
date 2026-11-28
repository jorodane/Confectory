"""Lightweight supervisor test; no browser or editor process is started."""
import json
import subprocess
import sys
from pathlib import Path

runner = Path(__file__).with_name("run_isolated_browser_test.py")
# An intentionally detached *disposable* child ignores TERM so both bounded
# fallback stages are exercised. Its parent returns a nonzero test status.
orphan = """import signal,time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
print('ready',flush=True)
time.sleep(60)
"""
parent = """import subprocess,sys
child=subprocess.Popen([sys.executable,'-c',sys.argv[1]],stdout=subprocess.PIPE,start_new_session=True)
assert child.stdout.readline()==b'ready\\n'
sys.exit(7)
"""
result = subprocess.run([sys.executable, str(runner), "--", sys.executable,
                         "-c", parent, orphan], capture_output=True, text=True, timeout=20)
report = json.loads(result.stderr.splitlines()[-1])
assert result.returncode == 7 and report["testExit"] == 7, result
assert report["remaining"] == 0 and sum(report["reaped"].values()) == 1, report
assert report["fallbackSignals"] == {"SIGTERM": 1, "SIGKILL": 1}, report
print("PASS bounded cleanup of owned detached child; original exit preserved", report)
