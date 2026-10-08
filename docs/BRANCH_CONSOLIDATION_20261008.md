# Canonical work branch and reversible cleanup — 2026-10-08

The canonical branch for future authorized feature work is `work/current`. It starts at completed `3ff60772404567678e77af111d62e3d3975e923b`; the remote former work head had no subsequent commits. Every remote branch head at the snapshot is an ancestor of this completed stack. Administration commits add only this recovery/numbering documentation; no feature files or main/default branch are changed. Schema representation remains undecided.

[Machine-readable recovery ledger](BRANCH_RECOVERY_20261008.json) records every remote name/full SHA, ancestry checks, planned deletion/retention reasons, archive refs, local divergent refs and bundle checksum. It is published before any deletion. Seven directly owned completed recent branches are eligible: owned-element-navigation, declared-element-relations, required-function-signatures, relation-target-registration, effective-metadata-explanation, lazy-semantic-catalog and lazy-edit-materialization. Each must have its exact head reachable from remote work/current and an independently verified remote lightweight archive tag before deletion. Retain historical/other-worker branches without positively established ownership/inactivity; in particular fix/ui-navigation is checked out in another worktree. No local worktree or feature branch is deleted.

The connected GitHub open-PR search returned zero on two successful scoped queries. CLI GitHub GraphQL/REST was forbidden; successful connected-app results supplied the read-only PR/default-branch check. Remote Git refs were fetched independently. A transient exec transport disconnect prevented process creation; no success was assumed, deletes remained stopped, and reconnection verified the canonical ref was still absent before retrying.

Local `work` pointed to the obsolete Python baseline `b5ea38c3d7eec3eb20f170e68f0f4215b86b2aee` and prevented the hierarchical `work/current` name. It was renamed only locally to `archive-local-work-20261008` at the exact same SHA, without checking out its obsolete code. Fifteen local branch histories are not ancestors of the completed stack; some patches are equivalent, some are not. They remain unchanged rather than silently integrating another worker's code or claiming those unique histories are in work/current. The verified complete-history bundle `/workspace/confectory-branch-recovery/20261008/pre-cleanup.bundle` preserves all pre-cleanup local refs, including the old work ref, outside Git; it is not uploaded or committed. The ledger records its SHA256. Local backup record: `/workspace/confectory-branch-recovery/20261008/pre-deletion-record.json`.

## Restore a deleted remote branch

Use the exact `backup_ref` and branch name from the ledger. Fetch that archive tag; verify its commit equals the recorded 40-character SHA. Check the target remote branch is absent, then use an ordinary non-forced push of the tag commit to `refs/heads/<original-name>`. For example:

```
git fetch origin refs/tags/archive/branches/20261008/lazy-edit-materialization:refs/tags/archive/branches/20261008/lazy-edit-materialization
git rev-parse refs/tags/archive/branches/20261008/lazy-edit-materialization
git ls-remote origin refs/heads/lazy-edit-materialization
git push origin refs/tags/archive/branches/20261008/lazy-edit-materialization:refs/heads/lazy-edit-materialization
```

Do not overwrite a recreated branch. The source commit is also reachable from work/current; local old branches remain. Recovery from the offline bundle is available if network refs become unavailable; `git bundle verify` and `git bundle list-heads` show the preserved names.

Deletion must compare the freshly advertised exact old branch SHA to the ledger and use an expected-SHA lease for the delete only. This prevents a concurrent new commit being deleted. No forced branch-tip update or work/current history rewrite is permitted. Remote archive tags are pushed/verified before deletes; the source bundle and published recovery ledger are already present. Any changed ref, new open PR, missing archive tag or ancestry failure stops deletion.

## Checkpoint numbering

Verified explicit completed commit markers in the canonical stack reach **Checkpoint 17** (`bca15ceb590912d9e57cca072b75cd552189ffe3`); Checkpoint 1 remains `73d793fdd9784a447780cc1e01bd7155a3a15370`. `CHECKPOINT_18_WORK_LOG.md` and the historical checkpoint-18 branch establish a numbered native-service stage, but there is no explicit `[Checkpoint 18]` completion commit marker in this stack. This administration task is not a new runnable checkpoint and receives no number. Preserve all earlier numbers. Before the next functional completion report, reconcile the accepted stage18 completion record with that work log: continue stage18 if still open; advance only if its closure is actually established. Do not guess or retrospectively relabel recent unnumbered functional commits as 18/19. Use the same confirmed number in commit/report/work log once established.

## Verification

Check Git bundle completeness/checksum, remote archive exact SHAs, ancestry from every deletion candidate to work/current, fresh PR state, final main/default/canonical refs, retained branches and clean working tree. Compare source trees excluding recovery/roadmap documents to `3ff6077`; no functional source may differ. No code tests are rerun for refs/documentation-only administration. Prior feature evidence remains unchanged in its own handoffs.
