# ProjectManager

Reusable project-data contexts with explicit active selection and an owned ProjectExecution session. No hardcoded editor host/game guest roles: any ProjectPack, including an engine or another editor producer, can be described/opened and run through the same capabilities. Opening/indexing metadata never executes code and games do not require an editor entry.

CreateManager(capacity) returns an opaque caller-owned token. Open requires an explicit path and returns a stable context handle; repeated Open returns the current open context. Select changes active data context only. Context returns `[handle,path,namespace,defaultEntry,targets,state]`; an empty handle means read active and returns an empty snapshot when none is selected. Close is idempotent and closes only data. Reopening creates a fresh context handle. Closed contexts remain observable until manager disposal; capacity bounds retained context history.

Executions borrows the manager-owned execution session for public Observe/Stop/Poll. Launch requires a specific open context/target; empty entry explicitly selects that context's declared entry. Multiple runs use distinct execution handles. Closing a View, stopping an execution and closing a context are independent. Manager Dispose implements caller stop-on-dispose: stop all owned executions, release their host resources, then release context state. View close alone must not Dispose the manager. Unknown/cross-manager handles and disposed callers fail. Caller operations are serialized on the UI thread.

CreateProject is an explicit source write to a new local directory, with a validated identifier and existing compiler-target pack path; existing directories are never overwritten. The initial generated gameplay entry returns zero and has no editor dependency. Selection/open/execution never modify source. Editing UI/Save/Confirm remains subsequent work.

Android keeps common manager contract/body architecture and binds Android execution capabilities. Native Android process/app launch and platform data-picker/create adapters remain unavailable; managed compile/selection is not native coverage. No Helper/multiplayer dependency.
