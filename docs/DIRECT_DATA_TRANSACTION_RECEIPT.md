# Direct-data transaction receipt foundation

This is an **unconnected foundation**, not a new editor Save endpoint or a
change to any existing checkpoint, project, pack, Review, or Confirm format.
The existing editor continues to stage, save, review, confirm, and recover
exactly as before. In particular, the earlier experimental combined Save
operation is not enabled.

## Current measured boundary

One instrumented run of each actual Linux Chromium path on disposable packs,
at the existing work/current revision fe408415, produced the following
integer-value timeline (milliseconds from the Save gesture; measurement
overhead and unrelated browser activity are included):

| Objects / surface | File persisted | UI stable | Requests started before / after file persistence | applySlots request span |
| --- | ---: | ---: | ---: | ---: |
| 40 / primary | 812 | 1,367 | 21 / 17 | 334–609 |
| 40 / independent | 1,037 | 1,839 | 28 / 19 | 360–631 |
| 400 / primary | 2,101 | 3,191 | 33 / 22 | 435–1,818 |
| 400 / independent | 2,124 | 3,361 | 39 / 25 | 439–1,499 |

The request count includes update/observation traffic, not just commands.
These are diagnostic samples, not repeated performance medians. In the
400-object runs, the applySlots consumer itself took approximately 1,307 ms
(primary) and 980 ms (independent). Its source candidate generation, effective
metadata checks, group guards, and existing checkpoint work remain necessary;
the evidence does not justify deleting those steps. Primary direct confirmation
and independent Review/Confirm both retain their current validation. After
actual file persistence, completion delivery, presentation and draft status,
and relation-map refresh still contribute to UI latency.

## Recovery contract

`DirectDataReceiptJournal` in Confectory.Core has no project source writer,
no browser trust boundary, and no automatic replay method. It records only
opaque fingerprints and immutable operation identities in a caller-owned
private, existing recovery directory scoped to exactly one project and owner.

- An intent binds operation ID, project and owner identity, source identity,
  original and candidate content hashes, existing checkpoint fingerprint, and
  exact request fingerprint. Equal original/candidate content is not admitted
  as a new transaction.
- Only an explicit new host admission may create an intent. A duplicate
  admission returns an observation of the existing operation; it does not
  grant a second admission. A different operation is blocked while a durable
  intent is unresolved. The bounded history is not automatically trimmed.
- Inspect never creates an intent or receipt or writes project data. A missing
  intent is not permission to retry a lost request. A pending intent requires
  explicit recovery even if the current source bytes equal the original or
  candidate bytes. Unreadable, corrupt, conflicting, or ambiguous records
  fail closed.
- A completion is accepted only as an explicit attestation for the exact
  intent from the trusted existing commit authority. The type carries an
  intent fingerprint, committed content hash, and authority proof fingerprint.
  The journal checks identity and consistency, **not** whether an arbitrary
  caller is the actual commit authority. Do not expose this method to IPC or
  derive its attestation from a file-content comparison.
- A persisted completion is historical evidence of that operation's commit.
  It does not establish current source ownership, current schema/reference
  validity, or permission, nor authorize another write. Reconciliation must
  still use the current authoritative source and the existing conflict guards.
- A crash after the source replacement and before the completion publication
  remains uncertain; a matching candidate hash does not resolve that gap.
  No inferred completion, automatic replay, or automatic record deletion is
  allowed. A future integration must make that outcome explicit in the
  existing recovery UX and preserve independent input and checkpoints.

The Linux prototype uses flushed files, atomic non-overwriting publication,
directory fsync, and an exclusive cooperative journal lock. This is tested
against process termination and cooperating concurrent processes, not a power
cut or arbitrary noncooperating external mutation. The private directory and
the trusted authority boundary are prerequisites; checksums detect corruption,
not authenticity against a writer that can forge the entire private journal.
Windows and other platform writers intentionally fail closed pending a
verified platform durability adapter. No production storage location or
receipt retention/archival policy has been chosen.

