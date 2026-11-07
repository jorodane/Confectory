# ProjectResources

`Request(manifest, project, operation, payload)` is an independent local resource
copy provider. The consumer supplies a previously authorized open manifest and
its existing ProjectManager durable project ID. It must select the ordinary
FileStream BoundedSnapshot/WriteAtomic/LeasePath providers. The editor adapter derives
both arguments from the active ProjectContext and accepts no client path.
It uses ProjectManager ReadIdentity, which validates the original identity
meaning without lazy creation/rebinding. Existing Identity creation is unchanged.

`load {}` returns confirmed metadata, an exact storage revision and limits.
It does not create asset storage. `read {id,hash}` returns verified original
bytes as canonical padded base64url; it never executes or opens the file.

`import {revision,command,item}` appends one selected copy. `item` has exact
fields `id,name,type,size,hash,modifiedAt,data`; IDs/commands are lowercase UUID
N strings, hash is SHA256 of raw bytes, and data is canonical padded base64url.
Names and supplied MIME are display metadata, never paths or execution hints.
Different resources can have the same name. The store assigns kind and UTC
creation time using the authored resource classification.

The first provider supports 1MiB per file, 4MiB decoded total and 64 identities.
Capabilities are explicit; this is not full-size or all-format editor support.
One bounded `.confectory/resources.v1.json` inside the active project owns the
metadata and encoded bytes. No original user file is moved, referenced or deleted.
Its version/project/manifest, exact record fields and every content hash are
validated. Corruption, links, unknown paths/identities and storage errors fail
closed without replacing the store with an empty list.

FileStream CommitPlan checks the exact resource revision, source manifest and
existing project identity in the same lease; only the resource file is written.
It preserves source/override contracts, Review/Confirm and existing permissions.
A digest on each immutable imported resource permits exact lost-response replay
even after another append. It is validated and excluded from public metadata.
It never silently rebases a stale append or treats another payload as the same command.

This file is durable project data, not a cache/output cleanup target. Moving or
exporting a whole project with its resources is not implemented by this provider.
Layout now provides category topology, moves, display names, and explicit single-file
copy deletion. See docs/V6_RESOURCE_FILE_DELETION.md for bounded receipt history,
late import replay protection, final CAS and old-writer limitations. Folder/multiple
removal, content editing/backup recovery and rich previews remain follow-up work. No account, shared ACL or external filesystem grant is added.
