# Direct relationship target registration

Baseline section3 assigns global registry/manifest data the minimal namespace/element locator role and keeps detailed meanings in owning packs. Existing Core Registry cannot be reused wholesale for this bounded editor query: its constructor reads all registered manifests and Get opens element declarations. Instead reuse the public Parser's manifest/qualified-ID grammar through the existing SchemaEditing Call metadata protocol. No parallel resolver, new execution function or new project-opening route.

## Scope and contract

Existing `SchemaEditing::Call("locate",payload)` accepts `{project,manifest,ids}`: explicit selected project/pack path, its current draft manifest text and up to256 qualified IDs. Manifest text is limited to1MiB. It parses the selected manifest, uses its own element locators for the same namespace, and opens only registered owning manifests needed by requested namespaces. Each namespace is read once per request; unrelated registrations and nested registries/dependencies are not traversed. Registered manifest namespace/kind must match its registration. Target source files, inheritance, module implementations and required-function signatures are not loaded/resolved/validated. Registered means a **manifest locator exists**, even if its target file is absent or wrong; it does not prove buildability, dependency permission, expected role or contract compatibility.

Reply:

```
{"scope":"manifest-locators","projectNamespace":"App","targets":[
 {"id":"Known::Function","status":"registered","namespaceRegistered":true,
  "kind":"function","reason":"locator-present"},
 {"id":"Absent::Function","status":"unregistered","namespaceRegistered":false,
  "kind":null,"reason":"namespace-not-registered"},
 {"id":"Broken::Function","status":"unavailable","namespaceRegistered":true,
  "kind":null,"reason":"manifest-unavailable"}
]}
```

IDs are deduplicated and ordinally sorted. Unregistered also includes element-not-declared in a successfully parsed owning manifest. Unavailable means no reliable negative result: unreadable/missing/out-of-scope/oversized/invalid registered manifest, manifest identity mismatch, invalid query ID or invalid selected manifest. namespaceRegistered is null when that fact cannot be established. A malformed/unreadable registered manifest never becomes element-not-declared. The current reason manifest-unavailable groups provider read/parse failures; it is not a diagnosis of the user's platform/filesystem.

Desktop reads explicitly registered manifest files using its existing local tool/file authority. Android/browser use their existing owned-root metadata provider boundary; outside-root or unmaterialized registered manifests produce unavailable. Same reply schema and accessible-fixture JSON are parity-tested; equal capabilities on different runtimes are not claimed. No platform scope is broadened, no remote fetch, automatic imported-pack provisioning or app/project launch.

Actual product: `EditorHome.Model::Command(session,"workspace",{context:activeContext,action:"locate"})` for the selected owned element. It returns ordinary snapshot, current `inspection`, `inspectionRevision`, `locationManifestRevision` and `locations`. It collects direct target IDs and provider-function IDs from current inspection and reads the current owned draft manifest using public List/Read/Identity. It does not take an arbitrary project argument, change selection/filter/review/drafts or Save/Confirm. Existing active-context guard applies. Ordinary inspect does not request locations: missing locations means **not queried**, not unregistered. Refresh explicitly after a selected-source or manifest revision change. Registered imported manifests are observed on disk at query time, not stored in the owned draft; this is not an atomic cross-file revision/transaction snapshot.

## Ledger and verification

Elements: PackWorkspace CommandBody adds existing SchemaEditing Call import/locate operation; no public signature or new function contract. Target-owned desktop and identical Android/browser templates add RelationLocators projection. Outside reads: public Registry constructor/Get demonstrate why their read scope is too broad; public Parser Manifest/qualified-ID and existing SchemaEditing Call establish reusable metadata grammar/protocol; EditWorkspace Identity/List/Read establish selected owned context and manifest draft. Outside edits: authoring tool and target templates are necessary because the existing Call operations did not expose locator metadata. Core, effective resolver, layout, arbitrary invocation and AI permissions unchanged.

Rebuild scope: PackWorkspace owning implementation assembly and final bindings; desktop authoring tool; regenerated Android/browser apps for metadata templates. Public contract DLL signatures unchanged. Existing SnapshotBody/CommandBody and actual EditorHome.Model CommandBody physical locality probes remain independent functional gates.

Existing SDK10.0.401; DOTNET_CLI_HOME=/tmp/confectory-dotnet10 and CONFECTORY_DOTNET=/workspace/toolchains/dotnet-10.0.401/dotnet:

```
$CONFECTORY_DOTNET build Confectory.sln -c Release --no-restore
$CONFECTORY_DOTNET run --project tests/Confectory.Tests -c Release --no-build -- --require-runtime PackWorkspaceTests SchemaEditingTests test_project_shell_domain_isolated_execution_no_null_chat_open_and_context_cleanup test_project_shell_windows_and_android_managed_compile
```

Gates cover owner/imported locator present, absent element, absent namespace, unreadable registered manifest, invalid ID, invalid selected manifest and namespace mismatch. Injected read-count gate proves two requested imported manifest reads attempted once each while an unrelated broken registration remains unopened. Locator points to a missing declaration file and still returns registered, proving target source isn't opened. Compiled metadata adapter JSON matches desktop; Android/browser templates are identical. Actual EditorHome selected module locate returns registered/unregistered/unavailable without loading its broken/unused registry graph or running target code, retains signature/draft revision and leaves final source unchanged. Earlier navigation/signature/relation/Save/review/lifetime/locality checks retained. Windows/Android actual common managed product compilation remains separate from OS/device/browser runtime acceptance. No new tools/installations/native packaging.

Remaining candidates are unchanged: lazy owned indexing, provenance-aware effective contract explanation, typed schema/reference presentation, explicit cross-pack migration and bounded graph navigation. Do not start those larger policies automatically from locator availability.

Recorded result (2026-10-08): solution build passes zero warnings/errors (2.20s); final test-runner build passes zero warnings/errors (2.76s). Final combined five functional/product/provider/target gates pass5/0/0 (139.458s), including selected inspectionRevision1/locationManifestRevision0 and actual product tri-state results. Additional readable-outside-owned-root metadata regression passes1/0/0 (2.162s), returning unavailable with namespaceRegistered=true. Initial actual-product fixture was corrected from an invalid registry-bearing Pack to a valid non-runnable ProjectPack before the final passing run; declaration grammar/policies were not relaxed. Private evidence: /tmp/confectory-relation-locators-build.log, /tmp/confectory-relation-locators-final-tests.log, /tmp/confectory-relation-locators-final-build.log, /tmp/confectory-relation-locators-scope.log. This work branch preserves prior navigation/relation/signature commits4e9ff89/372d686/447e473; no main merge or larger follow-up.
