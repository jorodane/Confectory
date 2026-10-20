# Codex CLI onboarding

This change starts from `eca156f6f79ce9466a8c90a22d36bf67475278e1` and retains v508, existing generated-settings repair, and user data.

## Behavior

The normal Codex form has one initial **로그인** action. It discovers supported native runtimes, requests official installation consent only when needed, uses the supported official device login only when needed, shows official account identity before choosing an existing account, and asks for a model only when saved/configured/default/single-model selection cannot resolve one. Successful readiness saves the existing provider settings and registers a real Agent. Helpers still require an Agent.

The coordinator owns asynchronous runtime probing, installer, login and verification state. Reopening a ready form and reconnecting an offline Agent reuse current proof. A fresh engine renews readiness using the persisted confirmed identity without repeating login. Identity changes require a new explicit choice. Cancellation, consent tokens, repeated clicks, failures and retry retain completed installation/login and original settings. Manual recovery stays behind a closed advanced disclosure.

The optional **설정 → 외부 ChatGPT 연결** integration is separate. CLI onboarding does not launch its Site/WebView relay, require a ChatGPT plugin, grant project access, deploy a Site, or revoke/delete external integration state. Windows opens only the current official device-login URL through a validated native action.

## Validation boundaries

`tests/web/editor_codex_onboarding.py` renders the actual engine UI in Chromium. It copies the editor and Codex pack to an owned temporary tree; only passive discovery and the preparation asset descriptor are substituted. The real coordinator, archive download/hash/extraction, private storage, device-login lifecycle, provider protocol checks, account/model choices, settings save, Agent registry and Helper transport execute. Runtime/account replies and installation archives are isolated fixtures; all displayed fixture emails use `.invalid`.

These tests do **not** prove real OAuth success, service entitlement, a real model response, or paid inference. Account metadata is explicitly distinct from live service authentication. No real user credentials, account login, user-computer installation, paid provider request, plugin uninstall, scope grant or external deployment was performed.

Implementation commit: `23b6770ca2ab9a4e084c3bb64e1d8b67dd9f0141`. Windows target and native host compilation do not establish Windows/WebView2 runtime behavior; that requires a Windows machine.

## Executed checks

[Structured evidence](codex-cli-onboarding.json) records 16 passing onboarding scenarios and 13 distinct passing test methods, run in targeted groups. The nine main connection/model/Helper scenarios passed in the final complete attempt; after correcting an installation-cancellation fixture race, the seven interruption/failure/change scenarios passed in a separate final group. This is not reported as one uninterrupted 16-case run.

| Check | Result |
| --- | --- |
| Actual CLI onboarding UI | Supported/absent/unsupported runtime; authenticated/logged-out; official default/configured/single/choice/empty models; identified account choices and identity changes; install/login/probe cancel, failure and retry; provider switch; duplicate/stale tokens; retained original account sentinel |
| Agent and global Helper | Agent required before Helper creation; ready/offline/reconnect; reopen without repeated completed steps; engine restart renews saved identity; one explicitly approved owned Helper protocol reply |
| Existing regressions | Core namespace diagnostics, 20 first-settings backend scenarios, six Responses-first UI profiles, metadata/current-byte and approval guards, owned Codex protocol/control/workspace receipts, global Helper ownership/history/restart, v508 Helper UI and manual recovery/preparation |
| UI network/errors | No page errors or external browser requests in the final onboarding groups; no external bridge/Site launch endpoint invocation |
| Product builds | Linux and Windows targets passed from implementation commit; Windows host Release compile passed with zero warnings/errors |
| Git checkout/startup | Actual ordinary retained-CRLF-after-pull and fresh-LF checkout; all 50 served resource identities; content/encoding/BOM/binary/budget rejection; original bytes retained |
| Protected bytes | Original v508 stylesheet and ZIP hashes unchanged; no Android or main edits |

Earlier failed attempts are retained in the execution workspace and described in the structured evidence. The advanced recovery UI had a real busy/disclosure timing defect that was fixed and retested. Two integration fixture issues were corrected: synchronous waiting had blocked Playwright routing, and the install-cancel test had released its held download before cancellation admission, then incorrectly demanded that a completed installation be repeated. The final cancellation fixture waits for cancellation to be admitted before releasing the download.

## Rendered evidence

The following PNGs are actual Chromium captures of the production UI with the isolated provider fixtures described above. They retain v508 styling and are not design mockups.

1. [Initial Login](codex-cli-onboarding/01-Confectory-CLI-Login.png)
2. [Installation consent when the supported runtime is absent](codex-cli-onboarding/02-Confectory-CLI-Install-Consent.png)
3. [Official device-login stage with a synthetic test code](codex-cli-onboarding/03-Confectory-CLI-Device-Login.png)
4. [Explicit choice between identified fixture accounts](codex-cli-onboarding/04-Confectory-CLI-Account-Choice.png)
5. [Model choice only when no default/configured/single model applies](codex-cli-onboarding/05-Confectory-CLI-Model-Choice.png)
6. [Ready Agent, with account metadata distinguished from a real response](codex-cli-onboarding/06-Confectory-CLI-Ready.png)
7. [Global Helper receiving an owned protocol reply](codex-cli-onboarding/07-Confectory-CLI-Helper-Reply.png)

Library delivery was attempted through the supported batch helper. It failed during its initial tool-discovery request with a network error, before upload preparation. A normal Library metadata read succeeded, but one retry of the unchanged batch failed at the same preflight. No Library file IDs or successful Library writes are claimed. The exact image bytes are retained here as Git evidence.
