# Native text Views

Field borrows a BaseUI text buffer and control surface and returns a retained native View snapshot including its `key`. Editing, IME, selection, copy/paste, undo and scroll belong to the OS/toolkit. BaseUI owns model synchronization and eligibility; readonly is distinct from disabled.

`Clip(string host,string field,int[] regions)->void` clips the exact snapshot key to parent-client rectangles. The public ClipRegions layout output can be used directly. Each region must be contained in the Field bounds; maximum256 regions. Empty regions occlude the native View. The contract does not replace text or reset selection. Bindings sharing a control ID remain independent, including hidden contexts with different bounds.

Pump the Window's OS messages before Poll so snapshots reflect the messages just handled. Poll synchronizes actual native focus and clears stale native-owned model focus without clearing engine button focus. Focus is an explicit intent, not a callback to invoke for every paint/focus-loss/capture notification. Frame hides omitted keys only on a visibility transition. Close native Views before their borrowed buffers and parent Window.
