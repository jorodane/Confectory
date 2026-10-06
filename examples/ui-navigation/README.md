# Inventory navigation policy consumer

`project.cpack` runs assertions for Tab toggle priority, duplicate/repeated events, independent groups/Views, Unicode/text gating, modifiers, hidden/disabled focus, restoration and activation cancellation. `gui.cpack` runs the actual two-window desktop example. It composes BaseUI focus/activation through public contracts and owns separate RuntimeBase models/windows.

Build with SDK8 using `dotnet src/Confectory.Cli/bin/Release/net8.0/Confectory.Cli.dll build examples/ui-navigation/gui.cpack linux` (Windows: windows), then use the returned run launcher. Tab opens/closes the selected window's inventory group, F6 traverses inside inventory, Enter activates on release, T toggles text mode, Q exits. This is a routing demonstration, not an inventory data editor or text/IME widget. In text mode unconfigured navigation keys remain available for the consumer's text handler; the sample shows that state but does not implement text editing.

Android-named builds verify managed contracts only; the GUI assumes native desktop windows. Real Android surface/touch/lifecycle integration and APK/runtime acceptance remain open. No installation occurs.
