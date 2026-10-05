# EditWorkspace

Open requires a selected ProjectPack path, participant and work-context. Identical identity shares a live opaque session; different participants keep independent drafts. There is no null-context fallback or automatic project/chat switching. Owned declarations and implementation body units use stable element IDs; runtime body-unit IDs append `/body:target` to their owner implementation ID.

Read returns coherent draft and revision; subscriptions are exact unit tokens. SetText preserves ID/kind, SetValue uses SchemaEditing, Create stages a declaration and its manifest registration. No View or table owns these models. Native View close only releases its borrowed subscription. Explicit workspace owner Close releases the session without implicit Save or Confirm; repeated Close and late Poll are safe.

Export emits version-1 identity and modified units only, including original text/hash. Restore preserves saved baselines and rejects a different identity/version/path. Accept is called after successful selected source commit. Caller mutations are serialized in the milestone; conflicting parallel property intents need caller coordination rather than a general merge claim. There is no migration, collaborative transport or generic conflict merge.
