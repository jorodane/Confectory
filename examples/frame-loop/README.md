# Ordinary cooperative frame loop

A headless local .NET ProjectPack runs a declared RealTimeUpdate cadence and a real Tick implementation over its own model. Run it through the existing CLI or open `project.cpack` in EditorHome and press Run. The Run viewport can Pause, Step, resume and reconnect when launched by the desktop execution owner. Its output is actual model frame/tick telemetry, not a render surface.

The ordinary `Main` entry is independent of EditorHome, ProjectManager and AI. Without a ProjectExecution frame owner it runs normally until explicitly stopped. `protocol-verify.cpack` is a separate bounded protocol/owner test entry; it is not the ordinary game loop.
