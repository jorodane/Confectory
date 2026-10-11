# Portable pinned text resources: no manual checkout repair

Normal users update the code and run `Confectory.bat`. They do **not** need to re-check out UI files, change global Git settings, overwrite source files, or delete caches/settings. The preceding manual re-checkout instructions are withdrawn as a required recovery procedure. The working tree is never normalized in place by the engine.

The reported Windows crash (`ConfectoryIcon.svg`, expected 1373 / actual 1382) was reproduced using an ordinary Git `core.autocrlf=true` checkout. There was previously no attribute policy, so Git produced CRLF while the compiled manifest pinned LF bytes. Adding attributes alone leaves already clean CRLF files in place. The earlier `checkout --force HEAD -- ...` command can skip those clean files too; the first investigation missed this by testing a directly modified file. A real old-checkout -> attribute pull reproduced the omission. This is why attributes/manual repair alone were insufficient.

## Common byte policy

A compiled trusted consumer explicitly selects either:

| Policy | Identity fields | Validated and served representation |
| --- | --- | --- |
| absent or `exact` | `size`, `sha256` | Exact original bytes. Default, including PNG/JPEG/WebP and text requiring byte identity. |
| `utf8-lf-v1` | `canonicalSize`, `canonicalSha256` | Strict UTF-8 without BOM/NUL; CRLF becomes LF in memory. Bare CR is rejected. SHA-256 and size validate canonical UTF-8 LF bytes; the same bytes are snapshotted/served. |

The canonical policy is permitted only for declared file resources with HTML/CSS/JavaScript/JSON/SVG MIME. It is not inferred from a filename or selected for every text MIME automatically. Unknown policies, mixed identity fields, canonical policies on binary/inline resources, invalid UTF-8/UTF-16, BOM, NUL and bare CR are rejected. An exact text resource still rejects CRLF if only its LF identity is declared. Canonical mode accepts line-ending-equivalent content only; meaningful same-size changes still fail pinned SHA-256. No current filesystem hash is trusted as its own expected value.

EditorHome's trusted manifest explicitly chooses canonical identities for its text files; its nine PNGs retain exact identities. Existing identity values are unchanged, with names clarifying which representation they pin. `.gitattributes` remains useful for new checkouts but is not a runtime prerequisite. Source resources and original ZIP are not rewritten or regenerated.

Both physical bytes read and canonical bytes retained have unchanged **4 MiB per resource / 32 MiB aggregate** limits. Raw file lengths and aggregate are checked before allocation/read, so CRLF expansion cannot bypass a budget. Resource count/descriptor/inline base64 bounds, path/reparse-point restrictions, file-shrink/growth refusal and snapshots remain intact. Errors identify the safe relative resource ID and the relevant raw/canonical size/hash/budget without file data or absolute resource paths.

## Actual loading and verification

The launcher sets `CONFECTORY_EDITOR_REPO` to its repository; WebBundle resolves that repository's `examples/editor-home/ui`. Common Open loads those physical files before the embedded host. The general build produces assemblies/catalogs, not a copied UI resource tree. WebView2 receives only validated snapshots over IPC and serves them with `Cache-Control: no-store`. The observed startup error precedes WebView2 cache use; broad cache removal is unnecessary.

The registered original-ProjectPack regression recreates the exact existing-user state: old real Git CRLF checkout, pull new attributes/code, leave all resource files in place, and start the ordinary production EditorHome entry. It checks all 16 public resource snapshots against their canonical/exact identities and proves raw working-tree hashes are unchanged. A separate fresh LF checkout starts the same entry. In isolated test checkouts only, same-size text tampering, invalid UTF-8/UTF-16, BOM, bare CR, binary tampering and oversized raw files are rejected through that same production loading path. No replacement ProjectPack/provider/entry or special build allowance is supplied.

Common contract tests additionally verify exact text refusal, canonical LF/CRLF equivalence and unchanged originals, mixed/unknown/binary policy refusal, NUL and both canonical/exact aggregate and raw-expanded aggregate limits, plus prior scope/revision/cancellation/disposal/locality checks. Registered original-pack checkout/startup/negative gate: **1 passed, 0 failed, 0 skipped (167.311s)**. Common contract/boundary gate: **1 passed, 0 failed, 0 skipped (22.256s)**. Ordinary root Linux/Windows/Android managed builds: **tool.ok=true, 37 included packs each**. Final results are recorded in AI_DEVELOPMENT_STATUS.md. Actual Windows `Confectory.bat`/WebView2 execution still awaits user retry; the OS itself has not been accessed here.
