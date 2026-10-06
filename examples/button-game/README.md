# Editor-free shared Button game

An ordinary `Example.ButtonGame` ProjectPack consumes BaseUI::Button/ButtonInput with BaseUI control lifetimes, Navigation, RuntimeBase, RealTimeUpdate, RenderInput/Window and the compiler target. No Editor, EditWorkspace, SourceEditor, ProjectManager, Agent or Helper is registered/selected. Buttons contain no score model: the game binds Increase/Reset activation IDs to its own RuntimeBase score instances.

After `dotnet build Confectory.sln -c Release` with the existing SDK8, run from the checkout:

```
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll run examples/button-game/project.cpack linux
CONFECTORY_BUTTON_GAME_GUI=1 dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll run examples/button-game/project.cpack linux
```

First command runs contract/lifetime verification and exits. Second opens two actual desktop game windows with independent scores. Click Increase/Reset; Tab/Shift+Tab traverse shared focus; Enter/Space activate on release; F6 opens/closes the game menu and hides Increase. Close one window to retain the other, close both/SIGINT to dispose. Windows PowerShell: set `$env:CONFECTORY_BUTTON_GAME_GUI='1'` and run the same CLI with target `windows`. SDK8 executable may be selected through existing `CONFECTORY_DOTNET`/PATH.

The game forwards BaseUI's returned render/hit frame, sends native input plus Navigation's semantic press/release intents, and binds the resulting ID. It does not compute button style/hover/press hit or activation rules. `tests/gui/button_game_x11.py <build-report.json>` exercises actual shared paint/input/navigation/cancel/hidden/state/lifetime; private captures stay in /tmp. Windows/Android profiles are managed net8 compilation checks; Android native app/surface/lifecycle/toolchain limitations remain explicit and no APK/runtime is claimed.
