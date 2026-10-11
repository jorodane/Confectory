# Declaration description form

The original v196 data window now edits the declaration's actual `description` statement. The textarea keeps pending input in the existing per-project, per-object, per-window input store. Save and Confirm… stage that input through the selected owned declaration and its exact draft revision. Save persists the shared draft; Review and exact-token Confirm keep their separate existing meanings. Failed revision checks retain the input. Closing a Review retains the staged description and source remains unchanged until Confirm. Successful Confirm refreshes the actual schema and draft revision in the visible data window, so immediate follow-up editing does not use the pre-acceptance revision. The existing field-style reset explicitly restores the current description; stale pending input is never silently rebased.

The existing SchemaEditing Call parses the declaration, updates only Description/DescriptionPresent, formats with the existing declaration formatter and parses again. PackWorkspace applies the result with existing SetTextIfRevision; no raw string replacement, manifest mutation, ID change, reference rewriting, provider call or direct final write is introduced. An empty string is an explicit empty description statement (`DescriptionPresent=true`); no inherited-description removal policy is added. Desktop, Android and browser metadata authoring implementations expose the same operation. Primary and retained property windows share the same draft and retain separate pending inputs.

## Name decision

The current name input displays the last segment of the actual namespace-qualified declaration ID. Element has no independent display-name member, and EditWorkspace SetText explicitly preserves identity and kind. References, manifest registrations, schema associations, functions and implementation bindings use that ID. There is no existing safe ID-rename transaction.

The user subsequently proposed separating an immutable reference identity from the display name. The [staged identity design](DECLARATION_IDENTITY_PLAN.md) preserves current namespace contracts and does not perform ID renaming or bulk migration. Name editing waits for the additive domain metadata contract; this fix does not introduce an arbitrary scalar metadata key as a display-name convention.

## Validation

Evidence: [fresh process reopen](evidence/declaration-description-form/reopened.png) and [verification record](evidence/declaration-description-form/verification.json).

- Actual ordinary creation/description form/Save/Review cancellation/revision rejection/Confirm/process reopen: PASS (247.459s).
- Declaration identity/signature/reference/data preservation, description escaping and explicit empty/non-string behavior, actual compiler validation and locality: PASS (115.246s).
- Actual final-code retained CRLF/LF checkout and startup: PASS (34.675s).
- Full actual EditorHome/ButtonGame common Chromium transport regression: PASS (618.628s), including existing Worker/schema/input/Run/Stop and description process-reopen flows.
- Same ordinary ProjectPack managed builds for Linux, Windows and Android: PASS, 37 included packs each.

 Actual Windows/WebView2 and Android device execution remain outside this Linux environment. The ordinary EditorHome ProjectPack is used for the actual browser flow and managed target builds; no test-only pack or transport bypass is used for form editing.
