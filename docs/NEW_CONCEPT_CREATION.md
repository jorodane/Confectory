# Ordinary new concept creation

The Windows report used the lowercase name `test`. The user's project was not supplied. Reproduction uses the unchanged ordinary ButtonGame ProjectPack copied for isolation, through the actual EditorHome WebUI consumer; it does not substitute a pack, provider, or catalog.

## Cause and scope

The concept button creates an `object`, not a schema. `EditWorkspace.Create` already adds `Namespace::test` at `elements/test.celem`, with a missing baseline and revision 1, and edits the existing ProjectManifest/PackManifest registration in the same shared draft. Both are dirty and both are included by the existing Save export. Creation and Save do not write the final declaration or manifest.

The data window previously sent only the declaration ID to `reviewDraft`. PackWorkspace correctly refuses a missing-baseline declaration without its registration in the explicit Review group. WebInvoke then rejected the consumer operation and common WebUI returned `consumer_error`. This is a consumer connection failure; the source tracker and manifest creation contract were already present. The previous regression covered advanced group selection and missed the ordinary data-window path.

Creation can also occur while a search, kind filter, or later page hides its row. The existing workspace now selects the created declaration's kind, clears the query and chooses its actual sorted page. This reads the owned draft catalog, not a fabricated browser item.

## Resulting behavior

The selected missing-baseline declaration exposes its pending creation IDs and root registration ID independently of the visible browser page. Confirm… first shows those exact IDs, including any other pending creations already registered in the shared manifest. The user explicitly chooses that group for Review, inspects every before/after source, and separately chooses final Confirm. Existing declarations keep their single-unit Review path. Existing advanced group selection and compiler-backed Confirm are unchanged. Unrelated dirty declarations are not silently added.

Save persists the shared local draft. Pending field input must first be applied and remains intact when Save/Review is refused. Creation's missing baseline is a source change even when the empty object has no editable data fields. No claim of a ready Review is displayed before the creation selection is actually reviewed.

The common transport continues to reject failed operations, preserving the existing revision-conflict contract. The EditorHome public projection exposes fixed diagnostic categories for missing registration, no reviewed changes, unavailable compiler host, and other source failures. UI messages use those fixed categories rather than raw exception text or private paths. IDs and reviewed source content use the existing deliberate public projection.

Name editing remains unsupported because declaration ID rename and reference rewriting have no agreed contract. Description editing in the data form remains unsupported; the existing advanced source editor can edit the actual declaration description with revision checks, Save and Review/Confirm. No new metadata or rename policy is introduced.

## Validation

Evidence: [Review capture](evidence/new-concept-creation/review.png) and [verification record](evidence/new-concept-creation/verification.json).

- Ordinary EditorHome ProjectPack: Linux, Windows and Android managed builds PASS; each includes the same 37 packs using SDK 10.0.401.
- Windows WebView managed host: PASS, zero warnings/errors.
- Actual original HTML versus ordinary consumer Home/project/create layout: PASS (102.989s).
- Actual X11 full owned-pack source acceptance: PASS, including Save, Review/cancel, external source conflict, invalid compile, restart retention, exact Confirm, confirmed-source child editor Run/Stop/cleanup and native semantic authoring.
- Normal lowercase `test` UI creation: PASS, including real browser listing. The full surrounding web regression is being rerun after a later Run/Stop check encountered an explicitly rejected stale revision from live execution updates. The harness retries only that rejected UI Stop click; no source operation or production policy is replayed.
- Retained CRLF/LF checkout and declared-resource gate: pending local commit and run.

 Actual Windows WebView and Android device execution are not available in this Linux environment. Managed builds alone do not establish those device UI results. The previous browser WASM publish blocker is outside this fix and remains unresolved.
