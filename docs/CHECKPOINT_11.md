# Checkpoint 11: reusable bounded Physics2D foundation

Physics2D owns independent RuntimeBase worlds, exact fixed steps, deferred atomic changes, cancellation epochs, deterministic queries/contact events and snapshots with separate display interpolation. It has no Stage/Ballistic2D/render/timing/editor/AI dependency. The same contracts serve an independent preview and two Stage-owned worlds. The consumer manifest declares a shared candidate registry; unused Stage/ProjectExecution bodies are pruned from the preview's actual selected build closure.

Scope is translation-only dynamic circles and static circles/axis-aligned boxes, isolated analytic solid contact pairs, sensors, masks, configurable units/gravity and conservative bounds. Multiple solid contacts, post-response overlap, excessive motion/speed and invalid/nonfinite values reject the entire step without live publication. This is not a general solver or CCD: stacking, rotation, friction, constraints, polygons, kinematic and 3D remain unsupported. See ../packs/physics-2d/README.md for versioned contracts, policies, event overflow and numeric limits.

Source frozen at a9b50f96e647a613e2815fb7bd4cb83bcd7f3974; Physics pack commit 474b45c7e26316bb0d11ba94f0e23c1df19ef265. No product/test source changes during final full regression. Earlier focused Physics tests: 2/0,110.294s; final full regression below covers the final added post-response rejection test as well.

Actual native X11 GUI: visible fall/contact/bounce in Stage-free preview; two independently owned Stage worlds with distinct gravity/state; Stop/Enter retains world and window; selected close preserves the other; reopen and SIGINT cleanup passed. Exact harness PASS is recorded in /tmp/checkpoint11-physics-gui.log. /tmp/checkpoint11-physics-preview.png and /tmp/checkpoint11-physics-stages.png were inspected. The GUI ran the final pack post-response guard with otherwise unchanged consumer; the subsequent verification-only adversarial test addition does not change UI behavior. No screenshot/binary is committed.

Locality/structure gate: owned CommandBody implementation edit rebuilds only Confectory.Physics2D::CommandBody, zero contracts. Preview selected closure excludes Stage/ProjectExecution/Ballistic2D; analytic verification excludes Stage/Window/Ballistic2D/Agent. Shared CommandBody is a declared policy boundary, not false semantic independence of individual wrappers. No outside product implementation or shared core contract changes; only test registration is an outside source edit. Full outside-read/rebuild ledger in CHECKPOINT_11_WORK_LOG.md.

Managed named profile checks:

windows project: tool.ok=True; selected contracts/providers 37/37; newly compiled 37/37, reused 0/0.
windows stages: tool.ok=True; selected contracts/providers 70/70; newly compiled 34/34, reused 36/36.
android project: tool.ok=True; selected contracts/providers 37/37; newly compiled 37/37, reused 0/0.
android stages: tool.ok=True; selected contracts/providers 70/70; newly compiled 34/34, reused 36/36.

These profiles use Portable net8.0; native Windows execution and Android APK/device/emulator coverage were not run. Existing .NET Android workload is installed, but adb/sdkmanager/javac and a populated selected JDK/Google SDK are absent. No tools installed or license accepted. Android needs an app-owned surface/touch/cancel/lifecycle consumer and logical scene independence, not native desktop multiwindow equivalence.

Exact commands (SDK path environment remains consumer-local):

```sh
export CONFECTORY_DOTNET=/workspace/toolchains/dotnet-8.0.425/dotnet
export DOTNET_CLI_HOME=/tmp/confectory-dotnet
$CONFECTORY_DOTNET build tests/Confectory.Tests -c Release -o .confectory/verification-checkpoint11
$CONFECTORY_DOTNET .confectory/verification-checkpoint11/Confectory.Tests.dll
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/physics-lab/verify.cpack linux
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/physics-lab/project.cpack linux
$CONFECTORY_DOTNET src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/physics-lab/stages.cpack linux
DISPLAY=:97 python3 tests/gui/physics_x11_spotcheck.py /tmp/checkpoint11-preview-build.json /tmp/checkpoint11-stages-build.json
```

The last two build commands were also run with windows and android. Execute the returned run array with the same SDK environment; default is finite headless verification. To inspect motion yourself set CONFECTORY_PHYSICS_MODE=ui. In Stage mode S stops the selected window/world, E returns it, Q closes it; close the other window independently, reopen and interrupt to check cleanup. Actual native Windows and Android UX spot checks remain asynchronous gates and do not block development of later packs.

Next work: choose a dependency/version/license/platform plan before adopting a mature broad physics backend; preserve public world/Owner/change/event/query contracts and add meaningful analytic plus multi-contact/CCD tests for capabilities actually supported. Keep Physics3D distinct, and progress reusable render authoring/mod-loader/Mesh separately. No old Golemancer experiment is treated as engine acceptance. Original Library DOCX remains proxy-blocked; full verified official text was read, but original byte/page verification is not claimed.

Direct user message on 2026-10-06 authorizes pushing the finished verified integration/checkpoint-11 branch. No force push or merge is authorized. Publication evidence is finalized after all checks.
