# Physics consumers

The same Physics2D contracts serve a Stage-free preview (project.cpack), two independently owned Stage worlds (stages.cpack), and analytic/lifetime verification (verify.cpack). Consumers own fixed timing and presentation; Physics2D has no Stage/render dependency. Gravity differs between Stage A and B; each world persists across Stop/Enter and Fence rejects old callbacks. Closing A leaves B alive.

```sh
export CONFECTORY_DOTNET=/path/to/dotnet
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/physics-lab/project.cpack linux
```

Run the returned run array with the same SDK environment. Default mode is finite headless verification. Set CONFECTORY_PHYSICS_MODE=ui for native Linux windows, CONFECTORY_PHYSICS_TRACE=1 for public snapshot diagnostics. Q closes the selected window; in Stage mode S stops and E returns the selected world. Native close and SIGINT clean up. Preview runs independently of Stage. The display shows persistent surfaces, live circle motion and floor contact, not a full editor.

Windows and Android named profiles currently select Portable net8 managed providers. They are compile checks, not native Windows runtime/APK proof. Native desktop multiwindow is explicit; Android requires an app/surface/touch/lifecycle consumer rather than pretending two OS windows are available. No Android SDK/JDK tools were installed or licenses accepted.
