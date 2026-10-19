# Confectory development plugin

Build and package with `tools/package_mcp_plugin.py` as described in `docs/MCP_PLUGIN.md`.

This folder is the portable plugin, not a marketplace root or a ZIP installer. The built development source places it under `plugins/confectory/`, alongside a root `.agents/plugins/marketplace.json` that resolves `./plugins/confectory`. See the source root's README for the separate marketplace-registration and desktop installation steps.

The repository source folder intentionally omits generated `server/` binaries. Registering this Git repository alone does not provide an executable MCP server. The built development source includes the DLL and its runtime configuration. ZIP is only its transport archive; select the exposed plugin in the supported desktop Plugins Directory after its marketplace source is configured.

Requires an existing .NET 10 `dotnet` runtime on the local desktop plugin host. The package does not install one, edit user configuration, create credentials, open a TCP port or register itself. Actual ChatGPT app installation/connection remains a separate user-environment check.

To diagnose launch prerequisites, run `dotnet --list-runtimes` in the desktop host environment. A missing command means `dotnet` is absent from that environment's PATH; no `Microsoft.NETCore.App 10.x.x` line means the required runtime is unavailable. A newer major runtime alone is insufficient for this package's default runtime policy. This check installs nothing.