## Integration boundary still to prove

The next host-only experiment must derive the authority fingerprint from the
actual existing validated commit result and durable checkpoint/commit evidence,
under the same project-owner lock and current source/manifest/schema/permission
checks. Admission and completion are not themselves source compare-and-swap.
The current detached sequence has explicit select, Review, and Confirm requests;
combining their transport is not permission to combine or remove their guards.
An unresolved intent or absent/mismatched receipt must preserve the original
recovery operation and independent draft state. The prototype deliberately has
no path that resumes a pending mutation. This means it is not yet an end-to-end
host direct-save operation or a measured product speed improvement.

## Test

From the repository root, on Linux with .NET 10:

```sh
dotnet run --project tests/probes/direct-data-receipt/direct-data-receipt.csproj -c Release
```

The probe uses temporary synthetic sources and recovery directories. Its child
processes are forcibly terminated before intent, after durable intent, after
staging, after synthetic source replacement, and after receipt publication.
It checks historical completion, no inference from identical bytes/ABA,
missing/corrupt/mismatched records, denial, project/owner isolation,
independent input preservation, and concurrent admissions. The synthetic
source writer exists only in the probe.

### Commit boundary inspection (378cb590 follow-up)

The existing `ConfirmReviewed` calls `FileStream.CommitPlan` or `Commit`,
then separately accepts and acknowledges the selected draft. Both commit
functions return only the string `applied` after their source-lease write
loop, not a durable operation-bound attestation. `WriteAtomic` uses
`File.WriteAllText` followed by `File.Move` and does not flush the file or its
parent directory. Consequently an adapter calling completion after the
current `applied` result would not establish the required durable transaction
identity. No receipt is connected to this lifecycle, no faster Save route is
enabled, and identical file bytes are still insufficient to infer success.
A future opt-in integration needs a commit-authority operation binding and a
verified durable replacement/publication protocol before UI recovery testing;
Windows still requires its own durability adapter.

## Isolated Linux exchange proof (not enabled in the editor)

The standalone `DurableLocalDataExchange` primitive exercises one existing
owner-writable ordinary .celem file, with a private recovery directory on the
same filesystem. It does not change the project format, editor Save, or
Review semantics. Admission binds the exact intent, project/owner, original
inode and content, candidate content, and request/checkpoint fingerprints.
It holds the existing cooperative source transaction lease. A flushed
prepared record binds two pinned hard-link witnesses. Linux
`renameat2(RENAME_EXCHANGE)` swaps the candidate and source atomically,
retaining the displaced inode. Both files and containing directories are
flushed before publishing the receipt.

After a process kill, the exact exchanged inode pair can be recognized even
before the receipt exists, and an explicit seal can publish its attestation
without writing the source again. A merely prepared pair never authorizes
replay. Missing or inconsistent evidence remains uncertain; equal bytes on
a replacement inode are not success. A completed receipt is historical,
not evidence that the source is still unchanged.

Run the isolated native child-process probe:
`dotnet run -c Release --project tests/probes/direct-data-exchange`.
It kills workers at eight boundaries, restarts classification and seal in
fresh processes, races a duplicate cooperative writer, tests external
replacement before/after the last check and same-byte/ABA replacement, and
checks the independent file is preserved.

**Limits:** this is not production compare-and-swap against noncooperating
writers. A writer racing the final comparison can be displaced by the
exchange; its bytes remain in the stage and recovery is required, not
automatic rollback or success. The experiment assumes trusted private
recovery and stable directory ancestry, rejects aliased sources, extended
metadata/ACLs, and nonordinary files. Witness retirement is deliberately
unspecified; retained links currently prevent another edit to that file.
The test proves process-crash recovery on the tested Linux filesystem, not
physical power-loss behavior, Windows portability, or semantic validation.
Do not connect this to product Save until these limitations, retention,
authoritative graph validation, and actual editor recovery integration
are resolved.
