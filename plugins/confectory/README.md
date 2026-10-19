# Confectory development plugin source

Build and package with `tools/package_mcp_plugin.py` as described in `docs/MCP_PLUGIN.md`.

Install/test the **extracted built ZIP**, whose `server/Confectory.Mcp.dll` exists. This source folder intentionally does not commit generated binaries. Point a personal marketplace entry at that complete extracted plugin folder; `marketplace.example.json` is only a template and is not registered automatically.

Requires an existing .NET 10 `dotnet` runtime on the local desktop plugin host. The package does not install one, edit user configuration, create credentials, open a TCP port or register itself. Actual ChatGPT app installation/connection remains a separate user-environment check.
