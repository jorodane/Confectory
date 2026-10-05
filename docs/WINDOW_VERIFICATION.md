# Single-window pack verification

Base commit: b750d0d2b06acb738ffca5b442a8d78d4b58aa42 (main and the previously verified core). This change adds Confectory.Window, Example.Window and a focused C# regression; core/compiler-provider code is unchanged. Tests use .NET SDK 8.0.425/runtime 8.0.31 on Linux x86-64.

## Executed commands

Set CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet and DOTNET_CLI_HOME=/tmp/confectory-dotnet-home. Build with the SDK host:

```sh
dotnet build Confectory.sln -c Release -m:1 -p:UseSharedCompilation=false --nologo
# Existing X.Org server and dummy video driver; local display, no TCP listener.
Xorg :97 -config "$PWD/docs/window-xorg.conf" -logfile /tmp/confectory-xorg.log -nolisten tcp -noreset
DISPLAY=:97 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll WindowTests
DISPLAY=:97 dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/window/project.cpack portable
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/window/project.cpack linux
# Execute the report's run command with the same environment:
DISPLAY=:97 CONFECTORY_WINDOW_CLOSE_AFTER_MS=250 <generated-run-command>
DISPLAY=:97 xwininfo -root -tree
```

In this environment the SDK host is an absolute path rather than globally on PATH; the launcher therefore needs CONFECTORY_DOTNET set. The virtual display required the environment's local-socket access permission, not an Internet service or a production dependency. X.Org reported server 1.21.1.16 and dummy_drv. The regression checks actual XQueryTree/window title and sends WM_PROTOCOLS/WM_DELETE_WINDOW to a running window with no timeout; it must exit 0. Timed close also exits 0. `xwininfo` independently observed one child: `0x200001 "Confectory": () 800x600+0+0`. Invalid timeout exits 2 with a clear diagnostic; invalid DISPLAY exits 1 with the X11 connection diagnostic. A second pack build reused both implementation DLLs. Portable and Linux launcher samples ran successfully.

The Release solution build has zero warnings/errors. The focused regression passed (1/1); see [full test output](window-test-output.txt) for the final suite. GUI checks execute because DISPLAY=:97 is set; headless Linux test runs cover diagnostics without claiming real window creation. Windows Win32 implementation compiles into the generated portable DLL but **Windows runtime execution was not tested**. Native Wayland/macOS, rendering, input contracts, multiple windows and engine self-hosting are not supplied by this first pack. Runtime prerequisites and Windows/Linux run instructions are in [the pack README](../packs/window/README.md).
