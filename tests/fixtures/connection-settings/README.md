# Historical generated settings manifests

These public fixtures retain the registry and dependency order from `examples/editor-home/project.cpack` at:

- `pre-instant-table.cpack`: `539d17c730999c12243fe055e485072850302b33`.
- `pre-worker-tasks.cpack`: `2b083276c9ae48b95fe4a3ae5ab2824f5d414010`.

As in the settings generator, the owner becomes `Confectory.AISettings`, standalone is false, and the sole element is `Settings`. Paths use the test-only `@repo/` prefix rather than a private checkout location. Tests supply owned Settings source separately.

With current installed pack manifests, both fixtures fail with `MISSING_NAMESPACE` before recovery: `Confectory.EditorHome.Model` now requires the absent `Confectory.InstantTable` or `Confectory.WorkerTasks` registration. They reproduce stale generated registration metadata independently of Agent registration and credentials. They do not establish which namespace is missing on a user's PC.
