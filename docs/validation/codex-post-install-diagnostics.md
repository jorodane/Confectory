# Codex installation and readiness diagnostics

Baseline: `835a60b3eb9477263674782787819f887e99f8a9`. The reported sequence was Login → installation consent → installation loading ends → the generic existing-Codex-settings error, before official account login.

## Established facts and limits

The original flow already treats a successful `account/read` response with `account: null` as an ordinary logged-out state and requests login consent. Both owned integration cases (an empty discovered account directory and no discovered directory) follow that path after installation. No model-list or account-login request is sent before login consent in those logged-out cases.

The reported phrase is reproducible after successful owned installation when the subsequent CLI exits, initialization fails, account RPC fails, or model listing fails. It does not identify an installation failure or establish that the user has old configuration. The original provider left the initialization failure code active while querying the account, so an `account/read` RPC error was incorrectly classified as `provider-protocol-unsupported`. Onboarding then replaced the provider's diagnosis with the same generic message and retained only the last failing candidate.

The execution environment's CLI reported `codex-cli 0.159.0-alpha.3`. An explicit opt-in probe with a new empty private home, cleared environment and ephemeral credential mode accepted `initialize` and `account/read(refreshToken=false)` and returned `account: null`. Child-only seccomp rules denied socket/connect/send and io_uring operations before execution; no network, login, token read/copy, model-list, thread or inference request was permitted. The probe created no auth.json and removed its own temporary tree. This is Linux runtime evidence, **not Windows runtime evidence or live account authentication**. The [pinned official CLI source](https://github.com/openai/codex/blob/rust-v0.159.0-alpha.3/codex-rs/cli/src/main.rs) also declares `--stdio` and `--strict-config`; that does not establish that the user's Windows process initialized successfully.

**The user's Windows cause remains unconfirmed.** No actual user account, user PC, private configuration, credential store, OAuth login or paid inference was inspected or used.

## Change

- Provider failure records retain a fixed stage, bounded classification, numeric RPC/native/process exit codes when available, a fixed exception class, observed version, and a fixed control identifier when applicable. Raw RPC error messages and stderr are not forwarded. Account/configuration RPC errors are distinct from protocol initialization and unsupported configuration.
- Onboarding retains bounded failure summaries for all candidates and selects the first non-authentication failure instead of allowing the last missing-account result to erase it. When every candidate simply needs login, the normal login consent remains.
- Installation is marked complete only from the real preparation transaction's `prepared` result, after archive/digest and version verification. That result is preserved separately from later readiness failure. A valid completed installation is reused on retry.
- Failure text states the failed stage and a retry direction. One closed **오류 정보** disclosure exposes only the sanitized diagnostic projection. Initial Login, account/model choices, settings migrations, strict provider restrictions, Helper ownership and optional external integration stay in the existing flow.
- Diagnostics contain no filesystem paths, account identities, token values, configuration contents, raw RPC messages or raw stderr. Diagnostic payload keys and strings are controlled by the engine; candidate numbers reveal only ordering.

## Minimal follow-up on the user's computer

Run a build containing this change, then use **Codex → 로그인** or **다시 시도** once. If it fails again, leave the failure visible, expand **오류 정보 · 문의할 때 이 내용만 전달하세요**, and send that text. The report distinguishes `installation.state`, `failure.stage`, `failure.code`, and available RPC/native/exit codes. No auth.json, token, complete config.toml, or private log is needed. Retry does not imply that another account or reinstall will fix an initialization error.

[Structured validation evidence](codex-post-install-diagnostics.json) records executed checks and the limits above.

## Validation

Implementation commit: `d0f4af5855141fcb909f672e9d5dd8c260549751`. Twenty-three distinct UI scenarios passed across targeted groups: the existing sixteen connection/Helper scenarios plus seven new empty-home and post-install failure cases. The six failure cases cover process exit, process-start EACCES, initialization RPC, account RPC, model RPC, and mixed candidates. All groups had no browser page errors or external browser requests. Retrying a valid completed installation did not download it again; original account sentinel files remained unchanged.

The installed-process EACCES case verifies that an unstarted process has no ExitCode; diagnostics retain `processStarted: false` and a numeric native error rather than leaving readiness stuck. This is a Linux kernel result, not a Windows reproduction. The Windows target and native host compiled; actual Windows/WebView2 execution remains untested.

Five distinct .NET test methods passed: owned stdio protocol, global Helper backend ownership/approval/cancel/history, Agent presentation/manual recovery, actual CLI onboarding UI, and ordinary Git checkout/resource startup. All 50 pinned resources match; retained CRLF and fresh LF checkout startup and invalid content/encoding/BOM/binary/budget rejection passed. Original v508 reference ZIP/style hashes are unchanged.

The first integration attempt stopped after three successful cases because a new test variable shadowed its build report. The fixture was corrected and the remaining cases rerun; the aborted attempt is not presented as a complete passing run.

[Rendered account-query failure](codex-post-install-account-diagnostic.png) shows installation outcome separately from the failed readiness stage. Its account/runtime data are synthetic; the diagnostic contains no private payload.
