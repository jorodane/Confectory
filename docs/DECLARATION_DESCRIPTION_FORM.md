# Declaration description form

The original v196 data window now edits the declaration's actual `description` statement. The textarea keeps pending input in the existing per-project, per-object, per-window input store. Save and Confirm… stage that input through the selected owned declaration and its exact draft revision. Save persists the shared draft; Review and exact-token Confirm keep their separate existing meanings. Failed revision checks retain the input. Closing a Review retains the staged description and source remains unchanged until Confirm.

The existing SchemaEditing Call parses the declaration, updates only Description/DescriptionPresent, formats with the existing declaration formatter and parses again. PackWorkspace applies the result with existing SetTextIfRevision; no raw string replacement, manifest mutation, ID change, reference rewriting, provider call or direct final write is introduced. An empty string is an explicit empty description statement (`DescriptionPresent=true`); no inherited-description removal policy is added. Desktop, Android and browser metadata authoring implementations expose the same operation. Primary and retained property windows share the same draft and retain separate pending inputs.

## Name decision

The current name input displays the last segment of the actual namespace-qualified declaration ID. Element has no independent display-name member, and EditWorkspace SetText explicitly preserves identity and kind. References, manifest registrations, schema associations, functions and implementation bindings use that ID. There is no existing safe ID-rename transaction.

Two product choices remain: introduce an independent display-name contract while retaining IDs, or design an explicit ID-rename transaction covering owned registrations/references and decisions for external references. Neither is inferred from the prototype. This change keeps the name read-only and does not introduce an arbitrary metadata key as a display-name convention.

## Validation

Final results are recorded with the change's verification evidence. Actual Windows/WebView2 and Android device execution remain outside this Linux environment. The ordinary EditorHome ProjectPack is used for the actual browser flow and managed target builds; no test-only pack or transport bypass is used for form editing.
