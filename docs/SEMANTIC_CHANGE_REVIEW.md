# Semantic change review in the ordinary editor

The default data-window Review now shows the actual changes the user edits: declaration description, scalar values, field data/definitions, new concepts/schemas and their project registrations. It no longer crosses out “current source” or substitutes “shared draft” for a change description. Before and after contents are the real parsed values. Explicit absence and an empty string remain distinct.

The existing Review retains its exact ordered IDs, before/after texts, revisions, baseline hashes, token, source validation and compiler-backed Confirm. A pure projection is computed once from those exact immutable review rows using the existing declaration/manifest parser and formatter, and stored alongside them. It does not edit, reformat or substitute the reviewed sources. Desktop and Android/browser metadata authoring use the same projection method. If projection is unavailable or parsing fails, Review still works with an explicit advanced-review requirement.

Known differences are projected and removed from a parsed comparison copy; remaining declarations/relations/imports/bodies/options or manifest policy differences make the review incomplete. Changed source comments, unsupported syntax, body changes, same-looking numeric representation differences and reordered entries also require advanced review. A known description alongside an unknown schema relation therefore shows both the real description change and a clear additional-changes warning. No inferred summary hides the remaining change. Unsupported null metadata remains unsupported; it is not silently accepted by review projection.

The basic Review DOM contains no source diff. The user must explicitly press “고급 검토 · 소스 변경 보기” to construct the exact full source comparison. If additional changes exist, Confirm stays disabled until the user explicitly acknowledges that full advanced review. That is a consumer review interaction, not a new model validation/permission policy: exact-token Confirm, compiler validation and conflict checks remain authoritative. Rejecting/canceling Review and failed Confirm continue to retain drafts and inputs; spent/stale tokens do not become reusable.

## Reference and verification boundaries

The Library screenshot `libfile_251d388d1ccc81918f10e9b5be1793f4` was resolved with the current official Library skill and its supported materialization helper in this execution environment. Preparation succeeded but download failed with `download failed`; no pixels were obtained or inspected. The implementation relies on the user's explicit UX report and actual repository code. The original Library image and Site were not changed. New actual ordinary-ProjectPack captures are recorded with the final evidence.

The user separately confirmed Windows value edit/Confirm/reopen and complete-process restart persistence before this review presentation fix. That supports the reported Windows persistence flow only, not all fields, devices or this new review UI. Name editing remains at the [identity design stage](DECLARATION_IDENTITY_PLAN.md).

## Final validation

- Actual ordinary description/new-concept/value/registration Review, explicit advanced viewing, unknown-change acknowledgment, cancel/rejected compiler acceptance/draft retention/exact Confirm/process reopen: PASS (222.954s).
- Full EditorHome/ButtonGame common Chromium transport regression, including existing Worker/schema/input/Run/Stop behavior and the new Review flows: PASS (539.104s).
- Actual parser/projection preservation, mixed known/unknown changes, numeric/order/comment/body refusal, escaped descriptions and compiler/provider locality: PASS (68.384s).
- Final code be552c3 retained CRLF/LF checkout and actual startup: PASS (18.202s).
- Same ordinary EditorHome ProjectPack Linux, Windows and Android managed builds: PASS, SDK 10.0.401, 37 included packs each. Actual device execution of the new presentation is not claimed.

[Description Review capture](evidence/semantic-change-review/description.png), [creation Review capture](evidence/semantic-change-review/creation.png), [verification record](evidence/semantic-change-review/verification.json).
