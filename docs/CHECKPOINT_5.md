# Checkpoint 5: optional bounded collaboration

The executable ProjectPack composes optional MultiPlay, CollaborationEditing, EditWorkspace, Save, ChangeSet and reusable ElementView providers. Core has no networking. Two TCP clients maintain participant-local drafts and share actual confirmed project source through validated conditional commits. The desktop consumer runs two native windows with independent controls.

Public contracts, outside implementation reads, necessary shared Workspace.RefreshClean addition and separate functional/locality gates are recorded in CHECKPOINT_5_WORK_LOG.md. Consumer-selected Policy and Authorize providers configure transport and Apply authority; body-only changes rebuild only selected providers with zero contracts.

Supported first policy: trusted IPv4 loopback/local star, bounded framed messages/connections/presence, one existing owned unit per Confirm, one work context per participant per room, explicit Apply authorization and first successful real source CAS. Project/context binding is checked before opening drafts. Two active dirty participants conflict; three clash. Offline participants retain identity/saved drafts without competing active intent. Same-participant extra Views share reference-counted drafts. Clean confirmed peers refresh; dirty text and true baseline remain intact. Close cancels and joins owned work, releases connections/subscriptions/models, and preserves source/saves.

Final executable gates: complete suite **97 passed, zero failed (1159.219s)**; final actual Linux X11 two-client/interruption/cleanup check passes; final Windows desktop target compiles; managed Android consumer compiles in the full suite. No-filter complete regressions include controlled concurrent edits and Confirm, binding rejection, authority denial, clean refresh versus dirty retention, reconnect, failed compilation, owner cleanup and offline pack exclusion.

## Reproduce

Use the installed .NET 8 SDK; set CONFECTORY_DOTNET to its executable and DOTNET_CLI_HOME to a writable local directory.

```sh
$CONFECTORY_DOTNET tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/collaboration-ui/project.cpack linux > /tmp/collaboration-ui.json
DISPLAY=:97 python3 tests/gui/collaboration_x11_spotcheck.py /tmp/collaboration-ui.json
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/collaboration-ui/project.cpack windows
```

Build SDK/tests in Release first if binaries are absent. For manual desktop checks, run the report's `run` command with CONFECTORY_COLLAB_PROJECT set to the authoring project path. Alice/Bob: I edits, D saves, F confirms asynchronously, B disconnects, R reconnects. Check early conflict, peer responsiveness during compilation, clean refresh/dirty retention and interrupted validation cleanup. Automated GUI check creates a private source fixture; do not experiment against production source.

## Limits and next-stage handoff

Windows target compile and managed Android consumer checks do not prove native execution. Corrected native Windows user acceptance remains asynchronous. Android SDK/licenses/adb/full JDK are absent or pending; no APK/device/native networking permission coverage, installation or license acceptance claimed. Desktop multiwindow is distinct from Android app/surface capability.

Next policy work should resolve explicit handoff/authority transfer, compound creation transactions, multi-context participant routing and merge/adjudication before implementing them. Internet/P2P/dedicated deployment, accounts/authentication, AI adjudication and automatic merge are deferred. Existing offline applications prune the optional transport even if an unreachable transport body is invalid. Full twenty-section design reading is complete; blocked original DOCX transfer is not a specification-reading gap. No binary/image/raw log/original DOCX is tracked.

Publication remains blocked in this execution: automatic review rejected the final integration-branch push under the trusted local-only delegation. The current deliverable is local source/docs/tests and a local milestone commit. Later direct user approval exists in the parent conversation, but the identical retry was also denied because review treats that carried approval as untrusted. Parent must resolve approval propagation; do not ask the user to repeat authorization or use another publication route.
