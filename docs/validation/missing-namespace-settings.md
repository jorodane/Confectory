# Agent settings: MISSING_NAMESPACE

This follows `4226be9`. The user's new evidence explicitly says `connection_settings_invalid / settings-schema / MISSING_NAMESPACE`. The earlier `UNDECLARED_DEPENDENCY` reproduction is a separate defect, not a diagnosis of this user's PC.

## Exact reproduction and limits

An isolated profile with **zero registered Agents** and a historical generated settings manifest reproduces the exact reported code, stage and cause through `EditorHome.Model::Command("connection-setup")`. No credentials or provider calls are involved.

| Historical editor manifest used by the settings generator | Missing namespace with current installed packs | Referencing owner |
| --- | --- | --- |
| `539d17c730999c12243fe055e485072850302b33` | `Confectory.InstantTable` | `Confectory.EditorHome.Model` |
| `2b083276c9ae48b95fe4a3ae5ab2824f5d414010` | `Confectory.WorkerTasks` | `Confectory.EditorHome.Model` |

The settings generator copied the editor's registry into a private `Confectory.AISettings` project. Installed pack files later gained dependencies, but the old settings copy retained its original registry. For example, today's `packs/editor-home-model/pack.cpack` requires InstantTable; the historical settings project has no InstantTable registration. Registry construction validates dependencies of every registered pack, including the editor model, before it reaches the selected Settings object's inherited schema. The current editor's catalog can therefore work while the old settings copy fails.

The previous recovery required the same generated manifest shape and registry count, so registry growth was not recovered. The two historical manifests are retained as public test fixtures with repository-relative path placeholders.

**These are proven fixture identifiers, not identifiers observed on the user's PC.** The user's actual missing namespace and owning registration remain unknown until the new diagnostic is observed there. A different missing installed declaration must not be silently replaced or guessed.

## All throw sites and related failures

| Site | Reachability in settings-schema | Meaning |
| --- | --- | --- |
| `Registry` constructor in `Resolution.cs` | Directly reachable when EffectiveMetadata constructs the copied project's registry | A dependency declared by the Settings project or any registered pack has no registered namespace |
| `Registry.Get` in `Resolution.cs` | Reachable during effective/schema contract reads, including an installed compound field whose type namespace is absent | A queried element's namespace is not registered; the diagnostic retains the reference ID |
| `Builder.Check` in `Build.cs` | Not called by the read-only settings metadata path | A separately requested build/check pack was not selected |

A registry key pointing to a differently named pack is `REGISTRY_ID`. A wrong Settings owner/identifier is checked separately; an absent local element is `MISSING_ELEMENT`. An undeclared cross-pack reference can fail as `UNDECLARED_DEPENDENCY` before namespace lookup. An unreadable path is not evidence for any particular missing namespace. These cases are not relabeled as the user's reported cause.

## Change

- A typed, read-only repair proposal recognizes generated Settings manifests, verifies their Settings identity, unchanged dependency versions and current authoritative registrations, then completes the transitive registration set required by their installed packs. It retains the earlier missing-direct-dependency and proven moved-checkout recovery.
- The caller backs up the exact old manifest and uses expected file revisions for the commit. Settings source is never rewritten by metadata recovery. Reopening a repaired copy is idempotent.
- Custom comments, descriptions, declarations, dependency changes, foreign registrations or inconsistent paths are retained and diagnosed. Partial copies are retained. A missing pack outside the authoritative installed registry is not guessed, installed or granted access.
- `BuildError` carries structured missing-namespace context. The authoring boundary permits only bounded namespace/element identifiers and a closed resolution category. PackWorkspace and SchemaEditing retain it across errors; Home publishes it and the v508 dialog displays it. No source text, settings values, exception message or filesystem path is added to this diagnostic.

An unrepaired dependency failure now includes, for example:

```json
{"cause":"MISSING_NAMESPACE","namespaceDiagnostic":{"missingNamespace":"Confectory.InstantTable","resolution":"dependency","ownerNamespace":"Confectory.EditorHome.Model"}}
```

The screen labels these as `누락된 네임스페이스` and `참조 팩`; an element lookup also shows `참조`. If the error persists on the real PC after updating and restarting with the normal launcher, those displayed identifiers are the precise remaining diagnostic needed. The private profile path and Settings contents are not needed.

## Validation

The [structured evidence](missing-namespace-settings.json) and linked logs record:

- 20 backend scenarios, including both historical copies with Responses and Codex, exact missing dependency/owner assertions before recovery, byte-preserved Settings and exact manifest backups, idempotent reopen, custom-copy refusal, and a genuinely fresh installed-field namespace failure followed by cancel/correct/retry.
- Classification of all three Core throw sites, with a mismatched registration verified as `REGISTRY_ID`.
- Six production Responses-first UI profiles: clean, missing installed schema, invalid existing Settings, automatic old-registry recovery, preserved custom old registry with exact public identifiers, and first-run missing compound-type namespace with exact reference and successful retry. All begin with zero registered Agents. Local registration remains unauthenticated.
- Four existing declaration/settings/Helper/UI regressions, Windows target compilation, and actual Git checkout/resource startup with all 50 identities.

The Linux production host and Chromium were executed. Windows native execution and the user's actual profile were not inspected. User settings, existing backups, the v508 stylesheet, original reference ZIP, main and Android settings were not modified by this task. No real account registration, provider login, paid request or permission grant was performed.
