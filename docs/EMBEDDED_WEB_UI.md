# Windows embedded WebUI boundary — 2026-10-11

This is **partial infrastructure**, not the requested v196 editor port. Root
`Confectory.bat` still opens the existing actual native EditorHome directly.
No external browser or old diagnostic page is substituted as the new default UI.

## Source blocker

The authorized input is Library `libfile_591bd5f16e688191bb52d26fe8054729`, version 0,
`Confectory-Editor-Prototype-HTML-CSS-JS(1).zip` (15,892,643 bytes), expected SHA256
`02d4824e92ed0edbb43113659982b37a99a614117652bde4d8ac92367e334e34`.
The official resolved-reference materialization and transfer helper failed with
`library file transfer failed: download failed`. One fresh preparation and
consumer-local retry produced the same error. `/workspace/confectory-v196-input`
contains no ZIP. No transfer URL was guessed, alternate authentication used, or
403 bypass attempted. The helper did not expose an HTTP status; 403 is not claimed.
No source bytes, hash, source pixel inspection or visual comparison is available.
The parent's file inventory is context, not independently verified source content.

## Implemented independently

- `Confectory.WebViewHost::Serve` is a generic pack adapter over the existing
  `WebUI::Resource`, `Request`, and `Close` interfaces. It has no EditorHome imports
  or hard-coded editor paths. It owns an explicitly configured rendering child and
  retires the WebUI owner after the child exits/cancels. Domain context stays in
  the ordinary running ProjectPack process.
- `targets/webview-windows` owns WinForms/WebView2 and renders declared resources
  inside a native Windows window. Official `Microsoft.Web.WebView2` 1.0.4258.31 is
  pinned; NuGet.org restore is scoped to this project. The solution includes its
  normal managed cross-build. The package adds both WPF and WinForms references;
  this WinForms-only host excludes the unused WPF wrapper before resolving them.
- A private stdin/stdout channel carries resource IDs and existing JSON envelopes.
  Resource bytes come from the compiled consumer bundle. There is no HTTP listener,
  folder mapping, file URL, arbitrary engine dispatcher or JavaScript host object.
  The injected client only transports requests. Scope, revision, CAS, cancellation,
  deduplication and endpoint permissions remain in WebUI and the consumer.
- Declared resource paths are served beneath a per-window synthetic HTTPS origin;
  relative assets such as `assets/image.png` keep their folder structure. Current
  descriptors use a root HTML entry. The existing 4 Mi-character descriptor and
  1 MiB resource limits have NOT been changed: larger ZIP assets need inspection
  and an ordinary resource packaging enhancement before the actual port.
- Origin checks, resource interception, CSP, denied permissions/downloads/popups
  and navigation checks restrict the renderer. External Google Fonts are not
  fetched; an approved local font decision remains with the source port.
- The existing JS client selects the injected transport when present. Explicit
  `CONFECTORY_UI=embedded` connects the **same actual EditorHome ProjectPack** and
  its existing object browsing/shared-draft editing/Save endpoints. This is an
  opt-in integration boundary using the existing small page, not v196 acceptance.
  The normal launcher deliberately does not enable it while the source port is blocked.

