# Reusable Rig/Motion consumers

`verify.cpack` runs analytic 3D hierarchy/quaternion, duration/Bezier, projection, inheritance and invalid-domain checks. `preview.cpack` is a standalone motion preview; `workbench.cpack` adds existing EditWorkspace/Save/ChangeSet authoring. Neither requires Stage, Physics or Helper. `asset-project/project.cpack` owns the Rig and Render documents; Views borrow those documents and own only presentation/lifetime state.

Build using the repository-selected SDK 8, from the repository root:

```sh
dotnet build Confectory.sln -c Release
dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/rig-lab/preview.cpack linux
```

Use the `run` launcher returned by the build JSON. Without `CONFECTORY_RIG_MODE=ui`, consumers run their assertion-based flows. With that variable, Preview opens one window and Workbench opens independent front/side Views. Set `CONFECTORY_ELEMENT_AUTHORING_HOST` to the built `targets/element-authoring/bin/Release/net8.0/Confectory.ElementAuthoring.dll` and `CONFECTORY_RIG_AUTHOR_PROJECT` to an explicitly selected **owned copy** of asset-project/project.cpack. Preserve or resolve its relative pack registry paths when copying. Workbench refuses to infer an authoring destination.

Space toggles playback in the selected View; arrows scrub its time; Q closes that View. Workbench: H changes a hierarchy parent, P changes an opened KeyPose depth, D changes duration, L toggles the tool layer, O swaps layer order, S saves the draft, R reloads it, C validates and Confirms both documents through the real source/build path. Save does not change final source. Reload keeps the native windows. Confirm runs in a scoped background authoring job while cached coherent snapshots keep rendering; draft mutations pause during that job. SIGINT cancels outstanding scoped work and cleans up Owners/subscriptions/windows.

Pure reusable Scene contracts explicitly create, frame, poll and close a View. Presentation mutations require the creating UI thread. SceneFrame evaluates one coherent 3D pose and projects it once; each View has its own Owner, frame counter, plane and playback state. A shared workspace participant deliberately shares authored drafts; a different participant has an independent draft. No table-owned model semantics.

RealTimeUpdate uses bounded fixed-step catch-up (8 × .01 seconds), an independent 60 Hz presentation cadence, and previous/current interpolation with the returned alpha. Pausing/scrubbing resets the interpolation pair. The underlying pack reports dropped overflow; playback does not silently simulate an unbounded backlog. This geometric fixture has no skinning, perspective, mesh generation or external assets.

Windows/Android manifests select existing target contracts for managed compilation. This desktop consumer explicitly requires native multiwindow capability. Android needs a separate app-owned surface/touch/lifecycle presentation consumer; a portable build is not an APK or runtime acceptance. Missing SDK/Java prerequisites are documented in the checkpoint.
