# ElementView

Reusable card and table projections borrow workspace/element IDs. Each View has independent selection, cached snapshot, subscription, size and pressed state; the model lives in EditWorkspace. The table is a small paginated ID aggregate: J advances the selected row; it owns no row data or locks. A concept, object, function or owned body can also appear as a standalone card. Persistent View identity survives model updates; Bind only changes selection/subscription.

Layout returns renderer rectangles, Labels returns projected strings, Input returns command intents. No file IO, compiler/tool call or schema inspection runs per frame. Poll follows exact element revisions and aggregate membership. Close releases only its subscription/View; owner disposal remains explicit. The milestone supports scalar metadata and preset functional body edits, not full text/IME editing, migration or a complete editor.
