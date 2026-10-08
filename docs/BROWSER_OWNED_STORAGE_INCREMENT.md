# Browser owned storage continuation

Role: browser target bootstrap and existing FileStream virtual filesystem provider. No new pack IDs or core contracts. Target Bridge exports `ExportStorage` and `RestoreStorage`; JS storage exposes awaited `flush()` and honest `error` state. Existing NativeUI Request dispatch gains `storage-flush` (start) and `storage-poll` (pending/saved/error/idle), so the common consumer can wait for a durable transaction before reporting a save. These are target transport contracts, not editor model APIs.

Only `/confectory-owned` file bytes are serialized, with 512 files and 16MiB decoded byte limits. Imported manifests/bodies and owned editor files persist; runtime assemblies outside this root are excluded. IndexedDB stores one opaque bounded file map per origin and site directory. Restore is awaited before the actual generated public entry executes. File path traversal and invalid records fail startup instead of silently losing user files. Quota/transaction failures remain visible through console and storage.error. Existing record survives failed writes. There is no business namespace, model schema, alias or repository-path branch.

Periodic one-second serialized commits and visibility-change requests support ordinary operation. Callers can await `confectoryPlatform.storage.flush()` for acknowledged durability. Closing a tab abruptly does not guarantee an in-flight transaction completes; this limitation is explicit. Browser origin storage can be cleared by the browser/user; exported archives remain a separate transport.

Outside reads: actual EditorHome Main/README to choose the existing leave action that saves its draft; browser provider JS and target Bridge because pack FileStream contracts alone cannot initialize asynchronous IndexedDB before synchronous entry startup. Outside edits: target bridge owns file transport and startup; platform asset bootstrap owns browser scheduling. Core, product layout/model and shared contracts remain unchanged.

Rebuild scope: browser asset/compiler fingerprint invalidates selected browser target output. Functional tests and locality assessment remain separate. No native OS persistence or Android/Windows runtime coverage follows from browser success.

Validation: native target build with SDK10.0.401 zero warnings/errors; `node --check` both platform app.js and storage.js. Actual product gate `tests/web/editor_home_persistence.py` uses unmodified generated EditorHome output, real webkitdirectory selection, common runtime draft editing/leave, acknowledged commit, reload and recent project reopen. The existing chat draft is runtime-only and is expected empty after app reload; this gate does not relabel it as durable Save-pack content. Result is recorded after execution.

Actual result: PASS on Chromium static GET-only generated same-product WASM. Command:

```
DOTNET_CLI_HOME=/tmp/confectory-dotnet10 CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet /workspace/toolchains/dotnet-10.0.401/dotnet src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll build examples/editor-home/project.cpack browser > /tmp/confectory-browser-persistence-build.json
python3 tests/web/editor_home_persistence.py /tmp/confectory-browser-persistence-build.json
```

The gate uses public NativeUI storage-flush/storage-poll and requires `saved`, then reloads the same origin and reopens the listed actual selected project. Exact saved/restored file map equality passes; runtime-only chat is empty after reload as documented. Latest source platform app.js/storage.js bytes match generated output. Private evidence `/tmp/confectory-browser-persistence-chromium.log`. No generated source/body/assembly patch, server mutation or external publication.
