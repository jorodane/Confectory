# InstantTable

A disposable View borrows an EditWorkspace and projects selected object IDs/columns. Snapshot reads fresh source revisions and values; SetCell uses the existing schema editor and workspace compare-and-set. Description is a read-only current-grammar column. Poll consumes only this View's subscriptions; Close releases subscriptions without closing the borrowed workspace or discarding drafts. Confirm delegates selected row IDs to existing ChangeSet validation and conditional source publication.

Definition contains IDs, columns and request, without row values or table-owned model semantics. Capacity is 64 rows and 16 columns. Cached UI labels are presentation data only. Reopening a View projects the same workspace drafts. This pack does not implement arbitrary computed columns, general schema widgets, semantic merge or its own lock/data authority.
