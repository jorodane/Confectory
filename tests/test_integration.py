from __future__ import annotations

import hashlib
import json
import os
import shutil
import unittest
from pathlib import Path

from confectory.build import Builder
from confectory.declarations import BuildError
from tests.support import Fixture, REPO, execute


SDK_AVAILABLE = bool(os.environ.get("CONFECTORY_DOTNET") or shutil.which("dotnet"))


@unittest.skipUnless(SDK_AVAILABLE, "Install .NET 8 SDK / set CONFECTORY_DOTNET for real compilation and execution")
class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.addCleanup(self.f.close)

    def build(self, target="portable"):
        return Builder(self.f.project, target).build()

    def output(self, report, expected):
        result = execute(report)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(expected + "\n", result.stdout)

    def error(self, code, call):
        with self.assertRaises(BuildError) as ctx:
            call()
        self.assertEqual(code, ctx.exception.diagnostic["code"], str(ctx.exception))
        return ctx.exception

    def test_actual_linked_output_and_public_catalog(self):
        report = self.build()
        self.output(report, "5")
        self.assertEqual(["App", "Provider"], report["statistics"]["compiledPacks"])
        self.assertIn("Unused", report["excludedPacks"])
        self.assertIn("Confectory.Build.DotNet", report["excludedPacks"])
        self.assertFalse(any(p.endswith("Dormant.celem") for p in report["statistics"]["readDocuments"]))
        catalog_text = Path(report["publicCatalog"]).read_text()
        catalog = json.loads(catalog_text)
        self.assertEqual(1, catalog["formatVersion"])
        self.assertEqual("linked-elements", catalog["surface"])
        self.assertEqual({"App::Main", "Api::Value"}, {i["id"] for i in catalog["functions"]})
        self.assertTrue(any(i["id"] == "Provider::ValueBody" for i in catalog["implementations"]))
        self.assertFalse(catalog["coreProvidesRuntimeModLoader"])
        self.assertNotIn(str(self.f.root), catalog_text)
        self.assertFalse(list(Path(report["output"]).glob("*.ref.dll")))

    def test_contract_only_compile_without_provider_and_reuse_at_final_link(self):
        del self.f.packs["Provider"]
        del self.f.packs["App"]["dependencies"]["Provider"]
        self.f.main()
        self.f.sync()
        local = Builder(self.f.project, "portable").check("App")
        self.assertEqual("contract-only", local["mode"])
        self.assertEqual(b"MZ", Path(local["artifact"]["assembly"]).read_bytes()[:2])
        self.assertFalse(any("Provider" in p for p in local["statistics"]["readDocuments"]))
        self.error("MISSING_IMPLEMENTATION", self.build)
        self.f.new_pack("Provider", {"Api": "1"})
        self.f.add("Provider", "implementation", "ValueBody", 'implementation Provider::ValueBody for Api::Value (int n) -> int { body common "value.csbody"; }')
        self.f.body("Provider", "value.csbody", "return n + 3;")
        self.f.packs["App"]["dependencies"]["Provider"] = "1"
        self.f.main("provide Api::Value with Provider::ValueBody;")
        self.f.sync()
        final = self.build()
        self.output(final, "5")
        self.assertEqual(local["artifact"]["assembly"], final["implementationArtifacts"]["App"]["assembly"])
        self.assertEqual(["Provider"], final["statistics"]["compiledPacks"])

    def test_unchanged_build_and_provider_only_change(self):
        first = self.build()
        self.output(first, "5")
        caller = Path(first["implementationArtifacts"]["App"]["assembly"])
        before = (hashlib.sha256(caller.read_bytes()).hexdigest(), caller.stat().st_mtime_ns)
        second = self.build()
        self.output(second, "5")
        self.assertEqual([], second["statistics"]["compiledPacks"])
        self.assertEqual([], second["statistics"]["compiledContracts"])
        self.assertEqual([], second["statistics"]["readDocuments"])
        self.f.body("Provider", "value.csbody", "return n + 9;")
        changed = self.build()
        self.output(changed, "11")
        self.output(first, "5")
        self.assertEqual(["Provider"], changed["statistics"]["compiledPacks"])
        self.assertEqual(["App"], changed["statistics"]["reusedPacks"])
        self.assertEqual(before, (hashlib.sha256(caller.read_bytes()).hexdigest(), caller.stat().st_mtime_ns))
        self.assertEqual([], changed["statistics"]["parsedDocuments"])
        self.assertEqual([str(self.f.packs["Provider"]["root"] / "value.csbody")], changed["statistics"]["readDocuments"])

    def test_contract_change_rechecks_consumers_and_rebuilds_only_affected_packs(self):
        self.f.new_pack("Stable")
        self.f.packs["App"]["dependencies"]["Stable"] = "1"
        self.f.add("Stable", "function", "Ping", 'function Stable::Ping () -> int { provide Stable::Ping with Stable::PingBody; }')
        self.f.add("Stable", "implementation", "PingBody", 'implementation Stable::PingBody for Stable::Ping () -> int { body common "ping.csbody"; }')
        self.f.body("Stable", "ping.csbody", "return 7;")
        self.f.always = ["Stable::Ping"]
        self.f.sync()
        first = self.build()
        self.f.add("Api", "function", "Value", "function Api::Value (int n) -> long {}")
        self.f.add("Provider", "implementation", "ValueBody", 'implementation Provider::ValueBody for Api::Value (int n) -> long { body common "value.csbody"; }')
        self.error("CONTRACT_MISMATCH", self.build)
        self.f.add("App", "implementation", "MainBody", 'implementation App::MainBody for App::Main () -> int { import Api::Value as Value (int) -> long; body common "main.csbody"; }')
        changed = self.build()
        self.output(changed, "5")
        self.assertEqual(["App", "Provider"], changed["statistics"]["compiledPacks"])
        self.assertEqual(["Stable"], changed["statistics"]["reusedPacks"])
        self.assertEqual(["Api::Value"], changed["statistics"]["compiledContracts"])
        self.assertEqual(first["implementationArtifacts"]["Stable"]["assembly"], changed["implementationArtifacts"]["Stable"]["assembly"])
        self.assertTrue({"App::Main", "Api::Value", "Stable::Ping"} <= set(changed["statistics"]["checkedContracts"]))

    def test_unrelated_contract_in_same_pack_does_not_invalidate_consumers(self):
        self.f.add("Api", "function", "UnusedContract", "function Api::UnusedContract (int n) -> int {}")
        self.f.sync()
        self.build()
        self.f.add("Api", "function", "UnusedContract", "function Api::UnusedContract (string n) -> string {}")
        report = self.build()
        self.output(report, "5")
        self.assertEqual([], report["statistics"]["compiledPacks"])
        self.assertEqual([], report["statistics"]["compiledContracts"])
        self.assertFalse(any(p.endswith("UnusedContract.celem") for p in report["statistics"]["readDocuments"]))

    def test_target_specific_common_fallback_and_linux_launcher(self):
        common = self.build("portable")
        self.output(common, "5")
        linux = self.build("linux")
        self.output(linux, "32")
        self.assertEqual("run", Path(linux["run"][0]).name)
        self.f.add("Provider", "implementation", "ValueBody", 'implementation Provider::ValueBody for Api::Value (int n) -> int { body common "value.csbody"; }')
        fallback = self.build("linux")
        self.output(fallback, "5")
        catalog = json.loads(Path(fallback["publicCatalog"]).read_text())
        self.assertEqual("common", next(i for i in catalog["implementations"] if i["id"] == "Provider::ValueBody")["bodySelection"])

    def test_broken_selected_target_body_does_not_fall_back(self):
        good = self.build("linux")
        self.f.body("Provider", "value_linux.csbody", 'return "wrong type";')
        ex = self.error("TARGET_FAILURE", lambda: self.build("linux"))
        self.assertIn("value_linux.csbody", str(ex))
        self.output(good, "32")

    def test_recursive_function_calls_execute(self):
        self.f.add("Provider", "implementation", "ValueBody", 'implementation Provider::ValueBody for Api::Value (int n) -> int { import Api::Value as Self (int) -> int; body common "value.csbody"; }')
        self.f.body("Provider", "value.csbody", "if (n <= 0) return 0; return n + calls.Self.Invoke(n - 1);")
        self.output(self.build(), "3")

    def test_independent_scopes_and_inherited_bindings_execute(self):
        self.f.second_provider()
        self.f.module("Default", "Provider::Second")
        self.f.add("App", "object", "Parent", "object App::Parent { provide Api::Value with Provider::ValueBody; }")
        self.f.add("App", "object", "Child", "object App::Child extends App::Parent { module App::Default; }")
        self.f.add("App", "object", "Other", "object App::Other { module App::Default; }")
        self.f.main()
        self.f.add("App", "implementation", "MainBody", 'implementation App::MainBody for App::Main () -> int { import Api::Value as First (int) -> int in App::Child; import Api::Value as Second (int) -> int in App::Other; body common "main.csbody"; }')
        self.f.body("App", "main.csbody", 'Console.WriteLine($"{calls.First.Invoke(2)}/{calls.Second.Invoke(2)}"); return 0;')
        self.f.sync()
        self.output(self.build(), "5/102")

    def test_inherited_cross_pack_references_keep_original_owner_dependencies(self):
        self.f.new_pack("Parents", {"Api": "1", "Provider": "1"})
        self.f.packs["App"]["dependencies"]["Parents"] = "1"
        del self.f.packs["App"]["dependencies"]["Provider"]
        self.f.add("Parents", "object", "Parent", "object Parents::Parent { provide Api::Value with Provider::ValueBody; }")
        self.f.add("App", "object", "Child", "object App::Child extends Parents::Parent {}")
        self.f.main()
        self.f.add("App", "implementation", "MainBody", 'implementation App::MainBody for App::Main () -> int { import Api::Value as Value (int) -> int in App::Child; body common "main.csbody"; }')
        self.f.sync()
        self.output(self.build(), "5")

    def test_implementation_inherits_target_body_from_owning_pack(self):
        self.f.new_pack("Derived", {"Api": "1", "Provider": "1"})
        self.f.packs["App"]["dependencies"]["Derived"] = "1"
        self.f.add("Derived", "implementation", "Body", "implementation Derived::Body for Api::Value (int n) -> int extends Provider::ValueBody {}")
        self.f.main("provide Api::Value with Derived::Body;")
        self.f.sync()
        report = self.build()
        self.output(report, "5")
        self.assertEqual(["App", "Derived"], report["statistics"]["compiledPacks"])

    def test_private_implementation_class_cannot_be_an_authoring_reference(self):
        from confectory.generation import implementation
        provider_class = implementation("Provider::ValueBody")
        self.f.body("App", "main.csbody", f"return new {provider_class}(null!).Invoke(2);")
        ex = self.error("TARGET_FAILURE", self.build)
        self.assertIn("main.csbody", str(ex))

    def test_csharp_body_is_type_checked_against_generated_contract(self):
        self.f.body("App", "main.csbody", 'Console.WriteLine(calls.Value.Invoke("wrong argument")); return 0;')
        ex = self.error("TARGET_FAILURE", self.build)
        self.assertIn("main.csbody", str(ex))
        self.assertIn("CS1503", str(ex))

    def test_inherited_build_target_uses_parent_owned_tool(self):
        self.f.new_pack("CustomTarget", {"Confectory.Build.DotNet": "0.1.0"})
        self.f.packs["App"]["dependencies"]["CustomTarget"] = "1"
        self.f.add("CustomTarget", "buildtarget", "Portable", "buildtarget CustomTarget::Portable extends Confectory.Build.DotNet::Portable {}")
        self.f.targets["portable"] = "CustomTarget::Portable"
        self.f.sync()
        self.output(self.build(), "5")

    def test_distinct_module_defaults_and_missing_target_fail_before_execution(self):
        self.f.second_provider()
        self.f.module("M1")
        self.f.module("M2", "Provider::Second")
        self.f.main("module App::M1; module App::M2;")
        self.f.sync()
        self.error("DEFAULT_CONFLICT", self.build)
        self.f.main("provide Api::Value with Provider::ValueBody;")
        self.f.add("Provider", "implementation", "ValueBody", 'implementation Provider::ValueBody for Api::Value (int n) -> int { body other "value.csbody"; }')
        self.error("MISSING_TARGET_IMPLEMENTATION", self.build)

    def test_addition_of_a_newer_pack_does_not_change_project_selected_version(self):
        first = self.build()
        newer = self.f.root / "engine-updates/Api-2"
        newer.mkdir(parents=True)
        (newer / "pack.cpack").write_text('pack Api version "2" { element Value function "Value.celem"; }')
        (newer / "Value.celem").write_text('function Api::Value (string n) -> string {}')
        unchanged = self.build()
        self.output(unchanged, "5")
        self.assertEqual([], unchanged["statistics"]["compiledPacks"])
        self.assertEqual(first["contractArtifacts"]["Api::Value"]["assembly"], unchanged["contractArtifacts"]["Api::Value"]["assembly"])
        catalog = json.loads(Path(unchanged["publicCatalog"]).read_text())
        self.assertEqual("1", next(p for p in catalog["packs"] if p["namespace"] == "Api")["version"])

    def test_corrupted_local_artifact_is_rebuilt(self):
        first = self.build()
        Path(first["implementationArtifacts"]["App"]["assembly"]).write_bytes(b"corrupted")
        repaired = self.build()
        self.output(repaired, "5")
        self.assertEqual(["App"], repaired["statistics"]["compiledPacks"])
        self.assertEqual(["Provider"], repaired["statistics"]["reusedPacks"])

    def test_tool_source_change_invalidates_local_artifacts(self):
        self.build()
        tool = self.f.root / "target/tool.py"
        tool.write_text(tool.read_text() + "\n# tool revision changed\n")
        changed = self.build()
        self.output(changed, "5")
        self.assertEqual(["App", "Provider"], changed["statistics"]["compiledPacks"])

    def test_failure_preserves_latest_successful_runnable_output(self):
        first = self.build()
        latest = self.f.project.parent / ".confectory/outputs/portable/latest.json"
        before = latest.read_bytes()
        self.f.body("Provider", "value.csbody", "this is not C#;")
        self.error("TARGET_FAILURE", self.build)
        self.assertEqual(before, latest.read_bytes())
        self.output(first, "5")
        self.assertFalse(list((self.f.project.parent / ".confectory").rglob("*.pending")))

    def test_selected_versions_warn_without_breaking_executable(self):
        self.f.packs["App"]["dependencies"]["Api"] = "99"
        self.f.sync()
        report = self.build()
        self.output(report, "5")
        self.assertEqual("VERSION_MISMATCH", report["warnings"][0]["code"])

    def test_contract_location_move_keeps_identity_and_local_dlls(self):
        first = self.build()
        pack = self.f.packs["Api"]
        old = pack["root"] / "Value.celem"
        moved = pack["root"] / "moved.celem"
        old.rename(moved)
        pack["elements"]["Value"]["path"] = "moved.celem"
        self.f.sync()
        report = self.build()
        self.output(report, "5")
        self.assertEqual([], report["statistics"]["compiledPacks"])
        self.assertEqual(first["contractArtifacts"]["Api::Value"]["assembly"], report["contractArtifacts"]["Api::Value"]["assembly"])

    def test_local_compilation_reads_do_not_grow_with_unrelated_element_documents(self):
        small = Builder(self.f.project, "portable").check("App")
        large = Fixture()
        self.addCleanup(large.close)
        for i in range(40):
            ns = "Extra" + str(i)
            large.new_pack(ns)
            large.add(ns, "object", "Data", "invalid and deliberately unopened")
        large.sync()
        big = Builder(large.project, "portable").check("App")
        def semantic_reads(result):
            return [p for p in result["statistics"]["readDocuments"] if p.endswith((".celem", ".csbody"))]
        self.assertEqual(len(semantic_reads(small)), len(semantic_reads(big)))
        self.assertFalse(any("Extra" in p for p in semantic_reads(big)))

    def test_engine_projectpack_uses_identical_build_path(self):
        shutil.copytree(REPO / "examples/engine", self.f.root / "engine", ignore=shutil.ignore_patterns(".confectory"))
        project = self.f.root / "engine/project.cpack"
        project.write_text(project.read_text().replace('../../targets/dotnet/pack.cpack', '../target/pack.cpack'))
        report = Builder(project, "portable").build()
        self.output(report, "Confectory.Engine built as a ProjectPack")
        self.assertEqual("Confectory.Engine::Boot", report["entry"])

    def test_missing_target_and_tool_protocol_errors(self):
        self.error("MISSING_TARGET", lambda: Builder(self.f.project, "unknown"))
        tool = self.f.root / "target/tool.py"
        tool.unlink()
        self.error("MISSING_TOOL", lambda: Builder(self.f.project, "portable"))
        tool.write_text("print('not json')\n")
        self.error("TOOL_PROTOCOL", lambda: Builder(self.f.project, "portable"))
        tool.write_text('print(\'{"protocol":999,"ok":true}\')\n')
        self.error("TOOL_PROTOCOL", lambda: Builder(self.f.project, "portable"))
        tool.write_text('print(\'{"protocol":1,"ok":false,"error":"intentional tool failure"}\')\n')
        self.error("TARGET_FAILURE", lambda: Builder(self.f.project, "portable"))


if __name__ == "__main__":
    unittest.main()
