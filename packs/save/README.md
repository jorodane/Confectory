# Save

Location is identity-specific project-local `.confectory/edit-workspaces/<hash>/draft.json`. Write persists version-1 changed units through FileStream's conditional local write; final declarations/bodies are untouched. Read and Restore target the supplied workspace only. Reopening explicitly restores the stored original baselines, so an external final change remains a genuine Confirm conflict.

Workspace data, View definitions and final source have separate lifetimes. The milestone persists data diffs, not a complete configurable editor layout or project/chat navigation history. Android local storage must be app-private or explicitly granted; native authoring strategy is still unavailable.

Activity prepares a bounded manifest/project-ID-owned receipt CAS tuple; it never writes alone. Changed Save content and successful source Confirm include this tuple in the same FileStream.Commit transaction. No-op Save, read/restore, rejected writes and cancelled review do not advance it. Corrupt receipts are preserved. See [Home events](../../docs/V480_HOME_INCLUSION_AND_EDIT_EVENTS.md).
