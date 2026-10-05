# RuntimeBase 0.1

Public functions: `Confectory.RuntimeBase::{CreateOwner,CreateInstance,Read,Write,Subscribe,Poll,Unsubscribe,DisposeOwner}`. Each has an independent generated contract and implementation. No core runtime, global registry or provider implementation references are used.

`CreateOwner(capacity)` returns opaque owner state. `CreateInstance(owner, elementID)` returns an owner-scoped integer handle. Never use a handle with another owner. Model values are currently signed 64-bit integers; this is a small scalar model, not a general schema or table model. `Read` returns a fresh `[value,revision]` snapshot; `Write` increments revision only on change. Overflow throws before changing state.

Subscriptions are non-owning, target an instance and exact element ID, and retain an owner identity token. `Poll` returns `[value,revision]` only when changed, coalescing intermediate changes; it is a UI-thread pull notification contract, not a general event bus. Subscribe then Read when connecting a View. Cross-owner subscriptions fail. Unsubscribe is idempotent and does not destroy the model. Owner disposal invalidates every instance; late commands and subscription polls are ignored. Read after disposal fails. Reopening a View creates a new subscription and retains the live model.

All access is serialized by the consumer's UI thread. Returned state and subscription arrays are opaque, mutable capability tokens: do not edit their contents or share them across unrelated sessions. No background-thread synchronization, transfer of instance ownership or live DLL replacement is claimed in this increment.

Run `examples/runtime-base/project.cpack` through the ordinary CLI; the executable exercises 30 repeated isolated-owner, release, late-event and reopen cycles.
