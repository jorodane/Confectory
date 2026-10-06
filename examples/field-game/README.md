# Independent shared Field consumer

Two independent score/name views compose BaseUI text buffers, Fields, Buttons and Stack with RuntimeBase, UINavigation, RealTimeUpdate and desktop Window/render roles. No Editor, SourceEditor, EditWorkspace or ProjectManager dependency is registered. Name and JSON integer validation belong to this consumer.

With .NET SDK8 available:

```sh
dotnet build Confectory.sln -c Release
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/field-game/project.cpack linux
```

Execute the returned build report's `run` command for the headless behavioral checks. Set `CONFECTORY_FIELD_GAME_GUI=1` to open the two desktop windows; set `CONFECTORY_FIELD_GAME_TRACE=1` for diagnostic snapshots. Tab traverses fields/actions, F4 selects all, Enter advances/submits, F6 switches navigation group, and F7 reopens the other closed view. Windows uses target `windows`.

This is the bounded local Checkpoint14 Field consumer. Linux native measured font/caret pixels, click/range/scroll/cancel, resize/reopen/interrupt and headless fixture checks passed, with independent-state/dependency/locality gates. Font scales1 and1.5 were exercised. Windows/Android named managed targets compile; native Windows/Android acceptance remains separate. Android native font/surface providers and runtime prerequisites are required; a portable managed build alone is not APK/runtime coverage. See `docs/CHECKPOINT_14.md` and `docs/CHECKPOINT_14_WORK_LOG.md` for scope and handoff.
