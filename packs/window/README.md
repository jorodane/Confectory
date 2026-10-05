# Confectory.Window

First runtime pack: open one native window, process its events, and return when it closes. The build core is unchanged. The reusable pack declares `Confectory.Window::Open`; the sample ProjectPack in `examples/window` supplies its provider binding to `Confectory.Window::Native`.

The contract is `(string title, int width, int height, int closeAfterMilliseconds) -> int`. Dimensions must be positive. A zero timeout waits for the user to close the window; a positive timeout permits automated smoke tests. Return 0 means normal close, 1 a platform/display creation failure, and 2 invalid dimensions/timeout. Windows uses Win32/user32 and its owning-pack registered class; Linux uses libX11 and handles WM_DELETE_WINDOW. Linux requires `libX11.so.6` and a working X11 or XWayland DISPLAY. Native Wayland and macOS are not supported. No extra NuGet package or native binary is bundled.

## Build and run

Install the .NET 8 SDK to build, or only the .NET 8 runtime to execute an existing package. From the repository root:

```powershell
# Windows PowerShell
.\build-windows.bat
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
$r = dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/window/project.cpack portable | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Pack build failed' }
& $r.run[0] $r.run[1]
```

```sh
# Linux; run the launcher path returned in the JSON report's run array.
dotnet build Confectory.sln -c Release
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/window/project.cpack linux
<output-directory>/run
```

The sample opens an 800x600 window titled Confectory. Closing it exits the process. Set `CONFECTORY_WINDOW_CLOSE_AFTER_MS=1000` for an automated one-second run; leaving it unset waits for close. Runtime/launcher packaging remains framework-dependent and belongs to the .NET target provider. The window implementation belongs to this pack, not that compiler provider.

## Verification

Linux x86-64, .NET SDK 8.0.425/runtime 8.0.31. An X.Org 1.21.1.16 server with the dummy display driver provided DISPLAY=:97. `xwininfo -root -tree` observed a real mapped `Confectory` window at 800x600. The C# regression builds a fresh copied ProjectPack, checks cache reuse, tests invalid timeout and missing display diagnostics, creates/closes a window by timeout, then locates another window via XQueryTree and sends the actual WM_PROTOCOLS/WM_DELETE_WINDOW client message. The latter has no timeout and must exit successfully after the close event. These GUI assertions run when DISPLAY is set on Linux; headless runs verify only the failure paths. Windows native code compiles in the generated DLL but has not been executed in this environment.

```sh
DISPLAY=:97 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll WindowTests
```

The scope is one synchronous window/event loop. Rendering, input contracts, multiple windows, persistent runtime owners and an editor are separate work. This pack alone does not establish engine self-hosting.

## Persistent surface capabilities

The original Open contract remains available. New IDs `CreateSurfaces`, `Reopen`, `Close`, `Capabilities`, `SurfaceLifecycle`, `SurfaceInfo`, and `SurfaceDimensions` add persistent session ownership without changing the build core. `Confectory.Window::{PumpBody,DrawBody}` implement the independent RenderInput contracts. Common bodies use Win32/X11; Android-specific bodies override Pump/Draw/Capabilities with the same contracts.

Desktop CreateSurfaces accepts 1–16 window titles and a positive initial size. SurfaceInfo returns `[active,opaqueResourceIdentity]` pairs, and SurfaceDimensions queries current desktop client size. Windows creation adjusts outer frame size to the requested client area. The returned array is an opaque session token; do not inspect, alter or share it between unrelated sessions. Pump/Draw/Reopen/Close operate on that token. Close(view) removes only that window, retaining session resources; Close(-1) releases all windows and the shared X11 display. Reopen replaces only an absent handle. Creation failure releases already-created native resources. Win32 pointer capture and X11's automatic button grab preserve outside-release handling. The X11 adapter currently requires the 64-bit event ABI and coalesces autorepeat release/press pairs.

Capabilities is `[nativeIndependentWindows,appOwnedSurface,touch]`: desktop `[1,0,0]`, Android `[0,1,1]`. Android SurfaceLifecycle receives an opaque five-slot state initially zero and actions `created`, `changed`, `surfaceDestroyed`, `resume`, `pause`, `destroy`. It separates surface availability from app resume and model lifetime. Surface loss pauses presentation and disconnects View subscriptions; model Owners survive until Activity destruction. Destroy cannot be revived. Surface recreation increments generation. The Android native bridge is an adapter resource and holds no model state.

The initial native renderer uses X11 rectangles/text or Win32 GDI; it is not a GPU render pack, high-DPI/accessibility-complete UI or native Wayland provider. Windows code is compiled through the Windows-named framework-dependent profile but has not run on Windows in this environment. Android's managed contracts and target-specific bodies compile; the exported Activity/SurfaceView project needs the missing Android toolchain and is not yet claimed to compile or run.

Windows native user acceptance failed in the original STATIC-class implementation. The scoped correction adds owning-pack Win32Create/Win32Pump/Win32Draw/Win32Close capabilities: rooted registered callback, HWND-specific sent/queued input, creator-thread enforcement, default non-client OS dispatch, retained GDI bitmap paint and destruction cleanup. Existing common window/render/input APIs remain compatible. Linux ABI/shim tests and Windows compilation pass, but corrected native Windows acceptance remains pending user recheck; see [evidence/limits](../../docs/WINDOWS_NATIVE_FIX.md).
