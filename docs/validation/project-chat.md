# Project Helper chat: ownership and failure classification

Baseline: `9822c01eed85a274cd9c1503a2e79f93ca54af8c`. Full v508 restoration remains deferred. This patch preserves the existing layout, project identity, Agent/account guards and explicit project content/tool permission review.

The reported Korean source-operation message was not proof that an ordinary message invoked source editing. `prepareHelperMessage` selects the assigned Helper, binds its registered Agent, verifies readiness, stores the conversation draft and prepares `kind=chat`. ProjectAI opens an owned DevelopmentTools capability during preparation; no source command is issued merely by preparing chat. Confirm and execution are not granted. A shared WebState fallback previously labelled any uncategorized command exception as a source operation failure.

## Verified defect

On Windows, EditWorkspace.Open canonicalizes the supplied project path to uppercase before describing it. The authoring host's `describe` result uses that path's filename, and workspace Read returns that metadata filename unchanged. DevelopmentTools.Open then compared it to the original filename with ordinal case sensitivity. An ordinary `project.cproj` could therefore be rejected as an unowned manifest when metadata named `PROJECT.CPROJ`, before any provider response was requested. Global conversations do not open this project capability.

The filename guard now uses OrdinalIgnoreCase on Windows and Ordinal elsewhere, consistent with the existing workspace path policy. The owned view, namespace, manifest kind and filename checks remain. Different names, path traversal, foreign namespace and non-manifest kinds are still rejected. This code-path defect was reproduced by compiling the shipped Open body with controlled view metadata and both OS policies. The pre-change guard rejected the same-filename Windows case; the changed guard passes all 12 positive/negative cases. This is a simulated Windows comparison policy on Linux, not native Windows filesystem/account validation, and does not establish the user's actual PC cause.

## Failure and input behavior

Project chat selection, binding, draft, permission, workspace-open and dispatch failures now publish only a fixed `project_chat_failed` code, an allowlisted stage and an allowlisted cause. Error text, exception paths, message content and account/credential data are not copied into that diagnostic. Existing transient error UI displays the bracketed code; no debug panel is added. Source-edit failures retain their own classification.

Project floating and compact chat now handle Enter through the same submit path as Send, Shift+Enter as a newline, and suppress sending during IME composition. The existing busy gate prevents duplicate command submission. The floating card's hidden state is respected by its flex CSS so a hidden card cannot cover permission controls. Dimensions, controls and the original layout remain unchanged.

## Validation

The [JSON record](project-chat.json) contains the exact checks and shipped source hashes. Rendered screenshots show [safe failure](project-chat/safe-project-failure.png), [explicit project permissions](project-chat/project-permission.png), [project response](project-chat/project-response.png), and [global response](project-chat/global-response.png). Checks distinguish preparation (zero provider requests before consent) from a complete owned HTTP request/response. The focused browser run passed injected workspace-open failure/redaction, retained input and project scope, retry, IME/Enter/Shift+Enter, zero provider calls before explicit consent, one project response, one separate global response and unchanged project source bytes. The existing declared-connection/Responses approval and owned draft-tool regression passed (1/0/0). Release compilation completed with zero warnings/errors. Windows x64 cross-publication produced 2,225 files; the package probe passed all 50 resources, runtime-only startup from an unrelated working directory, existing profile preservation, and tampered/missing dependency rejection. All five changed production source files match the package byte-for-byte.

No live Codex account, OAuth, auth-file access, paid inference, native Windows WebView2 or user project was used. Actual Windows/provider success requires the user to retry with the new build.

If the same message still fails, the minimum useful report is the bracketed `project_chat_failed / stage / cause`, or the already-redacted provider error bracket if it reaches response handling. No token, auth file, account identifier, raw prompt or full private path is needed.

Windows distribution: `Builds/Windows-x64/Confectory.exe`, with its entire sibling output folder. .NET Desktop Runtime 10 x64 and WebView2 Runtime are prerequisites; neither is installed on the user's computer by this patch.
