# ProjectEntry

A reusable desktop file-open inbox, independent of editor models. `Confectory.ProjectEntry::Request(string handle,string operation,string payload)->string` defaults to `RequestBody`. Common Windows/Linux transport uses same-user named pipes; the Android-specific body explicitly requires an Activity/content-URI adapter and does not pretend to provide desktop paths/windows.

- `listen`: handle is the absolute installation scope; returns an opaque token owned by the calling UI thread. One exclusive owner per user/scope.
- `poll`: token, `{}`; returns one `{id,path}` or `{}`. It never parses/builds/runs a user project.
- `reply`: token, `{id,status,message}`; status is opened/already-open/busy/failed. Only the owning UI thread may poll/reply/close.
- `close`: token, `{}`; resolves pending requests as failed, cancels the worker, releases ownership; repeated close is harmless.

Transport is version1, 4-byte little-endian length plus UTF-8 JSON, capped at16384bytes. GUID-N request IDs deduplicate the last128 records; reusing an ID for another path fails. At most16 queued requests and30seconds per connection. A sender losing its acknowledgment receives failure/uncertainty rather than silently spawning another engine. Malformed requests and disconnected senders leave the listener usable. UI consumers decide transition/unsaved-work policy and send acknowledgment only after the open completes.

`CONFECTORY_ENTRY_SCOPE` selects installation identity in consumers/launcher; `CONFECTORY_ENTRY_STORAGE` overrides the private inbox root (default local user application-data/Confectory/entry). Windows identities are case-normalized. Separate installations/scopes intentionally have separate instances; same-user/elevation mismatches may fail delivery and are not a reason to launch a replacement. No machine-wide registration, network service or untrusted code execution is involved.

Independent public consumer: `tests/native/project-entry-probe/project.cproj`. It verifies deduplication, competing owners, bounded malformed protocol replies, disconnect survival, UI-thread ownership, cleanup/relisten and implementation-only rebuild scope.
