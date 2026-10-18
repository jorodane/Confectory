# Declared editor context action example

Open `project.cpack` in EditorHome, open the concept browser, select `Selected`, and right-click it. Choose **등록 기능 · 메타데이터 변경안**, enter field `initial` and JSON value `23`, then select **함수 호출**. The existing `Confectory.SchemaEditing::SetValue` returns a declaration with `value initial = 23;`. The selected shared draft and physical source remain unchanged; the result is a proposal string, with no automatic Apply, Save or Confirm.

`MetadataProposal.celem` uses existing primitive metadata and typed `provide` declarations. `editorContextMenu=true` opts into discovery, `editorName` supplies the label, and the two bindings name the exact function and existing authoring provider. Discovery does not invoke either function. The host currently binds only this reviewed SetValue route. Other registered functions, alternate bodies, unsupported targets and changed contracts stay unavailable.

The ProjectPack is explicitly nonstandalone. These are editor authoring actions, independent of ProjectExecution Run and game simulation. See [scope, ownership, limits and actual checks](../../docs/EDITOR_CONTEXT_ACTIONS.md).