[Microsoft's local-content guidance](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/working-with-local-content)
documents resource interception; [WebView2 security guidance](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/security)
informs origin checks, JSON messages and disabled host objects.

## Runtime and development invocation

A Windows .NET 10 **Desktop** runtime and an existing WebView2 runtime are needed.
Missing .NET Desktop is diagnosed by the standard dotnet host; missing WebView2
produces a message and exit 2. No runtime installer, registry, global setting,
credential, account or user-PC operation is invoked. Linux/Android do not have an
embedded renderer in this change. Cross-compilation is not OS runtime evidence.
The host uses a private temporary WebView2 profile; profile reclamation after the
browser process exits remains unfinished (no unsafe deletion while it is active).

For a Windows developer with those prerequisites already present, build the normal
solution and explicitly run the ordinary pack, with an owned existing ProjectPack:

```powershell
$env:CONFECTORY_UI = 'embedded'
$env:CONFECTORY_EDITOR_REPO = (Get-Location).Path
$env:CONFECTORY_WEBVIEW_HOST = Join-Path $env:CONFECTORY_EDITOR_REPO 'targets/webview-windows/bin/Release/net10.0-windows/Confectory.WebView.Windows.dll'
$env:CONFECTORY_WEB_PROJECT = 'C:\path\to\existing\project.cproj'
$env:CONFECTORY_ENTRY_STORAGE = 'C:\path\to\owned\editor-storage'
dotnet src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll run examples/editor-home/project.cpack windows
```

These are developer diagnostics, not new user launch instructions. Child stdin EOF
closes the renderer; Ctrl+C closes the channel and cleanup waits then terminates
only the owned rendering child if needed. Cooperative WebUI calls are retired before
the domain session is released. Native Windows close/IME/resize/cancellation and
missing-runtime dialogs still require actual Windows acceptance.

## Supported versus remaining

| Area | Current evidence/boundary |
| --- | --- |
| Host and bounded message/resource transport | Implemented; managed build and channel regression below |
| Existing object browsing / shared draft edit / Save | Same domain endpoints; browser regression below; Windows rendering unverified |
| v196 HTML/CSS/JS/images and pixel comparison | Blocked on original ZIP bytes; no source screenshots claimed |
| v196 home → project → real object editor | Not ported; existing diagnostic requires host-selected project |
| Helper, Worker status, AI, augment, direction, Review/Confirm | Existing native contracts preserved; v196 consumer bindings not implemented |
| Hide versus complete close, multiple windows, close confirmation | Existing native behavior preserved; embedded product lifecycle integration not implemented |
| Mock replacement / disabled controls / storage-failure TDZ | Requires source inspection; no mock is represented as a real provider |
| Browser/Android embedded support | Not implemented; Windows-first host only |

The original 18-file paused work and backup are not copied into this increment.
Main, Android version settings and Sites are unchanged.

## Verification evidence

- SDK 10.0.401, normal solution Release build (including the new Windows host):
  success, zero warnings/errors; `/tmp/confectory-embedded-solution.log`.
- Production `PackChannel` source linked into the normal test runner: out-of-order
  reply correlation, rejected resources, pending-call retirement on EOF, and
  rejection after close: **1 passed, 0 failed** (0.265s).
- Same ordinary EditorHome and ButtonGame packs in Chromium plus WebUI
  scope/revision/cancellation/disposal and locality: passed. Windows/Android
  managed EditorHome profiles: passed. Combined batch **3 passed, 0 failed,
  1 skipped** (607.150s); `/tmp/confectory-embedded-gates.log`. The skip was the
  initial native test without DISPLAY; the explicit Xorg run is recorded below.
- Final actual `examples/editor-home/project.cpack windows` normal CLI build after
  the cancellation change: `tool.ok=true`, `Confectory.WebViewHost` linked;
  `/tmp/confectory-embedded-final-windows.json`. No alternate test page or
  per-editor compiler/timeout exception was used.
- Windows launcher layout checks: **4 passed**. Original paused HEAD and all
  18 file hashes still match the preserved manifest. Main ref unchanged.
- Windows OS execution, source ZIP verification, original visual inspection and
  v196 screenshot comparison: **not performed / blocked**, not covered by any of
  the above managed or browser checks.

The first Linux GUI batch passed the GUI assertions but failed its later rebuild
locality assertion because this work changed WebViewHost while the test was running
(expected only EditorHome rebuilt; observed EditorHome and WebViewHost). This was
not hidden or relaxed. The final source was frozen for a fresh full rerun.

Final actual Linux GUI and rebuild locality rerun with the installed Xorg dummy
server: **1 passed, 0 failed, 0 skipped** (211.953s),
`/tmp/confectory-embedded-linux-final.log`. The native test uses the ordinary
EditorHome ProjectPack and exercises menus/tabs/run/logs/resize/context/lifetime.
It verifies preservation of the existing native UI, not embedded Linux support.
