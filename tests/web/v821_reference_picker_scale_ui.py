"""Actual generic reference chooser and explicit Review/Confirm on clean large packs.

Run with REPO BUILD_REPORT 40|249|250|400 [--pick] [--malformed] [--trace-files].
For final Confirm use the built .NET target and SDK; --pick needs no compiler.
The fixture has six extra semantic declarations beyond the object-count parameter,
so 249/250 exercise the existing 255/256 declaration context boundary.
"""
import json
import sys
from playwright.sync_api import expect, sync_playwright
import v666_workspace_finder_fixture as f
from v821_project_browser_search_labels import NS, browser_window

count = int(sys.argv[3])
flags = set(sys.argv[4:])
assert count in (40, 249, 250, 400)
assert flags <= {"--pick", "--malformed", "--trace-files"}
assert "--malformed" not in flags or "--pick" in flags
FIRST, SECOND = "Reference First", "Reference Second"
TARGETS = {"TargetZero": "Zero label", "TargetNonzero": "Nonzero label", "TargetAbsent": "Absent label"}
prefix = NS + "::"
for manifest, peer in zip(f.projects, (False, True)):
    label = lambda name: ("Peer " if peer else "") + TARGETS[name]
    declarations = {
        "TargetInfo": ("schema", "field Count single general long;"),
        "LinkInfo": ("schema", f"field Target single reference {prefix}TargetInfo; field Note single general string;"),
        "TargetZero": ("object", f'use schema {prefix}TargetInfo; data Count = 0; value editorName = "{label("TargetZero")}";'),
        "TargetNonzero": ("object", f'use schema {prefix}TargetInfo; data Count = 7; value editorName = "{label("TargetNonzero")}";'),
        "TargetAbsent": ("object", f'use schema {prefix}TargetInfo; value editorName = "{label("TargetAbsent")}";'),
        "WrongTarget": ("object", 'value editorName = "Wrong label";'),
        "SourceLink": ("object", f'use schema {prefix}LinkInfo; data Target = {prefix}TargetZero; data Note = "Keep note";'),
    }
    for i in range(count - 5):
        declarations[f"Extra{i:04}"] = ("object", f'value editorName = "Extra {i:04}";')
    entries = []
    for name, (kind, body) in declarations.items():
        path = manifest.parent / f"{name}.celem"
        text = f"{kind} {prefix}{name} {{ {body} }}\n"
        if "--malformed" in flags and name == "Extra0000" and not peer:
            text = f"object {prefix}{name} {{ !"
        path.write_text(text)
        f.before[str(path)] = path.read_bytes()
        entries.append(f'element {name} {kind} "{path.name}";')
    manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" + "\n".join(entries) + "\n}\n")
    f.before[str(manifest)] = manifest.read_bytes()
profile = f.root / "profile"
profile.mkdir(exist_ok=True)
(profile / "projects.json").write_text(json.dumps([{"path": str(p), "title": t, "description": ""} for p, t in zip(f.projects, (FIRST, SECOND))]))
source = f.projects[0].parent / "SourceLink.celem"
trace = f.root / "files.log"
if "--trace-files" in flags:
    f.report["run"] = ["strace", "-f", "-s", "256", "-e", "trace=execve,openat", "-o", str(trace), *f.report["run"]]
expect.set_options(timeout=120000)

def idle(page):
    expect(page.locator("#project-menu")).to_be_enabled()

def enter(page, title):
    page.get_by_role("button", name="Confectory 홈으로").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.locator(".project-card").filter(has=page.get_by_role("heading", name=title, exact=True)).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(title)

def owner(page):
    idle(page)
    w = browser_window(page)
    w.get_by_role("textbox", name="의미 객체 검색", exact=True).fill("SourceLink")
    w.get_by_role("button", name="검색 확정", exact=True).click()
    row = w.locator(f'[data-object="{prefix}SourceLink"]')
    expect(row).to_be_visible()
    idle(page)
    row.click(button="right")
    page.locator(".context-menu").get_by_role("button", name="스키마 열기", exact=True).click()
    editor = page.locator('.window[data-key="schema"]')
    expect(editor.locator(".object-title-name")).to_have_text("SourceLink")
    return editor

def picker(editor, labels):
    editor.get_by_role("button", name="Target 기본값 선택", exact=True).click()
    dialog = editor.page.get_by_role("dialog", name="기본값 선택", exact=True)
    expect(dialog).to_be_visible()
    expect(dialog.locator("[data-reference-choice]")).to_have_count(3)
    for name, label in labels.items():
        expect(dialog.locator(f'[data-reference-choice="{prefix}{name}"]')).to_contain_text(label)
    expect(dialog.locator(f'[data-reference-choice="{prefix}WrongTarget"]')).to_have_count(0)
    expect(dialog.locator(f'[data-reference-choice="{prefix}Extra0000"]')).to_have_count(0)
    return dialog

def choose(dialog, name):
    dialog.locator(f'[data-reference-choice="{prefix}{name}"]').click()
    expect(dialog).to_be_hidden()

def confirm(page, editor, old, new):
    button = editor.locator('[data-element-action="confirm"]')
    # References must remain in the existing explicit review policy.
    expect(button).to_have_text("확정")
    expect(button).to_be_enabled()
    button.click()
    group = page.get_by_role("dialog", name="관련 변경 검토", exact=True)
    expect(group).to_be_visible()
    assert f"data Target = {prefix}{old}" in source.read_text()
    group.locator("#review-creation").click()
    review = page.locator('.window[data-key="review"]')
    expect(review).to_be_visible()
    assert f"data Target = {prefix}{old}" in source.read_text()
    if review.locator("[data-review-advanced]").count():
        review.locator("[data-review-advanced]").click()
        if review.locator("[data-advanced-reviewed]").count():
            review.locator("[data-advanced-reviewed]").check()
    review.locator("#confirm").click()
    expect(review).to_be_hidden()
    idle(page)
    assert f"data Target = {prefix}{new}" in source.read_text(), page.locator("#status").inner_text()
    assert 'data Note = "Keep note"' in source.read_text()
    f.before[str(source)] = source.read_bytes()
    f.original()

