# EditorHome Helper scope increment

This intermediate increment composes Confectory.Helper into the actual EditorHome ProjectPack. It does not dispatch chat to a provider or complete the AI milestone.

The EditorHome.Model session owns a lazily opened Helper store and closes its handle at session retirement. Public Open/List/Recruit/ProjectContext/RememberScoped/Close contracts perform membership and scope checks. Main uses ordinary controls over the existing local draft; no table owns the model and no new native text field is created.

Users explicitly recruit a global main-helper or a Helper bound to the current durable project ID, select a permitted Helper, record current-project or common memory, and independently allow common memory for this project's selection. Recording common memory never enables inclusion. Foreign project membership is rejected. Private selection records are bound to the manifest and durable ID; full close/reopen and process restart preserve scoped memory without creating a project or making a model call. Legacy unscoped memory remains excluded.

## Locality and rebuild scope

Intended owners: EditorHome.Model CreateSession/Command/CloseSession and EditorHome Main/VerifyShell; their existing public signatures are unchanged. New declared Helper dependencies and explicit public role bindings rebuild these consumers and their target links. Core, Helper, Agent, WorkerTasks, Augment and ProjectShell implementations are unchanged.

Outside implementation reads: Helper Command's scoped memory JSON shape and EffectiveMetadata's configuration shape (the signatures alone do not specify these payloads); ProjectShell Command's accepted menu values after a native validation failure. The consumer uses ProjectShell's existing providers route plus its own helperPanel state, avoiding a shared menu contract change. Rendering, ordering, clipping and hit testing now share the same panel geometry after a second GUI failure exposed mismatched bounds. Domain assertions reject error status as well as checking memory counts.

## Verification and continuation

Functional checks cover project A/B exclusion, explicit common permission, rejected foreign Helper, complete close/reopen, restart and stable identity. The actual Linux GUI also recruits/selects a Helper, records and toggles scoped memory, preserves the draft and completes the existing execution/resize/hide/close lifecycle checks. Locality guards remain separate from functional checks; non-editor consumers still exclude Helper. Browser and managed target results are recorded in AI_DEVELOPMENT_STATUS.md after their gates finish.

Next: provider-owned configuration projection, explicit pinned content/usage approval, async Agent chat with scoped DevelopmentTools and human Review/Confirm/build feedback; original-project Agent/Worker close ownership; genuine three-card Augment generation, selected Worker review/adoption and development log. Live account/model usage is still untested and separately gated. No new numbered checkpoint is claimed.

The subsequent ProjectAI increment now consumes the same curated public context in real-provider chat/proposal/Worker composition. See ../packs/project-ai/README.md and AI_DEVELOPMENT_STATUS.md for exact per-turn preview, original-project lifecycle, final offline GUI gates and remaining live/device approval boundaries.
