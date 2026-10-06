# Editor-free Grid consumer

`Example.GridGame` registers only BaseUI, RuntimeBase and DotNet target roles. It exercises `BaseUI::Grid` as ordinary game/item layout: two-column row-major cells, deterministic unequal pixel remainder, viewport-clipped scroll, empty content, narrow sizes and bounded input. It has no editor, project management, SourceEditor or AI dependency.

Build `examples/grid-game/project.cpack linux` with the ordinary CLI, then execute the build report's `run` command. `EntryHomeTests.test_grid_editor_free_responsiveness_and_provider_locality` also copies the consumer and owning pack and proves a Grid provider-body change compiles only GridBody and zero public contracts.
