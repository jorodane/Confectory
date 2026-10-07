# Project browser / semantic window experiment

This additive ProjectPack opens a real, explicitly selected project through public EditWorkspace APIs. It keeps existing Home design and project creation paths intact. Choose Concepts, Features or Modules, then click an element to open its own declaration editor. Current language mapping is concept/function/module respectively; a Feature is an independent public function contract, not a module child. Namespace remains visible in the stable element ID. No category/namespace rename or refactor is implemented in this experiment.

Compact, Preview and Data currently change information density and show names/kinds; schema-generated columns, inline scalar editing, image previews, inheritance/category trees and collection-specific property editors remain later browser work. These are declaration editors for distinct semantic elements, not a completed full browser or full editor.

The browser stays behind several movable editing windows. Drag a title bar; use X to close, _ to minimize, the bottom browser buttons to restore, and Toggle Order 0/5 to check the higher-order boundary. Clicking a visible native field activates its window inside the same Render Order and keeps that field's focus. Draw clips and native visual/input clips come from the same public UIOrder frame. Native text editing/selection/clipboard/scroll/undo are delegated to the installed provider. Windows still uses the existing child RichEdit provider here; windowless RichEdit is a pending provider/composition step, and Windows runtime/IME/DPI checks are not claimed.

Each element's text model belongs to the browser context and survives closing/reopening its View. Each View owns only its native host and control state, with independent focus and clipping. Keep draft transfers a valid declaration to the existing workspace draft; there is no implicit Save, migration, overwrite, export or external sharing. Closing the browser releases every host/model/control, the workspace and RuntimeBase Owner. This experiment is limited to eight editing windows; the common order pack supports 32 windows.

Windows with an existing .NET 8 SDK:

```bat
run-browser-windows.bat "C:\your\existing-project\project.cpack"
```

Linux with built CLI and element-authoring host, GTK3/GtkSourceView4 and live DISPLAY:

```sh
export CONFECTORY_BROWSER_PROJECT=/absolute/path/to/project.cpack
export CONFECTORY_ELEMENT_AUTHORING_HOST="$PWD/targets/element-authoring/bin/Release/net8.0/Confectory.ElementAuthoring.dll"
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll run examples/project-browser/project.cpack linux
```

Set CONFECTORY_BROWSER_TRACE=1 for private frame/field diagnostics. They include declaration text and should stay out of Git. Actual X11 acceptance creates a private fixture project and never edits existing user projects. GUI acceptance and model/locality gates remain distinct.
