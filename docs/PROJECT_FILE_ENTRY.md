# Pack capability and desktop project file entry

New projects created by ProjectManager use `project.cproj`. The contents remain a ProjectPack (`project Namespace version "…" { … }`); this is a filename convention, not a new project model. Existing `.cpack` ProjectPacks and user paths continue to work. Plain packs remain `.cpack`; `.cproject` is not the selected extension. No existing user projects are renamed.

Each repository-owned pack/project now declares `standalone true;` or `standalone false;`. Declaration does not guarantee execution on every target/host. Legacy omission remains readable: an existing ProjectPack with an entry defaults true, a plain pack defaults false. `standalone false` never prohibits opening/editing. A true plain pack still needs ProjectPack composition to supply entry/target/registry. Explicit Run in CLI, ProjectExecutionHost and authoring preview rejects unsupported independent execution before building.

The target-owned inspector reports declaration, effective capability, entry, declared targets, current host and conservative host eligibility separately:
```sh
dotnet targets/desktop-entry/bin/Release/net8.0/Confectory.DesktopEntry.dll inspect /absolute/project.cproj linux
```
A metadata-eligible result is `requires-explicit-build-and-runtime-verification`, not a claim of tool/native/runtime readiness. Unknown/custom targets need their own host validation. Explicit build and execution remain the final checks.

## Open a file

Build the installed checkout with `dotnet build Confectory.sln -c Release`, then:
```sh
dotnet targets/desktop-entry/bin/Release/net8.0/Confectory.DesktopEntry.dll open "/absolute/한글 공백/project.cproj" --repository /absolute/trusted/Confectory
```
Windows shortcut/command route is `open-project-windows.bat "C:\folder\project.cproj"`. The trusted installed Entry/Home ProjectPack is the cold-start composition. The incoming file is read as bounded metadata only; its registry/build tools/scripts/bodies are not loaded or executed. File open does not request Play/Run.

An existing engine using ProjectEntry under the same installation scope consumes the request. Entry/Home acknowledges same-file requests without replacing its native text buffer/focus. Another active project, pending job/picker or creation form causes refusal; explicitly Leave first. Existing Leave stores its local draft and stops only its owned execution. The two-window engine similarly protects view0/current authoring work and treats a closed, clean context as available. View1 remains independent. Opening a plain library exposes its metadata/owned source to existing SchemaEditing/EditWorkspace contracts; Run is unavailable. Library validation is owned syntax/identity validation, not complete provider linking or C# compilation.

Cold starts serialize under a launch lease. A supervisor drains trusted engine output into the private inbox `engine.log`, permitting the file-open client to exit while the engine remains running. A PID/start-time marker prevents duplicate startup after a timeout; engine startup failure is surfaced with the log path. Connection timeout, unreachable existing owner, lost acknowledgment and project refusal have distinct failures. A request caller must not interpret uncertain delivery as permission to replace current work. Startup waits at most240seconds; one IPC connection waits30seconds, client acknowledgment15seconds. No process replacement or tool installation is attempted.

## Windows association installation

On Windows, after the build, run `register-project-files-windows.bat`. It **only generates** `.confectory/Confectory.cproj.reg` in the installed checkout. Review the file, then import it yourself if desired and select Confectory in Windows Open With/Default Apps. The file uses per-user `HKCU\Software\Classes`, `.cproj`, `OpenWithProgids` and a ProgID with fully quoted absolute dotnet/tool/installation paths plus `"%1"`. It does not force Windows UserChoice or register legacy `.cpack`. Keep that installation at its registered location; regenerate after moving it. Removing association/settings is an explicit user operation. This task did not import a registry file or alter this PC's associations.

Actual Windows double-click, registry import, elevation interoperability, native focus/DPI/IME and runtime checks require Windows and remain unrun here. Registration string/quoting tests and managed Windows target builds are separate evidence.

Linux supports the same CLI and actual same-user pipe/GUI forwarding. An XDG `.desktop`/MIME install is not implemented or applied in this slice; use the command above. Android needs app-owned Activity intent delivery, persisted/granted content URI access, surface/lifecycle/touch/native text providers and an Android toolchain. No desktop named-pipe/window/registry equivalence is claimed. adb, sdkmanager and javac are absent locally; no SDK install, APK build or Android runtime test was performed.

## Verification and handoff

See the increment ledger in `UI_ORDER_NATIVE_INTEGRATION.md` for commands, actual results and independent structural gates. Continue with actual Windows association/native acceptance and Android intent/storage/surface adapters while preserving optional platform checks as asynchronous feedback. Main merge, forced push and deployment remain outside this branch publication authorization. No binaries, images, registry outputs, secrets or raw runtime/chat logs belong in Git.

Registration follows [Microsoft file type/ProgID and per-user registration guidance](https://learn.microsoft.com/en-us/windows/win32/shell/fa-file-types). The generator creates registration data only; actual Windows Shell refresh/Default Apps behavior is an outstanding Windows acceptance check.
