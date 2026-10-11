# Confectory.WebViewHost

`Serve(owner) -> int` renders an existing WebUI owner in the generic Windows
WebView2 host configured by `CONFECTORY_WEBVIEW_HOST`. The host path comes from
trusted process configuration; it cannot be supplied by a page request. The
existing `CONFECTORY_DOTNET` selects the dotnet host. There is no EditorHome path,
function dispatcher, filesystem mapping or HTTP listener in this pack.

The child receives only declared resources and replies to existing WebUI envelopes
via private standard streams. The parent invokes `WebUI::Request` with its retained
owner, so host scope, bounded endpoints, revision and cancellation checks remain
mandatory. The renderer's stderr remains ordinary diagnostics. On close, only the
owned rendering process is retired; `WebUI::Close` is retried until pending consumer
calls retire. Consumers retain responsibility for project/Worker lifetime and any
product close-confirmation workflow before calling/releasing this presentation.

See [current support, source blocker and verification](../../docs/EMBEDDED_WEB_UI.md).
The v196 editor has not been ported and Windows rendering has not been executed in
this Linux environment. Ordinary root startup remains the working native editor.
