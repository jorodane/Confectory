# Durable public projection consumer

An ordinary optional ProjectPack demonstrates completed human edit batches, chief-directed maintenance Tasks, author self-update, existing changed-ID Confirm, source/draft isolation, recovery, bounded reads and revision delta application. The selected callback checks the borrowed Task session's public project/chief Context and uses stable Assign command/task IDs. Tasks remain `ready`; this demonstration starts no Agent and uses no live model. AlgorithmProjection has no WorkerTasks dependency.

Build and execute with the installed .NET 8 SDK:

```
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/projection-maintenance/project.cpack linux
```

Execute the returned `run` command with `CONFECTORY_PROJECTION_PROJECT` pointing to a private copy of `examples/projects/authoring/project.cpack`, `CONFECTORY_PROJECTION_DIR` selecting an existing local storage directory, and `CONFECTORY_ELEMENT_AUTHORING_HOST` pointing to the built ElementAuthoring DLL. Rebase the private fixture's target registry paths. The consumer performs a real local Confirm on that copy. The registered ProjectionDeliveryTests prepare this fixture and check behavior plus separate implementation/description rebuild locality.

Queries are syntactic outlines. Calls, alias effects, termination, concurrency and pre/postconditions remain unverified. Public full Query snapshots support recovery; normal Browse/Delta delivery is bounded and does not imply reduced parsing work. Node identity is conservative and body-revision bound. Named Windows/Android targets compile managed Portable selections; native Windows and APK execution remain separate acceptance gates.
