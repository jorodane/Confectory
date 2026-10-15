# Feature Blueprint source example

This ordinary ProjectPack prints `5`. The entry implementation explicitly selects a graph. The graph calls the existing typed `Add` feature and then an independent `print` node. `Add` keeps its ordinary C# source. The node record owns its complete function body; the final entry C# is a generated build artifact.

From the repository root with the .NET 10 SDK:

```
dotnet build targets/dotnet -c Release
dotnet run --project src/Confectory.Cli -c Release -- run examples/feature-blueprint/project.cproj portable
```

`main.graph.json` owns topology and node definitions. `print.node.json` owns a definition receipt and node implementation. A node definition or referenced contract change makes an old receipt stale. Reading or building does not call an AI provider or convert/delete any legacy source. Builder assembles and compiles the fixed inputs, and records their hashes, compiler identity and node diagnostics mapping in the generated build report. Reordering JSON edges or presentation data does not regenerate node implementations.

This is the first versioned `sync-acyclic-v1` compiler profile: synchronous primitive/array contracts, explicit execution edges, boolean branches and typed returns. Graph cycles, parallel/async scheduling and exception routing require further semantics. Ordinary C# loops and exceptions inside a node remain C#. The profile is a stage boundary, not a node size or permanent language restriction. Native compiler wrappers have not been advertised as supporting this profile.

An existing graph/node project can use shared EditWorkspace drafts, Save and compiler-backed Review/Confirm. `DevelopmentTools.OpenNode` grants one explicit node source, an assigned definition and observed graph/contracts; a changed assignment requires a fresh capability. Its four tools cannot edit the graph, another node, declarations or generated C#, create declarations, Confirm or run processes. The general legacy Worker capability does not automatically receive graph/node files. The new feature screen and automatic AI dispatch have not been connected in this backend example.

Node definition inspection is independent of topology completion. Unconnected nodes may be prepared from their own intent/contracts; the executable graph validates entry-reachable paths. Compiler markers include feature ID, node ID and content version.
