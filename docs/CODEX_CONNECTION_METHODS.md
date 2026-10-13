# Codex connection methods in the ordinary editor

Click the Codex connection pack in the existing Agent connection window. Three
method cards appear immediately below that pack: local CLI, Desktop/IDE and ChatGPT
Work. Choosing a card stages its method in the existing settings draft without
launching, authenticating, sending content or starting a provider. The chosen card
expands its required fields, official documentation, setup steps and support limits.
Settings open through the ordinary inherited Properties view; existing values for
other methods remain in the same settings object. Bind the saved configuration
explicitly after editing. An active owned AI request fences method selection and
rebinding, so a setting change cannot retarget its running owner.

The method definitions and method-setting field are declared by the connection pack.
The common catalogue validates their IDs/count/size and references to inherited
schema fields. The frontend renders these declarations and common state; it does not
hardcode Codex provider names, fields or methods. No alternate editor or provider
reply generator is introduced into the product.

| Method | Implemented local path | Current real-use boundary |
| --- | --- | --- |
| Local CLI | Existing owned stdio app-server, official public account preflight, scoped thread/turn and dynamic draft tools | Selected installation/account/service and chosen-model tool policy need verification; product live gate stays false |
| Desktop/IDE | Same JSON-RPC protocol over explicitly selected official app-server Unix control socket with HTTP Upgrade/WebSocket framing | Requires a public socket prepared by its owner; arbitrary Desktop/IDE private IPC, automatic app discovery and foreign conversation adoption are not provided; Windows native execution is unverified |
| ChatGPT Work | Separate `WorkspaceRequest` public function implements official Workspace Agent trigger, stable conversation/idempotency keys, owned receipt and run-status polling | Requires an admin-enabled published API channel and separately provisioned scoped credential binding; ordinary Work UI is distinct. Reply-body retrieval and remote cancellation are not documented API capabilities; product Helper/Worker dispatch stays unsupported |

The socket path reuses the production account, scope, error, message and tool logic.
It explicitly applies per-thread environment/extension restrictions, creates a new
owned ephemeral thread and never resumes an arbitrary existing app conversation.
Stop sends the owned thread/turn interruption before disposing this client's socket;
it does not kill the shared server. A pending socket read remains separately owned
until disposal, so cancelling the local wait does not destroy the channel before the
interruption is sent. A connection interruption before the owned turn identity is
known can leave an uncertain remote outcome; there is no automatic replay or claimed
remote cancellation for that case. Native/tool/startup verification is still required
before live support can be enabled.

`WorkspaceRequest` is deliberately a receipt/status contract, not an Agent reply
contract. It sends only the reviewed project/Helper context after an exact trusted
host grant, reads only an explicitly approved external environment credential
reference, refuses redirects/unapproved endpoints and bounds response size/time.
It never reads/copies login files or stores token values in project content. A repeated
execution returns the same receipt, and an uncertain POST is not retried automatically.
Its `stop`/`close` ends local polling and explicitly retains
`remoteCancelSupported:false`; remote completion is not Worker goal completion.
The current UI offers selection/configuration and displays this boundary. It does not
provide an automatic paid Workspace request/receipt dashboard or import Work answers
as Helper replies. Local tests can invoke the public receipt contract against an
explicitly owned loopback API fixture. A real API experiment requires a separate
owned account/channel/token/usage review and application receipt ownership workflow;
method selection alone authorizes none of those actions.

The Workspace API requires a published `agtch_...` channel and returns an
`apirun_...` run identifier when its beta status header is used. Native browser/Android
credential or process routes are not enabled. Tokens are not ordinary settings values;
only the separately bound `env:NAME` reference is accepted. Settings never infer an
account from this cloud execution environment.

## Validation

Actual Chromium uses ordinary EditorHome and ButtonGame, with the production packs
and settings view. It clicks the Codex pack, compares all three method cards, changes
each method in its real settings draft, explicitly binds CLI configuration, displays
passive diagnostics and proves that six consent checkboxes cannot launch the owned
executable sentinel while the live gate is false. Existing HTTP Helper messages,
errors, hidden work and project close behavior still use a clearly owned loopback
service fixture, not a real model.

A second gate compiles the normal public provider and WorkspaceRequest roles. Its
owned Unix listener verifies official Upgrade/framing and actual JSON-RPC calls,
scoped output, exact interruption for two separate turns and survival of the shared
listener. Its owned HTTP endpoint verifies one trigger POST, stable ownership and
idempotency, one status GET, ignored non-retrievable reply text and no remote-cancel
request. Fixture account/service output is explicitly synthetic. The stronger
existing stdio/tool/CAS/account-fence and installed unauthenticated no-inference
gates remain separate evidence. Initial failures and corrected results are retained
under the local `/workspace/scratch/confectory-codex-current` evidence directory.

## Official sources

- [App-server transports and account/thread/turn protocol](https://learn.chatgpt.com/docs/app-server)
- [Codex IDE extension](https://learn.chatgpt.com/docs/codex/ide)
- [ChatGPT desktop app](https://learn.chatgpt.com/docs/app)
- [ChatGPT Work entry and setup](https://learn.chatgpt.com/docs/get-started-with-work)
- [Workspace Agent trigger/status API and response-body limitation](https://learn.chatgpt.com/workspace-agents/trigger-runs)
- [Workspace Agent scoped access-token provisioning](https://learn.chatgpt.com/workspace-agents/authentication)
- [Earlier CLI-only preparation and verification record](CODEX_EXISTING_CLI_CONNECTION.md)

Final method UI and connection-declaration batch: 2 passed / 0 failed / 0 skipped
in 59.058s. The final UI includes direct sidebar Codex click and all three saved
method choices. The owned control-socket/Workspace method gate passed in the preceding
89.610s batch (that batch's UI failure was subsequently corrected). The wider affected
batch passed 4 and failed 1 in 473.842s: broad Editor/ButtonGame, Helper cold restart,
stdio/installed startup and project ownership passed; the declaration consumer lacked
an explicit BrowseDirectory provider. That test-only composition was corrected and
is included in the final 2/0/0 batch. Earlier method UI/protocol failures and fixes are
retained in local evidence: catalogue JsonElement conversion, endpoint registration,
state-update waiting, expected peer-disconnect classification, config diagnostics
excluded from revalidated configuration, and cancellable socket-read lifetime.
