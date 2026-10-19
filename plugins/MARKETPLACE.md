# Confectory local development marketplace source

This is a local development source for a supported ChatGPT desktop plugin surface. Its ZIP is a transport archive, not a user-facing ZIP installer or a public-directory submission package.

The built source has this complete structure:

```text
confectory-development/
  .agents/plugins/marketplace.json
  plugins/confectory/
    plugin.json
    mcp.json
    skills/setup/SKILL.md
    server/Confectory.Mcp.dll
    server/Confectory.Mcp.deps.json
    server/Confectory.Mcp.runtimeconfig.json
    README.md
  package-receipt.json
  README.md
```

The catalog's `./plugins/confectory` resolves from `confectory-development/`, not from `.agents/plugins/`. Keep this tree together when moving or extracting it. `package-receipt.json` hashes every bundled file except itself.

## Prerequisites and source registration

The desktop plugin host must already have .NET 10 on PATH. Run `dotnet --list-runtimes` in that host environment and look for `Microsoft.NETCore.App 10.x.x`. If the command is unavailable, check the existing runtime and PATH; if the line is absent, the required runtime is missing. Do not interpret either failure as a Confectory project-connection or account-authentication error. This source does not install a runtime or change PATH.

Extract the archive into a location you choose. The resulting `confectory-development` folder is the local marketplace root. The official developer registration command, if the supported local CLI is already available, is:

```text
codex plugin marketplace add "/absolute/path/to/confectory-development"
```

This is an explicit source-registration action that writes client configuration; it is shown for review and is not run by this package or by packaging tests. It does not install Confectory, authenticate an account, or publish to a workspace/public directory. No manual `config.toml` edit is required by this route. If the command or desktop surface is unavailable, stop at that prerequisite rather than inventing an app import button or installing software automatically.

The documented alternatives are an existing repository's `.agents/plugins/marketplace.json` or a personal `~/.agents/plugins/marketplace.json`. Add the catalog entry only after choosing that root and a plugin location inside it. Preserve existing entries; never replace the entire file. If the plugin is placed elsewhere, adjust `source.path` relative to that marketplace root. Copy the complete built plugin, including `server/`; a Git checkout of the current source repository omits that directory.

## Desktop installation and connection

After the source is registered, the official desktop workflow is to restart the app, select the marketplace source in Plugins, open Confectory's details and use the install plus button, then start a new chat. These are documented steps, not an assertion that they were executed in your app. A general ZIP import or personal Git-URL entry UI has not been verified. Workspace-admin marketplace import is a different administrative route and is not a personal-account instruction.

Once installed, the onboarding skill guides the existing connection flow: open a project in Confectory, choose **메뉴 → ChatGPT 플러그인 연결**, prepare the exact project or node scope with read-only checked, then list/select it through `confectory_instances`, `confectory_connect` and `confectory_status`. Changes remain in the existing draft until a human uses Confectory Review/Confirm.

The managed manifest command and marketplace paths are validated locally. Actual source registration, desktop installation/cache behavior, onboarding in a real ChatGPT app, user-host .NET/PATH and the real app connection remain unverified. This bundle performs none of those operations.

## Official references

- [Package a plugin: local marketplace roots, relative source paths and manual registration](https://developers.openai.com/plugins/build/plugins)
- [Developer commands: `codex plugin marketplace`](https://learn.chatgpt.com/docs/developer-commands)
- [Desktop Plugins Directory and installation](https://learn.chatgpt.com/docs/plugins)
- [Public desktop-only submission](https://developers.openai.com/plugins/deploy/desktop-only): partner approval and portal ZIP upload concern public submission; they are separate from this local development source. This archive's marketplace wrapper is not a portal submission package.
