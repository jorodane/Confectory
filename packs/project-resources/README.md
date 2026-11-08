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

The provider supports 4MiB per file, 4MiB decoded total and 64 identities.
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
copy deletion and confirmed category subtree removal. See docs/V6_RESOURCE_FOLDER_DELETION.md
for grouped ID/import receipts, moved-out history and stale-confirmation boundaries.
See docs/V6_RESOURCE_FILE_DELETION.md for bounded receipt history,
late import replay protection, final CAS and old-writer limitations. Explicit multi-root selection deletion is documented in
docs/V6_RESOURCE_MULTI_DELETION.md. Content editing/backup recovery and rich previews remain follow-up work. No account, shared ACL or external filesystem grant is added.

Selected groups and individual files support 4MiB within the same total store limit.
EditorHome sends larger groups through bounded session chunks and invokes the same
atomic provider only after complete SHA/UTF-8 verification. Stored v1 grammar and
small-file rollback readers retain their grammar. A store containing a file above
1MiB requires the new reader; old readers/writers reject it without resetting data.
`limits.readFileBytes` remains 1MiB. Larger `read` responses have verified metadata,
`encoding:"unavailable"`, `reason:"resource_preview_file_budget"` and no `data`.
Content edits/backups stay within 1MiB, including the original being replaced.
See docs/V6_RESOURCE_LARGE.md and the earlier group-transfer record.

Layout `read` can additionally advertise a `base64url-prefix-v1` capability for
owned text/code copies above 1MiB and up to the existing 4MiB file limit. Layout
`preview-text` requires the exact ID, full hash, import generation and compound
display revision. It verifies the whole stored copy and every final dependency,
then returns only its first 1MiB, prefix SHA256 and original total/hash. No path,
write, new external grant, storage grammar or public/override signature is added.
The editor uses a separate observation endpoint and validates those exact prefix
bytes before literal, read-only text rendering. Old metadata-only headers remain
supported. Full large content editing/backups and rich formats remain bounded as
before. See docs/V7_RESOURCE_TEXT_PREFIX.md.

Large stored PNG/JPEG/BMP/static WebP copies additionally advertise an optional `imagePreview`
capability. It is separate from the text `preview` descriptor. Metadata-only clients
keep their fallback; earlier image-part clients may reject newly supported formats at their
original decoder bound, without modifying the stored copy. `preview-image-part` accepts only the pinned
ID/full hash/import generation/display revision plus integer part index. Each
read verifies the whole original and final dependencies, returning at most1MiB
with exact offset/part/length/SHA. The editor verifies every part and whole SHA
before the existing decoder/Blob URL. Stored v1 bytes/receipts, file/total4MiB,
other encoded format budgets, dimensions/pixels/lease and all writer contracts
are unchanged. No source or arbitrary path is read or rewritten by the request.
See docs/V7_RESOURCE_RASTER_PARTS.md and docs/V7_RESOURCE_BMP_PARTS.md and docs/V7_RESOURCE_WEBP_PARTS.md for compatibility and verification limits.

Large stored PDF copies with a `%PDF-` signature now expose a separate optional
`pdfPreview` descriptor on the same metadata-only `read`. `preview-pdf-part` is
read-only, uses the same ID/hash/import/display basis and1MiB/maximum4-part bounds,
and checks the complete current copy and all final observation dependencies.
It is not the image-part lane or a file/path permission. Small reads, storage v1,
existing image/text parts and all writes/content backup budgets remain unchanged.
Consumers without this capability retain the metadata-only fallback; a full-file
SHA must pass before creating a PDF document/Worker. See docs/V7_RESOURCE_PDF_PARTS.md.

Large DOCX/XLSX/PPTX/ODT copies with a standard ZIP local-header signature expose
an optional officePreview descriptor with the resolved existing format.
preview-office-part is a separate read-only lane with the same1MiB parts,
maximum4MiB, full-copy/part SHA, import/display basis and final dependencies.
It does not grant an arbitrary path or write permission. ZIP/XML preview budgets
remain unchanged; archive editing and content/current/backup stay1MiB.
See docs/V7_RESOURCE_OFFICE_PARTS.md for exact paired-reader and lifecycle limits.
