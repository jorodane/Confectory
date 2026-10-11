# Review selection and compact semantic rows

On ordinary EditorHome at 1c3a68b, the actual Chromium UI reproduced disabled change checkboxes and an advanced-source button whose second click did not collapse the view. Closing with X did preserve final sources. [The reproduction log](evidence/review-selection-controls/before-reproduction.log) records both failures. The reproduction uses the ordinary unchanged ProjectPack and actual hosts, without a substitute pack/provider.

Independent reviewed units are selectable. A single known semantic change shows its checkbox, field label, struck-through previous value, arrow and next value on one line when space permits. Long text wraps with its complete content; absent values and empty strings remain distinct. The user-supplied live Site example informed this arrangement; the Site and original uploaded prototype are not modified.

Selection applies to complete reviewed units, not individual fields of a shared draft. New declarations and their reviewed manifest registrations form one mandatory selection group. Changing the selection disables Confirm until the selected ordered IDs have been reviewed again through the existing reviewGroup command. All deselected disables both rereview and Confirm. Rereview obtains a fresh exact token and actual before/after sources, preserving the original target; the reused floating window caption is refreshed to the current first reviewed unit; it does not confirm anything. Existing revision, source hash, exact ID/token, compile and conflict checks remain authoritative.

Advanced source rendering remains explicit and can repeatedly expand/collapse. Unknown additional changes retain their required acknowledgment. Cancellation or X closes Review and preserves inputs/drafts; reopening obtains a new Review. No source is written by selection, rereview, expansion or cancellation.

## Validation

- Core selection/Confirm/restart focused regression: 1 passed, 0 failed, 0 skipped (570.962s).
- Full ordinary EditorHome and generic ButtonGame Chromium regression: 1 passed, 0 failed, 0 skipped (888.453s). This ran before the final caption-only correction; [core resource identities](evidence/review-selection-controls/core-resource-identity.json) distinguish it from the final source.
- Final source 807bd96: ordinary Confirm/restart plus numeric-inline/fresh-subset-caption registered checks: 2 passed, 0 failed, 0 skipped (393.257s).
- Final same ordinary ProjectPack Linux, Windows and Android managed builds: tool.ok=true, SDK 10.0.401, 37 included packs each.
- Source 807bd96 actual retained CRLF/normal LF Git checkout and resource startup: 1 passed, 0 failed, 0 skipped (15.355s).
- Paused workspace HEAD and its 18 recorded files verified unchanged; origin/main remains 1c3a68b. Android version settings, Site, original uploads and real AI accounts were not changed.

[Short inline description](evidence/review-selection-controls/short-inline.png), [numeric row](evidence/review-selection-controls/numeric-inline.png), [long narrow content](evidence/review-selection-controls/long-narrow.png), [fresh subset caption](evidence/review-selection-controls/subset-caption.png), [verification](evidence/review-selection-controls/verification.json), [target reports](evidence/review-selection-controls/builds.json). Actual Windows/Android device UI is unavailable in this environment. The existing browser WASM publishing timeout is not resolved by this consumer change.
