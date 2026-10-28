# Desktop package probe copy lifetime — 2026-10-25

The package probe previously retained an approximately 79 MiB SDK-less runtime
copy and 134 MiB legacy-checkout package copy after each run. This change cleans
up only those directories created by the current probe. Product code, the v536
layout, permissions, source contracts and Review/Confirm behavior do not change.

## Approved existing copies

The user explicitly approved the following four directories under
`/workspace/scratch/v536-information-binding/tmp/`:

| Exact relative path | Allocated bytes before removal | Retained original |
| --- | ---: | --- |
| `confectory-desktop-package-3msxhwo2/runtime only` | 83,091,456 | SDK `dotnet-10.0.401`: dotnet, host, shared/Microsoft.NETCore.App |
| `confectory-desktop-package-3msxhwo2/owned checkout/Builds/Windows-x64` | 141,012,992 | `/workspace/artifacts/v536-information-inherited-copy/Windows-x64` |
| `confectory-desktop-package-vpba_s82/runtime only` | 83,148,800 | Same SDK |
| `confectory-desktop-package-vpba_s82/owned checkout/Builds/Windows-x64` | 141,062,144 | `/workspace/artifacts/v536-information-inherited-contract/Windows-x64` |

Immediately before removal, both runtimes' 191-file sets and both packages'
2,343-file sets matched their originals by SHA-256. No target/ancestor symlink,
shared file inode, active test process or observed open reference was present.
Deletion was restricted to those exact identities and directory-relative paths.
No parent directory was deleted. All 4,895 original and retained evidence/profile
files compared before/after remained unchanged. Actual free-space increase was
448,311,296 bytes (427.54 MiB); free space rose from 13,123,584 to 461,434,880 bytes.
Local audit: `/workspace/scratch/v536-package-cleanup/{revalidation,cleanup}.json`.

## New probe ownership

`tests/probes/desktop_package_copies.py` creates a fresh fixture root and records
the inode/device/owner of only the two explicit copy paths. It registers ownership
before copying, so partial copies are covered. It refuses existing directories,
unknown paths, replaced roots/parents/targets, and cleanup while its tracked host
is running. Removal uses the directory-relative, symlink-resistant rmtree API;
links inside a copy do not lead to removal outside it. A removed path cannot be
adopted again by a repeated close.

The probe terminates and waits for its host before context cleanup, escalating
only that process group if termination times out. Browser lifetime remains inside
the Playwright context. Success is printed/written only after cleanup succeeds.
On an ordinary exception, `copy-cleanup.json` records the operation error and
cleanup result while the original exception still fails the command.

The fixture root, logs, screenshots, source marker, owned data/profile, generated
package and external reused runtime remain. No glob is used to discover deletion
targets. This does not purge old builder outputs, caches, SDKs, retained packages
or `.previous-*` backups. SIGKILL/process loss cannot guarantee Python finally
execution; an unverified leftover must not be swept by a later run.

## Verification

Run the small isolated ownership/lifetime regression:

```sh
python3 tests/probes/desktop_package_copies_test.py
```

Seven tests passed: successful copies; assertion/partial-copy/early exceptions;
repeated hard-link copies and external runtime preservation; rejection of existing
and unapproved paths; live-process deferral and idempotent close; replaced parent
or target rejection; leaf-link containment. Only new isolated test data is used.

Run the real package composition/engine/browser cases with a previously verified
Windows cross-published package (set `CONFECTORY_DOTNET` to the SDK's dotnet):

```sh
python3 tests/probes/desktop_package_lifetime.py REPO PACKAGE [RUNTIME_FIXTURE]
```

Six cases passed using retained package
`/workspace/artifacts/v536-information-shared-callers/Windows-x64`:

| Case | Expected result | Copies removed | Retained disk delta |
| --- | --- | ---: | ---: |
| Normal | pass | 2 | 159,744 B |
| Normal repeat | pass | 2 | 155,648 B |
| Exception during legacy copy | OSError, exit 1 | 2 | 28,672 B |
| UI failure after real screenshot | RuntimeError, exit 1 | 2 | 151,552 B |
| Exception after real tamper rejection | OSError, exit 1 | 1 | 20,480 B |
| Read-only external runtime reuse | pass | 1 | 155,648 B |

The three expected nonzero exits are successful negative tests, not successful
probe runs. Package file sets, all bytes and link counts stayed equal to their
baseline after every case. External reused runtime hashes remained equal. Real
screenshots, host logs and settings sentinels survived the UI failure. The tamper
case restored the original resource through its existing finally block.

The first harness attempt failed because its deeply nested Chromium socket path
exceeded the Unix limit. That failure also cleaned both copies and retained its
logs/profile. The harness now creates a short, new browser-only temporary path;
no old browser/profile directory or product layout was changed.

At 200 ms sampling, minimum workspace free space was 108,924,928 bytes and maximum
cgroup memory was 16,814,526,464 of 17,179,869,184 bytes. OOM/oom_kill were zero.
These sampled values are not guarantees about every instant. Repeated completed
runs retained only bounded evidence, not the 214 MiB of copy contents.
Summarized evidence: `docs/evidence/v536-package-copy-cleanup/verification.json`.
Full local evidence: `/workspace/scratch/v536-package-cleanup/`.

This is a Python verification-tool change. The existing cross-published package
was exercised; a new Windows executable was not built. Its manifest SHA-256 is
`9d8f3fa88b1e8c62753ba2fe32228e02aa3be6ef41c34c394a81be15bd42f559`.
Actual Windows apphost/WebView2, mobile devices and Library delivery remain
unverified. No user project, real login or paid inference was used.

## Continuation

The row 7 independent-copy contract/ID/function/retarget policy still awaits the
user's separate answer. This cleanup approval does not resolve that policy.
Row 8 next remains shared output addition/deletion and return contracts; later
input/output combinations, C#/nested/private/whole-body and copy/inherited/registered
contexts remain separate. Row 9 advanced pin types/display-name identity and other
documented UI work remain. The recovered space permits the next bounded unit,
with disk/memory preflight and sequential tests. General builder generation/cache
retention was diagnosed but not changed or cleaned here.

## Clean checkout reproduction

The existing independent checkout at
`/workspace/scratch/v536-multiple-implementations/checkout` was fast-forwarded
to committed test source `ed7b6e99dcbc973fcb74eb133ceb8a970ddda81f`; it was clean
before and after verification. All seven isolated regressions passed there.
The committed package probe then passed actual packaged-engine web startup, all
74 resources and the minimal login screen using the preserved external runtime.
Its one new hard-linked legacy copy was removed after host exit; screenshot, log,
profile and cleanup evidence remained. Every original package hash/link count
was unchanged. The completed run retained 155,648 bytes. No new executable build
was needed for this Python test-only change; Windows execution remains untested.
Local committed-source logs: `clean-unit.log`, `clean-package.log`,
`clean-verification.json` in the audit directory. The later validation-record
commit changes only this document and its JSON evidence; tested Python sources
remain byte-for-byte identical.
