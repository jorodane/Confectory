# Linux browser test process lifetime

The browser checks in this repository are standalone Python scripts. On a
managed Linux environment whose PID 1 does not reap orphaned children, use
the Linux-only test supervisor for browser and performance checks:

```sh
python tests/run_isolated_browser_test.py -- python tests/web/v821_workspace_restore_performance.py REPO BUILD_REPORT 8
```

It runs the same test with the original arguments, lets Playwright perform its
normal browser/context shutdown, and reaps adopted test descendants (including
detached Chromium/Crashpad and engine workers). After a bounded grace period it
signals only its own adopted children, never existing system processes or
processes selected by executable name. It prints aggregate reaped-process names,
fallback signal counts and the number of remaining children; it preserves the
test exit status and fails if a child remains.

A single real browser lifecycle check is available without starting an editor
or accessing a project:

```sh
python tests/run_isolated_browser_test.py -- python tests/web/v821_chromium_shutdown_probe.py
```

The bounded fallback and original nonzero exit status can be checked without a browser:

```sh
python tests/test_isolated_browser_test.py
```

This is a test execution helper, not a product close operation. It cannot
remove zombies that already belong to PID 1, and it cannot guarantee cleanup
if the supervisor itself is forcibly killed. Native Linux GTK and Windows
WebView2 application lifetimes must be tested separately.
