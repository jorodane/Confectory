# Android export

Current exporter resolves the actual ProjectPack entry into `Generated/PackEntry.cs` and uses one target-owned generic Activity. It does not select a host by product namespace or generate a business-model alias facade. See [generic host and final API36 evidence](../../docs/ANDROID_GENERIC_HOST.md) and [Windows export/sign instructions](../../docs/ANDROID_WINDOWS_EXPORT.md).

```sh
dotnet build Confectory.sln -c Release
dotnet targets/android-export/bin/Release/net10.0/Confectory.AndroidExport.dll examples/editor-home/project.cpack /absolute/new/export-directory
python3 tests/android/compile_api.py /absolute/new/export-directory /workspace/toolchains/dotnet-10.0.401
```

Append `--package` for unsigned packaging using the installed Android SDK/JDK. Output must be a new directory. The direct C# API probe verifies generated source against installed API36 references; it does not package or run the app. APK/AAB compilation, unsigned alignment/manifest inspection, signing and device execution remain distinct gates. Android provides one Activity surface; desktop multiwindow behavior is not implied.

Historical sample-specific Activity templates were removed after generic-host acceptance. The managed AndroidPreparation test remains an auxiliary lifecycle/body-selection/locality probe; actual product acceptance uses the unchanged EditorHome entry.
