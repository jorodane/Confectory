# Checkpoint 17 — bounded rounded project navigation

Production entry remains `run-home-windows.bat` or `bash examples/editor-home/run-home.sh`. This continuation preserves CP15 home and CP16 project/chat/execution ownership; legacy `examples/editor` remains separate. In an open project, bottom actions now contain a circular `?` grievance entry, one state-dependent Run/Stop bubble and rounded Navigate launcher. Navigate opens an upward rounded bar; Project opens a left-preferred edge-aware submenu. Existing workspace/chat/logs/information/settings routes only. Escape, outside pointer press, resize/focus/capture cancellation close navigation; invisible/disabled underlying controls cannot activate. Existing control/buffer tokens are retained through tab/menu/leave/reopen.

The grievance entry deliberately reports unavailable data: no issue source/status/urgency ordering/recipient/report creation or sending contract is supplied by original sections8/12. Count and highest urgency are null, not false zero. The panel explains that reporting is unavailable. EY/LaY references do not invent a local report database or authorize sending.

Reusable BaseUI geometry/render/hit/anchor/clip additions are verified by `examples/rounded-game` with no editor/table/project model dependency. Existing shared Button/control routing remains authoritative. See [increment ledger](CHECKPOINT_17_WORK_LOG.md) for contracts, reads/edits and rebuild scope. Rounded panels use existing native rectangle rendering rather than a platform-specific scenegraph.

Validation records: Release build0 warnings/errors; scoped ProjectNavigationTests2/0,216.807s (independent consumer/functionality, six provider-only locality probes, Windows/Android managed profiles, actual X11 and Main provider locality). Direct actual X11 acceptance also passed and screenshots were visually inspected locally: rounded upward bar/submenu and unavailable-report circle/panel, no covered-text leakage. Final post-crash-repair run and EntryHome/ProjectShell regression results are recorded below when complete. No full-suite aggregate, native Windows, APK, Android input or Korean IME pass is claimed.

Commands with existing SDK8:
```
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet
export DOTNET_CLI_HOME=/tmp/confectory-dotnet
export PATH=/workspace/toolchains/dotnet-8.0.425:$PATH
dotnet build Confectory.sln -c Release --no-restore
DISPLAY=:97 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll ProjectNavigationTests
DISPLAY=:98 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll ProjectShellTests EntryHomeTests
```

Native Windows spot check: open a project; `?` must show unavailable-report status, not claim submitted issues; Navigate then Project/Information or Settings must use the same context; Escape/outside press/resize cancels; chat draft remains through menu and leave/reopen; Run/Stop acts only on selected ProjectPack. Repeated minimize/restore is an added urgent regression documented in [the crash repair](FIX_CP16_MINIMIZED_FIELD.md). Native Windows runtime remains asynchronous/unrun locally.

Native input migration is immediate next priority, explicitly all native input controls, not additional custom editing shortcuts. See [architecture and actual provider gaps](NATIVE_INPUT_MIGRATION.md). Required Windows Korean IME composition/candidate anchoring is a native runtime gate and cannot be inferred from committed Unicode strings. Existing Field stays unchanged functionally except budget diagnostics while this separate slice finishes. Android app-native hosting/picker/text controls remain open; Java21/GTK3 are installed, adb/sdkmanager and Windows runtime are absent; no installs or licenses changed.

CP15 four-image private Library upload was retried once under renewed authorization but failed at Library connection before upload. There are no confirmed Library IDs. No alternate route or extra retry was attempted; files remain ignored locally. Screenshots/binaries/secret/raw chat/original documents are excluded from Git.

Final affected EntryHome + ProjectShell regression:8 passed,0 failed,1015.590s. Exact final one-bubble production Main also passed actual X11 navigation acceptance (`/tmp/cp17-native-bubble-final.log`), with popup screenshots inspected privately. Final Release solution build0 warnings/errors,3.01s. Urgent CP16 backport is local commit `c88db28` on `fix/checkpoint16-small-field-layout`,1/0 scoped test,283.814s; the same fix is retained in this integration. New runtime-native text/picker providers are not implemented in CP17; their inspected gaps and target/provider separation are documented, not reported complete.
