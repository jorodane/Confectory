# Codex connection declaration

Connection extends AIConnection::Connection; Settings extends Configuration with an executable field. This is an editable declaration, not a launched or authenticated adapter. All runtime capabilities are currently unsupported and liveVerified=false. command-v found an existing codex executable in this environment; no command was launched and no account/auth file was read.

Official [Codex app-server documentation](https://developers.openai.com/codex/app-server) checked2026-10-09 describes stdio JSON messages, initialize/initialized, thread/start, turn/start, turn/interrupt and turn/completed. Dynamic tools require experimental opt-in; login has separately managed browser/device/API-key modes. An adapter still needs installed-version protocol verification, constrained tool routing, server request/approval handling, cancellation/process lifetime and credential-boundary work. Existing Codex sign-in is not automatically permission for this app to read/use it. No external project content or paid turn was sent.

Ledger: two new inherited declarations only. Outside reads: official protocol and repository schema/Agent public contracts. No editor/core/platform edit; no executable, auth or SDK installation. Declaration consumer test lives in AIConnectionTests; no Codex process/runtime/E2E coverage is claimed.
