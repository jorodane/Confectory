# Windows pinned-resource checkout fix

The user reported an actual Windows `Confectory.bat` crash in WebUI Open: `Resource size mismatch or budget exceeded`. The Windows machine is not accessible here. A normal Git checkout with `core.autocrlf=true` reproduces the failing condition using the original EditorHome resource manifest and loading path.

At the preceding revision there was no `.gitattributes`. Git converts several pinned text resources from LF to CRLF, while the compiled manifest retains exact repository byte sizes and SHA-256:

| Resource | Declared bytes | CRLF checkout bytes |
| --- | ---: | ---: |
| ConfectoryIcon.svg | 1,373 | 1,382 |
| app.js | 58,381 | 58,495 |
| assets/html2canvas.min.js | 198,689 | 198,708 |
| assets/portraits.json | 2,619 | 2,639 |
| consumer.css | 2,108 | 2,122 |
| style.css | 101,559 | 101,890 |

The first manifest resource is the icon, so it fails before host startup. The original manifest aggregate is below 32 MiB; the CRLF checkout aggregate is 16,711,095 bytes. The largest declared resource is 2,175,342 bytes, below the 4 MiB per-resource limit. This reproduces a size/identity mismatch, not budget exhaustion. Stale output/cache is not needed to reproduce it; the supplied user stack alone cannot exclude a separately stale installation. The fix does not relax any budget or dynamically trust unchecked filesystem hashes.

## Change

`.gitattributes` pins EditorHome HTML/CSS/JS/JSON/SVG text to LF and marks PNG resources binary. Existing manifest size/hash values remain exact; ordinary Git checkout now preserves those bytes on Windows. Common WebUI Open separately reports validated resource ID, expected/actual size, per-resource limit or aggregate loaded/declared/actual budget. Hash failure names the resource and SHA-256 check; diagnostics omit absolute resource paths and data. File shrink/growth during reading remains rejected. All checks and 4/32 MiB limits stay in place, with no EditorHome exception.

## User retry

Close the running Confectory window normally. In the repository, save any local modifications before updating. Switch to `work/current` and fast-forward to the pushed fix:

```bat
git fetch origin
git switch work/current
git pull --ff-only origin work/current
git status --short -- examples/editor-home/ui
```

If the last command lists your own UI source changes, back them up before the next command. Re-materialize only the tracked UI resources from the updated HEAD; this overwrites local edits in that directory, so the preceding backup matters. It does not reset project data or user settings:

```bat
git -c core.autocrlf=false checkout --force HEAD -- examples/editor-home/ui
Confectory.bat
```

The explicit checkout handles already-present CRLF files, which a new attribute file alone need not rewrite. The existing launcher performs its normal build; broad cache deletion, settings deletion, SDK reinstall or a global Git configuration change is unnecessary. If an error remains, send the new resource-specific diagnostic and current `git rev-parse HEAD`; an old generic message suggests an older executable/source route and needs inspection rather than guessing cache removal.

## Verification

`tests/probes/web_resource_checkout.py` makes an isolated real Git checkout with Windows autocrlf settings. It recreates the previous missing-attributes index, launches the actual compiled ordinary `examples/editor-home/project.cpack` and verifies the icon's expected/actual diagnostic. It then adds the fixed attributes, re-checks out resources, starts the same production entry and retrieves all 16 normal resource snapshots, checking exact size and SHA-256. No replacement ProjectPack/provider/test entry is supplied.

The registered `test_editor_web_resources_windows_git_checkout_and_actual_startup` passed (132.007s), and the common scope/boundary test passed (27.084s). Ordinary Linux/Windows/Android root builds report `tool.ok=true`, 37 included packs each.

Common WebUI tests separately reject wrong hash, mismatched file size, per-resource and aggregate budget exhaustion, traversal and resource count limits, alongside existing scope/revision/cancellation/disposal/locality checks. Final gate results are in AI_DEVELOPMENT_STATUS.md. These checks reproduce Git conversion and actual production resource loading on Linux; Windows `Confectory.bat`/WebView2 execution still awaits the user's retry.
