# FileStream

`Confectory.FileStream` is an ordinary reusable IO pack. Providers are selected by the consuming ProjectPack; it has no editor, project execution or schema dependency.

| Public element | Result / responsibility |
| --- | --- |
| Snapshot | `[exists or missing, text, exact-byte SHA256 or missing]`; strict readable text, BOM detection |
| WriteAtomic | Replace one local file through a temporary UTF-8 file and rename |
| LeasePath | Explicit shared source transaction lease path under the supplied project root |
| Commit | Compare selected relative file baselines, write all selected texts or return conflict paths; attempt exact-byte rollback on write failure |
| CopySources | Copy a project into a new candidate directory, excluding generated/VCS/binary output; reject source symlinks |
| Capabilities | Describe local IO scope; Android explicitly requires app-private storage or externally granted access |

Commit rejects absolute paths, root escapes, duplicates, symlink destinations and read-only files. Cooperating consumers hold LeasePath with exclusive FileShare.None. Nonparticipating editors are not locked. Multi-file operations are not crash-proof transactions; failed rollback is reported rather than hidden. Empty/missing baselines are distinct. Save policy, selection policy and draft lifetimes belong to other packs.

The example ProjectPack exercises actual IO and cleanup. The test separately verifies functional behavior and Snapshot-only provider rebuild locality, plus Android target body selection. Android selection is managed build coverage, not APK/device execution.

From the repository root, with .NET 8 configured:

```sh
dotnet build Confectory.sln -c Release
dotnet tests/Confectory.Tests/bin/Release/net8.0/Confectory.Tests.dll FileStreamTests
```

This increment is a foundation for Checkpoint 3, not a completed editing milestone.

CopySources holds the public source lease while taking its candidate copy. LeasePath has an ordinary owning-pack default provider; consumers may still select compatible providers. ProjectExecution Launch passes this public path to its host's build lease, so participating source Confirm/copy/execution build operations coordinate without Core policy. Readable snapshots remain non-locking reads; external nonparticipating writes still require baseline conflict checks.
