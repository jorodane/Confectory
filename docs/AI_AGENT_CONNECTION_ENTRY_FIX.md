# In-place AI Agent connection setup

The reported Home modal did contain a provider select; Responses being displayed
was not evidence that Codex was missing. The confirmed problem was the next step:
Home used an older select + Settings edit modal, which opened the settings as a
project workspace. The previous acceptance started inside an already open project
and directly selected Codex; it did not cover the actual Home entry. No cache,
installation or saved-state reset is needed to correct this flow.

Home and sidebar Agent entry now open the same ordinary connection dialog. Both
registered providers are visible by their declared display names, Codex and OpenAI
Responses. Selecting either loads its real inherited schema settings into that
modal. Codex's three methods are displayed there. Required method fields come from
the pack's declarations, and the fields use the same primitive schema input
component and PackWorkspace data-path/revision operations as Properties.

The dialog provides settings save, an explicit connection-readiness attempt,
back/cancel/reentry, and local configuration selection for an already open project.
It neither registers/selects the settings as a project nor navigates away from the
current project. Connection actions skip unrelated workspace input flushing, so
opening/checking a connection cannot silently apply the user's object inputs.
Settings and typed pending inputs remain available across dialog reentry; saved
settings drafts are reused after an ordinary host restart. Existing browser layout
and entry storage are retained, not deleted or migrated by an initializer.

The readiness result distinguishes incomplete configuration, Codex verification
blocking, and Responses' need for a separate per-request approval. It never claims
account authentication or a model response. It calls only configuration validation
and the provider's permission/diagnostic declaration: no provider open, credential
value read, login, external network request, model inference or persistent account
access. Named credential references are checked before staging; Workspace credential
references get the same secret-value protection. Selecting settings for a project
remains a configuration binding and does not override the existing live gate.

The actual Chromium gate starts by clicking Home's `Agent 추가` / AI Agent connection
entry. It covers a fresh entry state, both provider choices, field entry/save/readiness,
all three Codex method transitions, back/cancel/reentry and a second host with the
same saved settings plus a legacy browser layout marker. It proves that no project
was selected or listed, no managed-home contents were created and no account or
request was used. Existing Helper ownership/approval/loopback requests and numeric
Properties/subset review are separate regressions. They passed together 3/0/0 in
119.420s after the unified project entry and schema-input reuse.

The broader ordinary Editor/ButtonGame Chromium gate also passed, including its
editing, Augment and Worker Review/Confirm flow. Connection declaration/settings
and project scope/background/close gates passed. The original Home/project/create
characterization passed 1/0/0 in 32.162s after updating its obsolete Helper empty
message expectation. Its initial failures and the broad gate's old modal selector
were test expectations for the replaced flow; the final focused runs passed.
ElementAuthoring and test assembly Release builds had zero warnings and errors.
All 18 protected tracked files retained their baseline hashes, and object actions,
browser rendering, source editing/apply, detached editors and Review function bodies
retained their bytes. The schema input extraction is covered by the numeric gate.

The user screenshot could not be materialized into this execution environment:
Library resolved a signed transfer, but its current helper returned `download failed`.
No alternate environment path, manual credential access or transfer bypass was used.
The parent inspected the actual pixels and confirmed the select/arrow/settings-only
modal; the user's later description confirmed the workspace-navigation defect.
Native Windows execution is not claimed by Linux Chromium tests. The same packaged
HTML/JS and .NET metadata/command flow are used, with normal checkout/resource startup
validation before publishing. Original v318 ZIP, Android configuration, inbox and
unrelated object editor behavior remain protected; only the input construction was
extracted for reuse, and existing numeric editing regression confirms its behavior.
