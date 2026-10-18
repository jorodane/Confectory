# FrameControl 0.1

Cooperative frame ownership for local desktop ProjectExecution launches. `Open()->string`, `Begin(owner)->int`, `Complete(owner)->void`, `Close(owner)->void` are ordinary pack contracts. Begin returns 0 paused, 1 ordinary frame or 2 one requested fixed frame. Serialize callbacks on the creating loop thread. Call Complete only after successful actual model/presentation work; it is the sole Step/frame acknowledgement point. Always Close in cleanup. Without an owned launch environment the adapter leaves ordinary scheduling enabled and creates no pipe.

Use the caller's fixed delta for a Step, clear pause backlog, and keep host lifetime/input-close pumping alive while paused. This adapter does not suspend arbitrary code or own native surfaces. Its bounded local pipe is authenticated by launch handle/secret, runtime epoch and request/command sequence. Missed heartbeat pauses the next cooperative boundary; reconnect queries actual state without replay/resume. Existing owned-tree Stop remains available for blocked callbacks.

See [the complete protocol, supported consumers and limits](../../docs/V480_LOCAL_RUN_FRAME_CONTROL.md). Android/browser execution is not advertised. No remote service or Core/compiler dependency.