def trace_counts():
    if not trace.exists():
        return (0, 0)
    lines = trace.read_text(errors="replace").splitlines()
    return (sum("execve(" in x and ("csc.dll" in x or '"-noconfig"' in x) for x in lines),
            sum("openat(" in x and any(str(p.parent) in x for p in f.projects) and '.dll"' in x for x in lines))

def refused(editor):
    editor.get_by_role("button", name="Target 기본값 선택", exact=True).click()
    expect(editor.page.locator("#status")).to_contain_text("완료하지 못했습니다")
    expect(editor.page.get_by_role("dialog", name="기본값 선택", exact=True)).to_have_count(0)
    idle(editor.page)

try:
    f.start(0)
    with sync_playwright() as p, p.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
        page = f.setup(browser)
        page.set_default_timeout(120000)
        editor = owner(page)
        ref = editor.get_by_role("button", name="Target 기본값 선택", exact=True)
        expect(ref).to_have_text(TARGETS["TargetZero"])
        if "--malformed" in flags and count == 40:
            # The small existing full-overlay path rejects malformed declarations.
            refused(editor)
            print("PASS malformed unrelated source fails closed in full overlay", flush=True)
        else:
            dialog = picker(editor, TARGETS)
            choose(dialog, "TargetNonzero")
            expect(ref).to_have_text(TARGETS["TargetNonzero"])
            expect(editor.get_by_label("Note 기본값", exact=True)).to_have_value("Keep note")
            assert source.read_bytes() == f.before[str(source)]
            if "--trace-files" in flags:
                assert trace_counts() == (0, 0), trace_counts()
                print("selector compiler invocations 0; project DLL opens 0", flush=True)
            print("PASS exact valid zero/nonzero/absent target IDs, invalid targets excluded", count, flush=True)
            if "--pick" not in flags:
                confirm(page, editor, "TargetZero", "TargetNonzero")
                editor.get_by_role("button", name="창 닫기", exact=True).click()
                editor = owner(page)
                ref = editor.get_by_role("button", name="Target 기본값 선택", exact=True)
                expect(ref).to_have_text(TARGETS["TargetNonzero"])
                choose(picker(editor, TARGETS), "TargetAbsent")
                expect(ref).to_have_text(TARGETS["TargetAbsent"])
                confirm(page, editor, "TargetNonzero", "TargetAbsent")
                choose(picker(editor, TARGETS), "TargetZero")
                expect(ref).to_have_text(TARGETS["TargetZero"])
                confirm(page, editor, "TargetAbsent", "TargetZero")
                if "--trace-files" in flags:
                    assert trace_counts() == (0, 0), trace_counts()
                    print("confirmed pure leaf references: compiler and project DLL opens 0", flush=True)
                print("PASS explicit Review/Confirm for all three targets and reopened exact value", count, flush=True)
                enter(page, SECOND)
                peer = owner(page)
                peer_labels = {name: "Peer " + label for name, label in TARGETS.items()}
                choose(picker(peer, peer_labels), "TargetZero")
                expect(peer.get_by_role("button", name="Target 기본값 선택", exact=True)).to_have_text(peer_labels["TargetZero"])
                renamed = f.projects[0].parent / "TargetNonzero.celem"
                renamed.write_text(renamed.read_text().replace("Nonzero label", "Renamed label"))
                f.before[str(renamed)] = renamed.read_bytes()
                labels = {**TARGETS, "TargetNonzero": "Renamed label"}
                enter(page, FIRST)
                editor = owner(page)
                choose(picker(editor, labels), "TargetZero")
                print("PASS fresh renamed candidate label and same-ID project isolation", count, flush=True)
                note = editor.get_by_label("Note 기본값", exact=True)
                note.fill("Unsaved local input")
                choose(picker(editor, labels), "TargetZero")
                expect(note).to_have_value("Unsaved local input")
                original = source.read_bytes()
                source.write_bytes(original + b"\n// external owner edit\n")
                try:
                    refused(editor)
                    expect(note).to_have_value("Unsaved local input")
                    assert source.read_bytes() == original + b"\n// external owner edit\n"
                finally:
                    source.write_bytes(original)
                choose(picker(editor, labels), "TargetZero")
                mode = renamed.stat().st_mode
                renamed.chmod(0)
                try:
                    refused(editor)
                    expect(note).to_have_value("Unsaved local input")
                finally:
                    renamed.chmod(mode)
                choose(picker(editor, labels), "TargetZero")
                unrelated = f.projects[0].parent / "Extra0000.celem"
                raw = unrelated.read_bytes()
                unrelated.write_text(f"object {prefix}Extra0000 {{ !")
                try:
                    refused(editor)
                    expect(note).to_have_value("Unsaved local input")
                finally:
                    unrelated.write_bytes(raw)
                choose(picker(editor, labels), "TargetZero")
                f.original()
                print("PASS changed owner, unreadable target and unrelated external malformed source refuse selection and retain input", count, flush=True)
        f.original()
        assert not f.errors and not f.external, (f.errors, f.external)
finally:
    f.stop()
    if "--trace-files" in flags:
        print("final compiler invocations, project DLL opens", trace_counts(), flush=True)
    print("evidence", f.root, flush=True)
