# Independent shared Field consumer (in progress)

Two independent score/name views compose BaseUI text buffers, Fields, Buttons and Stack with RuntimeBase, UINavigation, RealTimeUpdate and desktop Window/render roles. No Editor, SourceEditor, EditWorkspace or ProjectManager dependency is registered. Name and JSON integer validation belong to this consumer.

With .NET SDK8 available:

```sh
dotnet build Confectory.sln -c Release
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/field-game/project.cpack linux
```

Execute the returned build report's `run` command for the headless behavioral checks. Set `CONFECTORY_FIELD_GAME_GUI=1` to open the two desktop windows; set `CONFECTORY_FIELD_GAME_TRACE=1` for diagnostic snapshots. Tab traverses fields/actions, F4 selects all, Enter advances/submits, F6 switches navigation group, and F7 reopens the other closed view. Windows uses target `windows`.

This source increment is not completed Checkpoint14. Linux pack builds and headless fixture checks passed; native visual/gesture regression, full affected tests and Windows/Android checks remain pending. Android native font/surface providers and runtime prerequisites are required; a portable managed build alone is not APK/runtime coverage. See `docs/CHECKPOINT_14_WORK_LOG.md` for scope and handoff.
