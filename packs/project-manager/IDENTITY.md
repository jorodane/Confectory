# Durable project identity

Identity(manager,context)->projectId requires an explicit open context belonging to that manager. It writes one versioned .confectory/project-identity.json through public FileStream optimistic Commit, bound to the exact full manifest path and namespace. A competing initial writer retries the winning snapshot; a process context ID is never reused as the durable ID. The record contains no memory, account or provider configuration.

Close/reopen preserves the project ID and obtains a fresh process context. Copying/moving the identity file or changing namespace fails with explicit rebind required; no legacy origin or old-project memory is inferred. A rebind workflow is not implemented here. Closed or implicit contexts cannot allocate an identity. Local filesystem link guards precede reads; browser virtual storage has no symbolic-link facility and skips the unsupported native LinkTarget API. Malformed or oversized records fail rather than silently replacing an identity.

EditorHome.Model now includes the durable projectId in the actual selected project and shell context. Existing chat/Worker composition is still pending; this field does not authorize memory or provider access. FileStream Snapshot/Commit/LeasePath/WriteAtomic remain explicit consumer bindings, as in the existing product composition. Core remains unchanged.

Ledger: additive Identity and IdentityBody in ProjectManager; existing Context remains a process-local context contract. FileStream public CAS is sufficient and has no implementation edit. Outside reads: ProjectExecution DescribeProject and FileStream Commit lifecycle/bounds to assess namespace/path provenance and initial-writer races. CreateProject source was checked when the sample initially assumed a filename; the test now obtains the actual manifest through public Context, which is sufficient. Consumer edits: ProjectManager sample, EditorHome.Model Command/CommandBody and VerifyShell. Rebuild scope: new ProjectManager contract/body, dependent consumer model and final links. Body-only Identity/Open probes separately assert owning physical pack rebuild and zero rebuilt contracts.

Tests exercise durable close/reopen, independent open projects, implicit context refusal, copied identity refusal, 70 slot-reuse cycles and actual EditorHome complete-close/reopen preserving ID and chat draft. Browser and Linux native product checks are separate from Windows/Android managed compilation; no native Windows or Android device claim.

## Local creator authority

EditorHome records creator authority after its successful Create command. ProjectManager observes the origin of the newly staged directory before its exclusive move. Only the resulting live context carries that creation evidence. The private `project-creators` directory is outside the project tree and belongs to the active EditorHome profile and Linux user.

The receipt binds the existing project UUID and manifest path to the machine, profile directory, project directory and original identity file. A persistent read verifies those bindings again. Ordinary open never writes a receipt. A copied project, a copied receipt in another profile, an older project with no receipt, or a changed project location remains unverified. Project content and manifest edits may continue while the original directory and identity file are retained.

The provider requires Linux machine identity, file birth times and an owner-private receipt directory. If proof cannot be recorded, creation retains its ordinary result and creator authority stays unverified. The model query does not transmit or save chat. Run `python3 tests/packs/editor_creator_host.py` after building the Release tools to exercise two real EditorHome model process lifetimes.
