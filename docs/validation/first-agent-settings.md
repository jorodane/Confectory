# First Agent settings initialization

Source commit: `bf6efbe8d341317f60fc7ee885a72e0bb64f26d9` (after v508 `7529415`).

## Reproduced cause

The clean-profile fixture has zero registered Agents and no `ai-settings` copy. Both Responses and Codex work on the normal checkout and the installed metadata fallback. A third valid installation shape reproduces the exact reported `connection_settings_invalid / settings-schema` failure: the Agent pack is present in the installed registry but is not a direct dependency of the editor project.

The catalog enumerates installed declarations successfully. Previously, the generated `Confectory.AISettings::Settings` object extended the selected Agent's Connection, but its generated project only copied the editor's dependencies. Resolving the inherited schema then failed with `UNDECLARED_DEPENDENCY`. First setup does not require a prior connection or Agent registration. This reproduces the reported code and stage in the shared implementation; the user's actual Windows profile has not been inspected.

The six-case before/after probe retains its original baseline separately. After the fix all six schemas resolve, with zero Agents before opening. The two installed-registry-only failures become valid; the other four remain valid. See [the structured evidence](first-agent-settings.json).

## Behavior

- The Settings project explicitly declares its selected installed Agent pack. Initial Settings source and manifest are created together with expected file revisions.
- Only a matching generated manifest can recover a missing selected dependency or the previously supported, consistently moved checkout paths. The prior manifest is backed up before replacement; Settings source bytes are retained. Customized manifests and partial copies are retained and diagnosed.
- A failed newly opened schema handle is closed, allowing a corrected declaration to be retried in the same session. Existing valid drafts retain their input.
- Public diagnostics distinguish initial setup from an existing copy and include a bounded cause code. The first-setup error no longer implies that prior Agent registration or settings are required.
- The v508 presentation is retained. Only its connection error text and setup-mode projection change; the updated runtime resource identity is pinned.

## Validation

| Check | Result |
| --- | --- |
| Backend first-setup regression | 14 scenarios passed: Responses/Codex across three installation shapes, cancel/save/reopen, missing dependency and moved-root backup, missing installed schema, missing Settings locator, invalid Settings identity, both partial-copy directions, customized-manifest preservation |
| Production Responses-first UI | Three isolated profiles passed: clean setup, missing installed declaration then retry, invalid existing settings then retry; cancel/reopen, local unauthenticated Agent registration, reload with saved input |
| Existing regressions | Four methods passed: live declaration-byte reads, declared settings/approval guards, global Helper ownership and moved-path recovery, actual Agent UI diagnostics/retry/late close |
| Resource identities | All 50 pinned resources match; v508 stylesheet and original reference ZIP remain byte-identical |
| Ordinary Git checkout/startup | Passed from the committed source: retained CRLF after attribute pull and fresh LF checkout; all 50 served resources and content/encoding/BOM/binary/budget rejection; original bytes retained |
| Windows target | Build passed; no Windows native execution in this Linux environment |

The UI fixture selects Responses before opening any Codex form. Its initial state has no settings copy or registered Agents. Registration only saves an unauthenticated local configuration row; no real account registration, provider login, model request or project grant is performed. Existing transport regressions use owned local fixtures. No user profile or settings were deleted.

The earlier first-setup test compile error and the UI fixture's incorrect assumption that registration would reopen the welcome screen were corrected in the tests. Neither failed attempt is counted as a successful product validation.

The accompanying evidence links four test logs covering seven passing methods with no failures or skips.
